# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---"""

import hashlib
import sys
from pathlib import Path

prompt_path = Path(r"C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\NC-PROMPT-DS-002-worker-universal.md")
p = prompt_path.read_text(encoding="utf-8")

# Remove existing hash header if any (first line starting with <!-- PROMPT_SHA)
lines = p.splitlines(keepends=True)
if lines and lines[0].startswith("<!-- PROMPT_SHA"):
    lines = lines[1:]
    p = "".join(lines)

h12 = hashlib.sha256(p.encode()).hexdigest()[:12]
print(f"PROMPT_SHA12: {h12}")
print(f"chars: {len(p)}")

# Prepend integrity header
new_content = f"<!-- PROMPT_SHA12:{h12}  workers: verificar hash antes de executar -->\n" + p
prompt_path.write_text(new_content, encoding="utf-8")
print(f"Header adicionado: <!-- PROMPT_SHA12:{h12} -->")
