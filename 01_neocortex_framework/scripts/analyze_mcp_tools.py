#!/usr/bin/env python3
"""
Analyze MCP tools and generate inventory report.
"""

import ast
import inspect
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOOLS_DIR = project_root / "neocortex" / "mcp" / "tools"


def extract_tool_info_from_source(source: str) -> Dict[str, Any]:
    """Extract tool information from Python source code."""
    info = {
        "name": None,
        "description": None,
        "actions": [],
    }

    # Try to find @mcp.tool decorator
    tool_name_match = re.search(r'@mcp\.tool\(name="([^"]+)"\)', source)
    if tool_name_match:
        info["name"] = tool_name_match.group(1)

    # Try to find function definition after decorator
    func_match = re.search(r"def (\w+)\(", source)
    if func_match:
        # Try to extract docstring
        docstring_match = re.search(r'"""(.*?)"""', source, re.DOTALL)
        if docstring_match:
            info["description"] = docstring_match.group(1).strip()

    # Try to parse AST for more detailed analysis
    try:
        tree = ast.parse(source)

        # Look for function definitions with decorators
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it has decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if (
                            hasattr(decorator.func, "attr")
                            and decorator.func.attr == "tool"
                        ):
                            # Found tool function
                            info["function_name"] = node.name

                            # Extract docstring
                            if ast.get_docstring(node):
                                info["description"] = ast.get_docstring(node).strip()

                            # Extract parameters
                            params = []
                            for arg in node.args.args:
                                if arg.arg != "self":
                                    params.append(arg.arg)

                            info["parameters"] = params

                            # Look for action handling logic (simple pattern)
                            # This is heuristic - we'll look for if/elif statements checking 'action' parameter
                            action_patterns = []
                            for child in ast.walk(node):
                                if isinstance(child, ast.If):
                                    # Check if testing action == "something"
                                    if isinstance(child.test, ast.Compare):
                                        if (
                                            isinstance(child.test.left, ast.Name)
                                            and child.test.left.id == "action"
                                        ):
                                            for comparator in child.test.comparators:
                                                if isinstance(comparator, ast.Constant):
                                                    action_patterns.append(
                                                        comparator.value
                                                    )

                            info["action_patterns"] = action_patterns
    except Exception as e:
        logger.debug(f"AST parsing failed: {e}")

    return info


def analyze_tool_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single tool file."""
    logger.info(f"Analyzing {file_path.name}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return {}

    # Basic extraction
    tool_info = extract_tool_info_from_source(source)
    tool_info["file"] = file_path.name

    # Manual override for known patterns
    if file_path.name == "cortex.py":
        tool_info.update(
            {
                "name": "neocortex_cortex",
                "description": "Access to central cortex",
                "actions": [
                    {
                        "name": "get_full",
                        "description": "Return full cortex content with metadata",
                    },
                    {"name": "get_section", "description": "Return a specific section"},
                    {
                        "name": "get_aliases",
                        "description": "Return all defined aliases",
                    },
                    {
                        "name": "get_workflows",
                        "description": "Return defined workflows",
                    },
                    {
                        "name": "validate_alias",
                        "description": "Validate if an alias is correct",
                    },
                ],
            }
        )

    return tool_info


def generate_inventory_report() -> Dict[str, Any]:
    """Generate comprehensive inventory report."""
    tools = []

    for tool_file in TOOLS_DIR.glob("*.py"):
        if tool_file.name == "__init__.py":
            continue

        tool_info = analyze_tool_file(tool_file)
        if tool_info:
            tools.append(tool_info)

    # Sort by tool name
    tools.sort(key=lambda x: x.get("name", ""))

    report = {
        "timestamp": "2026-04-10T18:00:00Z",
        "total_tools": len(tools),
        "tools": tools,
    }

    return report


def print_markdown_report(report: Dict[str, Any]):
    """Print report in Markdown format."""
    print("# NeoCortex MCP Tools Inventory Report")
    print(f"\n**Generated:** {report['timestamp']}")
    print(f"**Total Tools:** {report['total_tools']}")

    for tool in report["tools"]:
        print(f"\n## {tool.get('name', 'Unknown')}")
        print(f"**File:** `{tool.get('file', 'N/A')}`")

        if tool.get("description"):
            print(f"\n{tool.get('description')}")

        if tool.get("actions"):
            print("\n**Actions:**")
            for action in tool.get("actions", []):
                if isinstance(action, dict):
                    print(
                        f"  - **{action.get('name', 'Unknown')}**: {action.get('description', '')}"
                    )
                else:
                    print(f"  - {action}")

        if tool.get("parameters"):
            print(f"\n**Parameters:** {', '.join(tool.get('parameters', []))}")

        if tool.get("action_patterns"):
            print(
                f"\n**Action Patterns:** {', '.join(str(p) for p in tool.get('action_patterns', []))}"
            )

        print("\n---")


def main():
    """Main entry point."""
    print("=" * 60)
    print("NeoCortex MCP Tools Inventory Analysis")
    print("=" * 60)

    if not TOOLS_DIR.exists():
        logger.error(f"Tools directory not found: {TOOLS_DIR}")
        return 1

    report = generate_inventory_report()

    # Print markdown report
    print_markdown_report(report)

    # Save JSON report
    json_path = project_root / "mcp_tools_inventory.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"JSON report saved to: {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
