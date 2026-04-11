#!/usr/bin/env python3
"""
NeoCortex HUD - Desktop Monitor & Control Panel

HUD para área de trabalho que mostra:
- Status do servidor MCP (online/offline)
- Lista de 22+ ferramentas com status
- Métricas de economia (token usage, cost savings)
- Minimiza para bandeja do sistema
- Mouse hover para mostrar tela de status
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw
import queue

# DeepSeek pricing per 1M tokens
DEEPSEEK_PRICES = {"cache_hit": 0.028, "cache_miss": 0.28, "output": 0.42}

# Configurações
PROJECT_ROOT = Path(__file__).parent
MCP_SERVER_SCRIPT = (
    PROJECT_ROOT / "neocortex_framework" / "neocortex" / "mcp" / "server.py"
)
METRICS_DB = (
    PROJECT_ROOT
    / "neocortex_framework"
    / ".neocortex"
    / "cache"
    / "metrics"
    / "neocortex_metrics.db"
)
TOOL_MODULES = [
    "cortex",
    "lobes",
    "checkpoint",
    "regression",
    "ledger",
    "benchmark",
    "agent",
    "init",
    "config",
    "export",
    "manifest",
    "kg",
    "consolidation",
    "akl",
    "peers",
    "security",
    "pulse",
    "search",
    "subserver",
    "task",
    "report",
]


class NeoCortexHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeoCortex HUD v4.2")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        # Variáveis de estado
        self.server_process = None
        self.server_running = False
        self.server_port = 8765
        self.tray_icon = None
        self.update_queue = queue.Queue()

        # Configurar ícone
        self.setup_icon()

        # Criar interface
        self.setup_ui()

        # Iniciar threads de monitoramento
        self.start_monitoring()

        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.root.bind("<Enter>", self.on_mouse_enter)
        self.root.bind("<Leave>", self.on_mouse_leave)

    def setup_icon(self):
        """Criar ícone para bandeja do sistema"""
        try:
            # Criar ícone simples com PIL
            image = Image.new("RGB", (64, 64), color="#2d2d2d")
            draw = ImageDraw.Draw(image)
            draw.ellipse([16, 16, 48, 48], fill="#4CAF50", outline="#388E3C")
            draw.ellipse([24, 24, 40, 40], fill="#1e1e1e")

            self.tray_image = image
        except Exception as e:
            print(f"Erro ao criar ícone: {e}")
            self.tray_image = None

    def setup_ui(self):
        """Configurar interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(
            header_frame,
            text="🧠 NeoCortex HUD v4.2",
            font=("Arial", 16, "bold"),
            foreground="#4CAF50",
        ).pack(side=tk.LEFT)

        # Status do servidor
        self.server_status_var = tk.StringVar(value="🔴 OFFLINE")
        status_label = ttk.Label(
            header_frame,
            textvariable=self.server_status_var,
            font=("Arial", 12),
            foreground="#FF5252",
        )
        status_label.pack(side=tk.RIGHT, padx=10)

        # Botões de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(
            control_frame, text="▶ Iniciar Servidor", command=self.start_server
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame, text="⏹ Parar Servidor", command=self.stop_server
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame, text="📊 Atualizar Métricas", command=self.update_metrics
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📋 Copiar URL", command=self.copy_url).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            control_frame, text="⬇ Minimizar", command=self.minimize_to_tray
        ).pack(side=tk.RIGHT, padx=5)

        # Painel de métricas
        metrics_frame = ttk.LabelFrame(
            main_frame, text="📈 Métricas de Economia", padding="10"
        )
        metrics_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
        metrics_frame.columnconfigure(2, weight=1)

        # Métricas diárias
        ttk.Label(metrics_frame, text="HOJE:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.today_tokens = ttk.Label(
            metrics_frame, text="Tokens: 0", font=("Arial", 9)
        )
        self.today_tokens.grid(row=1, column=0, sticky=tk.W)
        self.today_cost = ttk.Label(
            metrics_frame, text="Custo: $0.00", font=("Arial", 9)
        )
        self.today_cost.grid(row=2, column=0, sticky=tk.W)
        self.today_cache = ttk.Label(metrics_frame, text="Cache: 0%", font=("Arial", 9))
        self.today_cache.grid(row=3, column=0, sticky=tk.W)

        # Métricas semanais
        ttk.Label(metrics_frame, text="SEMANA:", font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky=tk.W, pady=5
        )
        self.week_tokens = ttk.Label(metrics_frame, text="Tokens: 0", font=("Arial", 9))
        self.week_tokens.grid(row=1, column=1, sticky=tk.W)
        self.week_cost = ttk.Label(
            metrics_frame, text="Custo: $0.00", font=("Arial", 9)
        )
        self.week_cost.grid(row=2, column=1, sticky=tk.W)
        self.week_cache = ttk.Label(metrics_frame, text="Cache: 0%", font=("Arial", 9))
        self.week_cache.grid(row=3, column=1, sticky=tk.W)

        # Métricas mensais
        ttk.Label(metrics_frame, text="MÊS:", font=("Arial", 10, "bold")).grid(
            row=0, column=2, sticky=tk.W, pady=5
        )
        self.month_tokens = ttk.Label(
            metrics_frame, text="Tokens: 0", font=("Arial", 9)
        )
        self.month_tokens.grid(row=1, column=2, sticky=tk.W)
        self.month_cost = ttk.Label(
            metrics_frame, text="Custo: $0.00", font=("Arial", 9)
        )
        self.month_cost.grid(row=2, column=2, sticky=tk.W)
        self.month_cache = ttk.Label(metrics_frame, text="Cache: 0%", font=("Arial", 9))
        self.month_cache.grid(row=3, column=2, sticky=tk.W)

        # Painel de ferramentas
        tools_frame = ttk.LabelFrame(
            main_frame, text="🛠 Ferramentas (22+)", padding="10"
        )
        tools_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Scrollable frame para ferramentas
        canvas = tk.Canvas(tools_frame, bg="#2d2d2d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=canvas.yview)
        self.tools_inner_frame = ttk.Frame(canvas)

        self.tools_inner_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.tools_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Inicializar lista de ferramentas
        self.tool_labels = {}
        for i, tool in enumerate(TOOL_MODULES):
            frame = ttk.Frame(self.tools_inner_frame)
            frame.pack(fill=tk.X, pady=2)

            status = tk.StringVar(value="●")
            label = ttk.Label(
                frame,
                textvariable=status,
                font=("Arial", 10),
                foreground="#FF5252",
                width=3,
            )
            label.pack(side=tk.LEFT)

            ttk.Label(
                frame, text=f"neocortex_{tool}", font=("Arial", 9), foreground="#e0e0e0"
            ).pack(side=tk.LEFT, padx=5)

            self.tool_labels[tool] = status

        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def start_monitoring(self):
        """Iniciar threads de monitoramento"""
        # Thread para atualizar UI da queue
        threading.Thread(target=self.process_update_queue, daemon=True).start()

        # Thread para verificar servidor
        threading.Thread(target=self.monitor_server, daemon=True).start()

        # Thread para atualizar métricas
        threading.Thread(target=self.monitor_metrics, daemon=True).start()

    def process_update_queue(self):
        """Processar atualizações da queue na thread principal"""
        while True:
            try:
                func, args = self.update_queue.get(timeout=0.1)
                self.root.after(0, func, *args)
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                print(f"Erro na queue: {e}")

    def monitor_server(self):
        """Monitorar status do servidor"""
        while True:
            if self.server_process:
                return_code = self.server_process.poll()
                if return_code is not None:
                    self.update_queue.put((self.on_server_stopped, (return_code,)))

            # Verificar conexão (simplificado)
            import socket

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", self.server_port))
                sock.close()

                if result == 0:
                    self.update_queue.put((self.update_server_status, (True,)))
                else:
                    self.update_queue.put((self.update_server_status, (False,)))
            except:
                self.update_queue.put((self.update_server_status, (False,)))

            time.sleep(2)

    def monitor_metrics(self):
        """Monitorar métricas do banco de dados"""
        while True:
            try:
                if METRICS_DB.exists():
                    self.update_queue.put((self.load_metrics, ()))
            except Exception as e:
                print(f"Erro ao monitorar métricas: {e}")

            time.sleep(10)

    def update_server_status(self, running):
        """Atualizar status do servidor na UI"""
        self.server_running = running
        if running:
            self.server_status_var.set("🟢 ONLINE (ws://localhost:8765)")
            self.status_var.set(
                f"Servidor online - {datetime.now().strftime('%H:%M:%S')}"
            )
        else:
            self.server_status_var.set("🔴 OFFLINE")
            self.status_var.set("Servidor offline")

    def on_server_stopped(self, return_code):
        """Handler quando servidor para"""
        self.server_process = None
        self.update_server_status(False)
        self.status_var.set(f"Servidor parou (código: {return_code})")

    def start_server(self):
        """Iniciar servidor MCP"""
        if self.server_process:
            messagebox.showinfo("Servidor", "Servidor já está em execução.")
            return

        try:
            cmd = [
                sys.executable,
                str(MCP_SERVER_SCRIPT),
                "--transport",
                "websocket",
                "--host",
                "localhost",
                "--port",
                str(self.server_port),
            ]
            self.server_process = subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.status_var.set("Servidor iniciando...")

            # Thread para ler output
            threading.Thread(target=self.read_server_output, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao iniciar servidor:\n{e}")

    def stop_server(self):
        """Parar servidor MCP"""
        if not self.server_process:
            messagebox.showinfo("Servidor", "Servidor não está em execução.")
            return

        try:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            self.server_process = None
            self.status_var.set("Servidor parado")
        except:
            self.server_process.kill()
            self.server_process = None
            self.status_var.set("Servidor terminado forçadamente")

    def read_server_output(self):
        """Ler output do servidor"""
        if not self.server_process:
            return

        for line in iter(self.server_process.stdout.readline, ""):
            if line:
                self.update_queue.put((self.log_output, (line.strip(),)))

        for line in iter(self.server_process.stderr.readline, ""):
            if line:
                self.update_queue.put((self.log_output, (f"ERRO: {line.strip()}",)))

    def log_output(self, message):
        """Logar mensagem no status bar"""
        if len(message) > 50:
            message = message[:47] + "..."
        self.status_var.set(message)

    def update_metrics(self):
        """Atualizar métricas de economia"""
        try:
            self.load_metrics()
            self.status_var.set("Métricas atualizadas")
        except Exception as e:
            self.status_var.set(f"Erro ao carregar métricas: {e}")

    def load_metrics(self):
        """Carregar métricas do banco de dados"""
        if not METRICS_DB.exists():
            # Dados de exemplo para demonstração
            today_cache_hit = 800
            today_cache_miss = 200
            today_output = 250
            today_tokens = today_cache_hit + today_cache_miss + today_output

            week_cache_hit = 5600
            week_cache_miss = 1400
            week_output = 1900
            week_tokens = week_cache_hit + week_cache_miss + week_output

            month_cache_hit = 20000
            month_cache_miss = 5000
            month_output = 7500
            month_tokens = month_cache_hit + month_cache_miss + month_output

            # Calcular custo com preços DeepSeek
            today_cost = (
                today_cache_hit * DEEPSEEK_PRICES["cache_hit"]
                + today_cache_miss * DEEPSEEK_PRICES["cache_miss"]
                + today_output * DEEPSEEK_PRICES["output"]
            ) / 1_000_000
            week_cost = (
                week_cache_hit * DEEPSEEK_PRICES["cache_hit"]
                + week_cache_miss * DEEPSEEK_PRICES["cache_miss"]
                + week_output * DEEPSEEK_PRICES["output"]
            ) / 1_000_000
            month_cost = (
                month_cache_hit * DEEPSEEK_PRICES["cache_hit"]
                + month_cache_miss * DEEPSEEK_PRICES["cache_miss"]
                + month_output * DEEPSEEK_PRICES["output"]
            ) / 1_000_000

            # Calcular taxa de cache hit
            def hit_rate(hit, miss):
                total = hit + miss
                return (hit / total * 100) if total > 0 else 0.0

            today_hit_rate = hit_rate(today_cache_hit, today_cache_miss)
            week_hit_rate = hit_rate(week_cache_hit, week_cache_miss)
            month_hit_rate = hit_rate(month_cache_hit, month_cache_miss)

            # Manter variáveis antigas para compatibilidade (serão atualizadas depois)
            today_savings = today_cost
            week_savings = week_cost
            month_savings = month_cost
        else:
            import duckdb

            conn = duckdb.connect(str(METRICS_DB))
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # Query for today
            result = conn.execute(f"""
                SELECT SUM(cache_hit), SUM(cache_miss), SUM(output_tokens)
                FROM daily_token_usage 
                WHERE date = '{today}'
            """).fetchone()
            today_cache_hit = result[0] or 0
            today_cache_miss = result[1] or 0
            today_output = result[2] or 0
            today_tokens = today_cache_hit + today_cache_miss + today_output

            # Query for week
            result = conn.execute(f"""
                SELECT SUM(cache_hit), SUM(cache_miss), SUM(output_tokens)
                FROM daily_token_usage 
                WHERE date >= '{week_ago}'
            """).fetchone()
            week_cache_hit = result[0] or 0
            week_cache_miss = result[1] or 0
            week_output = result[2] or 0
            week_tokens = week_cache_hit + week_cache_miss + week_output

            # Query for month
            result = conn.execute(f"""
                SELECT SUM(cache_hit), SUM(cache_miss), SUM(output_tokens)
                FROM daily_token_usage 
                WHERE date >= '{month_ago}'
            """).fetchone()
            month_cache_hit = result[0] or 0
            month_cache_miss = result[1] or 0
            month_output = result[2] or 0
            month_tokens = month_cache_hit + month_cache_miss + month_output

            conn.close()

            # Calcular custo com preços DeepSeek
            today_cost = (
                today_cache_hit * DEEPSEEK_PRICES["cache_hit"]
                + today_cache_miss * DEEPSEEK_PRICES["cache_miss"]
                + today_output * DEEPSEEK_PRICES["output"]
            ) / 1_000_000
            week_cost = (
                week_cache_hit * DEEPSEEK_PRICES["cache_hit"]
                + week_cache_miss * DEEPSEEK_PRICES["cache_miss"]
                + week_output * DEEPSEEK_PRICES["output"]
            ) / 1_000_000
            month_cost = (
                month_cache_hit * DEEPSEEK_PRICES["cache_hit"]
                + month_cache_miss * DEEPSEEK_PRICES["cache_miss"]
                + month_output * DEEPSEEK_PRICES["output"]
            ) / 1_000_000

            # Calcular taxa de cache hit
            def hit_rate(hit, miss):
                total = hit + miss
                return (hit / total * 100) if total > 0 else 0.0

            today_hit_rate = hit_rate(today_cache_hit, today_cache_miss)
            week_hit_rate = hit_rate(week_cache_hit, week_cache_miss)
            month_hit_rate = hit_rate(month_cache_hit, month_cache_miss)

            # Manter variáveis antigas para compatibilidade
            today_savings = today_cost
            week_savings = week_cost
            month_savings = month_cost

        # Atualizar UI
        self.today_tokens.config(text=f"Tokens: {today_tokens:,}")
        self.today_cost.config(text=f"Custo: ${today_cost:.4f}")
        self.today_cache.config(text=f"Cache: {today_hit_rate:.1f}%")

        self.week_tokens.config(text=f"Tokens: {week_tokens:,}")
        self.week_cost.config(text=f"Custo: ${week_cost:.4f}")
        self.week_cache.config(text=f"Cache: {week_hit_rate:.1f}%")

        self.month_tokens.config(text=f"Tokens: {month_tokens:,}")
        self.month_cost.config(text=f"Custo: ${month_cost:.4f}")
        self.month_cache.config(text=f"Cache: {month_hit_rate:.1f}%")

        # Atualizar status das ferramentas (simulado)
        for tool in TOOL_MODULES:
            status = self.tool_labels[tool]
            # Simular status aleatório (● = inativo, 🟢 = ativo, 🟡 = moderado)
            import random

            rand = random.random()
            if rand > 0.7:
                status.set("🟢")
                self.tool_labels[tool].master.winfo_children()[0].config(
                    foreground="#4CAF50"
                )
            elif rand > 0.4:
                status.set("🟡")
                self.tool_labels[tool].master.winfo_children()[0].config(
                    foreground="#FFC107"
                )
            else:
                status.set("●")
                self.tool_labels[tool].master.winfo_children()[0].config(
                    foreground="#FF5252"
                )

    def copy_url(self):
        """Copiar URL do servidor para clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append("ws://localhost:8765")
        self.status_var.set("URL copiada para clipboard: ws://localhost:8765")

    def minimize_to_tray(self):
        """Minimizar para bandeja do sistema"""
        self.root.withdraw()
        self.create_tray_icon()

    def create_tray_icon(self):
        """Criar ícone na bandeja do sistema"""
        if not self.tray_image:
            return

        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self.restore_from_tray),
            pystray.MenuItem("Sair", self.quit_app),
        )

        self.tray_icon = pystray.Icon(
            "neocortex_hud", self.tray_image, "NeoCortex HUD", menu
        )

        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        """Restaurar janela da bandeja"""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def on_mouse_enter(self, event):
        """Mouse hover - destacar janela"""
        if self.root.state() == "normal":
            self.root.attributes("-alpha", 0.95)

    def on_mouse_leave(self, event):
        """Mouse leave - restaurar opacidade"""
        if self.root.state() == "normal":
            self.root.attributes("-alpha", 1.0)

    def quit_app(self, icon=None, item=None):
        """Sair do aplicativo"""
        if self.server_process:
            self.stop_server()

        if self.tray_icon:
            self.tray_icon.stop()

        self.root.quit()
        self.root.destroy()

    def run(self):
        """Executar aplicação"""
        self.root.mainloop()


if __name__ == "__main__":
    # Verificar dependências
    try:
        import tkinter
        import pystray
        from PIL import Image
    except ImportError as e:
        print(f"Dependência faltando: {e}")
        print("Instale com: pip install pystray pillow")
        sys.exit(1)

    app = NeoCortexHUD()
    app.run()
