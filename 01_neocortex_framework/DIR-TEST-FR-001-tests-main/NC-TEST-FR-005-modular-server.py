#!/usr/bin/env python3

"""---
_genealogy:
  injected_at: '2026-04-16T00:23:57.122629'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: tests
level: 5
tags:
  - tests
  - level-5
  - python
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:23:57.122629'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: tests
level: 5
tags:
  - tests
  - level-5
  - python
---
"""

"""---
_genealogy:
  injected_at: '2026-04-16T00:23:57.122629'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: tests
level: 5
tags:
  - tests
  - level-5
  - python
---"""


"""
Test the modular MCP server.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import server module
print("Testing modular server import...")
try:
    from neocortex.mcp.server import main, mcp

    print(" Server module imports successfully")

    # Check if all tools are registered
    # In FastMCP, tools might not be in mcp.tools attribute
    # Let's check if mcp object has expected attributes
    print(f"\nMCP object type: {type(mcp)}")

    # Try to run in simulation mode (without FastMCP)
    print("\nAttempting to run main() in simulation mode...")
    # We'll mock the run method to avoid actual execution
    original_run = getattr(mcp, "run", None)
    if original_run:

        def mock_run():
            print(" Mock MCP.run() called - tools would be registered")
            # Check if tools would be registered
            if hasattr(mcp, "tools"):
                print(f"  Tools registered: {len(mcp.tools)}")
            return {"serverInfo": {"name": "neocortex", "version": "4.2-cortex"}}

        mcp.run = mock_run

    # Call main() but capture output
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        try:
            main()
            output = f.getvalue()
            print(" main() executed without errors")
        except Exception as e:
            print(f" Error in main(): {e}")
            import traceback

            traceback.print_exc()

except ImportError as e:
    print(f" Import error: {e}")
    import traceback

    traceback.print_exc()

print("\n Modular server test complete!")
