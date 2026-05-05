import os
import re
import sys

src_path = r"C:\Users\Lucas Valrio\Desktop\CLAUDE_CODE_DISSECTION\free-code\src"
terms = [
    "KAIROS",
    "tick",
    "SendUserFile",
    "PushNotification",
    "SubscribePR",
    "BRIDGE_MODE",
    "VOICE_MODE",
    "AFK",
    "ULTRAPLAN",
    "TELEPORT_LOCAL",
    "DRM",
    "license",
    "telemetry",
    "obfuscat",
]
output_dir = r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\DIR-RES-CC-001-claude-leak-workzone\analysis-session-b\temp"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for term in terms:
    matches = []
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith((".ts", ".tsx")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if re.search(
                            r"\b" + re.escape(term) + r"\b", content, re.IGNORECASE
                        ):
                            matches.append(filepath)
                except Exception as e:
                    # fallback to latin-1 or ignore
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
