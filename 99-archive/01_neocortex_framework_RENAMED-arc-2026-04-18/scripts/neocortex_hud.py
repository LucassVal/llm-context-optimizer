#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---"""

"""
NeoCortex HUD v5.1  Desktop Monitor & Control Panel
NC-SCR-FR-002-neocortex-hud.py | 2026-04-11
- 3 abas: Ferramentas clicveis / Compliance GOV / Agentes
- Estatsticas de eficincia MCP (tokens consulta vs gerao)
- Logging estruturado: ENTRY / EXIT / CHECKPOINT / DIFF  NC-LOG-FR-001
- Deteco stdio (psutil lazy) + WebSocket
"""

#  stdlib first (sem imports pesados no nvel de mdulo)
import json
import logging
import os
import queue
import socket
import subprocess
import sys
import threading
import time

#  Tkinter
import tkinter as tk
import traceback
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

#  PIL (necessrio para cone da bandeja)
try:
    from PIL import Image, ImageDraw
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

#  pystray (bandeja  opcional, no trava boot)
try:
    import pystray as _pystray
    _PYSTRAY_OK = True
except ImportError:
    _PYSTRAY_OK = False

#  psutil  import TARDIO (nunca no nvel de mdulo)
def _get_psutil():
    try:
        import psutil
        return psutil
    except ImportError:
        return None

#  Path setup
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#  Logging estruturado
LOG_DIR = PROJECT_ROOT / ".neocortex" / "logs" / "NC-LOG-FR-001-hud-audit"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_session_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
_log_file = LOG_DIR / f"hud_session_{_session_ts}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(_log_file), encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ]
)
log = logging.getLogger("NC-HUD")


def _log_entry(event: str, data: dict = None):
    """Registra eventos estruturados: ENTRY / EXIT / CHECKPOINT / DIFF."""
    payload = {"event": event, "ts": datetime.now().isoformat(), "data": data or {}}
    log.info(json.dumps(payload, ensure_ascii=False))
    # Tambm append no JSONL de auditoria
    audit_file = LOG_DIR / f"audit_{_session_ts}.jsonl"
    with open(str(audit_file), "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


#  Compliance imports (opcionais)
def _try_import_compliance():
    try:
        from neocortex.core.lock_guard import get_lock_guard
        from neocortex.core.policy_loader import get_policy_loader
        return get_lock_guard, get_policy_loader
    except Exception:
        return None, None

_get_lock_guard, _get_policy_loader = _try_import_compliance()

#  Constants
DEEPSEEK_PRICES = {
    "cache_hit": 0.028,   # $/1M tokens  consulta (cache hit, BARATO)
    "cache_miss": 0.28,   # $/1M tokens  consulta (cache miss)
    "output": 0.42,       # $/1M tokens  gerao de contedo (CARO)
}
MCP_SERVER_SCRIPT = PROJECT_ROOT / "neocortex" / "mcp" / "server.py"
NC_TOOLS_DIR = PROJECT_ROOT / "neocortex" / "mcp" / "tools"

AGENT_PORTS = {"courier": 11435, "engineer": 11436, "guardian": 11437}

COMPLIANCE_STANDARDS = [
    ("lock_guard",    " HIGH",  "STEP 0  Atomic Locks (LockGuard)"),
    ("policy_yaml",   " HIGH",  "PRE-1   Policy YAML carregado"),
    ("mentor_mode",   " HIGH",  "STEP 0  Mentor mode ativo"),
    ("audit_trail",   " HIGH",  "Audit Trail  fallback=DENY (SEC-401)"),
    ("save_point",    " HIGH",  "STEP -1  Save Point (SAVE-002)"),
    ("ssot_naming",   " MED",   "R01  @SSOT arquivo presente"),
    ("heartbeat",     " MED",   "Pulse  PulseScheduler ativo"),
    ("tool_manifest", " LOW",   "Manifest  NC-TLM-FR-001 presente"),
]

TOOL_CATALOG = {
    "neocortex_brain":      ("NC-TOOL-FR-000",  "T-0 DeepSeek  think, plan, orchestrate",
                             [("think","Raciocinar sobre prompt"),("plan","Gerar plano de ao"),("orchestrate","Spawn agente para task"),("critique","Avaliar output de agente"),("feedback","Registrar feedback")]),
    "neocortex_cortex":     ("NC-TOOL-FR-001",  "SSOT central  l/escreve memria principal",
                             [("get_full","Cortex completo"),("get_section","Seo especfica"),("get_aliases","Aliases definidos"),("get_workflows","Workflows definidos")]),
    "neocortex_lobes":      ("NC-TOOL-FR-009",  "Gerenciamento de lobos de memria",
                             [("list_active","Listar ativos"),("get_content","Contedo do lobe"),("activate","Ativar lobe"),("deactivate","Desativar lobe"),("search","Buscar nos lobes"),("list_all","Todos os lobes")]),
    "neocortex_checkpoint": ("NC-TOOL-FR-004",  "Checkpoints de work  STEP +1 / STEP -1",
                             [("get_current","Checkpoint atual"),("set_current","Novo checkpoint"),("complete_task","Marcar tarefa done"),("list_history","Histrico de checkpoints")]),
    "neocortex_ledger":     ("NC-TOOL-FR-008",  "Ledger JSON  mtricas, atomic locks, deps",
                             [("get_metrics","Mtricas da sesso"),("get_atomic_locks","Locks ativos"),("get_dependency_graph","Grafo de dependncias"),("prune_context","Pruning de contexto")]),
    "neocortex_config":     ("NC-TOOL-FR-005",  "Config do sistema  modelo LLM, constraints",
                             [("get_config","Config atual"),("set_model","Definir modelo"),("list_models","Modelos disponveis"),("set_constraint","Definir constraint"),("set_agent_backend","Backend por role")]),
    "neocortex_pulse":      ("NC-TOOL-FR-011",  "Pulso Cognitivo  scheduler autnomo",
                             [("status","Status do pulse"),("force","Forar task"),("start","Iniciar pulse"),("stop","Parar pulse")]),
    "neocortex_regression": ("NC-TOOL-FR-012",  "Buffer STEP 0  erros e regresses",
                             [("check","Verificar erros similares"),("add_entry","Adicionar erro"),("list_all","Listar todos"),("stats","Estatsticas do buffer")]),
    "neocortex_benchmark":  ("NC-TOOL-FR-003",  "Benchmarks Drift Exhaustion + Titanomachy",
                             [("run_drift","Drift Exhaustion"),("run_titanomachy","Titanomachy"),("get_last_report","ltimo relatrio")]),
    "neocortex_agent":      ("NC-TOOL-FR-002",  "Agentes efmeros  spawn, heartbeat, consume",
                             [("spawn","Criar agente efmero"),("heartbeat","Status do agente"),("consume","Resultados do agente"),("list_ephemeral","Listar agentes ativos")]),
    "neocortex_security":   ("NC-TOOL-FR-015",  "Segurana, auditoria e controle de acesso",
                             [("validate_access","Validar acesso a recurso"),("audit_changes","Auditoria de alteraes"),("encrypt_sensitive","Criptografar dado sensvel")]),
    "neocortex_picoclaw":   ("NC-TOOL-FR-036",  "PicoClaw Gateway  agente local autnomo",
                             [("task.send","Enviar task ao gateway"),("task.status","Status de task"),("gateway.health","Health check :18790"),("gateway.restart","Reiniciar gateway")]),
}


class HUDStats:
    """Rastreia estatsticas de uso MCP e eficincia de tokens."""
    def __init__(self):
        self._lock = threading.Lock()
        self.tool_calls_total = 0
        self.tool_calls_by_name: dict = {}
        self.tokens_input = 0       # tokens de consulta (baratos)
        self.tokens_output = 0      # tokens de gerao (caros!)
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        self.session_start = datetime.now()
        self._prev_snapshot: dict = {}

    def record_call(self, tool: str, input_tokens=0, output_tokens=0,
                    cache_hit=False, error=False):
        with self._lock:
            self.tool_calls_total += 1
            self.tool_calls_by_name[tool] = self.tool_calls_by_name.get(tool, 0) + 1
            self.tokens_input += input_tokens
            self.tokens_output += output_tokens
            if cache_hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            if error:
                self.errors += 1

    def snapshot(self) -> dict:
        with self._lock:
            total_tokens = self.tokens_input + self.tokens_output
            cache_rate = (self.cache_hits / max(1, self.cache_hits + self.cache_misses)) * 100
            # Custo estimado DeepSeek
            cost_input_hit  = (self.cache_hits * 1000) / 1e6 * DEEPSEEK_PRICES["cache_hit"]
            cost_input_miss = (self.cache_misses * 1000) / 1e6 * DEEPSEEK_PRICES["cache_miss"]
            cost_output = self.tokens_output / 1e6 * DEEPSEEK_PRICES["output"]
            total_cost = cost_input_hit + cost_input_miss + cost_output
            # Eficincia: razo input/output (> 1 = mais consulta que gerao = bom)
            ratio = self.tokens_input / max(1, self.tokens_output)
            elapsed = (datetime.now() - self.session_start).total_seconds()
            return {
                "tool_calls": self.tool_calls_total,
                "tokens_input": self.tokens_input,
                "tokens_output": self.tokens_output,
                "total_tokens": total_tokens,
                "cache_rate": cache_rate,
                "cost_usd": total_cost,
                "efficiency_ratio": ratio,
                "errors": self.errors,
                "elapsed_s": elapsed,
                "top_tools": sorted(self.tool_calls_by_name.items(), key=lambda x: -x[1])[:5],
            }

    def diff_snapshot(self) -> dict:
        """Retorna diff desde o ltimo snapshot (para log DIFF)."""
        cur = self.snapshot()
        diff = {k: cur[k] - self._prev_snapshot.get(k, 0)
                for k in ("tool_calls", "tokens_input", "tokens_output", "errors")
                if isinstance(cur[k], (int, float))}
        self._prev_snapshot = cur
        return diff


_stats = HUDStats()


class NeoCortexHUD:
    def __init__(self):
        _log_entry("ENTRY", {"event_type": "hud_start", "session": _session_ts,
                              "project_root": str(PROJECT_ROOT)})
        self.root = tk.Tk()
        self.root.title("NeoCortex HUD v5.1")
        self.root.geometry("1150x720")
        self.root.configure(bg="#1a1a2e")
        self.root.minsize(900, 580)

        self._apply_dark_theme()
        self._setup_icon()

        self.server_process = None
        self.server_running = False
        self.tray_icon = None
        self.update_queue = queue.Queue()
        self._selected_tool = None
        self._server_info = ""

        self._build_ui()
        self._start_monitoring()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close_btn)
        _log_entry("CHECKPOINT", {"phase": "init_complete"})

    #  Theme
    def _apply_dark_theme(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        bg, panel, acc = "#1a1a2e", "#16213e", "#0f3460"
        fg, red = "#e0e0e0", "#e94560"
        s.configure(".", background=bg, foreground=fg, font=("Segoe UI", 9))
        s.configure("TFrame", background=bg)
        s.configure("TLabel", background=bg, foreground=fg)
        s.configure("TLabelframe", background=panel, foreground="#aaaaaa", bordercolor="#333355")
        s.configure("TLabelframe.Label", background=panel, foreground="#8888cc", font=("Segoe UI", 9, "bold"))
        s.configure("TNotebook", background=bg, tabmargins=[2, 5, 2, 0])
        s.configure("TNotebook.Tab", background=acc, foreground=fg, padding=[12, 4])
        s.map("TNotebook.Tab", background=[("selected", red)], foreground=[("selected", "white")])
        s.configure("TButton", background=acc, foreground=fg, relief="flat", padding=[8, 4])
        s.map("TButton", background=[("active", red)])
        s.configure("TScrollbar", background=panel, troughcolor=bg)
        s.configure("Online.TLabel",  foreground="#4CAF50", background=bg, font=("Segoe UI", 10, "bold"))
        s.configure("Offline.TLabel", foreground="#FF5252", background=bg, font=("Segoe UI", 10, "bold"))

    def _setup_icon(self):
        self.tray_image = None
        if _PIL_OK:
            try:
                img = Image.new("RGB", (64, 64), "#1a1a2e")
                d = ImageDraw.Draw(img)
                d.ellipse([8, 8, 56, 56], fill="#e94560", outline="#ff6b8a")
                d.ellipse([22, 22, 42, 42], fill="#1a1a2e")
                self.tray_image = img
            except Exception:
                pass

    #  Main UI
    def _build_ui(self):
        # Header
        hdr = ttk.Frame(self.root)
        hdr.pack(fill=tk.X, padx=12, pady=(8, 2))
        tk.Label(hdr, text=" NeoCortex HUD v5.1", font=("Segoe UI", 14, "bold"),
                 fg="#e94560", bg="#1a1a2e").pack(side=tk.LEFT)
        srv = ttk.Frame(hdr)
        srv.pack(side=tk.RIGHT)
        self.server_status_var = tk.StringVar(value=" OFFLINE")
        self._srv_lbl = ttk.Label(srv, textvariable=self.server_status_var, style="Offline.TLabel")
        self._srv_lbl.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(srv, text=" Iniciar WS",  command=self.start_server).pack(side=tk.LEFT, padx=2)
        ttk.Button(srv, text=" Parar",       command=self.stop_server).pack(side=tk.LEFT, padx=2)
        ttk.Button(srv, text=" Logs",       command=self._open_log_dir).pack(side=tk.LEFT, padx=2)
        ttk.Button(srv, text=" Bandeja",     command=self._minimize_to_tray).pack(side=tk.LEFT, padx=2)

        # Notebook
        nb = ttk.Notebook(self.root)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        t1 = ttk.Frame(nb); nb.add(t1, text=f"  Ferramentas ({len(TOOL_CATALOG)})")
        t2 = ttk.Frame(nb); nb.add(t2, text="  Estatsticas")
        t3 = ttk.Frame(nb); nb.add(t3, text="  Compliance GOV")
        t4 = ttk.Frame(nb); nb.add(t4, text="  Agentes")
        t5 = ttk.Frame(nb); nb.add(t5, text="  PicoClaw")

        self._build_tools_tab(t1)
        self._build_stats_tab(t2)
        self._build_compliance_tab(t3)
        self._build_agents_tab(t4)
        self._build_picoclaw_tab(t5)

        # Status bar
        self.status_var = tk.StringVar(value=f"Sesso: {_session_ts}  |  Log: {_log_file.name}")
        tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                 anchor=tk.W, fg="#666688", bg="#0d0d1a", font=("Segoe UI", 8)
                 ).pack(fill=tk.X, side=tk.BOTTOM)

    #  Tab 1: Ferramentas
    def _build_tools_tab(self, p):
        p.columnconfigure(0, weight=0, minsize=230)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(0, weight=1)

        # Left list
        left = tk.Frame(p, bg="#10102a")
        left.grid(row=0, column=0, sticky="nsew")
        tk.Label(left, text="  Ferramentas MCP", font=("Segoe UI", 9, "bold"),
                 fg="#8888cc", bg="#10102a", anchor=tk.W, pady=4).pack(fill=tk.X)

        cv = tk.Canvas(left, bg="#10102a", highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._tools_lf = tk.Frame(cv, bg="#10102a")
        cv.create_window((0, 0), window=self._tools_lf, anchor="nw")
        self._tools_lf.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))

        self._tool_rows = {}
        for name, (nc_id, desc, acts) in TOOL_CATALOG.items():
            self._add_tool_row(name, nc_id, acts)

        # Right detail
        right = tk.Frame(p, bg="#0d0d1a")
        right.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        self._detail_title = tk.StringVar(value=" Selecione uma ferramenta")
        tk.Label(right, textvariable=self._detail_title, font=("Segoe UI", 12, "bold"),
                 fg="#e94560", bg="#0d0d1a", anchor=tk.W, padx=12, pady=8
                 ).grid(row=0, column=0, sticky="ew")
        self._detail_desc = tk.StringVar(value="")
        tk.Label(right, textvariable=self._detail_desc, font=("Segoe UI", 9),
                 fg="#aaaaaa", bg="#0d0d1a", anchor=tk.W, padx=12, wraplength=600
                 ).grid(row=1, column=0, sticky="ew")
        tk.Label(right, text="Aes:", font=("Segoe UI", 9, "bold"),
                 fg="#8888cc", bg="#0d0d1a", anchor=tk.W, padx=12, pady=8
                 ).grid(row=2, column=0, sticky="ew")
        self._actions_frame = tk.Frame(right, bg="#0d0d1a")
        self._actions_frame.grid(row=3, column=0, sticky="nsew", padx=12)
        self._detail_file = tk.StringVar(value="")
        tk.Label(right, textvariable=self._detail_file, font=("Courier", 8),
                 fg="#444466", bg="#0d0d1a", anchor=tk.W, padx=12
                 ).grid(row=4, column=0, sticky="ew")

    def _add_tool_row(self, name, nc_id, actions):
        row = tk.Frame(self._tools_lf, bg="#16213e", cursor="hand2")
        row.pack(fill=tk.X, pady=1, padx=3)
        dot = tk.Label(row, text="", fg="#4CAF50", bg="#16213e", font=("Segoe UI", 8), width=2)
        dot.pack(side=tk.LEFT, padx=(4, 0), pady=3)
        lbl = tk.Label(row, text=name.replace("neocortex_","  nc/"), fg="#cccccc",
                       bg="#16213e", font=("Segoe UI", 9), anchor=tk.W, pady=3)
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        badge = tk.Label(row, text=f"{len(actions)}", fg="#555577", bg="#16213e", font=("Segoe UI", 8), padx=4)
        badge.pack(side=tk.RIGHT)
        nc_lbl = tk.Label(row, text=nc_id, fg="#333355", bg="#16213e", font=("Courier", 7), padx=4)
        nc_lbl.pack(side=tk.RIGHT)
        self._tool_rows[name] = {"row": row, "dot": dot, "lbl": lbl}
        for w in (row, dot, lbl, badge, nc_lbl):
            w.bind("<Button-1>", lambda e, t=name: self._on_tool_click(t))
            w.bind("<Enter>", lambda e, r=row: r.configure(bg="#1e2f5e"))
            w.bind("<Leave>", lambda e, r=row, t=name:
                r.configure(bg="#0f3460" if self._selected_tool == t else "#16213e"))

    def _on_tool_click(self, name):
        if self._selected_tool and self._selected_tool in self._tool_rows:
            pr = self._tool_rows[self._selected_tool]
            pr["row"].configure(bg="#16213e"); pr["lbl"].configure(bg="#16213e", fg="#cccccc", font=("Segoe UI", 9))
        self._selected_tool = name
        row_d = self._tool_rows[name]
        row_d["row"].configure(bg="#0f3460")
        row_d["lbl"].configure(bg="#0f3460", fg="#ffffff", font=("Segoe UI", 9, "bold"))

        nc_id, desc, acts = TOOL_CATALOG[name]
        self._detail_title.set(f"  {name}")
        self._detail_desc.set(f"[{nc_id}]  {desc}")
        self._detail_file.set(f" {NC_TOOLS_DIR / (nc_id + '-' + name.replace('neocortex_','') + '.py')}")

        for w in self._actions_frame.winfo_children():
            w.destroy()

        for i, (action, adesc) in enumerate(acts):
            bg = "#16213e" if i % 2 == 0 else "#1a1f3a"
            af = tk.Frame(self._actions_frame, bg=bg, pady=3)
            af.pack(fill=tk.X, pady=1)
            tk.Label(af, text=f"    {action}", font=("Courier", 10, "bold"),
                     fg="#e94560", bg=bg, width=26, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(af, text=adesc, font=("Segoe UI", 9), fg="#aaaaaa", bg=bg, anchor=tk.W
                     ).pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        _log_entry("CHECKPOINT", {"tool_selected": name, "actions": len(acts)})
        self.status_var.set(f"Tool: {name}  |  {len(acts)} aes  |  {nc_id}")

    #  Tab 2: Estatsticas
    def _build_stats_tab(self, p):
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(1, weight=1)

        # Title
        tk.Label(p, text="Eficincia & Mtricas MCP  Sesso Atual",
                 font=("Segoe UI", 11, "bold"), fg="#e94560", bg="#1a1a2e", pady=8
                 ).grid(row=0, column=0, columnspan=2, sticky="ew")

        # Left: token economy
        left = tk.Frame(p, bg="#16213e")
        left.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=4)
        left.columnconfigure(1, weight=1)

        tk.Label(left, text=" Economia de Tokens", font=("Segoe UI", 10, "bold"),
                 fg="#64b5f6", bg="#16213e", pady=6).grid(row=0, column=0, columnspan=2, sticky="w", padx=8)

        self._stat_vars = {}
        stats_rows = [
            ("tool_calls",     "Chamadas MCP",           "#e0e0e0"),
            ("tokens_input",   "Tokens consulta (baratos)", "#81c784"),
            ("tokens_output",  "Tokens gerao (caros)",  "#FF5252"),
            ("cache_rate",     "Cache hit rate",          "#ffb74d"),
            ("efficiency",     "Ratio entrada/sada",     "#64b5f6"),
            ("cost_usd",       "Custo estimado (USD)",    "#ba68c8"),
            ("errors",         "Erros MCP",               "#FF5252"),
            ("elapsed",        "Tempo de sesso",         "#888888"),
        ]
        for i, (key, label, color) in enumerate(stats_rows, start=1):
            bg = "#16213e" if i % 2 else "#1a1f3a"
            tk.Label(left, text=f"  {label}", font=("Segoe UI", 9), fg="#aaaaaa",
                     bg=bg, anchor=tk.W, pady=5).grid(row=i, column=0, sticky="nsew", padx=4)
            var = tk.StringVar(value="")
            self._stat_vars[key] = var
            tk.Label(left, textvariable=var, font=("Segoe UI", 10, "bold"),
                     fg=color, bg=bg, anchor=tk.E, padx=12
                     ).grid(row=i, column=1, sticky="nsew")

        # Note on efficiency
        note = (
            " Eficincia:\n"
            " Tokens de consulta (input) = BARATOS $0.0280.28/M\n"
            " Tokens de gerao (output) = CAROS $0.42/M\n"
            " Ratio > 3 = uso eficiente do contexto\n"
            " Cache hit alto = economia mxima\n\n"
            "O HUD rastreia chamadas MCP internas.\n"
            "Tokens do Antigravity (Google/Gemini) so separados\n"
            "e no visveis diretamente pelo MCP."
        )
        tk.Label(left, text=note, font=("Segoe UI", 8), fg="#555577",
                 bg="#16213e", anchor=tk.W, justify=tk.LEFT, padx=12, pady=8
                 ).grid(row=len(stats_rows) + 2, column=0, columnspan=2, sticky="ew")

        # Right: top tools + log
        right = tk.Frame(p, bg="#16213e")
        right.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=4)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        tk.Label(right, text=" Top Tools (chamadas)", font=("Segoe UI", 10, "bold"),
                 fg="#64b5f6", bg="#16213e", pady=6).grid(row=0, column=0, sticky="ew", padx=8)

        self._top_tools_frame = tk.Frame(right, bg="#16213e")
        self._top_tools_frame.grid(row=1, column=0, sticky="nsew", padx=8)

        tk.Label(right, text=" Log de Auditoria (ltimas linhas)", font=("Segoe UI", 9, "bold"),
                 fg="#8888cc", bg="#16213e", pady=4).grid(row=2, column=0, sticky="ew", padx=8)

        self._log_text = tk.Text(right, font=("Courier", 8), bg="#0d0d1a", fg="#4CAF50",
                                  height=8, state=tk.DISABLED, wrap=tk.WORD)
        self._log_text.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))
        right.rowconfigure(3, weight=1)

        # Refresh button
        ttk.Button(right, text=" Atualizar Stats", command=self._refresh_stats
                   ).grid(row=4, column=0, padx=8, pady=4)

    def _refresh_stats(self):
        snap = _stats.snapshot()
        self._stat_vars["tool_calls"].set(str(snap["tool_calls"]))
        self._stat_vars["tokens_input"].set(f"{snap['tokens_input']:,}")
        self._stat_vars["tokens_output"].set(f"{snap['tokens_output']:,}")
        self._stat_vars["cache_rate"].set(f"{snap['cache_rate']:.1f}%")
        self._stat_vars["efficiency"].set(f"{snap['efficiency_ratio']:.2f}")
        self._stat_vars["cost_usd"].set(f"${snap['cost_usd']:.4f}")
        self._stat_vars["errors"].set(str(snap["errors"]))
        e = int(snap["elapsed_s"])
        self._stat_vars["elapsed"].set(f"{e//3600:02d}:{(e%3600)//60:02d}:{e%60:02d}")

        # Top tools
        for w in self._top_tools_frame.winfo_children():
            w.destroy()
        for i, (tool, count) in enumerate(snap["top_tools"]):
            bg = "#16213e" if i % 2 else "#1a1f3a"
            row = tk.Frame(self._top_tools_frame, bg=bg)
            row.pack(fill=tk.X)
            tk.Label(row, text=f"  {i+1}. {tool}", fg="#cccccc", bg=bg,
                     font=("Segoe UI", 9), anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(row, text=str(count), fg="#e94560", bg=bg,
                     font=("Segoe UI", 10, "bold"), padx=8).pack(side=tk.RIGHT)

        # Log file tail
        try:
            audit_file = LOG_DIR / f"audit_{_session_ts}.jsonl"
            if audit_file.exists():
                lines = audit_file.read_text(encoding="utf-8").splitlines()[-8:]
                self._log_text.configure(state=tk.NORMAL)
                self._log_text.delete("1.0", tk.END)
                for line in lines:
                    try:
                        entry = json.loads(line)
                        self._log_text.insert(tk.END, f"[{entry['event']}] {entry['ts'][11:19]}  {json.dumps(entry.get('data', {}), ensure_ascii=False)}\n")
                    except Exception:
                        self._log_text.insert(tk.END, line + "\n")
                self._log_text.configure(state=tk.DISABLED)
                self._log_text.see(tk.END)
        except Exception:
            pass

    #  Tab 3: Compliance
    def _build_compliance_tab(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)
        tk.Label(p, text="Padres de Governana  Verificao em Tempo Real",
                 font=("Segoe UI", 10, "bold"), fg="#e94560", bg="#1a1a2e", pady=6
                 ).grid(row=0, column=0, sticky="ew")

        cf = tk.Frame(p, bg="#16213e")
        cf.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        cf.columnconfigure(2, weight=1)

        for c, txt in [(0, "STATUS"), (1, "NVEL"), (2, "PADRO / DETALHE")]:
            tk.Label(cf, text=txt, font=("Segoe UI", 8, "bold"), fg="#555577",
                     bg="#16213e", padx=8, pady=4).grid(row=0, column=c, sticky="w")

        self._compliance_vars = {}
        self._compliance_labels = {}
        self._compliance_detail_vars = {}

        for ri, (key, level, label) in enumerate(COMPLIANCE_STANDARDS, start=1):
            bg = "#1a1f3a" if ri % 2 == 0 else "#16213e"
            sv = tk.StringVar(value="")
            sl = tk.Label(cf, textvariable=sv, font=("Courier", 10, "bold"),
                          bg=bg, fg="#888888", width=12, anchor=tk.W, padx=8, pady=6)
            sl.grid(row=ri, column=0, sticky="nsew")
            self._compliance_vars[key] = sv
            self._compliance_labels[key] = sl
            lc = {" HIGH": "#FF5252", " MED": "#FFC107", " LOW": "#4CAF50"}.get(level, "#888")
            tk.Label(cf, text=level, font=("Segoe UI", 8, "bold"), fg=lc, bg=bg,
                     width=10, anchor=tk.W, padx=4).grid(row=ri, column=1, sticky="nsew")
            dv = tk.StringVar(value=label)
            self._compliance_detail_vars[key] = dv
            tk.Label(cf, textvariable=dv, font=("Segoe UI", 9), fg="#cccccc",
                     bg=bg, anchor=tk.W, padx=8).grid(row=ri, column=2, sticky="nsew")

        self._compliance_last_update = tk.StringVar(value="aguardando 1 verificao")
        tk.Label(p, textvariable=self._compliance_last_update, font=("Segoe UI", 8),
                 fg="#444466", bg="#1a1a2e", anchor=tk.E
                 ).grid(row=2, column=0, sticky="ew", padx=8, pady=2)

    #  Tab 4: Agentes
    def _build_agents_tab(self, p):
        f = tk.Frame(p, bg="#1a1a2e")
        f.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        tk.Label(f, text="Agent Heartbeats  portas locais (TCP)",
                 font=("Segoe UI", 11, "bold"), fg="#e94560", bg="#1a1a2e", pady=6
                 ).pack(anchor=tk.W)
        self._agent_vars = {}
        self._agent_labels = {}
        for agent, port in AGENT_PORTS.items():
            af = tk.Frame(f, bg="#16213e", pady=8, padx=12)
            af.pack(fill=tk.X, pady=4)
            var = tk.StringVar(value=f"  {agent.upper()} (:{port})")
            lbl = tk.Label(af, textvariable=var, font=("Courier", 11, "bold"),
                           fg="#555555", bg="#16213e", anchor=tk.W)
            lbl.pack(side=tk.LEFT)
            self._agent_vars[agent] = var
            self._agent_labels[agent] = lbl
        tk.Label(f, text="\nIniciar agente com:\n  python -m neocortex.mcp.sub_server --role courier --port 11435",
                 font=("Courier", 9), fg="#444466", bg="#1a1a2e", justify=tk.LEFT
                 ).pack(anchor=tk.W, pady=8)

    #  Tab 5: PicoClaw
    def _build_picoclaw_tab(self, p):
        f = tk.Frame(p, bg="#1a1a2e")
        f.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        tk.Label(f, text=" PicoClaw Gateway  Agente Local Autnomo",
                 font=("Segoe UI", 11, "bold"), fg="#e94560", bg="#1a1a2e", pady=6
                 ).pack(anchor=tk.W)

        # Status row
        sf = tk.Frame(f, bg="#16213e", pady=8, padx=12)
        sf.pack(fill=tk.X, pady=4)
        self._pic_status_var = tk.StringVar(value="  Verificando gateway :18790...")
        self._pic_status_lbl = tk.Label(sf, textvariable=self._pic_status_var,
                                        font=("Courier", 11, "bold"), fg="#555555",
                                        bg="#16213e", anchor=tk.W)
        self._pic_status_lbl.pack(side=tk.LEFT)

        # Buttons
        bf = tk.Frame(f, bg="#1a1a2e")
        bf.pack(fill=tk.X, pady=4)
        ttk.Button(bf, text=" Verificar",  command=self._pic_check).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(bf, text=" Iniciar",   command=self._pic_start).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=" Parar",    command=self._pic_stop).pack(side=tk.LEFT, padx=4)

        # Config path
        cfg = PROJECT_ROOT.parent / "DIR-DS-000-agent-config" / "NC-CFG-PIC-001-picoclaw-config.json"
        tk.Label(f, text=f"Config: {cfg}", font=("Courier", 8),
                 fg="#444466", bg="#1a1a2e", anchor=tk.W).pack(anchor=tk.W, pady=(8, 0))
        tk.Label(f, text="Porta: :18790  |  Tool MCP: NC-TOOL-FR-036-picoclaw.py",
                 font=("Segoe UI", 9), fg="#555577", bg="#1a1a2e", anchor=tk.W
                 ).pack(anchor=tk.W)

        # Log tail
        tk.Label(f, text="\nOutput recente:", font=("Segoe UI", 9, "bold"),
                 fg="#8888cc", bg="#1a1a2e").pack(anchor=tk.W)
        self._pic_log = tk.Text(f, font=("Courier", 8), bg="#0d0d1a", fg="#4CAF50",
                                height=8, state=tk.DISABLED, wrap=tk.WORD)
        self._pic_log.pack(fill=tk.BOTH, expand=True, pady=4)

        # Start monitoring
        threading.Thread(target=self._pic_monitor, daemon=True).start()

    def _pic_check_alive(self):
        """Retorna (alive: bool, latency_ms: int)."""
        import time
        t = time.monotonic()
        try:
            s = socket.socket()
            s.settimeout(1.5)
            ok = s.connect_ex(("127.0.0.1", 18790)) == 0
            s.close()
            return ok, int((time.monotonic() - t) * 1000)
        except Exception:
            return False, 0

    def _pic_monitor(self):
        """Background thread  monitora gateway a cada 8s."""
        while True:
            alive, ms = self._pic_check_alive()
            self.update_queue.put((self._pic_update_ui, (alive, ms)))
            import time; time.sleep(8)

    def _pic_update_ui(self, alive, ms=0):
        if alive:
            self._pic_status_var.set(f" ONLINE  :18790  ({ms}ms)")
            self._pic_status_lbl.configure(fg="#4CAF50")
        else:
            self._pic_status_var.set(" OFFLINE  :18790")
            self._pic_status_lbl.configure(fg="#FF5252")

    def _pic_check(self):
        alive, ms = self._pic_check_alive()
        self._pic_update_ui(alive, ms)
        self.status_var.set(f"PicoClaw: {'ONLINE' if alive else 'OFFLINE'}  {ms}ms")

    def _pic_start(self):
        cfg = PROJECT_ROOT.parent / "DIR-DS-000-agent-config" / "NC-CFG-PIC-001-picoclaw-config.json"
        try:
            if cfg.exists():
                subprocess.Popen(["picoclaw", "--port", "18790", "--config", str(cfg)],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0)
            else:
                subprocess.Popen(["picoclaw", "--port", "18790"],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0)
            self.status_var.set("PicoClaw: iniciando...")
            _log_entry("ENTRY", {"event_type": "picoclaw_start"})
        except Exception as e:
            self.status_var.set(f"PicoClaw erro: {e}")

    def _pic_stop(self):
        import subprocess as _sp
        try:
            _sp.run(["taskkill", "/f", "/im", "picoclaw.exe"], capture_output=True)
            self.status_var.set("PicoClaw: parado")
            _log_entry("EXIT", {"event_type": "picoclaw_stop"})
        except Exception as e:
            self.status_var.set(f"PicoClaw erro: {e}")

    #  Monitoring threads
    def _start_monitoring(self):
        _log_entry("ENTRY", {"event_type": "monitoring_start"})
        threading.Thread(target=self._queue_worker,    daemon=True).start()
        threading.Thread(target=self._monitor_server,  daemon=True).start()
        threading.Thread(target=self._monitor_compliance, daemon=True).start()
        threading.Thread(target=self._stats_loop,      daemon=True).start()

    def _queue_worker(self):
        while True:
            try:
                fn, args = self.update_queue.get(timeout=0.1)
                self.root.after(0, fn, *args)
            except queue.Empty:
                time.sleep(0.05)
            except Exception:
                pass

    def _is_server_running(self):
        try:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", 8765)) == 0:
                s.close()
                return True, "ws://127.0.0.1:8765"
            s.close()
        except Exception:
            pass
        # Lazy psutil  no trava o boot
        psutil = _get_psutil()
        if psutil:
            try:
                for proc in psutil.process_iter(["pid", "cmdline"]):
                    cmd = " ".join(proc.info.get("cmdline") or [])
                    if "neocortex.mcp.server" in cmd:
                        return True, f"stdio PID:{proc.info['pid']}"
            except Exception:
                pass
        if self.server_process and self.server_process.poll() is None:
            return True, f"ws PID:{self.server_process.pid}"
        return False, ""

    def _monitor_server(self):
        prev = None
        while True:
            running, info = self._is_server_running()
            if running != prev:
                _log_entry("DIFF", {"server_running": running, "info": info,
                                    "prev": prev})
                prev = running
            self.update_queue.put((self._update_server_ui, (running, info)))
            time.sleep(4)

    def _update_server_ui(self, running, info=""):
        self.server_running = running
        self._server_info = info
        if running:
            self.server_status_var.set(f" ONLINE  {info}")
            self._srv_lbl.configure(style="Online.TLabel")
        else:
            self.server_status_var.set(" OFFLINE")
            self._srv_lbl.configure(style="Offline.TLabel")

    def _stats_loop(self):
        while True:
            time.sleep(30)
            diff = _stats.diff_snapshot()
            _log_entry("DIFF", {"stats_delta_30s": diff})
            self.update_queue.put((self._refresh_stats, ()))

    def _monitor_compliance(self):
        while True:
            try:
                results = self._run_compliance_checks()
                agents = {}
                for agent, port in AGENT_PORTS.items():
                    try:
                        s = socket.socket()
                        s.settimeout(0.5)
                        agents[agent] = (s.connect_ex(("127.0.0.1", port)) == 0)
                        s.close()
                    except Exception:
                        agents[agent] = False
                self.update_queue.put((self._update_compliance_ui, (results, agents)))
            except Exception:
                pass
            time.sleep(6)

    def _update_compliance_ui(self, results, agents):
        for key, (status, detail) in results.items():
            if key not in self._compliance_vars:
                continue
            self._compliance_vars[key].set(status)
            orig_label = next((l for k, _, l in COMPLIANCE_STANDARDS if k == key), "")
            self._compliance_detail_vars[key].set(f"{orig_label}    {detail[:70]}")
            c = "#4CAF50" if "" in status else "#FFC107" if "" in status else "#FF5252"
            self._compliance_labels[key].configure(fg=c)
        for agent, alive in agents.items():
            if agent not in self._agent_vars:
                continue
            port = AGENT_PORTS[agent]
            if alive:
                self._agent_vars[agent].set(f" ALIVE  {agent.upper()} (:{port})")
                self._agent_labels[agent].configure(fg="#4CAF50")
            else:
                self._agent_vars[agent].set(f" OFFLINE  {agent.upper()} (:{port})")
                self._agent_labels[agent].configure(fg="#555555")
        self._compliance_last_update.set(f"atualizado: {datetime.now().strftime('%H:%M:%S')}")

    def _run_compliance_checks(self):
        root = PROJECT_ROOT
        r = {}
        # LockGuard
        if _get_lock_guard:
            try:
                cs = _get_lock_guard().get_compliance_status()
                ok = cs.get("yaml_loaded", False)
                r["lock_guard"] = (" ATIVO" if ok else " FALTA", str(cs.get("lock_file", "")))
            except Exception as e:
                r["lock_guard"] = (" ERR", str(e)[:50])
        else:
            files = list((root / "neocortex" / "core").glob("NC-CORE-FR-014*"))
            r["lock_guard"] = (" OK" if files else " FALTA", files[0].name if files else "NC-CORE-FR-014 ausente")
        # Policy YAML
        yaml_p = root / "DIR-DOC-FR-001-docs-main" / "NC-CFG-FR-001-agent-policy-template.yaml"
        r["policy_yaml"] = (" OK" if yaml_p.exists() else " FALTA", yaml_p.name)
        # Mentor mode
        ss = root / "neocortex" / "mcp" / "sub_server.py"
        ok = ss.exists() and "mentor_step_0" in ss.read_text("utf-8", errors="ignore") if ss.exists() else False
        r["mentor_mode"] = (" OK" if ok else " FALTA", "mentor_step_0 em sub_server.py")
        # Audit trail SEC-401
        sc = root / "neocortex" / "core" / "security_service.py"
        ok = sc.exists() and "deny_by_default_sec401" in sc.read_text("utf-8", errors="ignore") if sc.exists() else False
        r["audit_trail"] = (" FIXADO" if ok else " BRECHA", "deny_by_default_sec401")
        # Save Point SAVE-002
        sp = list((root / "neocortex" / "core").glob("NC-CORE-FR-022*"))
        r["save_point"] = (" ATIVO" if sp else " FALTA", sp[0].name if sp else "NC-CORE-FR-022 ausente")
        # SSOT
        ssot = root / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001-naming-convention.md"
        r["ssot_naming"] = (" OK" if ssot.exists() else " FALTA", ssot.name)
        # Pulse
        pf = list((root / "neocortex" / "core").glob("*pulse*scheduler*.py"))
        r["heartbeat"] = (" OK" if pf else " FALTA", pf[0].name if pf else "pulse_scheduler ausente")
        # Manifest
        mf = list((root / "DIR-DOC-FR-001-docs-main").glob("NC-TLM-FR-001*.json"))
        if not mf: mf = list(root.rglob("NC-TLM-FR-001*.json"))
        r["tool_manifest"] = (" OK" if mf else " FALTA", mf[0].name if mf else "N/A")
        return r

    #  Server control
    def start_server(self):
        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Servidor", "Servidor j est rodando.")
            return
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT)
            self.server_process = subprocess.Popen(
                [sys.executable, "-X", "utf8", str(MCP_SERVER_SCRIPT),
                 "--transport", "websocket", "--host", "127.0.0.1", "--port", "8765"],
                cwd=str(PROJECT_ROOT), env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
            )
            _log_entry("ENTRY", {"event_type": "server_start_ws", "pid": self.server_process.pid})
            self.status_var.set(f"Servidor WS iniciado PID:{self.server_process.pid}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha: {e}")

    def stop_server(self):
        if self.server_process:
            _log_entry("EXIT", {"event_type": "server_stop", "pid": self.server_process.pid})
            self.server_process.terminate()
            self.server_process = None
            self.status_var.set("Servidor parado.")

    def _open_log_dir(self):
        try:
            os.startfile(str(LOG_DIR))
        except Exception:
            self.status_var.set(f"Logs em: {LOG_DIR}")

    #  Tray
    def _minimize_to_tray(self):
        if _PYSTRAY_OK and self.tray_image:
            try:
                menu = _pystray.Menu(
                    _pystray.MenuItem("Restaurar", self._restore_from_tray, default=True),
                    _pystray.MenuItem("Sair", self._quit),
                )
                self.tray_icon = _pystray.Icon("NeoCortex", self.tray_image, "NeoCortex HUD v5.1", menu)
                self.root.withdraw()
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
                return
            except Exception:
                pass
        self.root.withdraw()

    def _restore_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.deiconify()
        self.root.lift()

    def _on_close_btn(self):
        _log_entry("EXIT", {"event_type": "hud_close", "server_running": self.server_running,
                             "stats": _stats.snapshot()})
        self._minimize_to_tray()

    def _quit(self, icon=None, item=None):
        _log_entry("EXIT", {"event_type": "hud_quit", "stats": _stats.snapshot()})
        self.stop_server()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()

    def run(self):
        _log_entry("ENTRY", {"event_type": "mainloop_start"})
        self.root.mainloop()


#  Entrypoint
if __name__ == "__main__":
    _log_entry("ENTRY", {"event_type": "process_start", "argv": sys.argv,
                          "python": sys.version.split()[0]})
    missing = []
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    if not _PIL_OK:
        missing.append("pillow")

    if missing:
        print(f"[ERRO] Dependncias ausentes: {', '.join(missing)}")
        print("Instale: pip install pillow pystray psutil")
        sys.exit(1)

    try:
        app = NeoCortexHUD()
        app.run()
    except Exception:
        _log_entry("EXIT", {"event_type": "crash", "error": traceback.format_exc()})
        raise
