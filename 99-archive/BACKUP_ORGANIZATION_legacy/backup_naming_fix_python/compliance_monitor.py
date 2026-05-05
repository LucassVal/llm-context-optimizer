#!/usr/bin/env python3
"""
Monitoramento automático de compliance NeoCortex
Verifica regularmente conformidade com regras e gera alertas
"""

import json
import yaml
import schedule
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import threading

class ComplianceMonitor:
    """Monitor de compliance automático"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.monitoring_dir = base_dir / "monitoring"
        self.monitoring_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.config = {
            "check_interval_minutes": 60,  # Verificar a cada hora
            "alert_threshold": 80,  # Alerta se compliance < 80%
            "retention_days": 30,  # Manter logs por 30 dias
            "monitor_components": [
                "yaml_security",
                "json_security", 
                "naming_convention",
                "ticket_structure",
                "checkpoint_system",
                "handoff_system",
                "roadmap_sync"
            ]
        }
        
        # Estado do monitor
        self.is_running = False
        self.monitor_thread = None
        
    def run_compliance_check(self) -> Dict[str, Any]:
        """Executa verificação completa de compliance"""
        print(f"[COMPLIANCE] Verificação iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            "timestamp": datetime.now().isoformat() + "Z",
            "components": {},
            "overall_score": 0,
            "status": "UNKNOWN",
            "alerts": [],
            "recommendations": []
        }
        
        # 1. Verificar segurança YAML
        yaml_score = self._check_yaml_security()
        results["components"]["yaml_security"] = {
            "score": yaml_score,
            "status": "PASS" if yaml_score >= 90 else "WARN" if yaml_score >= 70 else "FAIL"
        }
        
        # 2. Verificar segurança JSON
        json_score = self._check_json_security()
        results["components"]["json_security"] = {
            "score": json_score,
            "status": "PASS" if json_score >= 90 else "WARN" if json_score >= 70 else "FAIL"
        }
        
        # 3. Verificar convenção de nomenclatura
        naming_score = self._check_naming_convention()
        results["components"]["naming_convention"] = {
            "score": naming_score,
            "status": "PASS" if naming_score >= 90 else "WARN" if naming_score >= 70 else "FAIL"
        }
        
        # 4. Verificar estrutura de tickets
        ticket_score = self._check_ticket_structure()
        results["components"]["ticket_structure"] = {
            "score": ticket_score,
            "status": "PASS" if ticket_score >= 90 else "WARN" if ticket_score >= 70 else "FAIL"
        }
        
        # 5. Verificar sistema de checkpoints
        checkpoint_score = self._check_checkpoint_system()
        results["components"]["checkpoint_system"] = {
            "score": checkpoint_score,
            "status": "PASS" if checkpoint_score >= 90 else "WARN" if checkpoint_score >= 70 else "FAIL"
        }
        
        # 6. Verificar sistema de handoffs
        handoff_score = self._check_handoff_system()
        results["components"]["handoff_system"] = {
            "score": handoff_score,
            "status": "PASS" if handoff_score >= 90 else "WARN" if handoff_score >= 70 else "FAIL"
        }
        
        # 7. Verificar sincronização de roadmap
        roadmap_score = self._check_roadmap_sync()
        results["components"]["roadmap_sync"] = {
            "score": roadmap_score,
            "status": "PASS" if roadmap_score >= 90 else "WARN" if roadmap_score >= 70 else "FAIL"
        }
        
        # Calcular score geral
        scores = [comp["score"] for comp in results["components"].values()]
        results["overall_score"] = sum(scores) / len(scores) if scores else 0
        
        # Determinar status
        if results["overall_score"] >= 90:
            results["status"] = "COMPLIANT"
        elif results["overall_score"] >= 70:
            results["status"] = "WARNING"
        else:
            results["status"] = "NON_COMPLIANT"
        
        # Gerar alertas se necessário
        if results["overall_score"] < self.config["alert_threshold"]:
            results["alerts"].append({
                "level": "CRITICAL",
                "message": f"Compliance abaixo do limite: {results['overall_score']:.1f}% < {self.config['alert_threshold']}%",
                "component": "OVERALL"
            })
        
        # Gerar recomendações
        for comp_name, comp_data in results["components"].items():
            if comp_data["score"] < 70:
                results["recommendations"].append(
                    f"Melhorar {comp_name}: {comp_data['score']:.1f}% (status: {comp_data['status']})"
                )
        
        # Salvar resultado
        self._save_check_result(results)
        
        # Log resumo
        print(f"[COMPLIANCE] Verificação concluída: {results['overall_score']:.1f}% - {results['status']}")
        
        if results["alerts"]:
            print(f"[COMPLIANCE] Alertas: {len(results['alerts'])}")
            for alert in results["alerts"]:
                print(f"  • {alert['level']}: {alert['message']}")
        
        return results
    
    def _check_yaml_security(self) -> float:
        """Verifica segurança dos arquivos YAML"""
        try:
            # Verificar se scripts de validação existem
            validation_scripts = ["validate_yaml.py", "test_sanitization.py", "pre_commit_hook.py"]
            scripts_present = sum(1 for script in validation_scripts if (self.base_dir / script).exists())
            
            # Verificar tickets YAML
            yaml_files = list(self.base_dir.glob("NC-DS-*.yaml"))
            valid_yamls = 0
            
            for yaml_file in yaml_files[:3]:  # Amostra
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                    valid_yamls += 1
                except:
                    pass
            
            # Calcular score
            script_score = (scripts_present / len(validation_scripts)) * 50
            yaml_score = (valid_yamls / max(len(yaml_files), 1)) * 50
            
            return script_score + yaml_score
            
        except Exception as e:
            print(f"[ERROR] Falha na verificação YAML: {e}")
            return 0
    
    def _check_json_security(self) -> float:
        """Verifica segurança dos arquivos JSON"""
        try:
            # Verificar opencode.json
            opencode_file = self.base_dir / "opencode.json"
            opencode_valid = False
            
            if opencode_file.exists():
                try:
                    with open(opencode_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        opencode_valid = data.get("config_id", "").startswith("NC-")
                except:
                    pass
            
            # Verificar relatórios JSON
            report_files = list(self.base_dir.glob("*report.json"))
            valid_reports = 0
            
            for report_file in report_files[:3]:
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    valid_reports += 1
                except:
                    pass
            
            # Calcular score
            opencode_score = 50 if opencode_valid else 0
            report_score = (valid_reports / max(len(report_files), 1)) * 50
            
            return opencode_score + report_score
            
        except Exception as e:
            print(f"[ERROR] Falha na verificação JSON: {e}")
            return 0
    
    def _check_naming_convention(self) -> float:
        """Verifica convenção de nomenclatura NC-"""
        try:
            # Verificar arquivos com padrão NC-
            nc_files = list(self.base_dir.glob("NC-*"))
            total_files = len(list(self.base_dir.glob("*")))
            
            # Verificar tickets NC-DS-*
            ds_tickets = list(self.base_dir.glob("NC-DS-*.yaml"))
            
            # Calcular score
            nc_ratio = (len(nc_files) / max(total_files, 1)) * 50
            ds_ratio = (len(ds_tickets) / max(len(list(self.base_dir.glob("*.yaml"))), 1)) * 50
            
            return nc_ratio + ds_ratio
            
        except Exception as e:
            print(f"[ERROR] Falha na verificação de nomenclatura: {e}")
            return 0
    
    def _check_ticket_structure(self) -> float:
        """Verifica estrutura dos tickets"""
        try:
            yaml_files = list(self.base_dir.glob("NC-DS-*.yaml"))
            valid_tickets = 0
            
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        
                        # Campos obrigatórios
                        required_fields = ["ticket_id", "status", "title", "description", "priority"]
                        if data and all(field in data for field in required_fields):
                            valid_tickets += 1
                except:
                    pass
            
            return (valid_tickets / max(len(yaml_files), 1)) * 100
            
        except Exception as e:
            print(f"[ERROR] Falha na verificação de tickets: {e}")
            return 0
    
    def _check_checkpoint_system(self) -> float:
        """Verifica sistema de checkpoints"""
        try:
            checkpoints_dir = self.base_dir / "checkpoints"
            
            if not checkpoints_dir.exists():
                return 0
            
            # Verificar arquivos de checkpoint
            checkpoint_files = list(checkpoints_dir.glob("*.json"))
            
            # Verificar logs
            log_file = checkpoints_dir / "checkpoints_log.json"
            has_log = log_file.exists()
            
            # Calcular score
            checkpoint_score = min(len(checkpoint_files) * 20, 60)  # Máximo 60% por checkpoints
            log_score = 40 if has_log else 0
            
            return checkpoint_score + log_score
            
        except Exception as e:
            print(f"[ERROR] Falha na verificação de checkpoints: {e}")
            return 0
    
    def _check_handoff_system(self) -> float:
        """Verifica sistema de handoffs"""
        try:
            handoffs_dir = self.base_dir / "handoffs"
            
            if not handoffs_dir.exists():
                return 0
            
            # Verificar arquivos de handoff
            handoff_files = list(handoffs_dir.glob("*.json"))
            
            # Verificar logs
            log_file = handoffs_dir / "handoffs_log.json"
            has_log = log_file.exists()
            
            # Calcular score
            handoff_score = min(len(handoff_files) * 20, 60)  # Máximo 60% por handoffs
            log_score = 40 if has_log else 0
            
            return handoff_score + log_score
            
        except Exception as e:
            print(f"[ERROR] Falha na verificação de handoffs: {e}")
            return 0
    
    def _check_roadmap_sync(self) -> float:
        """Verifica sincronização de roadmap"""
        try:
            # Verificar roadmap consolidado
            roadmap_file = self.base_dir / "NC-TODO-FR-001-roadmap.yaml"
            
            if not roadmap_file.exists():
                return 0
            
            # Verificar se é YAML válido
            try:
                with open(roadmap_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                    # Verificar campos essenciais
                    essential_fields = ["roadmap_id", "version", "phases", "current_tickets"]
                    if data and all(field in data for field in essential_fields):
                        return 100
                    else:
                        return 50
            except:
                return 0
                
        except Exception as e:
            print(f"[ERROR] Falha na verificação de roadmap: {e}")
            return 0
    
    def _save_check_result(self, results: Dict):
        """Salva resultado da verificação"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.monitoring_dir / f"compliance_check_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Atualizar log de verificações
        self._update_monitoring_log(results)
    
    def _update_monitoring_log(self, results: Dict):
        """Atualiza log de monitoramento"""
        log_file = self.monitoring_dir / "monitoring_log.json"
        
        log_entry = {
            "timestamp": results["timestamp"],
            "overall_score": results["overall_score"],
            "status": results["status"],
            "alerts": len(results["alerts"]),
            "components": {k: v["status"] for k, v in results["components"].items()}
        }
        
        # Carregar ou criar log
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                log_data = {"checks": []}
        else:
            log_data = {"checks": []}
        
        # Adicionar nova verificação
        log_data["checks"].append(log_entry)
        
        # Manter apenas últimos 100 verificações
        if len(log_data["checks"]) > 100:
            log_data["checks"] = log_data["checks"][-100:]
        
        # Salvar
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.is_running:
            print("[MONITOR] Monitoramento já está em execução")
            return
        
        print("[MONITOR] Iniciando monitoramento de compliance...")
        print(f"[MONITOR] Intervalo: {self.config['check_interval_minutes']} minutos")
        print(f"[MONITOR] Limite de alerta: {self.config['alert_threshold']}%")
        
        self.is_running = True
        
        # Executar verificação inicial
        self.run_compliance_check()
        
        # Configurar agendamento
        schedule.every(self.config["check_interval_minutes"]).minutes.do(
            self.run_compliance_check
        )
        
        # Iniciar thread de monitoramento
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        print("[MONITOR] Monitoramento iniciado com sucesso")
    
    def stop_monitoring(self):
        """Para monitoramento contínuo"""
        if not self.is_running:
            print("[MONITOR] Monitoramento não está em execução")
            return
        
        print("[MONITOR] Parando monitoramento...")
        self.is_running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("[MONITOR] Monitoramento parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    def generate_summary_report(self) -> Dict:
        """Gera relatório resumido das verificações"""
        log_file = self.monitoring_dir / "monitoring_log.json"
        
        if not log_file.exists():
            return {"error": "Nenhuma verificação registrada"}
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            checks = log_data.get("checks", [])
            
            if not checks:
                return {"error": "Nenhuma verificação disponível"}
            
            # Estatísticas
            total_checks = len(checks)
            compliant_checks = sum(1 for c in checks if c.get("status") == "COMPLIANT")
            warning_checks = sum(1 for c in checks if c.get("status") == "WARNING")
            non_compliant_checks = sum(1 for c in checks if c.get("status") == "NON_COMPLIANT")
            
            # Scores médios
            avg_score = sum(c.get("overall_score", 0) for c in checks) / total_checks
            
            # Última verificação
            last_check = checks[-1] if checks else {}
            
            return {
                "summary_date": datetime.now().isoformat() + "Z",
                "total_checks": total_checks,
                "compliant_checks": compliant_checks,
                "warning_checks": warning_checks,
                "non_compliant_checks": non_compliant_checks,
                "compliance_rate": (compliant_checks / total_checks * 100) if total_checks > 0 else 0,
                "average_score": avg_score,
                "last_check": last_check,
                "status": "HEALTHY" if avg_score >= 90 else "WARNING" if avg_score >= 70 else "CRITICAL"
            }
            
        except Exception as e:
            return {"error": f"Falha ao gerar relatório: {e}"}

def main():
    """Função principal"""
    print("=== MONITORAMENTO AUTOMÁTICO DE COMPLIANCE ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Inicializar monitor
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    monitor = ComplianceMonitor(brain_dir)
    
    # Executar verificação única
    print("Executando verificação de compliance...")
    results = monitor.run_compliance_check()
    
    # Exibir resultados
    print(f"\n{'='*60}")
    print("RESULTADOS DA VERIFICAÇÃO DE COMPLIANCE")
    print("="*60)
    
    print(f"\n[SCORE] SCORE GERAL: {results['overall_score']:.1f}%")
    print(f"[STATUS] STATUS: {results['status']}")
    
    print(f"\n[COMP] COMPONENTES:")
    for comp_name, comp_data in results["components"].items():
        print(f"  {comp_name.upper():20} {comp_data['score']:5.1f}% [{comp_data['status']}]")
    
    if results["alerts"]:
        print(f"\n[ALERT] ALERTAS ({len(results['alerts'])}):")
        for alert in results["alerts"]:
            print(f"  - {alert['level']}: {alert['message']}")
    
    if results["recommendations"]:
        print(f"\n[REC] RECOMENDAÇÕES ({len(results['recommendations'])}):")
        for rec in results["recommendations"]:
            print(f"  - {rec}")
    
    # Gerar relatório resumido
    print(f"\n[REPORT] RELATÓRIO RESUMIDO:")
    summary = monitor.generate_summary_report()
    
    if "error" not in summary:
        print(f"  Verificações totais: {summary.get('total_checks', 0)}")
        print(f"  Taxa de conformidade: {summary.get('compliance_rate', 0):.1f}%")
        print(f"  Score médio: {summary.get('average_score', 0):.1f}%")
        print(f"  Status do sistema: {summary.get('status', 'UNKNOWN')}")
    
    # Instruções para monitoramento contínuo
    print(f"\n{'='*60}")
    print("INSTRUÇÕES PARA MONITORAMENTO CONTÍNUO:")
    print("="*60)
    print("\nPara iniciar monitoramento contínuo:")
    print("  monitor = ComplianceMonitor(Path('.'))")
    print("  monitor.start_monitoring()")
    print("\nPara parar monitoramento:")
    print("  monitor.stop_monitoring()")
    print("\nPara verificação manual:")
    print("  results = monitor.run_compliance_check()")
    print("\nLogs salvos em: brain/monitoring/")
    print("="*60)
    
    # Status final
    if results["overall_score"] >= 80:
        print("\n[OK] SISTEMA EM CONFORMIDADE")
        return 0
    else:
        print("\n[WARN] SISTEMA COM PROBLEMAS DE COMPLIANCE")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)