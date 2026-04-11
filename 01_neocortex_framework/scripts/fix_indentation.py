#!/usr/bin/env python3
"""
Fix indentation for tool modules.
"""

import re
from pathlib import Path

TOOLS_DIR = Path(r"neocortex_framework/neocortex/mcp/tools")


def fix_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Find the line with 'def tool_' inside register_tool
    in_register = False
    tool_func_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("def register_tool"):
            in_register = True
        elif in_register and line.strip().startswith("def tool_"):
            tool_func_start = i
            break

    if tool_func_start == -1:
        print(f"  WARNING: Could not find tool function in {file_path.name}")
        return

    # Find the line with the decorator just before the function
    decorator_line = tool_func_start - 1
    if not lines[decorator_line].strip().startswith("@mcp.tool"):
        print(f"  WARNING: Decorator not found before function in {file_path.name}")
        return

    # From decorator_line to end of function (find line with same indentation as 'def tool_')
    # Determine base indentation of the function definition
    func_def_line = lines[tool_func_start]
    base_indent = len(func_def_line) - len(func_def_line.lstrip())

    # Find end of function: next line with indent <= base_indent and not empty
    # Actually, we need to parse the whole function body. Simpler: we'll process the whole file
    # by adjusting indentation from tool_func_start onward.
    # Let's extract the function block by scanning lines.
    # We'll assume the function ends at the line before 'return tool_' line.
    # Find the line with 'return tool_'
    return_line = -1
    for i in range(tool_func_start + 1, len(lines)):
        if lines[i].strip().startswith("return tool_"):
            return_line = i
            break

    if return_line == -1:
        print(f"  WARNING: Return statement not found in {file_path.name}")
        return

    # Now we have the function block from tool_func_start to return_line-1
    # The decorator line should be at indent 4 (inside register_tool)
    # The function definition should be at indent 4 as well (same as decorator)
    # The body of the function should be at indent 8.
    # Currently the body lines have varying indentation (original indentation).
    # We need to normalize: find minimum indentation among body lines (excluding empty lines)
    # and shift left by that amount, then add 8 spaces.

    body_lines = lines[tool_func_start + 1 : return_line]
    if not body_lines:
        return

    # Find minimum indentation among non-empty lines
    min_indent = 1000
    for line in body_lines:
        stripped = line.strip()
        if stripped:  # non-empty
            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                min_indent = indent

    if min_indent == 1000:
        min_indent = 0

    # Adjust body lines: remove min_indent spaces, add 8 spaces
    new_body_lines = []
    for line in body_lines:
        if line.strip() == "":
            new_body_lines.append("")
        else:
            # Remove min_indent spaces (but not more than actual leading spaces)
            actual_indent = len(line) - len(line.lstrip())
            if actual_indent >= min_indent:
                line = line[min_indent:]
            # Add 8 spaces
            new_body_lines.append(" " * 8 + line)

    # Reconstruct lines
    new_lines = lines[: tool_func_start + 1] + new_body_lines + lines[return_line:]

    # Also ensure decorator line has indent 4
    if not lines[decorator_line].startswith(" " * 4):
        new_lines[decorator_line] = " " * 4 + lines[decorator_line].lstrip()

    # Ensure function definition line has indent 4
    if not new_lines[tool_func_start].startswith(" " * 4):
        new_lines[tool_func_start] = " " * 4 + new_lines[tool_func_start].lstrip()

    # Ensure return line has indent 4
    if not new_lines[return_line].startswith(" " * 4):
        new_lines[return_line] = " " * 4 + new_lines[return_line].lstrip()

    # Write back
    file_path.write_text("\n".join(new_lines), encoding="utf-8")


def main():
    print("Fixing indentation for all tool modules...")

    tool_files = list(TOOLS_DIR.glob("*.py"))
    for tf in tool_files:
        if tf.name == "__init__.py":
            continue
        print(f"  Fixing {tf.name}...")
        fix_file(tf)

    print("Done!")


if __name__ == "__main__":
    main()
