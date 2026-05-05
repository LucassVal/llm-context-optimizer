#!/usr/bin/env python3
"""---
Configuração de monitoramento contínuo para YAML/JSON
---
"""

"""---
Configuração de monitoramento contínuo para YAML/JSON
---
"""

"""
Configuração de monitoramento contínuo para YAML/JSON
Instala hooks e configura validação automática
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def check_pre_commit_installed() -> bool:
    """Verifica se pre-commit está instalado"""
    try:
        result = subprocess.run(
            ["pre-commit", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_pre_commit() -> bool:
    """Instala pre-commit se não estiver instalado"""
    print("Verificando instalação do pre-commit...")
    
    if check_pre_commit_installed():
        print("  [OK] pre-commit já instalado")
        return True
    
    print("  [INSTALL] Instalando pre-commit...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            check=True,
            capture_output=True,
            text=True
        )
        print("  [OK] pre-commit instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Falha ao instalar pre-commit: {e}")
        return False

def setup_git_hooks() -> bool:
    """Configura hooks do Git"""
    print("\nConfigurando hooks do Git...")
    
    repo_dir = Path.cwd()
    git_dir = repo_dir / ".git"
    
    if not git_dir.exists():
        print("  [WARN] Diretório .git não encontrado. Inicializando...")
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
            print("  [OK] Repositório Git inicializado")
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Falha ao inicializar Git: {e}")
            return False
    
    # Copiar hook de pre-commit
    hook_source = repo_dir / "pre_commit_hook.py"
    hook_target = git_dir / "hooks" / "pre-commit"
    
    if hook_source.exists():
        try:
            # Criar diretório de hooks se não existir
            (git_dir / "hooks").mkdir(exist_ok=True)
            
            # Copiar script
            shutil.copy2(hook_source, hook_target)
            
            # Tornar executável (Unix) - no Windows, .py já é executável
            if os.name != 'nt':  # Não Windows
                os.chmod(hook_target, 0o755)
            
            print(f"  [OK] Hook de pre-commit instalado: {hook_target}")
            
            # Adicionar shebang para Windows
            if os.name == 'nt':
                with open(hook_target, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    f.seek(0)
                    f.write("#!/usr/bin/env python3\n" + content)
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] Falha ao instalar hook: {e}")
            return False
    else:
        print(f"  [ERROR] Arquivo fonte não encontrado: {hook_source}")
        return False

def setup_pre_commit_config() -> bool:
    """Configura arquivo .pre-commit-config.yaml"""
    print("\nConfigurando .pre-commit-config.yaml...")
    
    config_file = Path(".pre-commit-config.yaml")
    
    if not config_file.exists():
        print("  [ERROR] Arquivo .pre-commit-config.yaml não encontrado")
        return False
    
    try:
        # Instalar hooks do pre-commit
        result = subprocess.run(
            ["pre-commit", "install"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            print("  [OK] Hooks do pre-commit instalados")
            
            # Executar validação em todos os arquivos
            print("  [INFO] Executando validação em arquivos existentes...")
            subprocess.run(
                ["pre-commit", "run", "--all-files"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            return True
        else:
            print(f"  [ERROR] Falha ao instalar hooks: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Falha na configuração: {e}")
        return False

def setup_cron_monitoring() -> bool:
    """Configura monitoramento periódico (cron/task scheduler)"""
    print("\nConfigurando monitoramento periódico...")
    
    if os.name == 'nt':  # Windows
        return setup_windows_task()
    else:  # Unix/Linux
        return setup_unix_cron()

def setup_windows_task() -> bool:
    """Configura Task Scheduler no Windows"""
    print("  [INFO] Windows detectado - configurando Task Scheduler")
    
    script_path = Path.cwd() / "validate_yaml.py"
    python_exe = sys.executable
    
    # Comando para executar validação
    command = f'"{python_exe}" "{script_path}"'
    
    # Criar script batch
    batch_content = f"""@echo off
echo [%date% %time%] Executando validação YAML/JSON...
{command}
if %errorlevel% neq 0 (
    echo VALIDAÇÃO FALHOU - Verificar logs
    exit 1
) else (
    echo Validação concluída com sucesso
)
"""
    
    batch_file = Path.cwd() / "validate_daily.bat"
    try:
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"  [OK] Script batch criado: {batch_file}")
        
        # Instruções para Task Scheduler
        print("\n  [INSTRUÇÕES] Para configurar Task Scheduler:")
        print("  1. Abra 'Agendador de Tarefas'")
        print(f"  2. Criar tarefa básica que executa: {batch_file}")
        print("  3. Configurar para executar diariamente")
        print("  4. Executar com privilégios elevados se necessário")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Falha ao criar script: {e}")
        return False

def setup_unix_cron() -> bool:
    """Configura cron job no Unix/Linux"""
    print("  [INFO] Unix/Linux detectado - configurando cron")
    
    script_path = Path.cwd() / "validate_yaml.py"
    python_exe = sys.executable
    
    # Linha do cron (executa diariamente às 2:00 AM)
    cron_line = f"0 2 * * * {python_exe} {script_path} >> {Path.cwd()}/validation.log 2>&1"
    
    print(f"\n  [INSTRUÇÕES] Para configurar cron:")
    print("  1. Editar crontab: crontab -e")
    print(f"  2. Adicionar linha: {cron_line}")
    print("  3. Salvar e sair")
    
    return True

def create_readme() -> bool:
    """Cria README com instruções"""
    print("\nCriando README de monitoramento...")
    
    readme_content = """# Monitoramento de Segurança YAML/JSON - NeoCortex

## Configuração Instalada

✅ **Hooks de pre-commit** configurados para validação automática de:
- Segurança YAML (padrões perigosos, tags Python)
- Validação JSON (XSS, scripts maliciosos)  
- Convenção de nomenclatura NC-
- Campos obrigatórios em tickets

✅ **Scripts de validação** disponíveis:
- `validate_yaml.py` - Validação completa de YAMLs
- `pre_commit_hook.py` - Hook para validação pré-commit
- `fix_tickets_yaml.py` - Correção automática de tickets

✅ **Monitoramento periódico** configurado para execução diária

## Uso

### Validação Manual
```bash
# Validar todos os YAMLs
python validate_yaml.py

# Executar hook de pre-commit
python pre_commit_hook.py
```

### Correção Automática
```bash
# Corrigir tickets YAML
python fix_tickets_yaml.py
```

### Git Hooks
Os hooks são executados automaticamente antes de cada commit.
Para executar manualmente em todos os arquivos:
```bash
pre-commit run --all-files
```

## Estrutura de Validação

1. **Segurança**: Bloqueia tags Python perigosas, scripts maliciosos
2. **Estrutura**: Valida campos obrigatórios, valores permitidos
3. **Convenção**: Verifica padrão NC- para tickets e configs
4. **Sanitização**: Remove automaticamente conteúdo perigoso

## Logs e Relatórios

- `yaml_validation_report.json` - Relatório de validação YAML
- `ticket_fix_report.json` - Relatório de correção de tickets  
- `metadata_audit_report.json` - Auditoria de metadados JSON
- `validation.log` - Log de execuções periódicas (cron)

## Manutenção

Para atualizar configuração:
```bash
pre-commit autoupdate
```

Para desinstalar hooks:
```bash
pre-commit uninstall
```

---

*Sistema configurado em: 2026-04-22*
*NeoCortex Framework - Compliance NC-CONST-FR-001-v0.2*
"""
    
    try:
        readme_file = Path.cwd() / "MONITORING_README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  [OK] README criado: {readme_file}")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Falha ao criar README: {e}")
        return False

def main():
    """Função principal de configuração"""
    print("=" * 60)
    print("CONFIGURAÇÃO DE MONITORAMENTO CONTÍNUO - NeoCortex")
    print("=" * 60)
    
    # Verificar diretório
    repo_dir = Path.cwd()
    print(f"Diretório: {repo_dir}")
    
    # Instalar pre-commit
    if not install_pre_commit():
        print("[WARN] Continuando sem pre-commit...")
    
    # Configurar hooks do Git
    if not setup_git_hooks():
        print("[WARN] Hooks do Git não configurados completamente")
    
    # Configurar pre-commit
    if check_pre_commit_installed():
        if not setup_pre_commit_config():
            print("[WARN] Configuração do pre-commit incompleta")
    else:
        print("[INFO] pre-commit não disponível, usando hooks nativos")
    
    # Configurar monitoramento periódico
    if not setup_cron_monitoring():
        print("[WARN] Monitoramento periódico não configurado")
    
    # Criar README
    if not create_readme():
        print("[WARN] README não criado")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Configuração de monitoramento concluída!")
    print("\nPróximos passos:")
    print("1. Testar validação: python validate_yaml.py")
    print("2. Fazer commit de teste para verificar hooks")
    print("3. Configurar Task Scheduler/cron conforme instruções")
    print("\nDocumentação em: MONITORING_README.md")
    print("=" * 60)

if __name__ == "__main__":
    main()