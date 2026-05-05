#!/usr/bin/env python3
"""
Sistema de Handoffs entre Ciclos NeoCortex (R12)
Documentação formal de transferência entre ciclos/agentes
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class HandoffSystem:
    """Sistema de gerenciamento de handoffs"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.handoffs_dir = base_dir / "handoffs"
        self.handoffs_dir.mkdir(exist_ok=True)
        
        # Templates de handoff
        self.templates = {
            "cycle_to_cycle": {
                "required_fields": ["from_cycle", "to_cycle", "summary", "pending_tasks", "completed_tasks"],
                "description": "Transferência entre ciclos de trabalho"
            },
            "agent_to_agent": {
                "required_fields": ["from_agent", "to_agent", "context", "instructions", "constraints"],
                "description": "Transferência entre agentes"
            },
            "phase_transition": {
                "required_fields": ["from_phase", "to_phase", "deliverables", "dependencies", "risks"],
                "description": "Transição entre fases de projeto"
            }
        }
    
    def create_handoff(self,
                      handoff_type: str,
                      from_entity: str,
                      to_entity: str,
                      summary: str,
                      details: Dict,
                      metadata: Dict = None) -> str:
        """Cria um novo handoff"""
        # Validar tipo
        if handoff_type not in self.templates:
            raise ValueError(f"Tipo de handoff inválido: {handoff_type}. Válidos: {list(self.templates.keys())}")
        
        # Gerar ID único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        handoff_id = f"HANDOFF_{handoff_type.upper()}_{timestamp}"
        
        # Coletar informações do contexto
        context_info = self._collect_context_info()
        
        # Estrutura do handoff
        handoff_data = {
            "handoff_id": handoff_id,
            "type": handoff_type,
            "template": self.templates[handoff_type]["description"],
            "timestamp": datetime.now().isoformat() + "Z",
            "status": "PENDING",  # PENDING, ACCEPTED, REJECTED, COMPLETED
            "from_entity": from_entity,
            "to_entity": to_entity,
            "summary": summary,
            "details": details,
            "context": context_info,
            "metadata": metadata or {},
            "acceptance": {
                "accepted_by": None,
                "accepted_at": None,
                "notes": None
            },
            "verification": {
                "verified": False,
                "verified_by": None,
                "verified_at": None
            },
            "hash": ""
        }
        
        # Validar campos obrigatórios
        required_fields = self.templates[handoff_type]["required_fields"]
        for field in required_fields:
            if field not in details:
                raise ValueError(f"Campo obrigatório faltante no details: {field}")
        
        # Calcular hash
        handoff_str = json.dumps(handoff_data, sort_keys=True)
        handoff_data["hash"] = hashlib.sha256(handoff_str.encode()).hexdigest()
        
        # Salvar handoff
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        with open(handoff_file, 'w', encoding='utf-8') as f:
            json.dump(handoff_data, f, indent=2, ensure_ascii=False)
        
        # Registrar no log de handoffs
        self._log_handoff(handoff_data)
        
        print(f"[HANDOFF] Criado: {handoff_id} ({handoff_type})")
        print(f"         De: {from_entity} -> Para: {to_entity}")
        print(f"         Resumo: {summary[:80]}...")
        
        return handoff_id
    
    def _collect_context_info(self) -> Dict[str, Any]:
        """Coleta informações de contexto para o handoff"""
        # Verificar checkpoints recentes
        checkpoints_dir = self.base_dir / "checkpoints"
        recent_checkpoints = []
        
        if checkpoints_dir.exists():
            checkpoint_files = list(checkpoints_dir.glob("*.json"))
            checkpoint_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for cp_file in checkpoint_files[:3]:  # Últimos 3
                try:
                    with open(cp_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        recent_checkpoints.append({
                            "id": data.get("checkpoint_id"),
                            "cycle": data.get("cycle"),
                            "timestamp": data.get("timestamp")
                        })
                except:
                    continue
        
        # Verificar tickets ativos
        tickets_dir = self.base_dir
        active_tickets = []
        
        yaml_files = list(tickets_dir.glob("NC-DS-*.yaml"))
        for yaml_file in yaml_files[:5]:  # Limitar análise
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        status = data.get("status", "")
                        if status in ["OPEN", "IN_PROGRESS"]:
                            active_tickets.append({
                                "id": data.get("ticket_id"),
                                "title": data.get("title", "")[:50],
                                "status": status,
                                "priority": data.get("priority", "")
                            })
            except:
                continue
        
        return {
            "recent_checkpoints": recent_checkpoints,
            "active_tickets": active_tickets,
            "timestamp": datetime.now().isoformat() + "Z"
        }
    
    def _log_handoff(self, handoff_data: Dict):
        """Registra handoff no log principal"""
        log_file = self.handoffs_dir / "handoffs_log.json"
        
        log_entry = {
            "handoff_id": handoff_data["handoff_id"],
            "type": handoff_data["type"],
            "timestamp": handoff_data["timestamp"],
            "from": handoff_data["from_entity"],
            "to": handoff_data["to_entity"],
            "status": handoff_data["status"],
            "summary": handoff_data["summary"][:100]
        }
        
        # Carregar log existente ou criar novo
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                log_data = {"handoffs": []}
        else:
            log_data = {"handoffs": []}
        
        # Adicionar novo handoff
        log_data["handoffs"].append(log_entry)
        
        # Manter apenas últimos 50 handoffs
        if len(log_data["handoffs"]) > 50:
            log_data["handoffs"] = log_data["handoffs"][-50:]
        
        # Salvar log
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def accept_handoff(self, handoff_id: str, accepted_by: str, notes: str = ""):
        """Aceita um handoff pendente"""
        handoff_data = self.get_handoff(handoff_id)
        if not handoff_data:
            raise ValueError(f"Handoff não encontrado: {handoff_id}")
        
        if handoff_data["status"] != "PENDING":
            raise ValueError(f"Handoff não está pendente: {handoff_data['status']}")
        
        # Atualizar status
        handoff_data["status"] = "ACCEPTED"
        handoff_data["acceptance"] = {
            "accepted_by": accepted_by,
            "accepted_at": datetime.now().isoformat() + "Z",
            "notes": notes
        }
        
        # Recalcular hash
        handoff_str = json.dumps(handoff_data, sort_keys=True)
        handoff_data["hash"] = hashlib.sha256(handoff_str.encode()).hexdigest()
        
        # Salvar
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        with open(handoff_file, 'w', encoding='utf-8') as f:
            json.dump(handoff_data, f, indent=2, ensure_ascii=False)
        
        # Atualizar log
        self._update_handoff_log(handoff_id, "ACCEPTED")
        
        print(f"[HANDOFF] Aceito: {handoff_id} por {accepted_by}")
    
    def complete_handoff(self, handoff_id: str, verified_by: str, verification_notes: str = ""):
        """Marca handoff como completado e verificado"""
        handoff_data = self.get_handoff(handoff_id)
        if not handoff_data:
            raise ValueError(f"Handoff não encontrado: {handoff_id}")
        
        if handoff_data["status"] != "ACCEPTED":
            raise ValueError(f"Handoff não está aceito: {handoff_data['status']}")
        
        # Atualizar status
        handoff_data["status"] = "COMPLETED"
        handoff_data["verification"] = {
            "verified": True,
            "verified_by": verified_by,
            "verified_at": datetime.now().isoformat() + "Z",
            "notes": verification_notes
        }
        
        # Recalcular hash
        handoff_str = json.dumps(handoff_data, sort_keys=True)
        handoff_data["hash"] = hashlib.sha256(handoff_str.encode()).hexdigest()
        
        # Salvar
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        with open(handoff_file, 'w', encoding='utf-8') as f:
            json.dump(handoff_data, f, indent=2, ensure_ascii=False)
        
        # Atualizar log
        self._update_handoff_log(handoff_id, "COMPLETED")
        
        print(f"[HANDOFF] Completado: {handoff_id} verificado por {verified_by}")
    
    def _update_handoff_log(self, handoff_id: str, new_status: str):
        """Atualiza status no log de handoffs"""
        log_file = self.handoffs_dir / "handoffs_log.json"
        
        if not log_file.exists():
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except:
            return
        
        # Atualizar status
        for handoff in log_data.get("handoffs", []):
            if handoff.get("handoff_id") == handoff_id:
                handoff["status"] = new_status
                break
        
        # Salvar
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def get_handoff(self, handoff_id: str) -> Optional[Dict]:
        """Obtém detalhes de um handoff específico"""
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        
        if not handoff_file.exists():
            return None
        
        try:
            with open(handoff_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def list_handoffs(self, status: str = None, handoff_type: str = None) -> List[Dict]:
        """Lista handoffs, opcionalmente filtrado"""
        handoffs = []
        
        for handoff_file in self.handoffs_dir.glob("*.json"):
            if handoff_file.name == "handoffs_log.json":
                continue
            
            try:
                with open(handoff_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if status and data.get("status") != status:
                        continue
                    
                    if handoff_type and data.get("type") != handoff_type:
                        continue
                    
                    handoffs.append({
                        "id": data.get("handoff_id"),
                        "type": data.get("type"),
                        "status": data.get("status"),
                        "timestamp": data.get("timestamp"),
                        "from": data.get("from_entity"),
                        "to": data.get("to_entity"),
                        "summary": data.get("summary", "")[:50]
                    })
            except:
                continue
        
        # Ordenar por timestamp (mais recente primeiro)
        handoffs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return handoffs

class CycleHandoffManager:
    """Gerenciador especializado em handoffs entre ciclos"""
    
    def __init__(self, handoff_system: HandoffSystem):
        self.handoff_system = handoff_system
    
    def create_cycle_handoff(self,
                           from_cycle: str,
                           to_cycle: str,
                           completed_tasks: List[str],
                           pending_tasks: List[str],
                           risks: List[str] = None,
                           recommendations: List[str] = None) -> str:
        """Cria handoff entre ciclos"""
        
        details = {
            "from_cycle": from_cycle,
            "to_cycle": to_cycle,
            "summary": f"Handoff de {from_cycle} para {to_cycle}",
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "risks": risks or [],
            "recommendations": recommendations or [],
            "deliverables": [],
            "dependencies": [],
            "context_changes": []
        }
        
        return self.handoff_system.create_handoff(
            handoff_type="cycle_to_cycle",
            from_entity=f"CYCLE_{from_cycle}",
            to_entity=f"CYCLE_{to_cycle}",
            summary=f"Transição de {from_cycle} para {to_cycle}",
            details=details,
            metadata={
                "cycle_transition": True,
                "auto_generated": False,
                "priority": "HIGH"
            }
        )
    
    def create_phase_transition(self,
                               from_phase: str,
                               to_phase: str,
                               deliverables: List[Dict],
                               dependencies: List[str]) -> str:
        """Cria handoff entre fases"""
        
        details = {
            "from_phase": from_phase,
            "to_phase": to_phase,
            "deliverables": deliverables,
            "dependencies": dependencies,
            "risks": [],
            "assumptions": [],
            "success_criteria": []
        }
        
        return self.handoff_system.create_handoff(
            handoff_type="phase_transition",
            from_entity=f"PHASE_{from_phase}",
            to_entity=f"PHASE_{to_phase}",
            summary=f"Transição da fase {from_phase} para {to_phase}",
            details=details
        )

def main():
    """Função principal de demonstração"""
    print("=== SISTEMA DE HANDOFFS NEOcortex (R12) ===")
    print()
    
    # Inicializar sistema
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    handoff_system = HandoffSystem(brain_dir)
    cycle_manager = CycleHandoffManager(handoff_system)
    
    # 1. Criar handoff entre ciclos
    print("1. Criando handoff entre ciclos...")
    
    completed_tasks = [
        "Auditoria de gaps YAML/JSON",
        "Implementação sistema de checkpoints",
        "Padronização tickets YAML"
    ]
    
    pending_tasks = [
        "Consolidar roadmaps",
        "Sincronizar tickets com roadmap v69",
        "Configurar monitoramento compliance"
    ]
    
    handoff_id = cycle_manager.create_cycle_handoff(
        from_cycle="CICLO_1",
        to_cycle="CICLO_2",
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        risks=["Falta de checkpoints regulares", "Roadmaps descentralizados"],
        recommendations=["Implementar checkpoints automáticos", "Consolidar roadmaps"]
    )
    
    print(f"   Handoff criado: {handoff_id}")
    
    # 2. Listar handoffs
    print("\n2. Handoffs existentes:")
    handoffs = handoff_system.list_handoffs()
    for h in handoffs[:5]:
        print(f"   - {h['id']} - {h['from']}->{h['to']} - {h['status']}")
    
    # 3. Aceitar handoff (simulação)
    print("\n3. Aceitando handoff...")
    try:
        handoff_system.accept_handoff(
            handoff_id=handoff_id,
            accepted_by="T0-Antigravity",
            notes="Handoff aceito, iniciando CICLO_2"
        )
    except ValueError as e:
        print(f"   [INFO] {e}")
    
    # 4. Completar handoff (simulação)
    print("\n4. Completando handoff...")
    try:
        handoff_system.complete_handoff(
            handoff_id=handoff_id,
            verified_by="T0-Auditor",
            verification_notes="Handoff verificado e validado"
        )
    except ValueError as e:
        print(f"   [INFO] {e}")
    
    # 5. Estatísticas
    print("\n5. Estatísticas do sistema:")
    total_handoffs = len(list((brain_dir / "handoffs").glob("*.json")))
    print(f"   Total de handoffs: {total_handoffs}")
    
    # 6. Instruções de uso
    print("\n" + "=" * 60)
    print("INSTRUÇÕES DE USO:")
    print("=" * 60)
    print("\nPara criar handoffs:")
    print("  from handoff_system import HandoffSystem, CycleHandoffManager")
    print("  system = HandoffSystem(Path('.'))")
    print("  manager = CycleHandoffManager(system)")
    print()
    print("  # Handoff entre ciclos")
    print("  manager.create_cycle_handoff('CICLO_1', 'CICLO_2', completed, pending)")
    print()
    print("  # Handoff entre fases")
    print("  manager.create_phase_transition('FASE_1', 'FASE_2', deliverables, dependencies)")
    print()
    print("Para gerenciar handoffs:")
    print("  system.accept_handoff(handoff_id, 'agente', 'notas')")
    print("  system.complete_handoff(handoff_id, 'verificador', 'notas')")
    print("\nHandoffs salvos em: brain/handoffs/")
    print("=" * 60)

if __name__ == "__main__":
    main()