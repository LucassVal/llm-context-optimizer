#!/usr/bin/env python3
import inspect
from mcp.client.session import ClientSession

print("ClientSession methods:")
for name, method in inspect.getmembers(ClientSession, predicate=inspect.isfunction):
    if not name.startswith("_"):
        print(f"  {name}{inspect.signature(method)}")

print("\nClientSession.__init__ signature:")
print(inspect.signature(ClientSession.__init__))

print("\nTrying to find initialize method...")
# Check if initialize exists
if hasattr(ClientSession, "initialize"):
    print("initialize signature:", inspect.signature(ClientSession.initialize))
