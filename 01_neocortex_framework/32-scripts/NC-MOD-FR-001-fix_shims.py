# @UBL @UBL @MOD-FR | LEXICO: #SCRIPTS
"""---
Módulo: NC MOD FR 001 fix_shims
---
"""


import os
import re

core_dir = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\core"

for filename in os.listdir(core_dir):
    if filename.endswith(".py") and not filename.startswith("NC-") and filename != "agent_service.py":
        filepath = os.path.join(core_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "_util.module_from_spec(_spec)" in content and "_spec.loader.exec_module(_mod)" in content:
            # Add package
            if "_mod.__package__ = __package__" not in content:
                content = content.replace(
                    "_mod = _util.module_from_spec(_spec)\n_spec.loader.exec_module(_mod)",
                    "_mod = _util.module_from_spec(_spec)\n_mod.__package__ = __package__\n_spec.loader.exec_module(_mod)"
                )
            
            # Replace literal spec names with __name__ + "_impl"
            content = re.sub(
                r'_spec = _util\.spec_from_file_location\("[^"]+", _NC_FILE\)',
                r'_spec = _util.spec_from_file_location(__name__ + "_impl", _NC_FILE)',
                content
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed {filename}")
