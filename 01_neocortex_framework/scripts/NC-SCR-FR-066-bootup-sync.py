#!/usr/bin/env python3
import re
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation', 'bootup', 'sync']
hash: "auto-generated"
---"""

"""
NC-SCR-FR-066-bootup-sync.py
Sincronizao automtica do Boot Manifest (NC-BOOT-FR-001-system-manifest.md) com o estado real do sistema.

Atualiza:
  - Seo 6: FRENTES OPERACIONAIS ATIVAS (com base em tickets YAML com handoff APPROVED)
  - Seo 9: TICKETS CRTICOS (pr-MCP) (SAVE-005, ORCH-301, ORCH-302, etc.)
  - Data no cabealho das sees

Uso:
    cd 01_neocortex_framework
    python scripts/NC-SCR-FR-066-bootup-sync.py [--dry-run]

Dependncias:
    - DIR-DS-001-tickets/ (tickets YAML)
    - DIR-DS-002-audit-logs/ (handoffs YAML)
    - DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md
"""

import argparse
import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

#  Setup do PATH
SCRIPT_DIR = Path(__file__).parent.resolve()
FRAMEWORK_ROOT = SCRIPT_DIR.parent  # 01_neocortex_framework/
PROJECT_ROOT = FRAMEWORK_ROOT.parent  # TURBOQUANT_V42/
sys.path.insert(0, str(FRAMEWORK_ROOT))

# Import WALService
_wal_path = FRAMEWORK_ROOT / "neocortex/core/services/NC-SVC-FR-016-wal-service.py"
_spec = importlib.util.spec_from_file_location("wal_service", _wal_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WALService = _mod.WALService

#  Paths crticos
TICKETS_DIR = PROJECT_ROOT / "DIR-DS-001-tickets"
HANDOFFS_DIR = PROJECT_ROOT / "DIR-DS-002-audit-logs"
BOOTUP_FILE = (
    PROJECT_ROOT / "DIR-BOOT-FR-001-bootup-main" / "NC-BOOT-FR-001-system-manifest.md"
)

#  Configurao
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_FULL = datetime.now().strftime("%Y-%m-%d %H:%M")


class BootupSync:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.tickets: Dict[str, Dict] = {}
        self.handoffs: Dict[str, Dict] = {}
        self.approved_tickets: List[str] = []

    def load_tickets(self) -> None:
        """Carrega todos os tickets YAML do DIR-DS-001-tickets/."""
        for yaml_file in TICKETS_DIR.glob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if not data:
                    continue
                ticket_id = data.get("id")
                # Fallback: usar nome do arquivo sem extenso como ticket_id
                if not ticket_id:
                    # Tentar extrair NC-DS-XXX do nome do arquivo
                    import re

                    match = re.search(r"(NC-DS-\d+)", yaml_file.stem)
                    if match:
                        ticket_id = match.group(1)
                    else:
                        ticket_id = yaml_file.stem
                if ticket_id:
                    self.tickets[ticket_id] = {
                        "id": ticket_id,
                        "code": data.get("code", ""),
                        "title": data.get("title", ""),
                        "assignee": data.get("assignee", ""),
                        "context": data.get("context", []),
                        "task": data.get("task", ""),
                        "file": yaml_file.name,
                    }
            except Exception as e:
                print(f"    Erro ao ler ticket {yaml_file.name}: {e}")

    def load_handoffs(self) -> None:
        """Carrega todos os handoffs YAML do DIR-DS-002-audit-logs/."""
        for yaml_file in HANDOFFS_DIR.glob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    # Usar safe_load_all para lidar com mltiplos documentos YAML
                    documents = list(yaml.safe_load_all(f))
                    if not documents:
                        continue
                    # Usar o primeiro documento (geralmente  o handoff principal)
                    data = documents[0]
                if not data:
                    continue
                ticket_id = data.get("ticket_id")
                status = data.get("status")
                if ticket_id and status == "APPROVED":
                    self.handoffs[ticket_id] = data
                    self.approved_tickets.append(ticket_id)
            except Exception as e:
                print(f"    Erro ao ler handoff {yaml_file.name}: {e}")

    def categorize_tickets(self) -> Dict[str, List[Dict]]:
        """Categoriza tickets por assignee (Courier, Engineer, Tester, etc.)."""
        categories: Dict[str, List[Dict]] = {}

        for ticket_id in self.approved_tickets:
            if ticket_id not in self.tickets:
                continue
            ticket = self.tickets[ticket_id]
            assignee = ticket.get("assignee", "")

            # Determinar categoria baseada no assignee
            category = "Outros"
            if "courier" in assignee.lower():
                category = "Courier"
            elif "engineer" in assignee.lower():
                category = "Engineer"
            elif "tester" in assignee.lower():
                category = "Tester"
            elif "guardian" in assignee.lower():
                category = "Guardian"
            elif "opencode" in assignee.lower():
                # Tentar inferir pela descrio
                if any(
                    x in ticket.get("title", "").lower()
                    for x in ["courier", "discrepancy", "renaming"]
                ):
                    category = "Courier"
                elif any(
                    x in ticket.get("title", "").lower()
                    for x in ["engineer", "encoding", "utf"]
                ):
                    category = "Engineer"
                elif any(
                    x in ticket.get("title", "").lower()
                    for x in ["tester", "test", "vector"]
                ):
                    category = "Tester"
                else:
                    category = "Outros"

            if category not in categories:
                categories[category] = []
            categories[category].append(ticket)

        return categories

    def extract_critical_tickets(self) -> List[Dict]:
        """Extrai tickets crticos pr-MCP (SAVE-005, ORCH-301, ORCH-302, etc.)."""
        critical = []
        critical_codes = ["SAVE-005", "ORCH-301", "ORCH-302", "INT-001", "INT-002"]

        for ticket_id, ticket in self.tickets.items():
            code = ticket.get("code", "")
            if code in critical_codes:
                # Verificar se j foi aprovado
                status = (
                    " Entregue" if ticket_id in self.approved_tickets else " PRXIMO"
                )
                critical.append(
                    {
                        "code": code,
                        "title": ticket.get("title", ""),
                        "status": status,
                        "ticket_id": ticket_id,
                    }
                )

        # Ordenar pela ordem desejada
        order = {code: i for i, code in enumerate(critical_codes)}
        critical.sort(key=lambda x: order.get(x["code"], 999))

        return critical

    def generate_section6(self, categories: Dict[str, List[Dict]]) -> str:
        """Gera o contedo da seo 6 (FRENTES OPERACIONAIS ATIVAS)."""
        lines = []
        lines.append(f"## 6. FRENTES OPERACIONAIS ATIVAS ({TODAY})")
        lines.append("")

        # Determinar se h frentes ativas
        active_categories = [cat for cat in categories if categories[cat]]

        if not active_categories:
            lines.append("** NENHUMA FRENTE ATIVA NO MOMENTO**")
            lines.append("")
            lines.append(
                "**MCP-WQUEUE:** Tickets YAML em `DIR-DS-001-tickets/`. Agentes OpenCode executam e geram handoffs em `DIR-DS-002-audit-logs/`. T0 (Antigravity) valida e aprova."
            )
            return "\n".join(lines)

        lines.append("** FRENTE ATIVA:** Correes Crticas NeoCortex (Orquestrao T0)")
        lines.append("")

        # Mapeamento categoria  descrio
        cat_descriptions = {
            "Courier": "Courier  Discrepncia de escopo renaming plan",
            "Engineer": "Engineer  Preparao ambiente UTF-8 Windows",
            "Tester": "Tester  Correo testes VectorEngine (async/API)",
            "Guardian": "Guardian  Auditoria de segurana e locks",
            "Outros": "Outros  Tarefas diversas",
        }

        for category in ["Courier", "Engineer", "Tester", "Guardian", "Outros"]:
            if category not in categories or not categories[category]:
                continue

            tickets = categories[category]
            # Pegar o ticket mais recente (assumindo que o ltimo na lista  o mais recente)
            ticket = tickets[-1]
            ticket_id = ticket["id"]

            # Extrair script relacionado do contexto
            script_name = ""
            for ctx in ticket.get("context", []):
                if "NC-SCR-FR-" in ctx:
                    parts = ctx.split("/")
                    for part in parts:
                        if "NC-SCR-FR-" in part:
                            script_name = part
                            break
                    if script_name:
                        break

            # Verificar se tem handoff
            handoff_status = (
                " COMPLETED" if ticket_id in self.approved_tickets else " EM ANDAMENTO"
            )

            desc = cat_descriptions.get(category, category)
            lines.append(f"1. **{desc}**")
            if script_name:
                lines.append(f"   - Ticket: {script_name}")
            lines.append(f"   - Handoff: {ticket_id} {handoff_status}")

            # Adicionar resultado se completado
            if ticket_id in self.approved_tickets and ticket_id in self.handoffs:
                handoff = self.handoffs[ticket_id]
                summary = handoff.get("summary", "")
                if summary:
                    # Extrair primeira linha do summary (pode ser string ou dict)
                    if isinstance(summary, dict):
                        # Se summary for dict, usar campo 'overall' se existir, senão converter para string
                        overall = summary.get("overall", "")
                        if overall:
                            first_line = str(overall)
                        else:
                            # Tentar notes se existir
                            notes = handoff.get("notes", "")
                            if notes:
                                first_line = notes.split("\n")[0].strip()
                            else:
                                first_line = str(summary)[:100]
                    else:
                        # summary é string
                        first_line = summary.split("\n")[0].strip()
                    lines.append(f"   - Resultado: {first_line}")

            lines.append("")

        lines.append(
            "**Prximo passo:** Executar testes corrigidos (`pytest tests/test_vector_engine.py -v --asyncio-mode=auto`)"
        )
        lines.append("")
        lines.append(
            "**MCP-WQUEUE:** Tickets YAML em `DIR-DS-001-tickets/`. Agentes OpenCode executam e geram handoffs em `DIR-DS-002-audit-logs/`. T0 (Antigravity) valida e aprova."
        )

        return "\n".join(lines)

    def generate_section9(self, critical_tickets: List[Dict]) -> str:
        """Gera o contedo da seo 9 (TICKETS CRTICOS)."""
        lines = []
        lines.append("## 9. TICKETS CRTICOS (PR-MCP)")
        lines.append("")
        lines.append("| Ticket | Status | Prxima ao |")
        lines.append("|---|---|---|")

        # Mapeamento cdigo  prxima ao
        next_actions = {
            "SAVE-005": "Dry-Run Preview middleware",
            "ORCH-301": "`send_task()` HTTP real",
            "ORCH-302": "`neocortex_task` tool via HTTP/SSE",
            "INT-001": "Mission Control integration",
            "INT-002": "Pixel Agents + bridge",
            "hooks/__init__.py": "Script visual-server criado",
        }

        for ticket in critical_tickets:
            code = ticket["code"]
            status = ticket["status"]
            next_action = next_actions.get(code, "")

            # Se for INT-001 ou INT-002 e status " Entregue", manter prxima ao vazia
            if code in ["INT-001", "INT-002"] and status == " Entregue":
                next_action = ""

            lines.append(f"| **{code}** | {status} | {next_action} |")

        return "\n".join(lines)

    def update_bootup(self, section6: str, section9: str) -> Optional[str]:
        """Atualiza o arquivo bootup com as novas sees."""
        try:
            with open(BOOTUP_FILE, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"   Arquivo bootup no encontrado: {BOOTUP_FILE}")
            return None

        # Atualizar seo 6
        section6_pattern = r"(## 6\. FRENTES OPERACIONAIS ATIVAS \(.*?\)).*?(?=## 7\. ESTADO ACUMULADO  O QUE FOI CONSTRUDO)"
        new_section6 = f"{section6}\n\n---\n"
        updated_content = re.sub(
            section6_pattern, new_section6, content, flags=re.DOTALL
        )

        # Atualizar seo 9
        section9_pattern = r"(## 9\. TICKETS CRTICOS \(PR-MCP\)).*?(?=(?:---\n)+\n## 10\. REGRAS OBRIGATRIAS)"
        new_section9 = f"{section9}\n\n---\n---\n"
        updated_content = re.sub(
            section9_pattern, new_section9, updated_content, flags=re.DOTALL
        )

        # Atualizar data no cabealho principal
        date_pattern = r"ltima atualizao: \d{4}-\d{2}-\d{2}"
        updated_content = re.sub(
            date_pattern, f"ltima atualizao: {TODAY}", updated_content
        )

        return updated_content

    def run(self) -> None:
        """Executa a sincronizao completa."""
        print("" * 60)
        print("  NeoCortex  Sincronizao Boot Manifest")
        print("" * 60)
        print(f"  Data: {TODAY_FULL}")
        print(
            f"  Dry-run: {'SIM (nada ser gravado)' if self.dry_run else 'NO (gravando)'}"
        )
        print("" * 60)

        # 1. Carregar dados
        print("   Carregando tickets YAML...")
        self.load_tickets()
        print(f"      {len(self.tickets)} tickets encontrados")

        print("   Carregando handoffs YAML...")
        self.load_handoffs()
        print(f"      {len(self.handoffs)} handoffs APPROVED")
        print(f"      {len(self.approved_tickets)} tickets com handoff aprovado")

        # 2. Categorizar tickets
        print("    Categorizando tickets...")
        categories = self.categorize_tickets()
        for cat, tickets in categories.items():
            print(f"      {cat}: {len(tickets)} tickets")

        # 3. Extrair tickets crticos
        print("    Extraindo tickets crticos...")
        critical_tickets = self.extract_critical_tickets()
        print(f"      {len(critical_tickets)} tickets crticos identificados")

        # 4. Gerar novas sees
        print("   Gerando seo 6 (FRENTES ATIVAS)...")
        section6 = self.generate_section6(categories)

        print("   Gerando seo 9 (TICKETS CRTICOS)...")
        section9 = self.generate_section9(critical_tickets)

        # 5. Atualizar arquivo
        print("   Atualizando boot manifest...")
        updated_content = self.update_bootup(section6, section9)

        if not updated_content:
            print("   Falha ao atualizar contedo.")
            return

        # NC-DS-092: validate_lobe do boot manifest antes de gravar (warning, não bloqueia)
        _norm_path = FRAMEWORK_ROOT / "neocortex/core/services/NC-SVC-FR-018-tag-normalizer.py"
        try:
            import importlib.util as _ilu_norm
            _norm_spec = _ilu_norm.spec_from_file_location("tag_normalizer", _norm_path)
            _norm_mod = _ilu_norm.module_from_spec(_norm_spec)  # type: ignore[arg-type]
            _norm_spec.loader.exec_module(_norm_mod)  # type: ignore[union-attr]
            _vr = _norm_mod.TagNormalizerService().validate_lobe(BOOTUP_FILE)
            if not _vr.valid:
                print(f"   [TAG-NORMALIZER] {len(_vr.violations)} violação(ões) no boot manifest (não bloqueia):")
                for v in _vr.violations[:3]:
                    print(f"      {v}")
        except Exception as _e_n:
            print(f"   [TAG-NORMALIZER] aviso: {_e_n}")

        if self.dry_run:
            print("   [DRY-RUN] Boot manifest seria atualizado.")
            print("   Visualizao das mudanas:")
            print("  " + "-" * 56)
            # Mostrar diferenas? Por simplicidade, apenas confirmar
            print("  Seo 6 atualizada com frentes ativas.")
            print("  Seo 9 atualizada com tickets crticos.")
            print("  Data de atualizao ajustada.")
        else:
            try:
                # Inicializar WAL
                wal = WALService()
                session_id = (
                    f"ciclo3-bootup-sync-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
                )
                with wal.transaction(
                    session_id, "NC-SCR-FR-066", ticket_id="NC-DS-089"
                ) as txn:
                    # Backup do arquivo original (CREATE)
                    backup_file = BOOTUP_FILE.with_suffix(".md.backup")
                    before_backup = txn.before_write(backup_file)  # None
                    with open(BOOTUP_FILE, "r", encoding="utf-8") as f:
                        original_content = f.read()
                    with open(backup_file, "w", encoding="utf-8") as f:
                        f.write(original_content)
                    txn.after_write(backup_file, before_backup)

                    # Escrever novo contedo no arquivo principal (MODIFY)
                    before_main = txn.before_write(BOOTUP_FILE)
                    with open(BOOTUP_FILE, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    txn.after_write(BOOTUP_FILE, before_main)

                print("   Boot manifest atualizado com sucesso!")
                print(f"   Backup salvo em: {backup_file.name}")
            except Exception as e:
                print(f"   Erro ao gravar arquivo: {e}")
                return

        print("" * 60)
        print("   Sincronizao concluda.")


def main():
    parser = argparse.ArgumentParser(
        description="Sincroniza Boot Manifest com estado real do sistema"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Apenas simula as alteraes"
    )
    args = parser.parse_args()

    sync = BootupSync(dry_run=args.dry_run)
    sync.run()


if __name__ == "__main__":
    main()
