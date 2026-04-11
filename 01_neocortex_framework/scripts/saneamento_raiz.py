#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Saneamento da raiz do projeto TURBOQUANT_V42.

1. Cria Lobo LEGACY para documentar arquivos legados
2. Move arquivos utilitários para archive apropriado
3. Limpa raiz do projeto
"""

import json
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

# Adicionar neocortex_framework ao path
neocortex_path = Path(__file__).parent / "neocortex_framework"
sys.path.insert(0, str(neocortex_path))

from neocortex.core import (
    get_lobe_service,
    get_manifest_service,
    get_kg_service,
    get_checkpoint_service,
)


def create_legacy_lobe():
    """Cria Lobo LEGACY para documentar arquivos legados."""
    print("\n1. Criando Lobo LEGACY...")

    lobe_service = get_lobe_service()
    lobe_name = "NC-LBE-FR-LEGACY-001.mdc"

    # Verificar se já existe
    existing_lobe = lobe_service.get_lobe(lobe_name)
    if existing_lobe.get("exists"):
        print(f"   [SKIP] Lobe '{lobe_name}' já existe")
        return lobe_name

    # Conteúdo do Lobo LEGACY
    content = (
        """# NC-LBE-FR-LEGACY-001

Gestão de arquivos e diretórios legados no projeto TURBOQUANT_V42.

## Propósito
Documentar e gerenciar arquivos legados, utilitários de desenvolvimento, 
e estruturas antigas que não fazem parte do framework NeoCortex consolidado.

## Status
Ativo (arquivamento)

## Tags
#legacy, #archive, #cleanup, #framework

## Checkpoints
- CP-LEGACY-001: Criação inicial do Lobo LEGACY
- CP-LEGACY-002: Inventário de arquivos legados
- CP-LEGACY-003: Movimentação para archive
- CP-LEGACY-004: Limpeza da raiz

## Inventário de Arquivos Legados

### Arquivos na Raiz (pré-saneamento)
| Arquivo | Descrição | Status | Ação Recomendada |
|---------|-----------|--------|------------------|
| clean_security.py | Limpeza do módulo security.py | Obsoleto | Mover para archive |
| extract_all_tools.py | Extração de ferramentas MCP | Obsoleto | Mover para archive |
| extract_tools_final.py | Extração final de ferramentas | Obsoleto | Mover para archive |
| extract_tools_robust.py | Extração robusta de ferramentas | Obsoleto | Mover para archive |
| fix_indentation.py | Correção de indentação | Obsoleto | Mover para archive |
| update_phase3_progress.py | Atualização de progresso | Obsoleto | Mover para archive |
| update_ledger_status.py | Atualização de status do ledger | Obsoleto | Mover para archive |
| verify_mcp.py | Verificação de MCP | Obsoleto | Mover para archive |
| update_antigravity_confirmation.py | Confirmação Antigravity | Obsoleto | Mover para archive |
| add_root_sanitize_event.py | Evento de saneamento | Obsoleto | Mover para archive |

### Diretórios na Raiz (pré-saneamento)
| Diretório | Descrição | Status | Ação Recomendada |
|-----------|-----------|--------|------------------|
| .agents/ | Regras e workflows antigos | Legado | Manter (pode conter histórico) |
| backup_root/ | Backups antigos do projeto | Legado | Mover para archive do framework |
| white_label/ | Template de white label | Ativo | Manter como template |
| examples/ | Exemplos diversos | Ativo | Manter |
| .ruff_cache/ | Cache do ruff | Temporário | Excluir (pode ser recriado) |

### Arquivos em backup_root/
| Arquivo | Descrição | Ação |
|---------|-----------|------|
| CHEATSHEET.md | Cheatsheet do projeto | Mover para docs |
| Sem título.txt | Arquivo temporário | Excluir |
| install.ps1 / install.sh | Scripts de instalação | Mover para archive |
| Vários scripts .py | Utilitários de desenvolvimento | Mover para archive |

## Plano de Saneamento

### Fase 1: Documentação
- [x] Criar Lobo LEGACY
- [x] Inventariar arquivos e diretórios
- [x] Definir ações para cada item

### Fase 2: Movimentação
- [ ] Mover arquivos .py utilitários para DIR-ARC-FR-001-archive-main
- [ ] Mover conteúdo de backup_root para DIR-BAK-FR-001-backup-main
- [ ] Organizar white_label dentro da estrutura do framework
- [ ] Preservar .agents/ como histórico

### Fase 3: Limpeza
- [ ] Remover arquivos .py da raiz
- [ ] Remover backup_root/ vazio
- [ ] Limpar .ruff_cache/
- [ ] Verificar integridade após movimentação

### Fase 4: Validação
- [ ] Verificar se framework ainda funciona
- [ ] Atualizar referências se necessário
- [ ] Criar checkpoint final

## Notas Importantes

1. **Preservação de Histórico**: Arquivos legados são movidos, não excluídos
2. **Estrutura do Framework**: Usar diretórios existentes do NeoCortex:
   - DIR-ARC-FR-001-archive-main: Para arquivos utilitários obsoletos
   - DIR-BAK-FR-001-backup-main: Para backups antigos
   - DIR-DOC-FR-001-docs-main: Para documentação legada
3. **White Label**: O diretório white_label/ na raiz será mantido como template
4. **Exemplos**: O diretório examples/ será mantido para referência

## Log de Execução
- **Data do saneamento**: """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """
- **Executado por**: OpenCode (assistente)
- **Framework NeoCortex**: v4.2-cortex
- **Estado inicial**: """
        + str(len(list(Path(".").glob("*.py"))))
        + """ arquivos .py na raiz

## Referências
- NC-CTX-FR-001-cortex-central.mdc: Cortex central do framework
- NC-LBE-FR-ARCHITECTURE-001.mdc: Arquitetura do framework
- NC-LBE-FR-DEVELOPMENT-001.mdc: Guias de desenvolvimento

---
*Este Lobo será atualizado durante o processo de saneamento.*
"""
    )

    # Criar Lobo
    lobe_result = lobe_service.create_lobe(
        lobe_name=lobe_name,
        content=content,
        metadata={
            "module": "legacy",
            "category": "operations",
            "status": "active",
            "purpose": "legacy_management",
            "created_by": "opencode_sanitization",
        },
    )

    if lobe_result.get("success"):
        print(f"   [OK] Lobe '{lobe_name}' criado")

        # Gerar manifesto
        manifest_service = get_manifest_service()
        manifest_result = manifest_service.generate_manifest(target=lobe_name)
        if manifest_result.get("success"):
            print(f"   [OK] Manifesto gerado para '{lobe_name}'")
        else:
            print(
                f"   [WARN] Falha ao gerar manifesto: {manifest_result.get('error', 'Unknown')}"
            )
    else:
        print(f"   [ERROR] Falha ao criar lobe: {lobe_result.get('error', 'Unknown')}")

    return lobe_name


def inventory_root_files():
    """Faz inventário de arquivos na raiz."""
    print("\n2. Inventariando arquivos na raiz...")

    root = Path(".")
    files = []

    # Arquivos Python
    py_files = list(root.glob("*.py"))
    print(f"   Arquivos .py: {len(py_files)}")
    for f in py_files:
        size = f.stat().st_size
        files.append({"path": str(f), "type": "python", "size": size, "name": f.name})
        print(f"     - {f.name} ({size} bytes)")

    # Arquivos Markdown
    md_files = list(root.glob("*.md"))
    print(f"   Arquivos .md: {len(md_files)}")
    for f in md_files:
        size = f.stat().st_size
        files.append({"path": str(f), "type": "markdown", "size": size, "name": f.name})
        print(f"     - {f.name} ({size} bytes)")

    # Diretórios
    dirs = [d for d in root.iterdir() if d.is_dir()]
    print(f"   Diretórios: {len(dirs)}")
    for d in dirs:
        if d.name.startswith("."):
            print(f"     - {d.name}/ (oculto)")
        else:
            print(f"     - {d.name}/")

    return files, dirs


def move_utility_files():
    """Move arquivos utilitários para o archive do framework."""
    print("\n3. Movendo arquivos utilitários para archive...")

    # Caminhos
    archive_dir = Path("neocortex_framework/DIR-ARC-FR-001-archive-main")
    backup_dir = Path("neocortex_framework/DIR-BAK-FR-001-backup-main")
    docs_dir = Path("neocortex_framework/DIR-DOC-FR-001-docs-main")

    # Criar subdiretórios no archive
    util_dir = archive_dir / "development_utilities"
    util_dir.mkdir(parents=True, exist_ok=True)

    scripts_dir = archive_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    # Lista de arquivos para mover
    files_to_move = [
        ("clean_security.py", util_dir, "Security cleaning utility"),
        ("extract_all_tools.py", util_dir, "MCP tools extraction"),
        ("extract_tools_final.py", util_dir, "Final tools extraction"),
        ("extract_tools_robust.py", util_dir, "Robust tools extraction"),
        ("fix_indentation.py", util_dir, "Indentation fix utility"),
        ("update_phase3_progress.py", scripts_dir, "Phase 3 progress update"),
        ("update_ledger_status.py", scripts_dir, "Ledger status update"),
        ("verify_mcp.py", scripts_dir, "MCP verification"),
        ("update_antigravity_confirmation.py", scripts_dir, "Antigravity confirmation"),
    ]

    moved = []
    failed = []

    for filename, target_dir, description in files_to_move:
        source = Path(filename)
        if not source.exists():
            print(f"   [SKIP] {filename} não encontrado")
            continue

        target = target_dir / filename

        try:
            # Preservar metadados
            shutil.copy2(source, target)

            # Registrar no log
            moved.append(
                {
                    "file": filename,
                    "target": str(target),
                    "description": description,
                    "size": source.stat().st_size,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            print(f"   [OK] Movido: {filename} -> {target}")

            # Remover da raiz (opcional - comentado por segurança)
            # source.unlink()

        except Exception as e:
            failed.append({"file": filename, "error": str(e)})
            print(f"   [ERROR] Falha ao mover {filename}: {e}")

    # Mover arquivos de backup_root
    print("\n4. Processando backup_root...")
    backup_root = Path("backup_root")
    if backup_root.exists():
        # Mover CHEATSHEET.md para docs
        cheatsheet = backup_root / "CHEATSHEET.md"
        if cheatsheet.exists():
            target = docs_dir / "legacy" / "CHEATSHEET.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cheatsheet, target)
            print(f"   [OK] Movido: CHEATSHEET.md -> {target}")

        # Mover scripts .py
        for py_file in backup_root.glob("*.py"):
            target = scripts_dir / py_file.name
            shutil.copy2(py_file, target)
            moved.append(
                {
                    "file": str(py_file),
                    "target": str(target),
                    "description": "Backup utility script",
                    "size": py_file.stat().st_size,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            print(f"   [OK] Movido: {py_file.name} -> {target}")

    return moved, failed


def update_legacy_lobe(lobe_name, moved_files, failed_files):
    """Atualiza o Lobo LEGACY com resultados do saneamento."""
    print("\n5. Atualizando Lobo LEGACY...")

    lobe_service = get_lobe_service()
    lobe_info = lobe_service.get_lobe(lobe_name)

    if not lobe_info.get("exists"):
        print(f"   [ERROR] Lobe '{lobe_name}' não encontrado")
        return

    content = lobe_info["content"]

    # Adicionar seção de resultados
    results_section = f"""

## Resultados do Saneamento

### Arquivos Movidos ({len(moved_files)})
| Arquivo | Destino | Tamanho | Descrição |
|---------|---------|---------|-----------|
"""

    for item in moved_files:
        filename = item["file"]
        target = item["target"]
        size = item["size"]
        desc = item.get("description", "")
        results_section += f"| {filename} | `{target}` | {size} bytes | {desc} |\n"

    if failed_files:
        results_section += f"""

### Falhas ({len(failed_files)})
| Arquivo | Erro |
|---------|------|
"""
        for item in failed_files:
            filename = item["file"]
            error = item["error"]
            results_section += f"| {filename} | {error} |\n"

    results_section += f"""

### Estado Pós-Saneamento
- **Data conclusão**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Arquivos movidos**: {len(moved_files)}
- **Falhas**: {len(failed_files)}
- **Próximas ações**: Remoção segura dos arquivos da raiz após validação

### Checkpoints Concluídos
- [x] CP-LEGACY-001: Criação inicial do Lobo LEGACY
- [x] CP-LEGACY-002: Inventário de arquivos legados
- [x] CP-LEGACY-003: Movimentação para archive
- [ ] CP-LEGACY-004: Limpeza da raiz (pendente validação)
"""

    # Adicionar ao conteúdo
    updated_content = content + results_section

    # Atualizar lobe
    update_result = lobe_service.update_lobe(lobe_name, updated_content)
    if update_result.get("success"):
        print(f"   [OK] Lobe '{lobe_name}' atualizado com resultados")
    else:
        print(
            f"   [ERROR] Falha ao atualizar lobe: {update_result.get('error', 'Unknown')}"
        )


def create_checkpoint():
    """Cria checkpoint do saneamento."""
    print("\n6. Criando checkpoint...")

    checkpoint_service = get_checkpoint_service()

    import uuid

    checkpoint_id = f"CP-SANEAMENTO-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

    checkpoint_result = checkpoint_service.set_current_checkpoint(
        checkpoint_id=checkpoint_id,
        description="Saneamento da raiz do projeto: movimentação de arquivos legados para archive",
        lobe_id="NC-LBE-FR-LEGACY-001.mdc",
    )

    if checkpoint_result.get("success"):
        print(f"   [OK] Checkpoint criado: {checkpoint_id}")
    else:
        print(
            f"   [ERROR] Falha ao criar checkpoint: {checkpoint_result.get('error', 'Unknown')}"
        )


def main():
    """Função principal."""
    print("=== SANEAMENTO DA RAIZ DO PROJETO TURBOQUANT_V42 ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 1. Criar Lobo LEGACY
        lobe_name = create_legacy_lobe()

        # 2. Inventariar arquivos
        files, dirs = inventory_root_files()

        # 3. Mover arquivos utilitários
        moved, failed = move_utility_files()

        # 4. Atualizar Lobo LEGACY
        update_legacy_lobe(lobe_name, moved, failed)

        # 5. Criar checkpoint
        create_checkpoint()

        # Resumo
        print("\n" + "=" * 60)
        print("RESUMO DO SANEAMENTO")
        print("=" * 60)
        print(f"- Lobo LEGACY criado: {lobe_name}")
        print(f"- Arquivos inventariados: {len(files)}")
        print(f"- Arquivos movidos: {len(moved)}")
        print(f"- Falhas: {len(failed)}")
        print(f"- Diretórios processados: {len(dirs)}")

        if failed:
            print("\n⚠️  ATENÇÃO: Alguns arquivos falharam ao mover:")
            for f in failed:
                print(f"   - {f['file']}: {f['error']}")

        print("\nPróximos passos:")
        print("1. Verificar se os arquivos foram movidos corretamente")
        print("2. Remover arquivos da raiz após validação (opcional)")
        print("3. Revisar estrutura do archive")
        print("4. Atualizar referências se necessário")

    except Exception as e:
        print(f"\n[ERROR] Erro durante saneamento: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
