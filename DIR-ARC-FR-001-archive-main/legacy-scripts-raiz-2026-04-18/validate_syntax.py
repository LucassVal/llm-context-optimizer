import glob
import subprocess
import sys
import os


def validate_py_files():
    root = "01_neocortex_framework_RENAMED"
    py_files = glob.glob(os.path.join(root, "**", "*.py"), recursive=True)
    total = len(py_files)
    print(f"Validating {total} Python files...")

    errors = []
    success = 0

    for i, file in enumerate(py_files, 1):
        try:
            # Use subprocess to run python -m py_compile
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                success += 1
            else:
                errors.append(
                    {"file": file, "stderr": result.stderr, "stdout": result.stdout}
                )
        except subprocess.TimeoutExpired:
            errors.append({"file": file, "error": "Timeout"})
        except Exception as e:
            errors.append({"file": file, "error": str(e)})

        if i % 20 == 0:
            print(f"Progress: {i}/{total}")

    print(f"\nValidation complete: {success}/{total} succeeded, {len(errors)} errors.")

    # Write errors to file
    with open("syntax_validation_errors.txt", "w", encoding="utf-8") as f:
        f.write("Syntax Validation Report\n")
        f.write(f"Total files: {total}\n")
        f.write(f"Success: {success}\n")
        f.write(f"Errors: {len(errors)}\n\n")
        for err in errors:
            f.write(f"File: {err['file']}\n")
            if "stderr" in err and err["stderr"]:
                f.write(f"Stderr:\n{err['stderr']}\n")
            if "stdout" in err and err["stdout"]:
                f.write(f"Stdout:\n{err['stdout']}\n")
            if "error" in err:
                f.write(f"Error: {err['error']}\n")
            f.write("-" * 80 + "\n")

    # Also print first few errors
    if errors:
        print("\nFirst 5 errors:")
        for err in errors[:5]:
            print(
                f"  {err['file']}: {err.get('stderr', err.get('error', 'Unknown'))[:200]}"
            )

    return success, errors


if __name__ == "__main__":
    validate_py_files()
