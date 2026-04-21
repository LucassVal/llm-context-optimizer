#!/usr/bin/env python3

"""---
domain: "testing"
layer: "test"
type: "TST"
tags: ['testing', 'unit', 'test']
hash: "auto-generated"
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
