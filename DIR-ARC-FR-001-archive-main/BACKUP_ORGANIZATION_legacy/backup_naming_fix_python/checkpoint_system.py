#!/usr/bin/env python3
"""
Sistema de Checkpoints para Ciclos NeoCortex (R13)
Implementa checkpoints regulares com registro estruturado
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class CheckpointSystem:
    """Sistema de gerenciamento de checkpoints"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.checkpoints_dir = base_dir / "checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Ciclos definidos
        self.cycles = {
            "CICLO_0": "Boot",
            "CICLO_1": "Início", 
            "CICLO_2": "Execução",
            "CICLO_3": "Encerramento",
            "CICLO_4": "Semanal"
        }
    
    def create_checkpoint(self, 
                         cycle: str,
                         checkpoint_type: str = "regular",
                         description: str = "",
                         metadata: Dict = None) -> str:
        """Cria um novo checkpoint"""
        # Validar ciclo
        if cycle not in self.cycles:
            raise ValueError(f"Ciclo inválido: {cycle}. Válidos: {list(self.cycles.keys())}")
        
        # Gerar ID único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_id = f"CP_{cycle}_{timestamp}"
        
        # Coletar informações do sistema
        system_info = self._collect_system_info()
        
        # Estrutura do checkpoint
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "cycle": cycle,
            "cycle_name": self.cycles[cycle],
            "timestamp": datetime.now().isoformat() + "Z",
            "type": checkpoint_type,  # regular, milestone, error, recovery
            "description": description,
            "system_info": system_info,
            "metadata": metadata or {},
            "hash": ""
        }
        
        # Calcular hash
        checkpoint_str = json.dumps(checkpoint_data, sort_keys=True)
        checkpoint_data["hash"] = hashlib.sha256(checkpoint_str.encode()).hexdigest()
        
        # Salvar checkpoint
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        # Registrar no log de checkpoints
        self._log_checkpoint(checkpoint_data)
        
        print(f"[CHECKPOINT] Criado: {checkpoint_id} ({checkpoint_type})")
        return checkpoint_id
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Coleta informações do sistema para o checkpoint"""
        # Contar tickets
        tickets_dir = self.base_dir
        yaml_files = list(tickets_dir.glob("NC-DS-*.yaml"))
        
        # Analisar status dos tickets
        tickets_by_status = {}
        for yaml_file in yaml_files[:10]:  # Limitar análise
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        status = data.get("status", "UNKNOWN")
                        tickets_by_status[status] = tickets_by_status.get(status, 0) + 1
            except:
                pass
        
        # Verificar scripts de segurança
        security_scripts = [
            "validate_yaml.py",
            "pre_commit_hook.py", 
            "test_sanitization.py",
            "checkpoint_system.py"
        ]
        
        scripts_present = []
        for script in security_scripts:
            if (self.base_dir / script).exists():
                scripts_present.append(script)
        
        return {
            "ticket_count": len(yaml_files),
            "tickets_by_status": tickets_by_status,
            "security_scripts": scripts_present,
            "checkpoints_total": len(list(self.checkpoints_dir.glob("*.json"))),
            "timestamp": datetime.now().isoformat() + "Z"
        }
    
    def _log_checkpoint(self, checkpoint_data: Dict):
        """Registra checkpoint no log principal"""
        log_file = self.checkpoints_dir / "checkpoints_log.json"
        
        log_entry = {
            "checkpoint_id": checkpoint_data["checkpoint_id"],
            "cycle": checkpoint_data["cycle"],
            "timestamp": checkpoint_data["timestamp"],
            "type": checkpoint_data["type"],
            "description": checkpoint_data["description"][:100]  # Limitar
        }
        
        # Carregar log existente ou criar novo
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                log_data = {"checkpoints": []}
        else:
            log_data = {"checkpoints": []}
        
        # Adicionar novo checkpoint
        log_data["checkpoints"].append(log_entry)
        
        # Manter apenas últimos 100 checkpoints
        if len(log_data["checkpoints"]) > 100:
            log_data["checkpoints"] = log_data["checkpoints"][-100:]
        
        # Salvar log
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def list_checkpoints(self, cycle: str = None) -> List[Dict]:
        """Lista checkpoints, opcionalmente filtrado por ciclo"""
        checkpoints = []
        
        for checkpoint_file in self.checkpoints_dir.glob("*.json"):
            if checkpoint_file.name == "checkpoints_log.json":
                continue
            
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if cycle and data.get("cycle") != cycle:
                        continue
                    
                    checkpoints.append({
                        "id": data.get("checkpoint_id"),
                        "cycle": data.get("cycle"),
                        "timestamp": data.get("timestamp"),
                        "type": data.get("type"),
                        "description": data.get("description", "")[:50]
                    })
            except:
                continue
        
        # Ordenar por timestamp (mais recente primeiro)
        checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return checkpoints
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Obtém detalhes de um checkpoint específico"""
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def create_cycle_checkpoint(self, cycle: str) -> str:
        """Cria checkpoint padrão para um ciclo"""
        cycle_name = self.cycles.get(cycle, "Desconhecido")
        
        description = f"Checkpoint do {cycle} - {cycle_name}"
        
        # Coletar métricas específicas do ciclo
        metadata = {
            "cycle_phase": cycle_name,
            "auto_generated": True,
            "purpose": "cycle_tracking"
        }
        
        return self.create_checkpoint(
            cycle=cycle,
            checkpoint_type="cycle",
            description=description,
            metadata=metadata
        )
    
    def verify_checkpoint_integrity(self, checkpoint_id: str) -> bool:
        """Verifica integridade de um checkpoint"""
        checkpoint_data = self.get_checkpoint(checkpoint_id)
        if not checkpoint_data:
            return False
        
        # Remover hash para cálculo
        original_hash = checkpoint_data.pop("hash", "")
        
        # Calcular hash atual
        checkpoint_str = json.dumps(checkpoint_data, sort_keys=True)
        current_hash = hashlib.sha256(checkpoint_str.encode()).hexdigest()
        
        # Restaurar hash
        checkpoint_data["hash"] = original_hash
        
        return original_hash == current_hash

class CycleManager:
    """Gerenciador de ciclos com checkpoints automáticos"""
    
    def __init__(self, checkpoint_system: CheckpointSystem):
        self.checkpoint_system = checkpoint_system
        self.current_cycle = "CICLO_1"  # Default
    
    def start_cycle(self, cycle: str, description: str = ""):
        """Inicia um novo ciclo com checkpoint inicial"""
        if cycle not in self.checkpoint_system.cycles:
            raise ValueError(f"Ciclo inválido: {cycle}")
        
        self.current_cycle = cycle
        cycle_name = self.checkpoint_system.cycles[cycle]
        
        print(f"[CYCLE] Iniciando {cycle} - {cycle_name}")
        
        # Criar checkpoint de início
        checkpoint_id = self.checkpoint_system.create_checkpoint(
            cycle=cycle,
            checkpoint_type="cycle_start",
            description=f"Início do {cycle} - {cycle_name}. {description}"
        )
        
        # Registrar início no ciclo log
        self._log_cycle_start(cycle, checkpoint_id)
        
        return checkpoint_id
    
    def end_cycle(self, summary: str = ""):
        """Finaliza o ciclo atual com checkpoint final"""
        cycle_name = self.checkpoint_system.cycles.get(self.current_cycle, "Desconhecido")
        
        print(f"[CYCLE] Finalizando {self.current_cycle} - {cycle_name}")
        
        # Criar checkpoint de fim
        checkpoint_id = self.checkpoint_system.create_checkpoint(
            cycle=self.current_cycle,
            checkpoint_type="cycle_end",
            description=f"Fim do {self.current_cycle} - {cycle_name}. {summary}"
        )
        
        # Registrar fim no ciclo log
        self._log_cycle_end(self.current_cycle, checkpoint_id, summary)
        
        return checkpoint_id
    
    def create_milestone(self, milestone_name: str, description: str = ""):
        """Cria checkpoint de milestone dentro do ciclo atual"""
        return self.checkpoint_system.create_checkpoint(
            cycle=self.current_cycle,
            checkpoint_type="milestone",
            description=f"Milestone: {milestone_name}. {description}"
        )
    
    def _log_cycle_start(self, cycle: str, checkpoint_id: str):
        """Registra início de ciclo"""
        log_file = self.checkpoint_system.checkpoints_dir / "cycles_log.json"
        
        log_entry = {
            "cycle": cycle,
            "cycle_name": self.checkpoint_system.cycles.get(cycle),
            "start_checkpoint": checkpoint_id,
            "start_timestamp": datetime.now().isoformat() + "Z",
            "end_checkpoint": None,
            "end_timestamp": None,
            "status": "ACTIVE"
        }
        
        # Carregar ou criar log
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except:
                log_data = {"cycles": []}
        else:
            log_data = {"cycles": []}
        
        # Adicionar novo ciclo
        log_data["cycles"].append(log_entry)
        
        # Salvar
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _log_cycle_end(self, cycle: str, checkpoint_id: str, summary: str):
        """Registra fim de ciclo"""
        log_file = self.checkpoint_system.checkpoints_dir / "cycles_log.json"
        
        if not log_file.exists():
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except:
            return
        
        # Encontrar ciclo ativo
        for cycle_entry in log_data.get("cycles", []):
            if cycle_entry.get("cycle") == cycle and cycle_entry.get("status") == "ACTIVE":
                cycle_entry["end_checkpoint"] = checkpoint_id
                cycle_entry["end_timestamp"] = datetime.now().isoformat() + "Z"
                cycle_entry["status"] = "COMPLETED"
                cycle_entry["summary"] = summary[:200]  # Limitar
                break
        
        # Salvar
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

def main():
    """Função principal de demonstração"""
    print("=== SISTEMA DE CHECKPOINTS NEOcortex (R13) ===")
    print()
    
    # Inicializar sistema
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    checkpoint_system = CheckpointSystem(brain_dir)
    cycle_manager = CycleManager(checkpoint_system)
    
    # 1. Criar checkpoint para ciclo atual
    print("1. Criando checkpoint para ciclo atual...")
    checkpoint_id = checkpoint_system.create_cycle_checkpoint("CICLO_1")
    print(f"   Checkpoint criado: {checkpoint_id}")
    
    # 2. Listar checkpoints existentes
    print("\n2. Checkpoints existentes:")
    checkpoints = checkpoint_system.list_checkpoints()
    for cp in checkpoints[:5]:  # Mostrar apenas 5
        print(f"   • {cp['id']} - {cp['cycle']} - {cp['description']}")
    
    if len(checkpoints) > 5:
        print(f"   ... e mais {len(checkpoints) - 5} checkpoints")
    
    # 3. Verificar integridade
    if checkpoints:
        print(f"\n3. Verificando integridade do último checkpoint...")
        last_checkpoint = checkpoints[0]
        is_valid = checkpoint_system.verify_checkpoint_integrity(last_checkpoint["id"])
        print(f"   {last_checkpoint['id']}: {'[VALID] VÁLIDO' if is_valid else '[INVALID] CORROMPIDO'}")
    
    # 4. Criar milestone
    print("\n4. Criando milestone de auditoria...")
    milestone_id = cycle_manager.create_milestone(
        "Auditoria de Governança",
        "Conclusão da auditoria de governança e roadmaps"
    )
    print(f"   Milestone criada: {milestone_id}")
    
    # 5. Estatísticas
    print("\n5. Estatísticas do sistema:")
    total_checkpoints = len(list((brain_dir / "checkpoints").glob("*.json")))
    print(f"   Total de checkpoints: {total_checkpoints}")
    
    # 6. Instruções de uso
    print("\n" + "=" * 60)
    print("INSTRUÇÕES DE USO:")
    print("=" * 60)
    print("\nPara criar checkpoints manualmente:")
    print("  from checkpoint_system import CheckpointSystem")
    print("  system = CheckpointSystem(Path('.'))")
    print("  system.create_checkpoint('CICLO_1', 'regular', 'Descrição')")
    print("\nPara gerenciar ciclos:")
    print("  manager = CycleManager(system)")
    print("  manager.start_cycle('CICLO_2', 'Nova fase')")
    print("  manager.create_milestone('Nome', 'Descrição')")
    print("  manager.end_cycle('Resumo')")
    print("\nCheckpoints salvos em: brain/checkpoints/")
    print("=" * 60)

if __name__ == "__main__":
    main()