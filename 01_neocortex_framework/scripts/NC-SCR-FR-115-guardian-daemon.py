#!/usr/bin/env python3
"""---
NC-SCR-FR-115 — Guardian Daemon (COG-001)
---
"""

"""---
NC-SCR-FR-115 — Guardian Daemon (COG-001)
---
"""

"""
NC-SCR-FR-115 — Guardian Daemon (COG-001)
Qwen 1.5b como "Cerebelo" permanente do NeoCortex.

Responsabilidades (loop de 60s):
  1. HEALTH    — monitor portas MCP, Ollama, LiteLLM, PicoClaw
  2. HISTORY   — salvar histórico de turnos de chat via AKL
  3. SEMANTIC  — manter AKL + KG íntegros (decay, prune)
  4. AUTO-PAUSE — detectar contexto > 85% budget e emitir alerta
  5. CIRCUIT   — verificar circuit breakers de agentes

Logs estruturados (10MB rotação):
  .neocortex/logs/guardian/startup.log  — boot/shutdown/reinício
  .neocortex/logs/guardian/errors.log   — erros, alertas, circuit OPEN
  .neocortex/logs/guardian/events.log   — ciclos, heartbeats, health checks

Modelo: Qwen 1.5b via Ollama :11434 (CUDA, keep_alive=-1)
"""
import json
import logging
import logging.handlers
import os
import signal
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from threading import Event, Thread
from typing import Any, Dict

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT   = Path(os.environ.get("NC_ROOT", "")).resolve() if os.environ.get("NC_ROOT") else Path(__file__).resolve().parents[2]
FW_DIR = ROOT / "01_neocortex_framework"
LOG_DIR = FW_DIR / ".neocortex" / "logs" / "guardian"
LOG_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(FW_DIR))


# ── Logging estruturado ────────────────────────────────────────────────────────
def _setup_logging() -> logging.Logger:
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    def _rh(filename: str, level: int) -> logging.handlers.RotatingFileHandler:
        h = logging.handlers.RotatingFileHandler(
            LOG_DIR / filename,
            maxBytes=10 * 1024 * 1024,   # 10MB
            backupCount=3,
            encoding="utf-8",
        )
        h.setLevel(level)
        h.setFormatter(fmt)
        return h

    root_logger = logging.getLogger("guardian")
    root_logger.setLevel(logging.DEBUG)

    # Console (INFO+)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root_logger.addHandler(ch)

    # startup.log — apenas INFO de boot/shutdown
    startup_h = _rh("startup.log", logging.INFO)
    startup_h.addFilter(lambda r: any(k in r.getMessage() for k in
                                       ["🚀", "🛑", "BOOT", "SHUTDOWN", "reinici"]))
    root_logger.addHandler(startup_h)

    # errors.log — WARNING+ (erros, alertas, circuit OPEN)
    root_logger.addHandler(_rh("errors.log", logging.WARNING))

    # events.log — DEBUG+ (tudo: ciclos, heartbeats, health)
    root_logger.addHandler(_rh("events.log", logging.DEBUG))

    return root_logger


logger = _setup_logging()

OLLAMA_BASE  = os.environ.get("NC_OLLAMA", "http://localhost:11434")
MODEL        = "qwen2.5-coder:1.5b-instruct"
INTERVAL_SEC = int(os.environ.get("NC_GUARDIAN_INTERVAL", "60"))

# Portas para monitorar
SERVICES = {
    "ollama_cuda": ("localhost", 11434),
    "ollama_igpu":  ("localhost", 11435),
    "litellm":      ("localhost", 4000),
    "picoclaw":     ("localhost", 18790),
}


# ── Utilidades ─────────────────────────────────────────────────────────────────

def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    import socket
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False


def _ollama_ask(prompt: str, max_tok: int = 80) -> str:
    """Chama Qwen 1.5b. Retorna '' em caso de erro."""
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tok, "temperature": 0.1},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())["response"].strip()
    except Exception:
        return ""


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ── Módulos do daemon ───────────────────────────────────────────────────────────

class HealthMonitor:
    """Módulo 1 — monitora portas e gera alerta via Qwen se serviço cair."""

    def __init__(self):
        self._state: Dict[str, bool] = {}

    def run(self) -> Dict[str, Any]:
        results = {}
        alerts  = []

        for name, (host, port) in SERVICES.items():
            up = _port_open(host, port)
            results[name] = up

            # Detectar transição up→down
            prev = self._state.get(name, True)
            if prev and not up:
                msg = f"ALERTA: {name}:{port} ficou OFFLINE"
                logger.warning(msg)
                # Qwen diagnostica brevemente
                diag = _ollama_ask(
                    f"Service {name} on port {port} went offline. "
                    f"Suggest 1 quick recovery action in Portuguese (max 15 words)."
                )
                alerts.append({"service": name, "port": port, "diagnosis": diag})
            elif not prev and up:
                logger.info(f"RECUPERADO: {name}:{port} voltou ONLINE")

            self._state[name] = up

        online = sum(1 for v in results.values() if v)
        logger.info(f"[HEALTH] {online}/{len(SERVICES)} serviços online | {results}")
        return {"online": online, "total": len(SERVICES), "services": results, "alerts": alerts}


class SessionHistoryRecorder:
    """Módulo 2 — persiste eventos de sessão no AKL."""

    def __init__(self):
        self._akl = None
        self._session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _get_akl(self):
        if self._akl is None:
            try:
                from neocortex.core.akl_service import get_akl_service
                self._akl = get_akl_service()
            except Exception:
                pass
        return self._akl

    def record_heartbeat(self, health_data: Dict) -> None:
        akl = self._get_akl()
        if not akl:
            return
        try:
            key = f"guardian-heartbeat-{_ts()}"
            content = json.dumps({
                "session": self._session_id,
                "health": health_data,
                "ts": _ts(),
            })
            akl.add(key=key, content=content, tag="guardian_heartbeat",
                    session_id=self._session_id)
        except Exception as e:
            logger.debug(f"AKL record_heartbeat falhou: {e}")

    def record_event(self, event_type: str, data: str) -> None:
        akl = self._get_akl()
        if not akl:
            return
        try:
            key = f"guardian-event-{event_type}-{_ts()}"
            akl.add(key=key, content=data, tag=f"guardian_{event_type}",
                    session_id=self._session_id)
            logger.debug(f"[HISTORY] Evento registrado: {event_type}")
        except Exception as e:
            logger.debug(f"AKL record_event falhou: {e}")

    def get_session_id(self) -> str:
        return self._session_id


class SemanticMaintainer:
    """Módulo 3 — mantém AKL e KG íntegros (decay, stats)."""

    def __init__(self):
        self._cycle = 0
        self._decay_interval = 10  # A cada 10 ciclos (~10min)

    def run(self) -> Dict[str, Any]:
        self._cycle += 1
        result = {"cycle": self._cycle}

        try:
            from neocortex.core.akl_service import get_akl_service
            akl = get_akl_service()

            # Stats
            metrics = akl.get_metrics()
            result["akl_rules"] = metrics.get("total_rules", 0)

            # Decay periódico
            if self._cycle % self._decay_interval == 0:
                decay = akl.decay_knowledge()
                result["decay_applied"] = decay.get("count", 0)
                logger.info(f"[SEMANTIC] AKL decay: {decay.get('count', 0)} regras decaídas")

            # KG stats
            try:
                from neocortex.core.kg_service import get_kg_service
                kg = get_kg_service()
                kg_stats = kg.get_stats()
                result["kg_entities"] = kg_stats.get("total_entities", 0)
                result["kg_relations"] = kg_stats.get("total_relations", 0)
            except Exception:
                pass

            logger.info(f"[SEMANTIC] AKL: {result.get('akl_rules')} regras | "
                        f"KG: {result.get('kg_entities', '?')} entidades")
        except Exception as e:
            result["error"] = str(e)

        return result


class ContextWatchdog:
    """Módulo 4 — NC-DS-128: detecta saturação de contexto > 85% e age.

    Ações ao atingir threshold:
      1. Escreve .neocortex/AUTO_PAUSE.flag (T0 pode ler e compactar)
      2. Envia push notification via MCP
      3. Registra evento no AKL para rastreabilidade
    """

    BUDGET_THRESHOLD = 0.85   # 85% — pausa suave
    CRITICAL_THRESHOLD = 0.95  # 95% — emergência

    def __init__(self):
        self._flag_path = FW_DIR / ".neocortex" / "AUTO_PAUSE.flag"
        self._paused    = False

    def _write_flag(self, pct: float, critical: bool = False) -> None:
        """Escreve flag file que T0 pode checar para compactar contexto."""
        payload = json.dumps({
            "auto_pause": True,
            "context_usage_pct": round(pct * 100, 1),
            "critical": critical,
            "action_required": "context.compress" if not critical else "context.prune",
            "timestamp": _ts(),
        }, ensure_ascii=False)
        try:
            self._flag_path.write_text(payload, encoding="utf-8")
        except Exception as e:
            logger.debug(f"[CONTEXT] Flag write falhou: {e}")

    def _clear_flag(self) -> None:
        """Remove flag quando contexto volta ao normal."""
        try:
            if self._flag_path.exists():
                self._flag_path.unlink()
        except Exception:
            pass

    def _push_notify(self, pct: float, critical: bool) -> None:
        """Notificação via AKL (não depende do MCP estar em pé)."""
        try:
            from neocortex.core.akl_service import get_akl_service
            akl = get_akl_service()
            level = "CRITICAL" if critical else "WARNING"
            akl.add(
                key=f"auto_pause_{_ts()}",
                content=f"[NC-DS-128] {level}: contexto em {round(pct*100,1)}%. "
                        f"Recomendado: context.compress",
                tag="nc_ds_128_auto_pause",
                session_id="guardian",
            )
        except Exception as e:
            logger.debug(f"[CONTEXT] Push notify falhou: {e}")

    def run(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"auto_pause": False}
        try:
            from neocortex.core import get_ledger_service
            svc = get_ledger_service()
            if not hasattr(svc, "read_ledger"):
                return result
            ledger  = svc.read_ledger()
            hot_ctx = ledger.get("hot_context", {})
            ctx_size = len(str(hot_ctx))
            usage = ctx_size / 100_000   # 100k chars ≈ 100k tokens
            pct   = round(usage * 100, 1)
            result["context_usage_pct"] = pct

            if usage >= self.CRITICAL_THRESHOLD:
                result["auto_pause"] = True
                result["level"] = "CRITICAL"
                if not self._paused:
                    logger.error(f"[NC-DS-128] 🚨 CRÍTICO — contexto em {pct}%! Pausa imediata.")
                    self._write_flag(usage, critical=True)
                    self._push_notify(usage, critical=True)
                    self._paused = True

            elif usage >= self.BUDGET_THRESHOLD:
                result["auto_pause"] = True
                result["level"] = "WARNING"
                if not self._paused:
                    logger.warning(f"[NC-DS-128] ⚠️  Contexto em {pct}% (>{int(self.BUDGET_THRESHOLD*100)}%). "
                                   f"Flag AUTO_PAUSE.flag escrita.")
                    self._write_flag(usage, critical=False)
                    self._push_notify(usage, critical=False)
                    self._paused = True

            else:
                # Contexto voltou ao normal → remover flag
                if self._paused:
                    logger.info(f"[NC-DS-128] ✅ Contexto normalizado: {pct}%")
                    self._clear_flag()
                    self._paused = False
                logger.debug(f"[CONTEXT] {pct}% OK")

        except Exception as e:
            result["error"] = str(e)
        return result



class CircuitBreakerMonitor:
    """Módulo 5 — verifica circuit breakers dos agentes."""

    def run(self) -> Dict[str, Any]:
        try:
            from neocortex.core.circuit_breaker import list_breakers
            breakers = list_breakers()
            open_agents = [aid for aid, s in breakers.items() if s["state"] == "OPEN"]
            if open_agents:
                logger.warning(f"[CB] Agentes OPEN (bloqueados): {open_agents}")
            else:
                logger.debug(f"[CB] Todos os {len(breakers)} agentes CLOSED")
            return {"breakers": len(breakers), "open": open_agents}
        except Exception as e:
            return {"error": str(e)}


# ── Ciclo 3 — Encerramento de Sessão Automático ────────────────────────────────

class Ciclo3Runner:
    """
    Módulo 6 — Ciclo 3 automático.
    Executa a cada CICLO3_INTERVAL ticks (~1h com interval=60s):
      1. catalog.refresh     (NC-SCR-FR-064)
      2. bootup.sync         (NC-SCR-FR-066)
      3. yaml.sanitize       (NC-SCR-FR-009 --check-only)
    """
    CICLO3_INTERVAL = int(os.environ.get("NC_CICLO3_INTERVAL", "60"))  # ciclos

    def __init__(self):
        self._last_run = 0

    def _run_script(self, script_name: str, extra_args: list = None) -> Dict[str, Any]:
        import subprocess
        script = FW_DIR / "scripts" / script_name
        if not script.exists():
            return {"ok": False, "error": f"Script ausente: {script_name}"}
        args = [sys.executable, str(script)] + (extra_args or [])
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=str(ROOT))
            return {"ok": r.returncode == 0, "rc": r.returncode,
                    "out": r.stdout[-400:], "err": r.stderr[-200:]}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Timeout 60s"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def should_run(self, cycle: int) -> bool:
        return cycle > 0 and cycle % self.CICLO3_INTERVAL == 0

    def run(self) -> Dict[str, Any]:
        logger.info("[CICLO-3] 🔄 Iniciando rotina de encerramento...")
        results = {}

        # 1. catalog.refresh (G1)
        r1 = self._run_script("NC-SCR-FR-064-artifact-catalog.py")
        results["catalog_refresh"] = r1
        if r1["ok"]:
            logger.info("[CICLO-3] ✅ catalog.refresh OK")
        else:
            logger.warning(f"[CICLO-3] ⚠️ catalog.refresh: {r1.get('error', r1.get('err', '?'))}")

        # 2. bootup.sync (G5)
        r2 = self._run_script("NC-SCR-FR-066-bootup-sync.py")
        results["bootup_sync"] = r2
        if r2["ok"]:
            logger.info("[CICLO-3] ✅ bootup.sync OK")
        else:
            logger.warning(f"[CICLO-3] ⚠️ bootup.sync: {r2.get('error', r2.get('err', '?'))}")

        # 3. yaml.sanitize check-only (G6)
        r3 = self._run_script("NC-SCR-FR-009-sanitize-all-yamls.py", ["--check-only"])
        results["yaml_sanitize"] = r3
        if r3["ok"]:
            logger.info("[CICLO-3] ✅ yaml.sanitize OK (check-only)")
        else:
            logger.warning(f"[CICLO-3] ⚠️ yaml.sanitize: {r3.get('error', r3.get('err', '?'))}")

        # 4. lexico.build — Neuroplasticidade Semântica (LEXICO-001)
        try:
            from neocortex.core.lexico_service import get_lexico_service
            svc = get_lexico_service()
            stats = svc.build()
            results["lexico_build"] = {"ok": True, **stats}
            logger.info(f"[CICLO-3] ✅ lexico.build OK | termos={stats.get('total_terms', '?')}")
        except Exception as e:
            results["lexico_build"] = {"ok": False, "error": str(e)}
            logger.warning(f"[CICLO-3] ⚠️ lexico.build: {e}")

        # 5. cascade.consolidate — Consolidação Semântica (CASC-001)
        try:
            from neocortex.core.cascade_consolidator import CascadeConsolidator
            cc = CascadeConsolidator()
            cr = cc.run_once()
            results["cascade_consolidate"] = {"ok": True, "patterns": cr.get("patterns_saved", 0)}
            logger.info(f"[CICLO-3] ✅ cascade OK | patterns={cr.get('patterns_saved', 0)}")
        except Exception as e:
            results["cascade_consolidate"] = {"ok": False, "error": str(e)}
            logger.warning(f"[CICLO-3] ⚠️ cascade: {e}")

        ok_count = sum(1 for v in results.values() if v.get("ok"))
        logger.info(f"[CICLO-3] Concluído — {ok_count}/5 steps OK")
        return {"ciclo": 3, "steps": ok_count, "total": 5, "details": results}


# ── Ciclo 4 — Limpeza Semanal Automática ──────────────────────────────────────

class Ciclo4Runner:
    """
    Módulo 7 — Ciclo 4 automático.
    Executa a cada CICLO4_INTERVAL ticks (~24h com interval=60s = 1440 ciclos):
      1. governance.full_audit  (NC-SCR-FR-080)
      2. cycle.archive_handoffs (archiving filesystem direto)
      3. lobe.populate          (NC-SCR-FR-001)
    """
    CICLO4_INTERVAL = int(os.environ.get("NC_CICLO4_INTERVAL", "1440"))  # ciclos

    def __init__(self):
        self._last_run = 0

    def _run_script(self, script_name: str, extra_args: list = None,
                    timeout: int = 120) -> Dict[str, Any]:
        import subprocess
        script = FW_DIR / "scripts" / script_name
        if not script.exists():
            return {"ok": False, "error": f"Script ausente: {script_name}"}
        args = [sys.executable, str(script)] + (extra_args or [])
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
            return {"ok": r.returncode == 0, "rc": r.returncode,
                    "out": r.stdout[-400:], "err": r.stderr[-200:]}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"Timeout {timeout}s"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _archive_handoffs(self) -> Dict[str, Any]:
        """Archiving direto no filesystem — idêntico ao G3 da governance tool."""
        import shutil
        from datetime import timedelta
        now = datetime.now()
        arc_dir = ROOT / "DIR-ARC-FR-001-archive-main"
        arc_dir.mkdir(parents=True, exist_ok=True)
        archived_h, archived_t = 0, 0
        audit_dir = ROOT / "DIR-DS-002-audit-logs"
        if audit_dir.exists():
            for f in audit_dir.glob("*.yaml"):
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime) < now - timedelta(days=7):
                        shutil.move(str(f), str(arc_dir / f.name))
                        archived_h += 1
                except Exception:
                    pass
        tickets_dir = ROOT / "DIR-DS-001-tickets"
        patches_dir = ROOT / "DIR-DS-004-patches"
        patches_dir.mkdir(parents=True, exist_ok=True)
        if tickets_dir.exists():
            for f in tickets_dir.glob("NC-DS-*.yaml"):
                if "TEMPLATE" in f.name:
                    continue
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime) < now - timedelta(days=30):
                        shutil.move(str(f), str(patches_dir / f.name))
                        archived_t += 1
                except Exception:
                    pass
        return {"ok": True, "archived_handoffs": archived_h, "archived_tickets": archived_t}

    def should_run(self, cycle: int) -> bool:
        return cycle > 0 and cycle % self.CICLO4_INTERVAL == 0

    def run(self) -> Dict[str, Any]:
        logger.info("[CICLO-4] 🧹 Iniciando limpeza semanal...")
        results = {}

        # 1. governance.full_audit (G2)
        r1 = self._run_script("NC-SCR-FR-080-governance-auditor.py", timeout=120)
        results["governance_audit"] = r1
        if r1["ok"]:
            logger.info("[CICLO-4] ✅ governance.full_audit OK")
        else:
            logger.warning(f"[CICLO-4] ⚠️ governance.full_audit: {r1.get('error', '?')}")

        # 2. archive_handoffs filesystem direto (G3)
        r2 = self._archive_handoffs()
        results["archive_handoffs"] = r2
        logger.info(f"[CICLO-4] ✅ archive_handoffs: "
                    f"{r2['archived_handoffs']}h/{r2['archived_tickets']}t arquivados")

        # 3. lobe.populate — @POPULATE (G4)
        r3 = self._run_script("NC-SCR-FR-001-populate-lobes-ssot.py", timeout=90)
        results["lobe_populate"] = r3
        if r3["ok"]:
            logger.info("[CICLO-4] ✅ lobe.populate OK")
        else:
            logger.warning(f"[CICLO-4] ⚠️ lobe.populate: {r3.get('error', '?')}")

        # 4. KG enrich — Knowledge Graph population (NC-DS-133 KG-002)
        r4 = self._run_script("NC-SCR-FR-113-kg-populate-lobes.py", timeout=180)
        results["kg_enrich"] = r4
        if r4["ok"]:
            logger.info("[CICLO-4] ✅ kg.enrich OK")
        else:
            logger.warning(f"[CICLO-4] ⚠️ kg.enrich: {r4.get('error', '?')}")

        # 5. semantic.categorize — Qwen 1.5b categoriza lobes (P3 NC-DS-148)
        r5 = self._run_script("NC-SCR-FR-114-auto-categorize-lobes.py", timeout=300)
        results["semantic_categorize"] = r5
        if r5["ok"]:
            logger.info("[CICLO-4] ✅ semantic.categorize OK")
        else:
            logger.warning(f"[CICLO-4] ⚠️ semantic.categorize: {r5.get('error', '?')}")

        # 6. smoke_test — Valida 40 tools (P1 NC-DS-134)
        r6 = self._run_script("NC-SCR-FR-134-smoke-test-tools.py", timeout=120)
        results["smoke_test"] = r6
        if r6["ok"]:
            logger.info("[CICLO-4] ✅ smoke_test OK")
        else:
            logger.warning(f"[CICLO-4] ⚠️ smoke_test: {r6.get('error', '?')}")

        ok_count = sum(1 for v in results.values() if v.get("ok"))
        logger.info(f"[CICLO-4] Concluído — {ok_count}/6 steps OK")
        return {"ciclo": 4, "steps": ok_count, "total": 6, "details": results}


class GuardianDaemon:
    """
    Daemon principal do Qwen 1.5b Guardian.
    Roda em thread separada, loop de INTERVAL_SEC segundos.
    """

    def __init__(self, interval: int = INTERVAL_SEC):
        self.interval   = interval
        self._stop      = Event()
        self._thread    = None
        self.health     = HealthMonitor()
        self.history    = SessionHistoryRecorder()
        self.semantic   = SemanticMaintainer()
        self.context    = ContextWatchdog()
        self.cb_monitor = CircuitBreakerMonitor()
        self.ciclo3     = Ciclo3Runner()   # ← Módulo 6: Ciclo 3 automático
        self.ciclo4     = Ciclo4Runner()   # ← Módulo 7: Ciclo 4 automático
        self._cycle     = 0

        # State file para persistência
        self._state_file = ROOT / "01_neocortex_framework" / ".neocortex" / "guardian_state.json"
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

    def _tick(self) -> None:
        """Um ciclo completo do guardian."""
        self._cycle += 1
        logger.info(f"{'='*50}")
        logger.info(f"🛡️  Guardian CICLO {self._cycle} | {_ts()}")

        report = {"cycle": self._cycle, "ts": _ts()}

        # 1. Health check
        try:
            report["health"] = self.health.run()
        except Exception as e:
            report["health"] = {"error": str(e)}

        # 2. Semantic maintenance
        try:
            report["semantic"] = self.semantic.run()
        except Exception as e:
            report["semantic"] = {"error": str(e)}

        # 3. Context watchdog (NC-DS-128)
        try:
            report["context"] = self.context.run()
            if report["context"].get("auto_pause"):
                self.history.record_event("auto_pause",
                    f"Contexto saturado: {report['context'].get('context_usage_pct')}%")
        except Exception as e:
            report["context"] = {"error": str(e)}

        # 4. Circuit breaker monitor
        try:
            report["circuit_breakers"] = self.cb_monitor.run()
        except Exception as e:
            report["circuit_breakers"] = {"error": str(e)}

        # 5. Ciclo 3 automático — a cada ~1h (default 60 ticks)
        if self.ciclo3.should_run(self._cycle):
            try:
                report["ciclo3"] = self.ciclo3.run()
                self.history.record_event("ciclo3", json.dumps(report["ciclo3"]))
            except Exception as e:
                report["ciclo3"] = {"error": str(e)}
                logger.error(f"[CICLO-3] Erro inesperado: {e}")

        # 6. Ciclo 4 automático — a cada ~24h (default 1440 ticks)
        if self.ciclo4.should_run(self._cycle):
            try:
                report["ciclo4"] = self.ciclo4.run()
                self.history.record_event("ciclo4", json.dumps(report["ciclo4"]))
            except Exception as e:
                report["ciclo4"] = {"error": str(e)}
                logger.error(f"[CICLO-4] Erro inesperado: {e}")

        # 7. Persistir heartbeat no histórico
        self.history.record_heartbeat(report.get("health", {}))

        # 8. Salvar state
        try:
            self._state_file.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

        logger.info(f"🛡️  Ciclo {self._cycle} concluído | próximo em {self.interval}s")


    def _loop(self) -> None:
        logger.info(f"🚀 Guardian iniciado | session={self.history.get_session_id()} | interval={self.interval}s")
        while not self._stop.is_set():
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Erro no tick: {e}")
            self._stop.wait(timeout=self.interval)
        logger.info("🛑 Guardian parado")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning("Guardian já está rodando")
            return
        self._stop.clear()
        self._thread = Thread(target=self._loop, name="guardian-daemon", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def status(self) -> Dict[str, Any]:
        alive = self._thread is not None and self._thread.is_alive()
        state = {}
        if self._state_file.exists():
            try:
                state = json.loads(self._state_file.read_text("utf-8"))
            except Exception:
                pass
        return {
            "running": alive,
            "session_id": self.history.get_session_id(),
            "cycle": self._cycle,
            "interval_sec": self.interval,
            "last_report": state,
        }


# ── Singleton global ────────────────────────────────────────────────────────────

_daemon: GuardianDaemon = None


def get_guardian() -> GuardianDaemon:
    global _daemon
    if _daemon is None:
        _daemon = GuardianDaemon()
    return _daemon


def start_guardian(interval: int = INTERVAL_SEC) -> Dict[str, Any]:
    d = get_guardian()
    d.interval = interval
    d.start()
    return {"started": True, "session_id": d.history.get_session_id(), "interval": interval}


def stop_guardian() -> Dict[str, Any]:
    d = get_guardian()
    d.stop()
    return {"stopped": True}


def guardian_status() -> Dict[str, Any]:
    return get_guardian().status()


# ── Entrypoint standalone ───────────────────────────────────────────────────────

if __name__ == "__main__":
    daemon = GuardianDaemon(interval=INTERVAL_SEC)

    def _handle_sig(sig, frame):
        logger.info(f"Sinal {sig} recebido — parando guardian...")
        daemon.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT,  _handle_sig)
    signal.signal(signal.SIGTERM, _handle_sig)

    daemon.start()
    daemon._thread.join()  # Bloqueia até Ctrl+C
