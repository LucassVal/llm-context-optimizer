import mcp.client.sse as sse_module
import inspect

print("=== mcp.client.sse ===")
for name in dir(sse_module):
    if not name.startswith("_"):
        obj = getattr(sse_module, name)
        if callable(obj):
            print(
                f"{name}: {inspect.signature(obj) if hasattr(obj, '__signature__') else 'callable'}"
            )
        else:
            print(f"{name}: {type(obj)}")

print("\n=== aconnect_sse ===")
if hasattr(sse_module, "aconnect_sse"):
    print(inspect.signature(sse_module.aconnect_sse))

print("\n=== create_mcp_http_client ===")
if hasattr(sse_module, "create_mcp_http_client"):
    print(inspect.signature(sse_module.create_mcp_http_client))
