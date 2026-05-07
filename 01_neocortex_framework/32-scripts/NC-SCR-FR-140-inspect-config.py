# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation', 'configuration']
hash: "auto-generated"
---
"""

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation', 'configuration']
hash: "auto-generated"
---
"""

if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation', 'configuration']
hash: "auto-generated"
---"""

import sys

sys.path.insert(0, ".")
from neocortex.config import get_config

config = get_config()
print("llm_config:", config.llm_config)
print("Type:", type(config.llm_config))
if isinstance(config.llm_config, dict):
    print("Keys:", list(config.llm_config.keys()))
elif isinstance(config.llm_config, list):
    print("Length:", len(config.llm_config))
    print("First item:", config.llm_config[0] if config.llm_config else None)
