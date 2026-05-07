# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
NC-SCR-FR-149: Atualizar Registry de Lobes
---
"""

"""---
NC-SCR-FR-149: Atualizar Registry de Lobes
---
"""

"""
NC-SCR-FR-149: Atualizar Registry de Lobes
Atualiza NC-NAM-FR-001b-lobes-registry.md com as novas localizações
"""

import os
import re
from pathlib import Path

def update_registry():
    """Atualiza o registry com as novas localizações"""
    framework_root = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
    registry_path = framework_root / "DIR-DOC-FR-001-docs-main" / "NC-NAM-FR-001b-lobes-registry.md"
    lobes_dir = framework_root / "02_memory_lobes"
    
    # Ler o registry atual
    with open(registry_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar todos os arquivos .mdc na nova estrutura
    mdc_files = list(lobes_dir.rglob("*.mdc"))
    
    # Criar mapeamento de nome para caminho relativo
    lobe_map = {}
    for mdc_file in mdc_files:
        if mdc_file.name.startswith("NC-LBE-"):
            rel_path = mdc_file.relative_to(framework_root)
            lobe_map[mdc_file.name] = str(rel_path).replace("\\", "/")
    
    print(f"Encontrados {len(lobe_map)} arquivos NC-LBE-*.mdc na nova estrutura")
    
    # Atualizar cada entrada no registry
    lines = content.split('\n')
    updated_lines = []
    updated_count = 0
    
    for line in lines:
        # Verificar se é uma linha da tabela com um arquivo .mdc
        if 'NC-LBE-' in line and '.mdc' in line and '|' in line:
            # Extrair o nome do arquivo
            match = re.search(r'NC-LBE-[^|]+\.mdc', line)
            if match:
                filename = match.group(0)
                if filename in lobe_map:
                    # Substituir o caminho antigo pelo novo
                    old_path_pattern = r'\\[^|]+\\NC-LBE-[^|]+\.mdc'
                    new_path = f"\\{lobe_map[filename]}"
                    line = re.sub(old_path_pattern, new_path, line)
                    updated_count += 1
                    print(f"  [ATUALIZADO] {filename} -> {lobe_map[filename]}")
        
        updated_lines.append(line)
    
    # Escrever o registry atualizado
    updated_content = '\n'.join(updated_lines)
    
    # Adicionar nota de atualização no changelog
    if updated_count > 0:
        if '## Changelog' in updated_content:
            changelog_section = updated_content.find('## Changelog')
            before_changelog = updated_content[:changelog_section]
            after_changelog = updated_content[changelog_section:]
            
            # Adicionar nova entrada no changelog
            new_entry = f"- [2026-04-21T00:00:00] Registry atualizado por T0 Antigravity. {updated_count} lobes migrados para nova estrutura 02_memory_lobes/.\n"
            updated_content = before_changelog + new_entry + after_changelog
    
    # Salvar backup do arquivo original
    backup_path = registry_path.with_suffix('.md.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Escrever o arquivo atualizado
    with open(registry_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n[RESUMO]")
    print(f"  Registry original salvo em: {backup_path}")
    print(f"  Entradas atualizadas: {updated_count}")
    print(f"  Registry atualizado: {registry_path}")
    
    return updated_count

def main():
    print("NC-SCR-FR-149: Atualizar Registry de Lobes")
    print("=" * 60)
    
    try:
        updated = update_registry()
        if updated > 0:
            print(f"\n[SUCESSO] Registry atualizado com {updated} entradas!")
        else:
            print("\n[AVISO] Nenhuma entrada foi atualizada.")
    except Exception as e:
        print(f"\n[ERRO] durante a atualização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
