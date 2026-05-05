import sys

sys.path.insert(0, "01_neocortex_framework")
from neocortex.core.utils import IDValidator, EXIT_CODE_PERMANENT

print("Testing IDValidator...")
validator = IDValidator()
print(f"EXIT_CODE_PERMANENT = {EXIT_CODE_PERMANENT}")

# Test validation
test_cases = [
    ("NC-DS-034", "ticket", True),
    ("NC-DS-999", "ticket", True),
    ("NC-DS-34", "ticket", False),
    ("worker-12345-abcd", "worker", True),
    ("worker-123-abcd", "worker", False),
    ("sess-20260413-011939", "session", True),
    ("sess-20260413-0119399", "session", False),
    ("NC-REV-FR-001-confidence-review.py", "nc_file", True),
    ("NC-LBE-DS-000-parent.mdc", "lobe", True),
]
for id_str, id_type, expected in test_cases:
    result = validator.validate(id_str, id_type)
    status = "PASS" if result == expected else "FAIL"
    print(f'{status}: {id_type} "{id_str}" -> {result} (expected {expected})')

# Test checksum
checksum = validator.get_checksum("test")
print(f'Checksum "test": {checksum}')
assert len(checksum) == 4

# Test session ID generation
session_id = validator.generate_session_id()
print(f"Session ID: {session_id}")
assert session_id.startswith("sess-")

# Test worker ID generation
worker_id = validator.generate_worker_id(8765)
print(f"Worker ID for port 8765: {worker_id}")
assert worker_id.startswith("worker-")

# Test permanent error
assert validator.is_permanent_error(42) == True
assert validator.is_permanent_error(0) == False

print("All tests passed.")
