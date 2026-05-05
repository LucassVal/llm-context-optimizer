#!/usr/bin/env python3
"""
Ferramenta de sincronização de tickets NC-DS-* com roadmap v69
Mapeia tickets atuais para fases e tickets do roadmap v69
"""

import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class TicketSyncTool:
    """Ferramenta de sincronização de tickets"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.results = {
            "sync_date": datetime.now().isoformat() + "Z",
            "tickets_analyzed": 0,
            "tickets_mapped": 0,
            "mapping_details": [],
            "recommendations": []
        }
    
    def analyze_tickets(self):
        """Analisa tickets NC-DS-* e mapeia para roadmap v69"""
        print("1. Analisando tickets NC-DS-*...")
        
        # Carregar roadmap consolidado
        roadmap_file = self.base_dir / "NC-TODO-FR-001-roadmap.yaml"
        if not roadmap_file.exists():
            print("  [ERROR] Roadmap não encontrado")
            return
        
        with open(roadmap_file, 'r', encoding='utf-8') as f:
            roadmap = yaml.safe_load(f)
        
        # Encontrar todos os tickets NC-DS-*
        ticket_files = list(self.base_dir.glob("NC-DS-*.yaml"))
        self.results["tickets_analyzed"] = len(ticket_files)
        
        print(f"  [INFO] {len(ticket_files)} tickets encontrados")
        
        # Analisar cada ticket
        for ticket_file in ticket_files:
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket_data = yaml.safe_load(f)
                
                if not ticket_data or not isinstance(ticket_data, dict):
                    continue
                
                ticket_id = ticket_data.get("ticket_id", "")
                ticket_title = ticket_data.get("title", "")
                ticket_desc = ticket_data.get("description", "")
                
                # Tentar mapear para fases v69
                mapping = self._map_to_v69_phases(ticket_title, ticket_desc, roadmap)
                
                # Tentar mapear para tickets v69 específicos
                v69_mapping = self._map_to_v69_tickets(ticket_title, ticket_desc)
                
                mapping_result = {
                    "ticket_id": ticket_id,
                    "ticket_title": ticket_title,
                    "file": ticket_file.name,
                    "v69_phase_mapping": mapping,
                    "v69_ticket_mapping": v69_mapping,
                    "recommended_phase": self._recommend_phase(ticket_title, ticket_desc),
                    "sync_actions": []
                }
                
                # Gerar ações de sincronização
                if mapping or v69_mapping:
                    mapping_result["sync_actions"] = self._generate_sync_actions(
                        ticket_id, mapping, v69_mapping, roadmap
                    )
                    self.results["tickets_mapped"] += 1
                
                self.results["mapping_details"].append(mapping_result)
                
            except Exception as e:
                print(f"  [ERROR] Erro ao processar {ticket_file.name}: {e}")
    
    def _map_to_v69_phases(self, title: str, description: str, roadmap: Dict) -> List[str]:
        """Mapeia ticket para fases do roadmap v69"""
        phases_found = []
        
        # Palavras-chave para cada fase
        phase_keywords = {
            "FASE_1": ["core", "hook", "compaction", "permission", "sandbox", "session", "feature flag"],
            "FASE_2": ["swarm", "agent", "persona", "picoclaw", "micro-executor", "kairos"],
            "FASE_3": ["mcp", "tool", "analysis", "code analysis", "file ops", "data suite"],
            "FASE_4": ["cache", "optimization", "telemetry", "cost", "failover", "deploy"]
        }
        
        text_to_search = f"{title} {description}".lower()
        
        for phase_id, keywords in phase_keywords.items():
            for keyword in keywords:
                if keyword in text_to_search:
                    phases_found.append(phase_id)
                    break
        
        return list(set(phases_found))  # Remover duplicatas
    
    def _map_to_v69_tickets(self, title: str, description: str) -> List[str]:
        """Mapeia ticket para tickets específicos do v69"""
        tickets_found = []
        
        # Padrões de tickets v69
        v69_patterns = [
            (r"picoclaw", ["TKT-203"]),
            (r"integration.*test", ["TKT-203"]),
            (r"hook", ["TKT-102", "TKT-105"]),
            (r"permission", ["TKT-104"]),
            (r"cache", ["TKT-401"]),
            (r"telemetry", ["TKT-402"]),
            (r"failover", ["TKT-403"]),
            (r"swarm", ["TKT-201"]),
            (r"persona", ["TKT-202"]),
            (r"mcp", ["TKT-301"]),
            (r"analysis", ["TKT-302"]),
            (r"file.*data", ["TKT-303"])
        ]
        
        text_to_search = f"{title} {description}".lower()
        
        for pattern, tickets in v69_patterns:
            if re.search(pattern, text_to_search):
                tickets_found.extend(tickets)
        
        return list(set(tickets_found))
    
    def _recommend_phase(self, title: str, description: str) -> Optional[str]:
        """Recomenda fase baseada no conteúdo do ticket"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["audit", "governance", "compliance", "yaml", "json"]):
            return "GOVERNANCE"  # Fase especial de governança
        
        elif any(word in text for word in ["picoclaw", "integration", "test"]):
            return "FASE_2"
        
        elif any(word in text for word in ["hook", "lexico"]):
            return "FASE_1"
        
        elif any(word in text for word in ["metric", "store", "f841"]):
            return "FASE_4"  # Otimização
        
        return None
    
    def _generate_sync_actions(self, ticket_id: str, phases: List[str], v69_tickets: List[str], roadmap: Dict) -> List[Dict]:
        """Gera ações para sincronizar ticket com roadmap"""
        actions = []
        
        # 1. Atualizar ticket YAML com mapeamento
        if phases or v69_tickets:
            actions.append({
                "type": "UPDATE_TICKET_YAML",
                "ticket_id": ticket_id,
                "fields_to_add": {
                    "roadmap_phase": phases[0] if phases else None,
                    "v69_mapping": v69_tickets[0] if v69_tickets else None,
                    "sync_date": datetime.now().isoformat() + "Z"
                }
            })
        
        # 2. Atualizar roadmap com mapeamento
        if v69_tickets:
            for v69_ticket in v69_tickets:
                actions.append({
                    "type": "UPDATE_ROADMAP_MAPPING",
                    "v69_ticket": v69_ticket,
                    "nc_ds_ticket": ticket_id,
                    "action": "add_mapping"
                })
        
        return actions
    
    def execute_sync_actions(self):
        """Executa ações de sincronização identificadas"""
        print("\n2. Executando ações de sincronização...")
        
        actions_executed = 0
        
        for mapping in self.results["mapping_details"]:
            ticket_id = mapping["ticket_id"]
            actions = mapping.get("sync_actions", [])
            
            for action in actions:
                try:
                    if action["type"] == "UPDATE_TICKET_YAML":
                        self._update_ticket_yaml(ticket_id, action["fields_to_add"])
                        actions_executed += 1
                        print(f"  [SYNC] Atualizado ticket {ticket_id}")
                    
                    elif action["type"] == "UPDATE_ROADMAP_MAPPING":
                        # Esta ação seria implementada para atualizar o roadmap
                        # Por enquanto apenas registramos
                        print(f"  [INFO] Mapeamento identificado: {action['v69_ticket']} -> {action['nc_ds_ticket']}")
                        
                except Exception as e:
                    print(f"  [ERROR] Falha na ação: {e}")
        
        print(f"  [INFO] {actions_executed} ações executadas")
    
    def _update_ticket_yaml(self, ticket_id: str, fields: Dict):
        """Atualiza ticket YAML com campos de sincronização"""
        ticket_file = self.base_dir / f"{ticket_id}.yaml"
        
        if not ticket_file.exists():
            # Tentar encontrar por padrão
            ticket_files = list(self.base_dir.glob(f"*{ticket_id}*.yaml"))
            if not ticket_files:
                raise FileNotFoundError(f"Ticket não encontrado: {ticket_id}")
            ticket_file = ticket_files[0]
        
        with open(ticket_file, 'r', encoding='utf-8') as f:
            ticket_data = yaml.safe_load(f)
        
        # Adicionar campos de sincronização
        if "metadata" not in ticket_data:
            ticket_data["metadata"] = {}
        
        ticket_data["metadata"]["roadmap_sync"] = {
            "synced_at": datetime.now().isoformat() + "Z",
            "phases": fields.get("roadmap_phase"),
            "v69_mapping": fields.get("v69_mapping")
        }
        
        # Salvar
        with open(ticket_file, 'w', encoding='utf-8') as f:
            yaml.dump(ticket_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def generate_report(self):
        """Gera relatório de sincronização"""
        print("\n3. Gerando relatório de sincronização...")
        
        # Estatísticas
        total_tickets = self.results["tickets_analyzed"]
        mapped_tickets = self.results["tickets_mapped"]
        mapping_rate = (mapped_tickets / total_tickets * 100) if total_tickets > 0 else 0
        
        # Recomendações
        if mapping_rate < 50:
            self.results["recommendations"].append(
                "Baixa taxa de mapeamento. Considerar revisão dos títulos/descrições dos tickets."
            )
        
        if total_tickets - mapped_tickets > 0:
            self.results["recommendations"].append(
                f"{total_tickets - mapped_tickets} tickets não mapeados. Revisar manualmente."
            )
        
        # Salvar relatório
        report_file = self.base_dir / "ticket_sync_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def print_summary(self):
        """Imprime resumo da sincronização"""
        print("\n" + "=" * 60)
        print("RESUMO DA SINCRONIZAÇÃO DE TICKETS")
        print("=" * 60)
        
        total = self.results["tickets_analyzed"]
        mapped = self.results["tickets_mapped"]
        rate = (mapped / total * 100) if total > 0 else 0
        
        print(f"\n[STATS] ESTATÍSTICAS:")
        print(f"   Tickets analisados: {total}")
        print(f"   Tickets mapeados: {mapped}")
        print(f"   Taxa de mapeamento: {rate:.1f}%")
        
        print(f"\n[MAP] MAPEAMENTOS IDENTIFICADOS:")
        for mapping in self.results["mapping_details"][:5]:  # Mostrar apenas 5
            if mapping.get("v69_phase_mapping") or mapping.get("v69_ticket_mapping"):
                print(f"   - {mapping['ticket_id']}: {mapping['ticket_title'][:40]}...")
                if mapping.get("v69_phase_mapping"):
                    print(f"     -> Fases: {', '.join(mapping['v69_phase_mapping'])}")
                if mapping.get("v69_ticket_mapping"):
                    print(f"     -> Tickets v69: {', '.join(mapping['v69_ticket_mapping'])}")
        
        if len(self.results["mapping_details"]) > 5:
            print(f"   ... e mais {len(self.results['mapping_details']) - 5} mapeamentos")
        
        if self.results["recommendations"]:
            print(f"\n[REC] RECOMENDAÇÕES:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n[REPORT] Relatório completo salvo em: ticket_sync_report.json")
        print("=" * 60)

def main():
    """Função principal"""
    print("=== SINCRONIZAÇÃO DE TICKETS NC-DS-* COM ROADMAP v69 ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Inicializar ferramenta
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    sync_tool = TicketSyncTool(brain_dir)
    
    # Executar sincronização
    sync_tool.analyze_tickets()
    sync_tool.execute_sync_actions()
    
    # Gerar relatório
    report_file = sync_tool.generate_report()
    
    # Imprimir resumo
    sync_tool.print_summary()
    
    # Status final
    mapping_rate = (sync_tool.results["tickets_mapped"] / sync_tool.results["tickets_analyzed"] * 100) if sync_tool.results["tickets_analyzed"] > 0 else 0
    
    if mapping_rate >= 50:
        print("\n[OK] SINCRONIZAÇÃO CONCLUÍDA - MAPEAMENTO SATISFATÓRIO")
        return 0
    else:
        print("\n[WARN] SINCRONIZAÇÃO CONCLUÍDA - MAPEAMENTO BAIXO")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)