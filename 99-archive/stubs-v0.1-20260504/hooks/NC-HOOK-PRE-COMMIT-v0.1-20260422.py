#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""---
NC-HOOK-PRE-COMMIT-v0.1-20260422.py
---
"""

"""---
NC-HOOK-PRE-COMMIT-v0.1-20260422.py
---
"""

"""
NC-HOOK-PRE-COMMIT-v0.1-20260422.py
Hook de Pré-Commit para Validação Automática

Validações executadas antes de cada commit:
1. Validação de YAML/JSON
2. Convenção de nomenclatura NC-
3. Estrutura de diretórios
4. Regras de governança básicas
5. Segurança básica

Uso:
    # Instalar como hook do Git
    cp NC-HOOK-PRE-COMMIT-v0.1-20260422.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    
    # Executar manualmente
    python NC-HOOK-PRE-COMMIT-v0.1-20260422.py --check-all
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

class PreCommitValidator:
    """Validador de Pré-Commit para NeoCortex."""
    
    def __init__(self, repo_root: Path = Path.cwd()):
        self.repo_root = repo_root
        self.errors = []
        self.warnings = []
        
    def run_validation(self, staged_files: Optional[List[str]] = None) -> bool:
        """Executa todas as validações."""
        logger.info("Iniciando validação de pré-commit...")
        
        if staged_files is None:
            staged_files = self._get_staged_files()
        
        if not staged_files:
            logger.info("Nenhum arquivo staged para commit.")
            return True
        
        logger.info(f"Validando {len(staged_files)} arquivo(s)...")
        
        # Executar validações
        self._validate_yaml_json(staged_files)
        self._validate_naming_convention(staged_files)
        self._validate_directory_structure(staged_files)
        self._validate_basic_security(staged_files)
        self._validate_governance_rules(staged_files)
        
        # Reportar resultados
        self._report_results()
        
        return len(self.errors) == 0
    
    def _get_staged_files(self) -> List[str]:
        """Obtém lista de arquivos staged para commit."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=self.repo_root
            )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                return files
            else:
                logger.warning(f"Erro ao obter arquivos staged: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Exceção ao obter arquivos staged: {e}")
            return []
    
    def _validate_yaml_json(self, files: List[str]) -> None:
        """Valida sintaxe de arquivos YAML e JSON."""
        logger.info("Validando YAML/JSON...")
        
        for file_path in files:
            path = self.repo_root / file_path
            
            if not path.exists():
                continue
            
            # Validação YAML
            if path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        yaml.safe_load(content)
                except yaml.YAMLError as e:
                    self.errors.append(f"YAML inválido em {file_path}: {e}")
                except Exception as e:
                    self.warnings.append(f"Erro ao ler YAML {file_path}: {e}")
            
            # Validação JSON
            elif path.suffix.lower() == '.json':
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    self.errors.append(f"JSON inválido em {file_path}: {e}")
                except Exception as e:
                    self.warnings.append(f"Erro ao ler JSON {file_path}: {e}")
    
    def _validate_naming_convention(self, files: List[str]) -> None:
        """Valida convenção de nomenclatura NC-."""
        logger.info("Validando convenção de nomenclatura...")
        
        nc_pattern = re.compile(r'^NC-[A-Z]+-[A-Z]+-\d{3}-.+\.\w+$')
        exempt_dirs = ['node_modules', '.git', '.claude', '.kilocode']
        
        for file_path in files:
            path = self.repo_root / file_path
            
            # Pular diretórios isentos
            if any(exempt in str(path) for exempt in exempt_dirs):
                continue
            
            filename = path.name
            
            # Verificar se é arquivo de framework NeoCortex
            is_framework_file = (
                '01_neocortex_framework' in str(path) or
                'DIR-DS-' in str(path) or
                'DIR-ARC-' in str(path) or
                'DIR-DOC-' in str(path)
            )
            
            if is_framework_file and not nc_pattern.match(filename):
                # Verificar exceções
                is_exception = (
                    filename.startswith('package.json') or
                    filename.startswith('README') or
                    filename.startswith('.gitignore') or
                    filename in ['opencode.json', 'antigravity_neocortex_config.json']
                )
                
                if not is_exception:
                    self.warnings.append(
                        f"Arquivo de framework sem convenção NC-: {file_path}\n"
                        f"  Esperado: NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext\n"
                        f"  Encontrado: {filename}"
                    )
    
    def _validate_directory_structure(self, files: List[str]) -> None:
        """Valida estrutura de diretórios canônica."""
        logger.info("Validando estrutura de diretórios...")
        
        canonical_structure = {
            '01_neocortex_framework': [
                'DIR-CORE-FR-001-core-central',
                'DIR-DOC-FR-001-docs-main',
                'DIR-TMP-FR-001-templates-main',
                'DIR-DS-001-tickets',
                'DIR-DS-002-audit-logs',
                'DIR-ARC-FR-001-archive-main',
                'neocortex',
                'scripts',
                'automation',
                'dashboard',
                'hooks'
            ]
        }
        
        for file_path in files:
            path = self.repo_root / file_path
            
            # Verificar se está em diretório conhecido
            parts = path.parts
            if len(parts) >= 2 and parts[0] == '01_neocortex_framework':
                parent_dir = parts[1] if len(parts) > 1 else ''
                
                if parent_dir and parent_dir not in canonical_structure['01_neocortex_framework']:
                    # Verificar se é subdiretório válido
                    is_valid_subdir = any(
                        parent_dir.startswith(valid_prefix)
                        for valid_prefix in ['DIR-', 'neocortex', 'scripts']
                    )
                    
                    if not is_valid_subdir:
                        self.warnings.append(
                            f"Diretório não canônico: {parent_dir} em {file_path}\n"
                            f"  Diretórios esperados: {', '.join(canonical_structure['01_neocortex_framework'])}"
                        )
    
    def _validate_basic_security(self, files: List[str]) -> None:
        """Validações básicas de segurança."""
        logger.info("Validando segurança básica...")
        
        sensitive_patterns = [
            (r'(?i)password\s*[:=]\s*["\']', "Senha em texto claro"),
            (r'(?i)api[_-]?key\s*[:=]\s*["\']', "API key em texto claro"),
            (r'(?i)secret\s*[:=]\s*["\']', "Secret em texto claro"),
            (r'(?i)token\s*[:=]\s*["\']', "Token em texto claro"),
            (r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----', "Chave privada"),
        ]
        
        exempt_files = [
            '.env.example',
            '.env.template',
            'example.config.yaml',
            'template.config.yaml'
        ]
        
        for file_path in files:
            path = self.repo_root / file_path
            
            if not path.exists() or not path.is_file():
                continue
            
            # Pular arquivos isentos
            if any(path.name == exempt for exempt in exempt_files):
                continue
            
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern, description in sensitive_patterns:
                        if re.search(pattern, content):
                            self.errors.append(
                                f"Possível vazamento de segurança em {file_path}: {description}"
                            )
                            break
                            
            except Exception as e:
                self.warnings.append(f"Erro ao verificar segurança de {file_path}: {e}")
    
    def _validate_governance_rules(self, files: List[str]) -> None:
        """Valida regras básicas de governança."""
        logger.info("Validando regras de governança...")
        
        for file_path in files:
            path = self.repo_root / file_path
            
            if not path.exists():
                continue
            
            # R04: Nomenclatura Padronizada (já validado)
            # R08: Atomic Locks - verificar se arquivos críticos estão protegidos
            critical_files = [
                'NC-CONST-FR-001-',
                'NC-GOV-FR-003-',
                'NC-SEC-FR-001-',
                'NC-CFG-FR-001-'
            ]
            
            if any(critical in path.name for critical in critical_files):
                # Verificar se há locks atômicos definidos
                locks_file = self.repo_root / '01_neocortex_framework' / 'DIR-DOC-FR-001-docs-main' / 'NC-SEC-FR-001-atomic-locks.yaml'
                if locks_file.exists():
                    try:
                        with open(locks_file, 'r', encoding='utf-8') as f:
                            locks_content = f.read()
                            if path.name not in locks_content:
                                self.warnings.append(
                                    f"Arquivo crítico sem lock atômico definido: {file_path}\n"
                                    f"  Adicione em: {locks_file.name}"
                                )
                    except Exception:
                        pass
    
    def _report_results(self) -> None:
        """Reporta resultados da validação."""
        print("\n" + "="*60)
        print("RELATÓRIO DE VALIDAÇÃO DE PRÉ-COMMIT")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERROS ENCONTRADOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  AVISOS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ Todas as validações passaram!")
        
        print("\n" + "="*60)
        
        # Salvar relatório em arquivo
        report_file = self.repo_root / 'pre-commit-validation-report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Relatório de Validação de Pré-Commit\n")
            f.write(f"Data: {datetime.now().isoformat()}\n")
            f.write("="*60 + "\n")
            
            if self.errors:
                f.write(f"\nERROS ({len(self.errors)}):\n")
                for error in self.errors:
                    f.write(f"• {error}\n")
            
            if self.warnings:
                f.write(f"\nAVISOS ({len(self.warnings)}):\n")
                for warning in self.warnings:
                    f.write(f"• {warning}\n")
            
            if not self.errors and not self.warnings:
                f.write("\n✅ Todas as validações passaram!\n")
        
        logger.info(f"Relatório salvo em: {report_file}")
    
    def check_all_files(self) -> bool:
        """Valida todos os arquivos do repositório (não apenas staged)."""
        logger.info("Validando todos os arquivos do repositório...")
        
        all_files = []
        exempt_dirs = ['.git', '.claude', '.kilocode', 'node_modules', '__pycache__']
        
        for root, dirs, files in os.walk(self.repo_root):
            # Pular diretórios isentos
            dirs[:] = [d for d in dirs if d not in exempt_dirs and not d.startswith('.')]
            
            # Verificar se diretório atual deve ser pulado
            if any(exempt in root for exempt in exempt_dirs):
                continue
            
            for file in files:
                # Pular arquivos grandes ou binários
                if file.endswith(('.pyc', '.so', '.dll', '.exe', '.bin')):
                    continue
                
                rel_path = os.path.relpath(os.path.join(root, file), self.repo_root)
                all_files.append(rel_path)
                
                # Limitar para teste
                if len(all_files) > 1000:
                    logger.warning(f"Limitando validação a 1000 arquivos (total: {len(all_files)})")
                    break
            
            if len(all_files) > 1000:
                break
        
        logger.info(f"Validando {len(all_files)} arquivo(s)...")
        return self.run_validation(all_files)

def install_git_hook() -> bool:
    """Instala o hook no diretório .git/hooks."""
    hook_source = Path(__file__).resolve()
    hooks_dir = Path.cwd() / '.git' / 'hooks'
    
    if not hooks_dir.exists():
        logger.error(f"Diretório de hooks não encontrado: {hooks_dir}")
        return False
    
    hook_dest = hooks_dir / 'pre-commit'
    
    try:
        # Copiar script
        with open(hook_source, 'r', encoding='utf-8') as src:
            content = src.read()
        
        # Adicionar shebang e tornar executável
        hook_content = f"#!/usr/bin/env python3\n{content}"
        
        with open(hook_dest, 'w', encoding='utf-8', newline='\n') as dst:
            dst.write(hook_content)
        
        # Tornar executável
        if sys.platform != "win32":
            import stat
            hook_dest.chmod(hook_dest.stat().st_mode | stat.S_IEXEC)
        
        logger.info(f"Hook instalado em: {hook_dest}")
        logger.info("O hook será executado automaticamente antes de cada commit.")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao instalar hook: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Hook de Pré-Commit NeoCortex")
    parser.add_argument("--check-all", action="store_true", help="Validar todos os arquivos")
    parser.add_argument("--install", action="store_true", help="Instalar como hook do Git")
    parser.add_argument("--repo-root", type=str, default=".", help="Raiz do repositório")
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.install:
        success = install_git_hook()
        sys.exit(0 if success else 1)
    
    validator = PreCommitValidator(Path(args.repo_root))
    
    if args.check_all:
        success = validator.check_all_files()
    else:
        success = validator.run_validation()
    
    # Retornar código de saída apropriado
    if not success:
        print("\n❌ Commit bloqueado devido a erros de validação.")
        print("Corrija os erros acima antes de commitar.")
        sys.exit(1)
    else:
        print("\n✅ Validação concluída com sucesso.")
        sys.exit(0)

if __name__ == "__main__":
    from datetime import datetime
    main()