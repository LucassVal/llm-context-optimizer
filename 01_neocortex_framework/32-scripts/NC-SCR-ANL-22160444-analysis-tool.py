# @UBL @UBL @SCR-ANL | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
Análise da estrutura de lobes do NeoCortex
---
"""

"""---
Análise da estrutura de lobes do NeoCortex
---
"""

"""
Análise da estrutura de lobes do NeoCortex
Verificar organização em categorias main e subs
"""

from pathlib import Path
import json

def analyze_lobe_structure():
    """Analisar estrutura de lobes"""
    framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
    
    print("=" * 70)
    print("ANÁLISE DA ESTRUTURA DE LOBES NEOcORTEX")
    print("=" * 70)
    
    # Procurar arquivos .mdc em todo o framework
    mdc_files = []
    for pattern in ["**/*.mdc", "**/*.MDC"]:
        mdc_files.extend(framework_path.glob(pattern))
    
    print(f"\nTotal de arquivos .mdc encontrados: {len(mdc_files)}")
    
    # Classificar por tipo
    lobe_files = []
    cortex_files = []
    other_files = []
    
    for file in mdc_files:
        name = file.name
        if name.startswith("NC-LBE-"):
            lobe_files.append(file)
        elif name.startswith("NC-CTX-") or "cortex" in name.lower():
            cortex_files.append(file)
        else:
            other_files.append(file)
    
    print(f"\nLOBE FILES (NC-LBE-*): {len(lobe_files)}")
    print(f"CORTEX FILES (NC-CTX-*): {len(cortex_files)}")
    print(f"OUTROS FILES: {len(other_files)}")
    
    # Analisar estrutura de lobes
    print("\n" + "=" * 70)
    print("ESTRUTURA DE LOBES ENCONTRADOS:")
    print("=" * 70)
    
    lobe_categories = {}
    for lobe_file in lobe_files:
        name = lobe_file.name
        # Extrair categoria do nome
        parts = name.split('-')
        if len(parts) >= 4:
            category = parts[3]  # NC-LBE-FR-CATEGORIA-001.mdc
        else:
            category = "UNKNOWN"
        
        if category not in lobe_categories:
            lobe_categories[category] = []
        lobe_categories[category].append({
            'name': name,
            'path': str(lobe_file.relative_to(framework_path)),
            'size': lobe_file.stat().st_size
        })
    
    # Mostrar categorias
    print("\nCATEGORIAS DE LOBES:")
    for category, files in sorted(lobe_categories.items()):
        print(f"\n  [{category}] - {len(files)} arquivos:")
        for file_info in files:
            print(f"    • {file_info['name']} ({file_info['size']} bytes)")
            print(f"      Path: {file_info['path']}")
    
    # Verificar organização em diretórios
    print("\n" + "=" * 70)
    print("ORGANIZAÇÃO EM DIRETÓRIOS:")
    print("=" * 70)
    
    dir_structure = {}
    for lobe_file in lobe_files:
        parent_dir = lobe_file.parent.name
        if parent_dir not in dir_structure:
            dir_structure[parent_dir] = []
        dir_structure[parent_dir].append(lobe_file.name)
    
    print("\nDistribuição por diretório:")
    for directory, files in sorted(dir_structure.items()):
        print(f"\n  {directory}/ - {len(files)} lobes:")
        for file in sorted(files)[:5]:  # Mostrar apenas 5 por diretório
            print(f"    • {file}")
        if len(files) > 5:
            print(f"    ... e mais {len(files)-5} arquivos")
    
    # Verificar se há estrutura main/subs
    print("\n" + "=" * 70)
    print("ANÁLISE DE ESTRUTURA MAIN/SUBS:")
    print("=" * 70)
    
    main_lobes = []
    sub_lobes = []
    
    for lobe_file in lobe_files:
        name = lobe_file.name.lower()
        if any(keyword in name for keyword in ['main', 'core', 'central', 'principal']):
            main_lobes.append(lobe_file)
        elif any(keyword in name for keyword in ['sub', 'child', 'secondary', 'auxiliary']):
            sub_lobes.append(lobe_file)
    
    print(f"\nLOBE MAIN/CORE: {len(main_lobes)}")
    for lobe in main_lobes[:10]:  # Limitar a 10
        print(f"  • {lobe.name}")
    
    print(f"\nLOBE SUB/SECONDARY: {len(sub_lobes)}")
    for lobe in sub_lobes[:10]:  # Limitar a 10
        print(f"  • {lobe.name}")
    
    # Recomendações
    print("\n" + "=" * 70)
    print("RECOMENDAÇÕES:")
    print("=" * 70)
    
    issues = []
    
    # 1. Verificar se lobes estão em backup/archive
    backup_dirs = ['backup', 'archive', 'migration', 'old', 'legacy']
    lobes_in_backup = []
    for lobe_file in lobe_files:
        path_str = str(lobe_file).lower()
        if any(backup_dir in path_str for backup_dir in backup_dirs):
            lobes_in_backup.append(lobe_file)
    
    if lobes_in_backup:
        issues.append(f"⚠️  {len(lobes_in_backup)} lobes encontrados em diretórios de backup/archive")
    
    # 2. Verificar duplicatas
    lobe_names = [f.name for f in lobe_files]
    duplicates = set([name for name in lobe_names if lobe_names.count(name) > 1])
    if duplicates:
        issues.append(f"⚠️  {len(duplicates)} nomes de lobe duplicados")
    
    # 3. Verificar estrutura organizada
    if len(dir_structure) > 5:
        issues.append(f"⚠️  Lobes distribuídos em {len(dir_structure)} diretórios diferentes (pode estar desorganizado)")
    
    if issues:
        print("\nPROBLEMAS IDENTIFICADOS:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Estrutura de lobes parece organizada")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_lobe_structure()
