"""---
NC-SVC-FR-018-tag-normalizer.py
---
"""



from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# WAL import (importlib para evitar dependência de path relativo no sys.path)
# ---------------------------------------------------------------------------

_wal_path = (
    Path(__file__).resolve().parents[2] / "core/services/NC-SVC-FR-016-wal-service.py"
)
_spec = importlib.util.spec_from_file_location("wal_service", _wal_path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
WALService = _mod.WALService

# ---------------------------------------------------------------------------
# SSOT — caminho do dicionário ubíquo
# ---------------------------------------------------------------------------

_DICT_PATH = (
    Path(__file__).resolve().parents[3]
    / "DIR-DOC-FR-001-docs-main"
    / "NC-DOC-FR-001-ubiquitous-language-dictionary.md"
)

# ---------------------------------------------------------------------------
# Padrões regex para símbolos ubíquos
# ---------------------------------------------------------------------------

_PAT_AT = re.compile(r"@([A-Z][A-Z0-9_]*)")   # @SSOT, @CONFIG, ...
_PAT_DOLLAR = re.compile(r"\$([A-Z][A-Z0-9_]*)")  # $ARCH, $SEC, ...
_PAT_PERCENT = re.compile(r"%([A-Z][A-Z0-9_]*)")  # %AGENT203, %NOW, ...

# Padrão para tags em frontmatter YAML (_genealogy.tags)
_PAT_TAG_LINE = re.compile(r"^(\s*-\s+)(.+)$")

# Campos obrigatórios em frontmatter .mdc
_MDC_REQUIRED = {"name", "description", "type"}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SymbolEntry:
    symbol: str           # ex: "@SSOT"
    expands_to: str
    real_path: str


@dataclass
class ScanResult:
    scanned: int = 0
    found: list[dict] = field(default_factory=list)      # todos os símbolos encontrados
    invalid: list[dict] = field(default_factory=list)    # casing errado
    unknown: list[dict] = field(default_factory=list)    # não existe no dict

    def to_dict(self) -> dict:
        return {
            "scanned": self.scanned,
            "found": self.found,
            "invalid": self.invalid,
            "unknown": self.unknown,
            "summary": {
                "total_found": len(self.found),
                "total_invalid": len(self.invalid),
                "total_unknown": len(self.unknown),
            },
        }


@dataclass
class NormalizeResult:
    path: str = ""
    changed: int = 0
    diff: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"path": self.path, "changed": self.changed, "diff": self.diff}


@dataclass
class ValidationResult:
    path: str = ""
    valid: bool = True
    violations: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "valid": self.valid,
            "violations": self.violations,
        }


# ---------------------------------------------------------------------------
# TagNormalizerService
# ---------------------------------------------------------------------------


class TagNormalizerService:
    """
    Central Universal de Sanitização de Tags NeoCortex.

    Uso básico:
        svc = TagNormalizerService()
        result = svc.scan("lobes/", recursive=True)
        print(result.to_dict())
    """

    def __init__(self, dict_path: Path | None = None) -> None:
        self._dict_path = Path(dict_path) if dict_path else _DICT_PATH
        self._symbols: dict[str, SymbolEntry] = {}
        self._wal = WALService()
        self._load_dictionary()

    # ------------------------------------------------------------------
    # Dictionary loading
    # ------------------------------------------------------------------

    def _load_dictionary(self) -> None:
        """Lê NC-DOC-FR-001 e extrai entradas das tabelas @, $, %."""
        if not self._dict_path.exists():
            return

        text = self._dict_path.read_text(encoding="utf-8", errors="replace")
        # Extrai linhas de tabela markdown: | `@SSOT` | descrição | caminho |
        row_pat = re.compile(
            r"\|\s*`([@$%][A-Z][A-Z0-9_]*)`\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
        )
        for m in row_pat.finditer(text):
            symbol = m.group(1).strip()
            expands = m.group(2).strip()
            path = m.group(3).strip()
            self._symbols[symbol] = SymbolEntry(
                symbol=symbol, expands_to=expands, real_path=path
            )

    # ------------------------------------------------------------------
    # scan
    # ------------------------------------------------------------------

    def scan(
        self, path: str | Path, recursive: bool = False
    ) -> ScanResult:
        """
        Localiza todos os padrões @[A-Z]+, $[A-Z_]+, %[A-Z_]+ no arquivo/dir.

        Classifica como:
          found   → símbolo canônico presente no dicionário
          invalid → símbolo existe no dict mas casing diferente
          unknown → não existe no dicionário
        """
        target = Path(path)
        result = ScanResult()

        files: list[Path] = []
        if target.is_dir():
            glob = "**/*" if recursive else "*"
            files = [f for f in target.glob(glob) if f.is_file()]
        elif target.is_file():
            files = [target]

        result.scanned = len(files)

        for fpath in files:
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except (PermissionError, OSError):
                continue

            for pat, prefix in [(_PAT_AT, "@"), (_PAT_DOLLAR, "$"), (_PAT_PERCENT, "%")]:
                for m in pat.finditer(text):
                    raw_symbol = prefix + m.group(1)
                    line_no = text[: m.start()].count("\n") + 1
                    entry = {
                        "file": str(fpath),
                        "line": line_no,
                        "symbol": raw_symbol,
                    }

                    if raw_symbol in self._symbols:
                        result.found.append(entry)
                    else:
                        # Tentar match case-insensitive
                        canonical = next(
                            (s for s in self._symbols if s.upper() == raw_symbol.upper()),
                            None,
                        )
                        if canonical:
                            entry["canonical"] = canonical
                            result.invalid.append(entry)
                        else:
                            result.unknown.append(entry)

        return result

    # ------------------------------------------------------------------
    # normalize
    # ------------------------------------------------------------------

    def normalize(
        self, path: str | Path, dry_run: bool = False
    ) -> NormalizeResult:
        """
        Corrige casing de tags em frontmatter YAML (_genealogy.tags).
        Regra: tags em minúsculas, sem espaços (kebab-case).
        WAL-logged via NC-SVC-FR-016.
        """
        target = Path(path)
        result = NormalizeResult(path=str(target))

        if not target.is_file():
            return result

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        in_tags_block = False
        new_lines = []
        changed = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detecta início do bloco _genealogy.tags
            if stripped == "_genealogy:" or stripped.startswith("_genealogy:"):
                in_tags_block = False

            if in_tags_block or "tags:" in line:
                if "tags:" in line:
                    in_tags_block = True

                m = _PAT_TAG_LINE.match(line.rstrip("\n\r"))
                if m and in_tags_block:
                    indent = m.group(1)
                    tag_val = m.group(2).strip()
                    normalized = tag_val.lower().replace(" ", "-")
                    if normalized != tag_val:
                        result.diff.append(
                            {"line": i + 1, "before": tag_val, "after": normalized}
                        )
                        changed += 1
                        eol = "\n" if line.endswith("\n") else ""
                        line = f"{indent}{normalized}{eol}"

            # Detecta fim do bloco tags (linha vazia ou nova chave sem indent)
            if in_tags_block and stripped and not stripped.startswith("-") and "tags:" not in stripped:
                in_tags_block = False

            new_lines.append(line)

        result.changed = changed

        if changed > 0 and not dry_run:
            session_id = f"svc018-norm-{uuid.uuid4().hex[:8]}"
            before_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            with self._wal.transaction(session_id, "NC-SVC-FR-018", "NC-DS-090"):
                target.write_text("".join(new_lines), encoding="utf-8")
                after_hash = hashlib.sha256(target.read_bytes()).hexdigest()
                self._wal.log_operation(
                    session_id, "MODIFY", str(target),
                    ticket_id="NC-DS-090",
                    before_hash=before_hash,
                    after_hash=after_hash,
                )

        return result

    # ------------------------------------------------------------------
    # validate_lobe
    # ------------------------------------------------------------------

    def validate_lobe(self, path: str | Path) -> ValidationResult:
        """
        Verifica campos obrigatórios de frontmatter .mdc (name, description, type)
        e valida que símbolos ubíquos no corpo existem em NC-DOC-FR-001.
        """
        target = Path(path)
        result = ValidationResult(path=str(target))

        if not target.exists():
            result.valid = False
            result.violations.append({"type": "FILE_NOT_FOUND", "path": str(target)})
            return result

        text = target.read_text(encoding="utf-8", errors="replace")

        # Extrai frontmatter YAML entre --- ... ---
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            present_keys: set = set()
            for line in fm_text.splitlines():
                kv = line.split(":", 1)
                if len(kv) == 2:
                    present_keys.add(kv[0].strip().lower())

            for req in _MDC_REQUIRED:
                if req not in present_keys:
                    result.valid = False
                    result.violations.append(
                        {"type": "MISSING_FIELD", "field": req}
                    )
        else:
            result.valid = False
            result.violations.append({"type": "NO_FRONTMATTER"})

        # Valida símbolos ubíquos no corpo
        for pat, prefix in [(_PAT_AT, "@"), (_PAT_DOLLAR, "$"), (_PAT_PERCENT, "%")]:
            for m in pat.finditer(text):
                symbol = prefix + m.group(1)
                if symbol not in self._symbols:
                    line_no = text[: m.start()].count("\n") + 1
                    result.valid = False
                    result.violations.append(
                        {
                            "type": "UNKNOWN_SYMBOL",
                            "symbol": symbol,
                            "line": line_no,
                        }
                    )

        return result

    # ------------------------------------------------------------------
    # stats
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        return {
            "dictionary_path": str(self._dict_path),
            "dictionary_loaded": self._dict_path.exists(),
            "total_symbols": len(self._symbols),
            "symbols_at": [s for s in self._symbols if s.startswith("@")],
            "symbols_dollar": [s for s in self._symbols if s.startswith("$")],
            "symbols_percent": [s for s in self._symbols if s.startswith("%")],
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    svc = TagNormalizerService()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "stats":
        print(json.dumps(svc.stats(), indent=2))

    elif cmd == "scan" and len(sys.argv) > 2:
        recursive = "--recursive" in sys.argv
        result = svc.scan(sys.argv[2], recursive=recursive)
        print(json.dumps(result.to_dict(), indent=2))

    elif cmd == "fix" and len(sys.argv) > 2:
        dry_run = "--dry-run" in sys.argv
        result = svc.normalize(sys.argv[2], dry_run=dry_run)
        label = "[DRY-RUN] " if dry_run else ""
        print(f"{label}Arquivo: {result.path}")
        print(f"{label}Tags alteradas: {result.changed}")
        if result.diff:
            for d in result.diff:
                print(f"  linha {d['line']}: '{d['before']}' → '{d['after']}'")

    elif cmd == "validate" and len(sys.argv) > 2:
        result = svc.validate_lobe(sys.argv[2])
        status = "VALID" if result.valid else "INVALID"
        print(f"[{status}] {result.path}")
        for v in result.violations:
            print(f"  {v}")

    else:
        print(
            "Uso:\n"
            "  python NC-SVC-FR-018-tag-normalizer.py stats\n"
            "  python NC-SVC-FR-018-tag-normalizer.py scan <path> [--recursive]\n"
            "  python NC-SVC-FR-018-tag-normalizer.py fix <path> [--dry-run]\n"
            "  python NC-SVC-FR-018-tag-normalizer.py validate <path>"
        )
