"""---
@Module NC-UTL-FR-002-hash-utils mcp _genealogy:   injected_at: '2026-04-16T00:23:59.11
---
"""


"""
NC-UTL-FR-002-hash-utils.py
Hash utilities for NeoCortex framework.
Provides SHA-256 and SHA-512 helpers for file integrity,
ticket hashing, and handoff checksums.
"""

import hashlib
import hmac
import json
from pathlib import Path
from typing import Union


def sha256_file(path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file. Returns hex string."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(text: str, encoding: str = "utf-8") -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


def sha256_short(text: str, length: int = 12) -> str:
    """Return first N chars of SHA-256 hash. Used for prompt SHAs and ticket IDs."""
    return sha256_str(text)[:length]


def sha512_file(path: Union[str, Path]) -> str:
    """Compute SHA-512 hash of a file."""
    h = hashlib.sha512()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_integrity_hash(ticket_id: str, write_zone: str, title: str) -> str:
    """
    Compute ticket integrity hash  matches format used in ticket YAMLs.
    Formula: sha256[:16] of "ticket_id|write_zone|title"
    """
    payload = f"{ticket_id}|{write_zone}|{title}"
    return sha256_str(payload)[:16]


def verify_file_integrity(path: Union[str, Path], expected_hash: str) -> bool:
    """Verify that a file's SHA-256 matches the expected hash."""
    return sha256_file(path) == expected_hash


def hash_dict(d: dict) -> str:
    """Deterministic SHA-256 of a JSON-serializable dict (sorted keys)."""
    serialized = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return sha256_str(serialized)


def hmac_sign(data: str, secret: str) -> str:
    """HMAC-SHA256 signature for data integrity verification."""
    return hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def hmac_verify(data: str, secret: str, signature: str) -> bool:
    """Verify HMAC-SHA256 signature."""
    expected = hmac_sign(data, secret)
    return hmac.compare_digest(expected, signature)


def compute_prompt_sha(prompt_path: Union[str, Path], length: int = 6) -> str:
    """
    Compute short hash of a prompt file  used for MY_CLAIM in worker identity.
    Skips the first line if it's a comment (<!-- ... -->).
    """
    content = Path(prompt_path).read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    body = "".join(lines[1:]) if lines and lines[0].startswith("<!--") else content
    return sha256_str(body)[:length]


if __name__ == "__main__":
    # Quick self-test
    test = "NC-DS-001|01_neocortex_framework/neocortex/|Test ticket"
    h = sha256_str(test)[:16]
    print(f"integrity_hash sample: {h}")
    print(f"sha256_short('hello', 8): {sha256_short('hello', 8)}")
    print("NC-UTL-FR-002-hash-utils: OK")
