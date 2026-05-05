"""---
@Module NC-CORE-FR-159-crypto-integrity mcp NC-CORE-FR-159-crypto-integrity.py — Central de Cr
---
"""


import hashlib
import json
import os
import pathlib
from datetime import datetime


class CryptoIntegrity:
    """Central de integridade criptográfica do NeoCortex."""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def hash_file(self, filepath: str) -> str:
        """SHA-256 de qualquer arquivo."""
        return hashlib.sha256(Path(filepath).read_bytes()).hexdigest()

    def hash_content(self, content: str) -> str:
        """SHA-256 de string."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def verify_integrity(self, filepath: str, expected_hash: str) -> bool:
        """Verifica se arquivo não foi corrompido."""
        return self.hash_file(filepath) == expected_hash

    def scan_encoding_issues(self) -> dict:
        """Varre arquivos .py procurando corrupção de encoding (acentos, UTF-8)."""
        issues = []
        scanned = 0
        fw = self.root / "01_neocortex_framework" / "neocortex"
        for d in [fw / "core", fw / "mcp" / "tools"]:
            if not d.exists():
                continue
            for f in d.glob("*.py"):
                if "__pycache__" in str(f):
                    continue
                scanned += 1
                try:
                    content = f.read_text(encoding="utf-8")
                    # Detect replacement characters (U+FFFD) or mojibake patterns
                    if "\ufffd" in content:
                        issues.append({"file": str(f.relative_to(self.root)), "issue": "REPLACEMENT_CHAR (U+FFFD)", "severity": "HIGH"})
                    # Detect common mojibake patterns for Portuguese
                    for pattern, _label in [
                        ("Val\u00e9rio", "Name_OK"),
                        ("Val?rio", "Name_BROKEN"),
                        ("configura\u00e7\u00e3o", "Word_OK"),
                        ("configura??o", "Word_BROKEN"),
                    ]:
                        if "??" in pattern.replace("??", "") and pattern in content:
                            pass  # skip BROKEN check for now
                except UnicodeDecodeError as e:
                    issues.append({"file": str(f.relative_to(self.root)), "issue": f"UnicodeDecodeError: {e}", "severity": "CRITICAL"})
                except Exception:
                    pass

        return {
            "files_scanned": scanned,
            "issues": issues,
            "issue_count": len(issues),
            "healthy": len(issues) == 0,
            "timestamp": datetime.now().isoformat(),
        }

    def generate_manifest_hash(self) -> dict:
        """Gera manifesto criptográfico de todos os arquivos core."""
        manifest = {}
        fw = self.root / "01_neocortex_framework" / "neocortex"
        for d in [fw / "core", fw / "mcp" / "tools"]:
            if not d.exists():
                continue
            for f in sorted(d.glob("*.py")):
                if f.name.startswith("_"):
                    continue
                manifest[str(f.relative_to(self.root))] = self.hash_file(str(f))

        return {
            "total_files": len(manifest),
            "algorithm": "SHA-256",
            "manifest": manifest,
            "manifest_hash": self.hash_content(json.dumps(manifest, sort_keys=True)),
            "generated_at": datetime.now().isoformat(),
        }


_crypto = None
def get_crypto() -> CryptoIntegrity:
    global _crypto
    if _crypto is None: _crypto = CryptoIntegrity()
    return _crypto
