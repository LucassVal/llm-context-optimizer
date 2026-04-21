import sys

sys.path.insert(0, "01_neocortex_framework")
try:
    from neocortex.core.services.NC_SVC_FR_005_event_bus import get_event_bus

    print("SUCCESS: imported hyphenated file using underscores")
except ImportError as e:
    print(f"FAILED: {e}")

# Try our review module
try:
    from neocortex.core.review import get_review_service

    print("SUCCESS: imported review module")
except ImportError as e:
    print(f"FAILED review: {e}")
