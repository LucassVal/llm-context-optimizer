#!/usr/bin/env python3

"""---
_genealogy:
  injected_at: '2026-04-16T00:23:57.131177'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: tests
level: 5
tags:
  - tests
  - level-5
  - python
---"""


import sys
import traceback

sys.path.insert(0, ".")

import json

from neocortex.mcp.tools.task import _execute_task

task_data = json.dumps({"type": "test", "prompt": "Hello world", "context": {}})

try:
    result = _execute_task("test1", task_data, backend=None)
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
