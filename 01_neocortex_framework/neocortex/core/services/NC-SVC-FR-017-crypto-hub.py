"""---
NC-SVC-FR-017-crypto-hub.py
---
"""



from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import sys
import uuid
import warnings
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# WAL import
# ---------------------------------------------------------------------------

_wal_path = (
    Path(__file__).resolve().parents[2] / "core/services/NC-SVC-FR-016-wal-service.py"
)
_spec = importlib.util.spec_from_file_location("wal_service", _wal_path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
WALService = _mod.WALService

# ---------------------------------------------------------------------------
# cryptography import (Fernet)
# ---------------------------------------------------------------------------

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False
    Fernet = None  # type: ignore[assignment,misc]
    InvalidToken = Exception  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

_PROJECT_ID = "neocortex-framework"  # salt base para PBKDF2
_PBKDF2_ITERATIONS = 100_000
_ENV_KEY = "NEOCORTEX_MASTER_KEY"

# Registro local de tokens (path → token_hash) para rotate_key
_TOKEN_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "DIR-DS-003-wal"
    / "crypto_token_registry.json"
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class EncryptResult:
    token: str = ""
    token_hash: str = ""    # sha256(token) — logado no WAL, nunca o plaintext
    success: bool = False

    def to_dict(self) -> dict:
        return {"token": self.token, "token_hash": self.token_hash, "success": self.success}


@dataclass
class DecryptResult:
    plaintext: str = ""
    success: bool = False
    error: str = ""

    def to_dict(self) -> dict:
        return {"success": self.success, "error": self.error}


@dataclass
class RotateResult:
    rotated: int = 0
    failed: int = 0
    success: bool = False

    def to_dict(self) -> dict:
        return {"rotated": self.rotated, "failed": self.failed, "success": self.success}


@dataclass
class ScanConfigResult:
    config_path: str = ""
    secret_fields: list[dict] = field(default_factory=list)
    total: int = 0

    def to_dict(self) -> dict:
        return {
            "config_path": self.config_path,
            "secret_fields": self.secret_fields,
            "total": self.total,
        }


# ---------------------------------------------------------------------------
# CryptoHub
# ---------------------------------------------------------------------------


class CryptoHub:
    """
    Central de criptografia NeoCortex usando Fernet (AES-128-CBC + HMAC-SHA256).

    Requer variável de ambiente NEOCORTEX_MASTER_KEY.
    Se ausente, opera em modo hash-only (encrypt/decrypt desabilitados).

    Uso básico:
        hub = CryptoHub()
        result = hub.encrypt("minha-api-key")
        token = result.token

        dec = hub.decrypt(token)
        print(dec.plaintext)  # "minha-api-key"
    """

    def __init__(self, master_key: str | None = None) -> None:
        self._wal = WALService()
        self._fernet: object | None = None
        self._hash_only = False
        self._token_registry: dict[str, str] = {}  # token_hash → encrypted_token

        raw_key = master_key or os.environ.get(_ENV_KEY)

        if not raw_key:
            warnings.warn(
                f"[CryptoHub] {_ENV_KEY} não definida — modo hash-only ativado. "
                "encrypt/decrypt desabilitados.",
                UserWarning,
                stacklevel=2,
            )
            self._hash_only = True
            return

        if not _CRYPTO_AVAILABLE:
            warnings.warn(
                "[CryptoHub] cryptography não instalada — modo hash-only ativado. "
                "Execute: pip install 'cryptography>=42.0.0'",
                UserWarning,
                stacklevel=2,
            )
            self._hash_only = True
            return

        self._fernet = self._derive_fernet(raw_key)
        self._load_token_registry()

    # ------------------------------------------------------------------
    # Key derivation
    # ------------------------------------------------------------------

    @staticmethod
    def _derive_fernet(master_key: str) -> Fernet:
        """Deriva chave Fernet via PBKDF2HMAC(SHA256). Nunca loga a chave."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=_PROJECT_ID.encode("utf-8"),
            iterations=_PBKDF2_ITERATIONS,
        )
        derived = kdf.derive(master_key.encode("utf-8"))
        fernet_key = base64.urlsafe_b64encode(derived)
        return Fernet(fernet_key)

    # ------------------------------------------------------------------
    # Token registry (persistido em JSON)
    # ------------------------------------------------------------------

    def _load_token_registry(self) -> None:
        if _TOKEN_REGISTRY_PATH.exists():
            try:
                self._token_registry = json.loads(
                    _TOKEN_REGISTRY_PATH.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                self._token_registry = {}

    def _save_token_registry(self) -> None:
        _TOKEN_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_REGISTRY_PATH.write_text(
            json.dumps(self._token_registry, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # encrypt
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: str) -> EncryptResult:
        """
        Encripta plaintext com Fernet.
        WAL-logged: registra sha256(ciphertext), nunca o plaintext.
        """
        result = EncryptResult()

        if self._hash_only or self._fernet is None:
            result.success = False
            return result

        token_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))  # type: ignore[union-attr]
        token = token_bytes.decode("utf-8")
        token_hash = hashlib.sha256(token_bytes).hexdigest()

        # Registra no registry local
        self._token_registry[token_hash] = token
        self._save_token_registry()

        # WAL log — sem plaintext, sem ciphertext, só hash
        session_id = f"svc017-enc-{uuid.uuid4().hex[:8]}"
        self._wal.open_session(session_id, "NC-SVC-FR-017", "NC-DS-091")
        self._wal.log_operation(
            session_id,
            "CREATE",
            f"crypto:encrypt:{token_hash[:16]}...",
            ticket_id="NC-DS-091",
            after_hash=token_hash,
        )
        self._wal.commit_session(session_id)

        result.token = token
        result.token_hash = token_hash
        result.success = True
        return result

    # ------------------------------------------------------------------
    # decrypt
    # ------------------------------------------------------------------

    def decrypt(self, token: str) -> DecryptResult:
        """
        Decripta token Fernet. Valida HMAC antes.
        WAL-logged: registra attempt + outcome.
        """
        result = DecryptResult()

        if self._hash_only or self._fernet is None:
            result.error = "hash-only mode: decrypt desabilitado"
            return result

        session_id = f"svc017-dec-{uuid.uuid4().hex[:8]}"
        self._wal.open_session(session_id, "NC-SVC-FR-017", "NC-DS-091")

        try:
            plaintext_bytes = self._fernet.decrypt(token.encode("utf-8"))  # type: ignore[union-attr]
            result.plaintext = plaintext_bytes.decode("utf-8")
            result.success = True

            self._wal.log_operation(
                session_id,
                "MODIFY",
                "crypto:decrypt:success",
                ticket_id="NC-DS-091",
            )
            self._wal.commit_session(session_id)

        except InvalidToken:
            result.error = "InvalidToken: HMAC inválido ou chave errada"
            self._wal.log_operation(
                session_id,
                "MODIFY",
                "crypto:decrypt:fail",
                ticket_id="NC-DS-091",
            )
            self._wal.rollback_session(session_id)

        return result

    # ------------------------------------------------------------------
    # rotate_key
    # ------------------------------------------------------------------

    def rotate_key(self, new_master_key: str) -> RotateResult:
        """
        Re-encripta todos os tokens registrados com nova chave.
        WAL-logged como sessão única.
        """
        result = RotateResult()

        if self._hash_only or self._fernet is None:
            return result

        new_fernet = self._derive_fernet(new_master_key)
        session_id = f"svc017-rotate-{uuid.uuid4().hex[:8]}"
        self._wal.open_session(session_id, "NC-SVC-FR-017", "NC-DS-091")

        new_registry: dict[str, str] = {}
        for token_hash, token in self._token_registry.items():
            try:
                # Decripta com chave antiga
                plaintext = self._fernet.decrypt(token.encode("utf-8"))  # type: ignore[union-attr]
                # Re-encripta com nova chave
                new_token_bytes = new_fernet.encrypt(plaintext)
                new_token = new_token_bytes.decode("utf-8")
                new_hash = hashlib.sha256(new_token_bytes).hexdigest()
                new_registry[new_hash] = new_token
                result.rotated += 1
            except InvalidToken:
                result.failed += 1
                new_registry[token_hash] = token  # mantém token antigo se falhar

        self._fernet = new_fernet
        self._token_registry = new_registry
        self._save_token_registry()

        self._wal.log_operation(
            session_id,
            "MODIFY",
            f"crypto:rotate_key:rotated={result.rotated}:failed={result.failed}",
            ticket_id="NC-DS-091",
        )
        self._wal.commit_session(session_id)

        result.success = True
        return result

    # ------------------------------------------------------------------
    # scan_config
    # ------------------------------------------------------------------

    def scan_config(self, config_path: str | Path) -> ScanConfigResult:
        """
        Detecta valores marcados com tag !secret no YAML.
        Retorna lista de campos que precisam ser encriptados.
        """
        target = Path(config_path)
        result = ScanConfigResult(config_path=str(target))

        if not target.exists():
            return result

        text = target.read_text(encoding="utf-8", errors="replace")

        # Detecta padrão: key: !secret valor_em_plain_text
        secret_pat = re.compile(
            r"^(\s*)([a-zA-Z_][a-zA-Z0-9_\-]*)\s*:\s*!secret\s+(.+)$",
            re.MULTILINE,
        )
        for m in secret_pat.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            result.secret_fields.append(
                {
                    "field": m.group(2).strip(),
                    "line": line_no,
                    "has_value": bool(m.group(3).strip()),
                }
            )

        result.total = len(result.secret_fields)
        return result

    # ------------------------------------------------------------------
    # stats
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        return {
            "mode": "hash-only" if self._hash_only else "fernet",
            "crypto_available": _CRYPTO_AVAILABLE,
            "master_key_set": bool(os.environ.get(_ENV_KEY)),
            "token_registry_size": len(self._token_registry),
            "token_registry_path": str(_TOKEN_REGISTRY_PATH),
            "pbkdf2_iterations": _PBKDF2_ITERATIONS,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    hub = CryptoHub()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "stats":
        print(json.dumps(hub.stats(), indent=2))

    elif cmd == "encrypt" and len(sys.argv) > 2:
        plaintext = " ".join(sys.argv[2:])
        result = hub.encrypt(plaintext)
        if result.success:
            print(f"Token: {result.token}")
            print(f"Hash:  {result.token_hash}")
        else:
            print("ERRO: encrypt falhou (modo hash-only ou cryptography não instalada)")
            sys.exit(1)

    elif cmd == "decrypt" and len(sys.argv) > 2:
        token = sys.argv[2]
        result = hub.decrypt(token)
        if result.success:
            print(f"Plaintext: {result.plaintext}")
        else:
            print(f"ERRO: {result.error}")
            sys.exit(1)

    elif cmd == "scan-config" and len(sys.argv) > 2:
        result = hub.scan_config(sys.argv[2])
        print(json.dumps(result.to_dict(), indent=2))

    elif cmd == "rotate-key" and len(sys.argv) > 2:
        new_key = sys.argv[2]
        result = hub.rotate_key(new_key)
        print(json.dumps(result.to_dict(), indent=2))

    else:
        print(
            "Uso:\n"
            f"  {_ENV_KEY}=xxx python NC-SVC-FR-017-crypto-hub.py encrypt 'valor'\n"
            f"  {_ENV_KEY}=xxx python NC-SVC-FR-017-crypto-hub.py decrypt '<token>'\n"
            f"  {_ENV_KEY}=xxx python NC-SVC-FR-017-crypto-hub.py scan-config <path>\n"
            f"  {_ENV_KEY}=xxx python NC-SVC-FR-017-crypto-hub.py rotate-key <new-key>\n"
            "  python NC-SVC-FR-017-crypto-hub.py stats"
        )
