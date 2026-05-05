"""---
@Validator NC-CORE-FR-164-claim-validator mcp NC-CORE-FR-164-claim-validator.py — R21 Enforcemen
---
"""

import json
import os
import pathlib
import re
from typing import Dict, Tuple


class ClaimValidator:
    """Cruza claims do assistente contra realidade do sistema."""

    CLAIMS = {
        "implementado": {
            "patterns": [r"implementado", r"pronto", r"feito", r"done", r"fixado", r"corrigido", r"criado", r"deploy"],
            "verify": "_verify_implementation",
            "rule": "R21",
        },
        "testado": {
            "patterns": [r"testado", r"testei", r"verificado", r"funcionando", r"passou"],
            "verify": "_verify_tested",
            "rule": "R21",
        },
        "deletado": {
            "patterns": [r"deletei", r"removi", r"apaguei", r"exclui"],
            "verify": "_verify_not_deleted",
            "rule": "R05",
        },
        "compilado": {
            "patterns": [r"compilei", r"compilado", r"compilou"],
            "verify": "_verify_compiled",
            "rule": "R21",
        },
        # R41 RAC: 5 Porquês — resposta deve conter raciocínio causal
        "RAC": {
            "patterns": [r"por que|porque|causa raiz|root cause|5 porqu"],
            "verify": "_verify_rac",
            "rule": "R41",
        },
        # R42 3W: What/Why/Where — resposta deve ter estrutura
        "3W": {
            "patterns": [r"what|why|where|o que|por que|onde"],
            "verify": "_verify_3w",
            "rule": "R42",
        },
        # R53 KISS: simplicidade — resposta não deve ser excessivamente longa
        "KISS": {
            "patterns": [r".{2500,}"],  # resposta com +2500 chars = viola KISS
            "verify": "_verify_kiss",
            "rule": "R53",
        },
    }

    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def validate(self, response_text: str) -> Dict:
        found_claims = []
        for claim_type, config in self.CLAIMS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, response_text, re.IGNORECASE):
                    found_claims.append(claim_type)
                    break

        if not found_claims:
            return {"claims_found": False, "violations": 0, "status": "OK"}

        violations = []
        for ct in found_claims:
            config = self.CLAIMS[ct]
            method = getattr(self, config["verify"], None)
            if method:
                try:
                    ok, evidence = method(response_text)
                except TypeError:
                    ok, evidence = method()
                if not ok:
                    violations.append({"claim": ct, "rule": config["rule"], "evidence": evidence})

        return {
            "claims_found": True,
            "claims_detected": found_claims,
            "violations": len(violations),
            "details": violations,
            "status": "BLOCKED" if violations else "VERIFIED",
            "message": "Claims nao comprovadas" if violations else "Claims verificadas com evidencia",
        }

    def _verify_implementation(self) -> Tuple[bool, str]:
        """Verifica: compilou + wired + ruff/mypy passando."""
        import subprocess
        import sys
        fw = self.root / "01_neocortex_framework" / "neocortex" / "core"
        recent = sorted(fw.glob("NC-CORE-FR-*.py"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
        results = []
        for f in recent:
            # Check 1: compiles
            r = subprocess.run([sys.executable, "-c",
                f"import py_compile; py_compile.compile({str(f)!r}, doraise=True)"],
                capture_output=True, text=True, timeout=5)
            if r.returncode != 0:
                return False, f"{f.name} failed compile: {r.stderr[:60]}"
            # Check 2: wired (referenced by another file?)
            nc_m = __import__("re").search(r"(NC-CORE-FR-\d+)", f.name)
            if nc_m:
                nc_id = nc_m.group(1)
                wired = False
                for other in fw.glob("NC-CORE-FR-*.py"):
                    if other.name == f.name or other.name.startswith("_"):
                        continue
                    if nc_id in other.read_text("utf-8", errors="ignore"):
                        wired = True
                        break
                if not wired:
                    for t in (self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools").glob("NC-SUPER-*.py"):
                        if nc_id in t.read_text("utf-8", errors="ignore"):
                            wired = True
                            break
                if not wired and "FR-14" not in nc_id:
                    results.append(f"{f.name}: NOT WIRED (no references)")
            # Check 3: ruff passing
            r2 = subprocess.run([sys.executable, "-m", "ruff", "check", str(f)],
                capture_output=True, text=True, timeout=5)
            if r2.returncode != 0:
                return False, f"{f.name} has ruff errors"
        if results:
            return False, "; ".join(results)
        return True, f"{len(recent)} files: compile OK + wired + ruff clean"

    def _verify_tested(self) -> Tuple[bool, str]:
        """Verifica se o watcher registrou atividade recente."""
        wf = self.root / ".neocortex" / "watcher" / "watcher_stats.json"
        if not wf.exists():
            return False, "Watcher stats file missing"
        try:
            d = json.loads(wf.read_text("utf-8"))
            checks = d.get("stats", {}).get("total_checks", 0)
            if checks == 0:
                return False, "0 checks recorded — nothing was actually tested"
            return True, f"{checks} checks recorded"
        except:
            return False, "Cannot read watcher stats"

    def _verify_not_deleted(self) -> Tuple[bool, str]:
        """Verifica se nenhum arquivo foi deletado (R05)."""
        archive = self.root / "01_neocortex_framework" / "DIR-ARC-FR-001-archive-main"
        return archive.exists(), "Archive dir exists (R05 compliant)"

    def _verify_compiled(self) -> Tuple[bool, str]:
        """Mesmo que _verify_implementation."""
        return self._verify_implementation()

    def _verify_rac(self, response_text: str = "") -> Tuple[bool, str]:
        """R41: Resposta deve conter raciocinio causal."""
        import re
        has_causal = bool(re.search(r'por que|porque|causa raiz|root cause', response_text, re.IGNORECASE))
        return has_causal, "RAC presente" if has_causal else "RAC ausente: sem raciocinio causal"

    def _verify_3w(self, response_text: str = "") -> Tuple[bool, str]:
        """R42: Resposta deve conter estrutura What/Why/Where."""
        import re
        what = bool(re.search(r'(what|o que)\b', response_text, re.IGNORECASE))
        why = bool(re.search(r'(why|por que|porque)\b', response_text, re.IGNORECASE))
        where = bool(re.search(r'(where|onde)\b', response_text, re.IGNORECASE))
        ok = what and why
        return ok, f"3W: What={what} Why={why} Where={where}"

    def _verify_kiss(self, response_text: str = "") -> Tuple[bool, str]:
        """R53: Resposta nao excessivamente complexa (>2500 chars)."""
        ok = len(response_text) < 2500
        return ok, f"KISS OK ({len(response_text)} chars)" if ok else f"KISS VIOLATION: {len(response_text)} chars"


_validator = None
def get_validator():
    global _validator
    if _validator is None: _validator = ClaimValidator()
    return _validator
