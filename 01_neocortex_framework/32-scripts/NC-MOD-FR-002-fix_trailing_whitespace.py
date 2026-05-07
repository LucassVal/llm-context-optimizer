# @UBL @UBL @MOD-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
Fix trailing whitespace in metrics_store.py
---
"""

"""---
Fix trailing whitespace in metrics_store.py
---
"""

"""
Fix trailing whitespace in metrics_store.py
"""

import re

def fix_trailing_whitespace(filepath):
    """Fix trailing whitespace in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix trailing whitespace
    fixed_lines = []
    changes = 0
    
    for i, line in enumerate(lines, 1):
        original = line
        # Remove trailing whitespace
        fixed = line.rstrip() + '\n'
        if original != fixed:
            changes += 1
            print(f"Line {i}: Fixed trailing whitespace")
        fixed_lines.append(fixed)
    
    if changes > 0:
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print(f"Fixed {changes} lines with trailing whitespace")
    else:
        print("No trailing whitespace found")
    
    return changes

if __name__ == "__main__":
    filepath = r"neocortex/infra/metrics_store.py"
    fix_trailing_whitespace(filepath)
