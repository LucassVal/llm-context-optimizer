import sys

sys.path.insert(0, "01_neocortex_framework")
print("Testing import of review module...")
try:
    from neocortex.core.review import get_review_service

    print("SUCCESS: get_review_service imported")
    service = get_review_service()
    print(f"Service created with {len(service.validators)} validators")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()

print("\nTesting import of validators...")
try:

    print("SUCCESS: validators imported")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback

    traceback.print_exc()
