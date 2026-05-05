"""---
@Audit NC-CORE-FR-158-system-integrity mcp NC-CORE-FR-158-system-integrity.py — 4 Checks de I
---
"""


import os
import pathlib
import re
from datetime import datetime
from typing import Dict

import yaml as _yaml

# ═══════════════════════════════════════════════════════════════
# R112 — YAML Validate (sintaxe + schema)
# ═══════════════════════════════════════════════════════════════

class YAMLValidator:
    """Valida sintaxe de TODOS os .yaml/.yml do sistema."""

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def validate_all(self) -> Dict:
        yaml_files = []
        for d in [self.root / "01_neocortex_framework", self.root / "02_memory_lobes"]:
            if d.exists():
                yaml_files.extend(d.rglob("*.yaml"))
                yaml_files.extend(d.rglob("*.yml"))
        yaml_files = [f for f in yaml_files if "__pycache__" not in str(f)]

        valid, invalid, errors = 0, 0, []
        for f in sorted(yaml_files):
            try:
                # Try single document first, then multi-document
                content = f.read_text(encoding="utf-8", errors="ignore")
                try:
                    _yaml.safe_load(content)
                except _yaml.YAMLError:
                    # Try multi-document
                    list(_yaml.safe_load_all(content))
                valid += 1
            except _yaml.YAMLError as e:
                invalid += 1
                errors.append({"file": str(f.relative_to(self.root)), "error": str(e)[:200]})

        return {
            "total": len(yaml_files),
            "valid": valid,
            "invalid": invalid,
            "errors": errors[:10],
            "pct": round(valid / max(len(yaml_files), 1) * 100, 1),
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# R113 — MDC Header Validate (todos os lobes .mdc)
# ═══════════════════════════════════════════════════════════════

class MDCValidator:
    """Valida cabeçalho YAML de TODOS os lobes .mdc."""

    REQUIRED_HEADERS = ["lobe_id", "domain", "type", "created", "status"]
    MINIMAL_HEADERS = ["title"]  # Lobes legacy podem ter só título

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def validate_all(self) -> Dict:
        lobes_dir = self.root / "02_memory_lobes"
        lobes = list(lobes_dir.rglob("*.mdc")) if lobes_dir.exists() else []

        valid, invalid, warnings, errors = 0, 0, 0, []
        for f in sorted(lobes):
            content = f.read_text(encoding="utf-8", errors="ignore")
            header = {}
            has_header = False
            if content.strip().startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        header = _yaml.safe_load(parts[1]) or {}
                        has_header = True
                    except: pass
            if not has_header:
                invalid += 1
                errors.append({"file": str(f.relative_to(self.root)), "severity": "ERROR", "error": "No valid YAML header"})
                continue
            # Check if minimal (legacy) or full (new standard)
            missing_full = [k for k in self.REQUIRED_HEADERS if k not in header]
            has_minimal = any(k in header for k in self.MINIMAL_HEADERS)
            if missing_full and not has_minimal:
                invalid += 1
                errors.append({"file": str(f.relative_to(self.root)), "severity": "ERROR", "error": f"Missing required headers: {missing_full}"})
            elif missing_full and has_minimal:
                warnings += 1
                errors.append({"file": str(f.relative_to(self.root)), "severity": "WARNING", "error": f"Legacy header — missing: {missing_full}"})
                valid += 1
            else:
                valid += 1

        return {
            "total": len(lobes),
            "valid_full": valid - warnings,
            "valid_legacy": warnings,
            "invalid": invalid,
            "errors": errors[:20],
            "pct_healthy": round((valid) / max(len(lobes), 1) * 100, 1),
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# R114 — Secret Scan (tokens, senhas, chaves)
# ═══════════════════════════════════════════════════════════════

class SecretScanner:
    """Detecta tokens/senhas em arquivos commitados."""

    PATTERNS = [
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI/LiteLLM API key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        (r'token\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded token"),
        (r'mongodb\+srv://[^"\'\s]+', "MongoDB connection string"),
        (r'postgres://[^"\'\s]+', "PostgreSQL connection string"),
    ]

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def scan(self) -> Dict:
        findings = []
        files_scanned = 0
        EXCLUDE_PATHS = ["config.yaml", "_dev.yaml", ".nc/", "DIR-CFG-", "DIR-BAK-"]
        EXCLUDE_VALUES = ["your-api-key", "your-key", "your-token", "sk-my-master-key", "example.com", "placeholder"]
        EXCLUDE_FILES = ["NC-CORE-FR-158", "secret_scanner", "system-integrity"]

        for d in [self.root / "01_neocortex_framework", self.root / "02_memory_lobes"]:
            if not d.exists(): continue
            for f in d.rglob("*"):
                if f.is_dir() or "__pycache__" in str(f) or ".git" in str(f): continue
                rel = str(f.relative_to(self.root) if self.root in f.parents else f)
                if any(ex in rel for ex in EXCLUDE_PATHS): continue
                if any(ex in f.name for ex in EXCLUDE_FILES): continue
                if f.suffix in (".py", ".yaml", ".yml", ".md", ".mdc", ".json", ".toml", ".bat", ".ps1"):
                    files_scanned += 1
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        for pattern, label in self.PATTERNS:
                            m = re.search(pattern, content, re.IGNORECASE)
                            if m:
                                match_val = m.group()
                                if any(ev in match_val.lower() for ev in EXCLUDE_VALUES): continue
                                findings.append({"file": rel, "type": label, "match": match_val[:50]})
                    except: pass

        return {
            "files_scanned": files_scanned,
            "findings": findings,
            "leaks": len(findings),
            "safe": len(findings) == 0,
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# R115 — Dead Code / Orphan Scanner
# ═══════════════════════════════════════════════════════════════

class DeadCodeScanner:
    """Encontra arquivos orfaos nao referenciados por nenhum outro."""

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self._gitignore_cache = None

    def _get_gitignored(self) -> set:
        if self._gitignore_cache is not None:
            return self._gitignore_cache
        ignored = set()
        # Git ignore
        gi = self.root / "01_neocortex_framework" / ".gitignore"
        if gi.exists():
            for line in gi.read_text("utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "/" in line:
                    ignored.add(line.split("/")[-1])
        # NeoCortex ignore (falsos positivos: scripts/tests/docs)
        ni = self.root / "01_neocortex_framework" / ".neocortex_ignore"
        if ni.exists():
            for line in ni.read_text("utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "/" in line:
                    ignored.add(line.split("/")[-1])
        self._gitignore_cache = ignored
        return ignored

    def scan(self) -> Dict:
        fw = self.root / "01_neocortex_framework"
        gitignored = self._get_gitignored()
        all_files = {}
        all_ids = {}
        for d in [fw / "neocortex" / "core", fw / "neocortex" / "mcp" / "tools"]:
            if not d.exists(): continue
            for f in d.glob("*.py"):
                if f.name.startswith("_") or f.name in gitignored: continue
                rel = str(f.relative_to(self.root))
                all_files[rel] = f.read_text(encoding="utf-8", errors="ignore")
                nc_id = re.search(r'(NC-(?:CORE|SUPER|SVC|UTL)-FR-\d+)', f.name)
                if nc_id:
                    all_ids[nc_id.group(1)] = rel

        referenced = set()
        for fname, content in all_files.items():
            # Check NC-ID references across ALL content (not just this file)
            for nc_id, ref_fname in all_ids.items():
                if ref_fname == fname: continue
                if nc_id in content:
                    referenced.add(ref_fname)

        orphans = [f for f in all_files if f not in referenced]
        return {
            "total_files": len(all_files),
            "referenced": len(referenced),
            "orphans": orphans[:20],
            "orphan_count": len(orphans),
            "pct_healthy": round(len(referenced) / max(len(all_files), 1) * 100, 1),
            "timestamp": datetime.now().isoformat(),
        }


# ═══════════════════════════════════════════════════════════════
# Combined System Integrity Engine
# ═══════════════════════════════════════════════════════════════

class SystemIntegrityEngine:
    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))
        self.yaml = YAMLValidator(root=self.root)
        self.mdc = MDCValidator(root=self.root)
        self.secrets = SecretScanner(root=self.root)
        self.deadcode = DeadCodeScanner(root=self.root)

    def full_audit(self) -> Dict:
        return {
            "yaml_validate": self.yaml.validate_all(),
            "mdc_header": self.mdc.validate_all(),
            "secret_scan": self.secrets.scan(),
            "dead_code": self.deadcode.scan(),
            "generated_at": datetime.now().isoformat(),
        }


_integrity = None
def get_integrity() -> SystemIntegrityEngine:
    global _integrity
    if _integrity is None: _integrity = SystemIntegrityEngine()
    return _integrity
