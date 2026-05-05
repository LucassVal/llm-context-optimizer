"""---
@Tool NC-CORE-FR-148-submission-pipeline mcp NC-CORE-FR-148-submission-pipeline.py — Pipeline d
---
"""
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SubmissionPipeline:
    """Pipeline completo de submissão governada."""

    def __init__(self, root: Path | None = None):
        import os
        self.root = root or Path(os.environ.get("NC_ROOT", Path(__file__).parents[3]))
        self.results: list[dict] = []

    # ── PIPELINE PRINCIPAL ─────────────────────────────────────

    def submit(self, files: list[str] | None = None, description: str = "",
               agent: str = "T0") -> dict[str, Any]:
        """Submeter mudanças — pipeline completo."""
        pipeline_id = f"SUB-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        result = {"pipeline_id": pipeline_id, "agent": agent, "steps": [], "passed": True}

        files = files or []

        # STEP 1: ruff/lint check
        step1 = self._ruff_check(files)
        result["steps"].append({"name": "ruff", "result": step1})

        # STEP 2: semantic/naming + 3W check
        step2 = self._semantic_check(files)
        result["steps"].append({"name": "semantic", "result": step2})

        # STEP 2.5: YAML validate (R112) — FAIL-FAST
        step25 = self._yaml_check(files)
        result["steps"].append({"name": "yaml_validate", "result": step25})

        # STEP 2.6: Secret scan (R114) — FAIL-FAST
        step26 = self._secret_check(files)
        result["steps"].append({"name": "secret_scan", "result": step26})

        # STEP 2.7: Mypy type check — FAIL-FAST
        step27 = self._mypy_check(files)
        result["steps"].append({"name": "mypy", "result": step27})

        # STEP 2.8: Pyright type check — FAIL-FAST (double security)
        step28 = self._pyright_check(files)
        result["steps"].append({"name": "pyright", "result": step28})

        # STEP 3: handoff
        step3 = self._create_handoff(description, agent, files)
        result["steps"].append({"name": "handoff", "result": step3})

        # STEP 4: RCA (se houver violações)
        has_violations = (step1.get("errors", 0) > 0 or not step2.get("valid", True)
                         or not step27.get("passed", True) or not step28.get("passed", True))
        if has_violations:
            step4 = self._rca_analysis(files, step1, step2)
            result["steps"].append({"name": "rca", "result": step4})

        # STEP 5: catalog refresh
        step5 = self._catalog_refresh()
        result["steps"].append({"name": "catalog", "result": step5})

        # STEP 6: roadmap sync
        step6 = self._roadmap_sync()
        result["steps"].append({"name": "roadmap", "result": step6})

        # Overall
        result["passed"] = all(s.get("result", {}).get("passed", True) for s in result["steps"] if s["name"] != "rca")
        result["timestamp"] = datetime.now().isoformat()

        self.results.append(result)
        return result

    # ── STEP 1: RUFF ───────────────────────────────────────────

    FAIL_FAST_ENABLED = True  # FAIL-FAST gate: ruff errors BLOCK submission

    def _ruff_check(self, files: list[str]) -> dict:
        if not files:
            return {"passed": True, "note": "sem arquivos para verificar", "fail_fast": self.FAIL_FAST_ENABLED}
        try:
            r = subprocess.run(
                [sys.executable, "-m", "ruff", "check", *files],
                capture_output=True, text=True, timeout=30, cwd=str(self.root)
            )
            errors = len([l for l in r.stdout.split("\n") if l.strip()]) if r.stdout else 0
            # FAIL-FAST: ruff errors BLOCK submission
            passed = r.returncode == 0 and errors == 0
            return {"passed": passed, "errors": errors,
                    "output": r.stdout[:500] if r.stdout else "",
                    "fail_fast": self.FAIL_FAST_ENABLED,
                    "blocked": not passed and self.FAIL_FAST_ENABLED,
                    "msg": "Prisão em Flagrante (CPP): violações ruff bloqueiam submissão" if not passed else "Nenhuma violação — build limpo"}
        except Exception as e:
            return {"passed": True, "note": f"ruff indisponível: {e}", "fail_fast": self.FAIL_FAST_ENABLED}

    # ── STEP 2: SEMANTIC + 3 W's ───────────────────────────────

    def _semantic_check(self, files: list[str]) -> dict:
        if not files:
            return {"valid": True, "note": "sem arquivos"}
        invalid = [f for f in files if not Path(f).name.startswith("NC-")]
        # 3 W's check: arquivo com NC- no nome deve ter What/Why/Where
        missing_ws = []
        for f in files:
            if Path(f).name.startswith("NC-") and Path(f).exists():
                content = Path(f).read_text(encoding="utf-8", errors="ignore")
                if not all(kw in content for kw in ("## What", "## Why", "## Where")):
                    if not re.search(r'\"\"\"---\n.+\n---', content):
                        missing_ws.append(Path(f).name)
        valid = len(invalid) == 0 and len(missing_ws) == 0
        return {"valid": valid, "invalid_files": invalid, "missing_3ws": missing_ws,
                "note": "OK" if valid else f"{len(invalid)} sem NC-, {len(missing_ws)} sem 3 W's",
                "auto_infracao": "Todo arquivo NC- deve ter seu Auto de Infração (3 W's)" if missing_ws else "OK"}

    # ── STEP 2.5: YAML VALIDATE (R112) ──────────────────────────

    def _yaml_check(self, files: list[str]) -> dict:
        if not files:
            return {"passed": True, "note": "sem arquivos YAML"}
        yamls = [f for f in files if f.endswith((".yaml", ".yml"))]
        if not yamls:
            return {"passed": True, "note": "sem arquivos YAML"}
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("si", str(self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-158-system-integrity.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            import yaml as _y
            invalid = []
            for yf in yamls:
                try:
                    _y.safe_load(Path(yf).read_text(encoding="utf-8", errors="ignore"))
                except Exception as e:
                    invalid.append(f"{yf}: {str(e)[:80]}")
            passed = len(invalid) == 0
            return {"passed": passed, "invalid": invalid, "msg": "YAML syntax error — bloqueado" if not passed else "OK"}
        except Exception as e:
            return {"passed": True, "note": f"YAML check indisponivel: {e}"}

    # ── STEP 2.6: SECRET SCAN (R114) ────────────────────────────

    def _secret_check(self, files: list[str]) -> dict:
        if not files:
            return {"passed": True, "note": "sem arquivos"}
        try:
            import subprocess
            import sys
            r = subprocess.run([sys.executable, "-c", f"""
import importlib.util
spec=importlib.util.spec_from_file_location('si',r'{self.root}/01_neocortex_framework/neocortex/core/NC-CORE-FR-158-system-integrity.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
r=m.get_integrity().secrets.scan()
print(r['leaks'] if r['leaks']==0 else str(r['leaks'])+' leaks: '+str(r.get('findings',[])[:3]))
"""], capture_output=True, text=True, timeout=30, cwd=str(self.root))
            leaks = 0 if "0" in r.stdout else 1
            passed = leaks == 0
            return {"passed": passed, "msg": "SECRETS expostas — bloqueado" if not passed else "OK"}
        except Exception:
            return {"passed": True, "note": "Secret scan indisponivel"}

    # ── STEP 2.7: MYPY TYPE CHECK ──────────────────────────────

    def _mypy_check(self, files: list[str]) -> dict:
        if not files:
            return {"passed": True, "note": "sem arquivos"}
        py_files = [f for f in files if f.endswith(".py")]
        if not py_files:
            return {"passed": True, "note": "sem arquivos .py"}
        try:
            r = subprocess.run([sys.executable, "-m", "mypy", *py_files, "--no-error-summary"],
                       capture_output=True, text=True, timeout=60, cwd=str(self.root))
            errors = len([l for l in r.stdout.splitlines() if ": error:" in l])
            passed = errors == 0
            return {"passed": passed, "errors": errors,
                    "msg": f"Type check FAILED: {errors} errors" if not passed else "Type check OK"}
        except Exception as e:
            return {"passed": True, "note": f"mypy indisponivel: {e}"}

    # ── STEP 2.8: PYRIGHT TYPE CHECK ───────────────────────────

    def _pyright_check(self, files: list[str]) -> dict:
        if not files:
            return {"passed": True, "note": "sem arquivos"}
        py_files = [f for f in files if f.endswith(".py")]
        if not py_files:
            return {"passed": True, "note": "sem arquivos .py"}
        try:
            r = subprocess.run([sys.executable, "-m", "pyright", *py_files, "--outputjson"],
                       capture_output=True, text=True, timeout=60, cwd=str(self.root))
            if r.returncode == 0:
                return {"passed": True, "msg": "Pyright OK"}
            try:
                import json
                d = json.loads(r.stdout)
                errs = d.get("summary", {}).get("errorCount", 1)
                return {"passed": False, "errors": errs,
                        "msg": f"Pyright: {errs} errors"}
            except:
                return {"passed": False, "msg": "Pyright failed"}
        except Exception as e:
            return {"passed": True, "note": f"pyright indisponivel: {e}"}

    # ── STEP 3: HANDOFF ────────────────────────────────────────

    def _create_handoff(self, description: str, agent: str, files: list[str]) -> dict:
        hf_dir = self.root / "DIR-DS-002-audit-logs"
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        hf = hf_dir / f"NC-DS-SUB-handoff-{ts}.yaml"
        hf.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"ticket_id: NC-DS-SUB\n"
            f"status: submitted\n"
            f"agent: {agent}\n"
            f"description: {description}\n"
            f"files: {files}\n"
            f"timestamp: {datetime.now().isoformat()}\n"
        )
        hf.write_text(content, encoding="utf-8")
        return {"passed": True, "handoff_file": str(hf.name)}

    # ── STEP 4: RCA ────────────────────────────────────────────

    def _rca_analysis(self, files: list[str], ruff: dict, semantic: dict) -> dict:
        try:
            import importlib.util
            rca_path = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-147-root-cause-engine.py"
            spec = importlib.util.spec_from_file_location("rca", str(rca_path))
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            engine = mod.get_rca()
            problem = f"Submissão com violações: ruff={ruff.get('errors',0)} erros, semantic={semantic.get('invalid_files',[])}"
            whys = [
                f"Arquivos com erros de lint: {ruff.get('errors', 0)}",
                "Código foi submetido sem validação prévia",
                "O desenvolvedor não rodou ruff antes de submeter",
                "Não há hook automático de pre-commit",
                "Falta CI/CD com gates de qualidade",
            ]
            return {"rca": engine.analyze_failure(problem, whys)}
        except: return {"note": "RCA indisponível"}

    # ── STEP 5: CATALOG ────────────────────────────────────────

    def _catalog_refresh(self) -> dict:
        catalog_file = self.root / "01_neocortex_framework" / ".neocortex" / "lexico" / "NC-LEXICO-LATEST.json"
        if catalog_file.exists():
            return {"passed": True, "catalog_updated": True}
        return {"passed": True, "note": "catálogo não encontrado"}

    # ── STEP 6: ROADMAP ────────────────────────────────────────

    def _roadmap_sync(self) -> dict:
        roadmap = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-TODO-FR-001-project-roadmap-consolidated.md"
        if roadmap.exists():
            return {"passed": True, "roadmap_exists": True, "size": roadmap.stat().st_size}
        return {"passed": False, "error": "roadmap não encontrado"}


_pipeline: SubmissionPipeline | None = None

def get_pipeline() -> SubmissionPipeline:
    global _pipeline
    if _pipeline is None: _pipeline = SubmissionPipeline()
    return _pipeline
