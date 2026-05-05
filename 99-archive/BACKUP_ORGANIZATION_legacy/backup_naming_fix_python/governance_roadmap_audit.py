#!/usr/bin/env python3
"""
Auditoria de Governança e Roadmaps
Analisa compliance, tickets, roadmaps e ciclos
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class GovernanceAuditor:
    """Auditor de governança NeoCortex"""
    
    def __init__(self):
        self.brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
        self.results = {
            "audit_date": datetime.now().isoformat() + "Z",
            "compliance": {},
            "roadmaps": {},
            "tickets": {},
            "cycles": {},
            "gaps": [],
            "recommendations": []
        }
    
    def audit_compliance(self):
        """Audita compliance com regras"""
        print("1. Auditando compliance...")
        
        # Verificar regras básicas
        rules_checked = {
            "NC- naming convention": False,
            "YAML structure": False,
            "JSON security": False,
            "Ticket fields": False,
            "Cycle adherence": False
        }
        
        # Verificar opencode.json
        opencode_file = self.brain_dir / "opencode.json"
        if opencode_file.exists():
            try:
                with open(opencode_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("config_id", "").startswith("NC-"):
                        rules_checked["NC- naming convention"] = True
            except:
                pass
        
        # Verificar tickets YAML
        yaml_files = list(self.brain_dir.glob("NC-DS-*.yaml"))
        valid_tickets = 0
        for yaml_file in yaml_files[:5]:  # Amostra
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and all(field in data for field in ["ticket_id", "status", "title", "description", "priority"]):
                        valid_tickets += 1
            except:
                pass
        
        rules_checked["Ticket fields"] = valid_tickets >= 3  # Pelo menos 3 tickets válidos
        rules_checked["YAML structure"] = len(yaml_files) > 0
        
        # Verificar scripts de segurança
        security_scripts = ["validate_yaml.py", "pre_commit_hook.py", "test_sanitization.py"]
        rules_checked["JSON security"] = all((self.brain_dir / script).exists() for script in security_scripts)
        
        self.results["compliance"] = {
            "rules_checked": rules_checked,
            "score": sum(1 for v in rules_checked.values() if v) / len(rules_checked) * 100,
            "details": rules_checked
        }
    
    def audit_roadmaps(self):
        """Audita roadmaps existentes"""
        print("2. Auditando roadmaps...")
        
        roadmaps_found = []
        
        # Procurar arquivos de roadmap
        for pattern in ["**/*roadmap*", "**/*ROADMAP*", "**/*tickets*"]:
            for file_path in self.brain_dir.glob(pattern):
                if file_path.suffix in ['.md', '.yaml', '.json']:
                    roadmaps_found.append({
                        "file": str(file_path.relative_to(self.brain_dir)),
                        "size": file_path.stat().st_size,
                        "type": file_path.suffix
                    })
        
        # Analisar roadmap principal se existir
        roadmap_analysis = {
            "found": len(roadmaps_found),
            "files": roadmaps_found[:10],  # Limitar a 10
            "has_main_roadmap": False,
            "ticket_count": 0,
            "phases": []
        }
        
        # Verificar roadmap v69
        v69_roadmap = self.brain_dir / "e458b7a2-8e87-4899-8c0a-5cac5901c952" / "roadmap_v69_tickets.md"
        if v69_roadmap.exists():
            roadmap_analysis["has_main_roadmap"] = True
            try:
                with open(v69_roadmap, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Contar tickets
                    ticket_count = content.count("### TKT-")
                    roadmap_analysis["ticket_count"] = ticket_count
                    
                    # Extrair fases
                    import re
                    phases = re.findall(r"## FASE \d+: .+", content)
                    roadmap_analysis["phases"] = phases
            except:
                pass
        
        self.results["roadmaps"] = roadmap_analysis
        
        # Identificar gaps
        if roadmap_analysis["found"] == 0:
            self.results["gaps"].append("Nenhum roadmap encontrado")
            self.results["recommendations"].append("Criar roadmap centralizado @ROADMAP")
        elif not roadmap_analysis["has_main_roadmap"]:
            self.results["gaps"].append("Roadmap principal não identificado")
            self.results["recommendations"].append("Consolidar roadmaps em NC-TODO-FR-001-roadmap.yaml")
    
    def audit_tickets(self):
        """Audita tickets do sistema"""
        print("3. Auditando tickets...")
        
        # Contar tickets por status
        tickets_by_status = {}
        tickets_by_priority = {}
        
        yaml_files = list(self.brain_dir.glob("NC-DS-*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        status = data.get("status", "UNKNOWN")
                        priority = data.get("priority", "UNKNOWN")
                        
                        tickets_by_status[status] = tickets_by_status.get(status, 0) + 1
                        tickets_by_priority[priority] = tickets_by_priority.get(priority, 0) + 1
            except:
                pass
        
        ticket_analysis = {
            "total_tickets": len(yaml_files),
            "by_status": tickets_by_status,
            "by_priority": tickets_by_priority,
            "recent_tickets": []
        }
        
        # Identificar tickets recentes (últimos 7 dias)
        recent_count = 0
        for yaml_file in yaml_files:
            try:
                file_mtime = datetime.fromtimestamp(yaml_file.stat().st_mtime)
                days_old = (datetime.now() - file_mtime).days
                if days_old <= 7:
                    recent_count += 1
            except:
                pass
        
        ticket_analysis["recent_7_days"] = recent_count
        
        self.results["tickets"] = ticket_analysis
        
        # Identificar gaps
        if ticket_analysis["total_tickets"] == 0:
            self.results["gaps"].append("Nenhum ticket encontrado")
        elif ticket_analysis.get("recent_7_days", 0) == 0:
            self.results["gaps"].append("Nenhum ticket recente (últimos 7 dias)")
            self.results["recommendations"].append("Criar tickets para atividades correntes")
    
    def audit_cycles(self):
        """Audita ciclos de trabalho"""
        print("4. Auditando ciclos...")
        
        cycle_analysis = {
            "current_cycle": "CICLO 1 (Início)",
            "cycle_files": [],
            "checkpoints": 0,
            "handoffs": 0
        }
        
        # Procurar arquivos de ciclo
        for pattern in ["**/*cycle*", "**/*CICLO*", "**/*checkpoint*"]:
            for file_path in self.brain_dir.glob(pattern):
                if file_path.suffix in ['.yaml', '.json', '.md']:
                    cycle_analysis["cycle_files"].append(str(file_path.relative_to(self.brain_dir)))
        
        # Contar checkpoints
        checkpoint_files = list(self.brain_dir.glob("**/*checkpoint*"))
        cycle_analysis["checkpoints"] = len(checkpoint_files)
        
        # Contar handoffs
        handoff_files = list(self.brain_dir.glob("**/*handoff*"))
        cycle_analysis["handoffs"] = len(handoff_files)
        
        self.results["cycles"] = cycle_analysis
        
        # Identificar gaps
        if cycle_analysis["checkpoints"] == 0:
            self.results["gaps"].append("Nenhum checkpoint registrado")
            self.results["recommendations"].append("Implementar checkpoints regulares")
        
        if cycle_analysis["handoffs"] == 0:
            self.results["gaps"].append("Nenhum handoff registrado")
            self.results["recommendations"].append("Documentar handoffs entre ciclos")
    
    def generate_report(self):
        """Gera relatório de auditoria"""
        print("\n5. Gerando relatório...")
        
        # Calcular score geral
        compliance_score = self.results["compliance"].get("score", 0)
        roadmap_score = 100 if self.results["roadmaps"].get("has_main_roadmap", False) else 50
        ticket_score = min(100, self.results["tickets"].get("total_tickets", 0) * 10)
        cycle_score = min(100, self.results["cycles"].get("checkpoints", 0) * 20)
        
        overall_score = (compliance_score + roadmap_score + ticket_score + cycle_score) / 4
        
        self.results["overall_score"] = overall_score
        self.results["status"] = "COMPLIANT" if overall_score >= 80 else "NON_COMPLIANT"
        
        # Salvar relatório
        report_file = self.brain_dir / "governance_audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def print_summary(self):
        """Imprime resumo da auditoria"""
        print("\n" + "=" * 60)
        print("AUDITORIA DE GOVERNANÇA E ROADMAPS - NEOcortex")
        print("=" * 60)
        
        print(f"\n[SCORE] SCORE GERAL: {self.results.get('overall_score', 0):.1f}/100")
        print(f"[STATUS] STATUS: {self.results.get('status', 'UNKNOWN')}")
        
        print(f"\n[COMPLIANCE] COMPLIANCE: {self.results['compliance'].get('score', 0):.1f}/100")
        for rule, status in self.results['compliance'].get('details', {}).items():
            print(f"  {'[OK]' if status else '[FAIL]'} {rule}")
        
        print(f"\n[ROADMAP] ROADMAPS: {self.results['roadmaps'].get('found', 0)} encontrados")
        if self.results['roadmaps'].get('has_main_roadmap'):
            print(f"  [OK] Roadmap principal: {self.results['roadmaps'].get('ticket_count', 0)} tickets")
            for phase in self.results['roadmaps'].get('phases', [])[:3]:
                print(f"  [PHASE] {phase}")
        
        print(f"\n[TICKET] TICKETS: {self.results['tickets'].get('total_tickets', 0)} no total")
        print(f"  [RECENT] Recentes (7 dias): {self.results['tickets'].get('recent_7_days', 0)}")
        print("  [STATS] Por status:")
        for status, count in self.results['tickets'].get('by_status', {}).items():
            print(f"    {status}: {count}")
        
        print(f"\n[CYCLE] CICLOS: {self.results['cycles'].get('current_cycle', 'Desconhecido')}")
        print(f"  [CHECK] Checkpoints: {self.results['cycles'].get('checkpoints', 0)}")
        print(f"  [HANDOFF] Handoffs: {self.results['cycles'].get('handoffs', 0)}")
        
        if self.results["gaps"]:
            print(f"\n[GAP] GAPS IDENTIFICADOS ({len(self.results['gaps'])}):")
            for gap in self.results["gaps"]:
                print(f"  • {gap}")
        
        if self.results["recommendations"]:
            print(f"\n[REC] RECOMENDAÇÕES ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n[REPORT] Relatório completo salvo em: governance_audit_report.json")
        print("=" * 60)

def main():
    """Função principal"""
    print("AUDITORIA DE GOVERNANÇA E ROADMAPS - NeoCortex")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    auditor = GovernanceAuditor()
    
    # Executar auditorias
    auditor.audit_compliance()
    auditor.audit_roadmaps()
    auditor.audit_tickets()
    auditor.audit_cycles()
    
    # Gerar relatório
    report_file = auditor.generate_report()
    
    # Imprimir resumo
    auditor.print_summary()
    
    # Status final
    if auditor.results.get("overall_score", 0) >= 80:
        print("\n[OK] AUDITORIA CONCLUÍDA - SISTEMA EM CONFORMIDADE")
        return 0
    else:
        print("\n[WARN] AUDITORIA CONCLUÍDA - GAPS IDENTIFICADOS")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)