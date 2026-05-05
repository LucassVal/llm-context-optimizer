import os
import re
import sys

src_path = r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION"
terms = ["kairos", "timer", "daemon", "scheduler", "tick"]
output_dir = r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\DIR-RES-CC-001-claude-leak-workzone\analysis-session-a\temp"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read list of KAIROS files from previous grep
kairos_files = []
kairos_list_path = r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\DIR-RES-CC-001-claude-leak-workzone\analysis-session-b\temp\KAIROS_files.txt"
if os.path.exists(kairos_list_path):
    with open(kairos_list_path, "r", encoding="utf-8") as f:
        kairos_files = [line.strip() for line in f if line.strip()]

print(f"Found {len(kairos_files)} files with KAIROS")

# Search for terms in all source files
for term in terms:
    matches = []
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx", ".py")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if re.search(
                            r"\b" + re.escape(term) + r"\b", content, re.IGNORECASE
                        ):
                            matches.append(filepath)
                except Exception as e:
                    try:
                        with open(filepath, "r", encoding="latin-1") as f:
                            content = f.read()
                            if re.search(
                                r"\b" + re.escape(term) + r"\b", content, re.IGNORECASE
                            ):
                                matches.append(filepath)
                    except:
                        pass
    print(f"{term}: {len(matches)} files")
    out_file = os.path.join(output_dir, f"{term}_files.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        for match in matches:
            f.write(match + "\n")

# Extract snippets from top KAIROS files
print("\nExtracting snippets from key KAIROS files...")
key_files = [
    r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION\free-code\src\interactiveHelpers.tsx",
    r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION\free-code\src\tools.ts",
    r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION\free-code\src\bridge\bridgeMain.ts",
    r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION\free-code\src\main.tsx",
    r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION\free-code\src\commands.ts",
]

snippets = []
for filepath in key_files:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if re.search(
                        r"\b(kairos|tick|timer|daemon|scheduler)\b", line, re.IGNORECASE
                    ):
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        snippet = "".join(lines[start:end])
                        snippets.append(
                            f"=== {os.path.basename(filepath)} lines {start + 1}-{end} ===\n{snippet}\n"
                        )
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

snippets_file = os.path.join(output_dir, "kairos_snippets.txt")
with open(snippets_file, "w", encoding="utf-8") as f:
    f.write("\n".join(snippets))
print(f"Written snippets to {snippets_file}")
