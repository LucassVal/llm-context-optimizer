#!/usr/bin/env python3
"""
Clean security.py tool module.
"""

from pathlib import Path

SECURITY_PATH = Path(r"neocortex_framework/neocortex/mcp/tools/security.py")


def main():
    content = SECURITY_PATH.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the line with MAIN comment
    main_start = -1
    for i, line in enumerate(lines):
        if "# ==================== MAIN ====================" in line:
            main_start = i
            break

    if main_start == -1:
        print("Main comment not found, file already clean?")
        return

    # Find the line with 'return tool_security' after main_start
    return_line = -1
    for i in range(main_start, len(lines)):
        if lines[i].strip() == "return tool_security":
            return_line = i
            break

    if return_line == -1:
        print("Return statement not found")
        return

    # Keep lines up to main_start (exclusive) and the return line
    new_lines = lines[:main_start] + [lines[return_line]]

    # Write back
    SECURITY_PATH.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"Cleaned {SECURITY_PATH}")


if __name__ == "__main__":
    main()
