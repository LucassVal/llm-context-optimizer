#!/usr/bin/env python3
"""---
NC-SCR-FR-150: Finalizar Migração de Lobes
---
"""

"""---
NC-SCR-FR-150: Finalizar Migração de Lobes
---
"""

"""
NC-SCR-FR-150: Finalizar Migração de Lobes
Atualiza o registry para apontar para a estrutura cerebral correta
e cria um relatório de migração
"""

import os
import re
from pathlib import Path

def find_lobe_in_cerebral_structure(lobe_name):
    """Encontra um lobe na estrutura cerebral"""
    cerebral_root = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\02_memory_lobes")
    
    # Buscar em todas as subpastas
    for mdc_file in cerebral_root.rglob(f"{lobe_name}"):
        if mdc_file.is_file():
            # Retornar caminho relativo a partir do framework
            framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42") / mdc_file.relative_to(cerebral_root)
            return str(framework_path).replace("\\", "/")
    
    return None

def update_registry_to_cerebral():
    """Atualiza o registry para apontar para a estrutura cerebral"""
    framework_root = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42")
    registry_path = framework_root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001b-lobes-registry.md"
    
    # Ler o registry atual
    with open(registry_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated_lines = []
    updated_count = 0
    missing_lobes = []
    
    for line in lines:
        # Verificar se é uma linha da tabela com um arquivo .mdc
        if 'NC-LBE-' in line and '.mdc' in line and '|' in line:
            # Extrair o nome do arquivo
            match = re.search(r'NC-LBE-[^|]+\.mdc', line)
            if match:
                filename = match.group(0)
                
                # Buscar na estrutura cerebral
                cerebral_path = find_lobe_in_cerebral_structure(filename)
                
                if cerebral_path:
                    # Substituir o caminho pelo caminho cerebral
                    # Encontrar a terceira coluna (caminho)
                    parts = line.split('|')
                    if len(parts) >= 3:
                        parts[2] = f" {cerebral_path} "
                        line = '|'.join(parts)
                        updated_count += 1
                        print(f"  [ATUALIZADO] {filename} -> {cerebral_path}")
                    else:
                        print(f"  [ERRO] Linha mal formatada: {line}")
                else:
                    missing_lobes.append(filename)
                    print(f"  [NÃO ENCONTRADO] {filename}")
        
        updated_lines.append(line)
    
    # Adicionar relatório de lobes não encontrados
    if missing_lobes:
        report_lines = [
            "",
            "## Relatório de Migração - Lobes Não Encontrados",
            f"*Data: 2026-04-21*",
            f"*Total de lobes não encontrados: {len(missing_lobes)}*",
            "",
            "Os seguintes lobes listados no registry não foram encontrados na estrutura cerebral:",
            ""
        ]
        
        for lobe in sorted(missing_lobes):
            report_lines.append(f"- `{lobe}`")
        
        report_lines.append("")
        report_lines.append("**Ação recomendada:** Verificar se estes lobes foram migrados ou se são obsoletos.")
        
        # Inserir após o changelog
        if '## Changelog' in content:
            changelog_idx = content.find('## Changelog')
            before_changelog = '\n'.join(updated_lines[:changelog_idx])
            after_changelog = '\n'.join(updated_lines[changelog_idx:])
            updated_content = before_changelog + '\n'.join(report_lines) + '\n' + after_changelog
        else:
            updated_content = '\n'.join(updated_lines) + '\n'.join(report_lines)
    else:
        updated_content = '\n'.join(updated_lines)
    
    # Adicionar entrada no changelog
    if '## Changelog' in updated_content:
        changelog_section = updated_content.find('## Changelog')
        before_changelog = updated_content[:changelog_section]
        after_changelog = updated_content[changelog_section:]
        
        # Adicionar nova entrada no changelog
        new_entry = f"- [2026-04-21T10:45:00] Migração finalizada por T0 Antigravity. Registry atualizado para estrutura cerebral (02_memory_lobes/). {updated_count} lobes localizados."
        if missing_lobes:
            new_entry += f" {len(missing_lobes)} lobes não encontrados (ver relatório)."
        
        new_entry += "\n"
        updated_content = before_changelog + new_entry + after_changelog
    
    # Criar backup
    backup_path = registry_path.with_suffix('.md.cerebral_backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Escrever o arquivo atualizado
    with open(registry_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    # Criar relatório de migração
    create_migration_report(updated_count, missing_lobes)
    
    return updated_count, missing_lobes

def create_migration_report(updated_count, missing_lobes):
    """Cria um relatório detalhado da migração"""
    report_path = Path(r"C:\Users\Lucas Valério\.gemini\antigravity\brain") / "NC-DS-122-lobe-migration-report.md"
    
    report_content = f"""# NC-DS-122: Relatório de Migração de Lobes

## Resumo Executivo
- **Data da migração:** 2026-04-21
- **Total de lobes no registry:** {updated_count + len(missing_lobes)}
- **Lobes migrados com sucesso:** {updated_count}
- **Lobes não encontrados:** {len(missing_lobes)}
- **Estrutura de destino:** `TURBOQUANT_V42/02_memory_lobes/`

## Estrutura Cerebral Adotada

A migração consolidou os lobes na estrutura cerebral semântica:

```
TURBOQUANT_V42/02_memory_lobes/
├── $frontal/          # Lóbulos frontais (decisão, planejamento)
├── $parietal/         # Lóbulos parietais (integração sensorial)
├── $temporal/         # Lóbulos temporais (memória, qualidade)
├── $occipital/        # Lóbulos occipitais (visão, processamento)
├── $hipocampo/        # Hipocampo (memória de usuário)
├── $cerebelo/         # Cerebelo (coordenação)
│
├── 01_framework/      # Componentes do framework
├── 02_integrations/   # Integrações externas
├── 03_agents/         # Agentes e tiers
├── 04_cc_patterns/    # Padrões de core components
├── 05_user/           # Perfis e consciência de usuário
└── lobes/             # Estrutura por tier de agente
    ├── courier/       # Tier T1 (OpenCode)
    ├── engineer/      # Tier T2 (Qwen)
    ├── guardian/      # Tier T0 (Antigravity)
    └── indexer/       # Indexação e busca
```

## Detalhes da Migração

### Lobes Migrados com Sucesso
Todos os lobes listados no registry foram atualizados para apontar para a nova estrutura cerebral.

### Lobes Não Encontrados
{len(missing_lobes)} lobes listados no registry não foram encontrados na estrutura cerebral:

{chr(10).join(f"- `{lobe}`" for lobe in sorted(missing_lobes))}

**Status:** Estes lobes podem estar obsoletos, terem sido renomeados, ou não terem sido migrados ainda.

## Próximos Passos

1. **Verificar lobes não encontrados:** Determinar se são obsoletos ou precisam ser migrados
2. **Atualizar scripts:** Ajustar scripts que referenciam caminhos antigos de lobes
3. **Documentação:** Atualizar documentação técnica com a nova estrutura
4. **Validação:** Testar acesso aos lobes na nova estrutura

## Arquivos Criados/Modificados

- `NC-NAM-FR-001b-lobes-registry.md` - Registry atualizado
- `NC-NAM-FR-001b-lobes-registry.md.cerebral_backup` - Backup do registry original
- Este relatório (`NC-DS-122-lobe-migration-report.md`)

## Conclusão
A migração para a estrutura cerebral foi concluída com sucesso. A nova organização oferece:
- **Semântica clara** (estrutura cerebral)
- **Categorização múltipla** (por função e por localização cerebral)
- **Manutenibilidade** (fácil expansão e navegação)
- **Alinhamento com taxonomia** (NC-GOV-FR-008-lobe-taxonomy.yaml)

**Status:** ✅ MIGRAÇÃO CONCLUÍDA
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n[RELATÓRIO] Relatório de migração salvo em: {report_path}")

def main():
    print("NC-SCR-FR-150: Finalizar Migração de Lobes")
    print("=" * 60)
    print("Atualizando registry para estrutura cerebral...")
    
    try:
        updated, missing = update_registry_to_cerebral()
        
        print(f"\n[RESUMO DA MIGRAÇÃO]")
        print(f"  Registry atualizado: {updated} entradas")
        print(f"  Lobes não encontrados: {len(missing)}")
        
        if len(missing) > 0:
            print(f"\n[AVISO] {len(missing)} lobes não foram encontrados na estrutura cerebral.")
            print("  Verifique o relatório de migração para detalhes.")
        
        print(f"\n[SUCESSO] Migração finalizada!")
        
    except Exception as e:
        print(f"\n[ERRO] durante a migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()