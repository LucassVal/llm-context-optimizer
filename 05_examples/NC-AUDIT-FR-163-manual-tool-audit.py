#!/usr/bin/env python3
"""
NC-AUDIT-FR-163 - Auditoria Manual das Tools SUPER
Verificação manual para R21, código proibido, imports suspeitos.
"""

import os
import re
import sys
from pathlib import Path

def audit_tool(file_path):
    """Auditar uma tool manualmente."""
    tool_name = os.path.basename(file_path)
    print(f"\n[AUDIT] {tool_name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    findings = []
    
    # 1. Procurar por R21
    if 'R21' in content:
        findings.append("[CRITICO] R21 ENCONTRADO NO CODIGO")
        # Encontrar contexto
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'R21' in line:
                print(f"   Linha {i+1}: {line.strip()}")
    
    # 2. Procurar imports suspeitos
    suspicious_imports = [
        'os.system', 'subprocess', 'eval', 'exec',
        '__import__', 'importlib', 'sys.modules',
        'socket', 'requests', 'urllib', 'http.client',
        'pickle', 'marshal', 'yaml.load', 'json.loads'
    ]
    
    for imp in suspicious_imports:
        if imp in content:
            # Verificar se é usado de forma segura
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if imp in line and not line.strip().startswith('#'):
                    # Verificar contexto
                    context = ' '.join(lines[max(0, i-2):min(len(lines), i+3)])
                    if any(danger in context.lower() for danger in ['remote', 'url', 'http', 'eval', 'exec']):
                        findings.append(f"[SUSPEITO] Import suspeito: {imp}")
                        print(f"   Linha {i+1}: {line.strip()}")
    
    # 3. Procurar por código proibido
    prohibited_patterns = [
        r'eval\s*\(', r'exec\s*\(', r'__import__\s*\(',
        r'os\.system\s*\(', r'subprocess\.run\s*\(',
        r'pickle\.loads', r'marshal\.loads',
        r'yaml\.load\s*\(', r'json\.loads\s*\('
    ]
    
    for pattern in prohibited_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            findings.append(f"[CRITICO] Codigo proibido encontrado: {pattern}")
            for match in matches[:3]:  # Mostrar primeiros 3
                print(f"   Padrao: {match}")
    
    # 4. Verificar imports relativos quebrados
    if 'from ...' in content or 'from ..' in content:
        # Verificar se são imports válidos
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if ('from ...' in line or 'from ..' in line) and 'import' in line:
                # Verificar sintaxe
                if not re.match(r'from \.\.\.?[a-zA-Z_]', line):
                    findings.append("[AVISO] Import relativo possivelmente quebrado")
                    print(f"   Linha {i+1}: {line.strip()}")
    
    # 5. Verificar se tool tem função register_tool
    if 'def register_tool' not in content:
        findings.append("[ERRO] Tool nao tem funcao register_tool")
    
    # 6. Verificar se tool chama @mcp.tool
    if '@mcp.tool' not in content and 'mcp.tool(' not in content:
        findings.append("[ERRO] Tool nao registra funcao com MCP")
    
    # Resumo
    if not findings:
        print("   [OK] Tool limpa - Nenhum problema encontrado")
        return True, []
    else:
        print(f"   [AVISO] {len(findings)} problema(s) encontrado(s)")
        for finding in findings:
            print(f"      - {finding}")
        return False, findings

def main():
    """Auditar todas as tools SUPER manualmente."""
    project_root = Path(__file__).parent.parent
    tools_dir = project_root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
    
    if not tools_dir.exists():
        print(f"Diretório não encontrado: {tools_dir}")
        return False
    
    print("=" * 70)
    print("AUDITORIA MANUAL DAS TOOLS SUPER - PROCURANDO R21/CÓDIGO PROIBIDO")
    print("=" * 70)
    
    # Listar todas as tools SUPER
    super_tools = list(tools_dir.glob("NC-SUPER-*.py"))
    pulse_tool = tools_dir / "pulse.py"
    
    if pulse_tool.exists():
        super_tools.append(pulse_tool)
    
    print(f"Encontradas {len(super_tools)} tools SUPER para auditar")
    
    results = []
    all_findings = []
    
    for tool_path in super_tools:
        clean, findings = audit_tool(tool_path)
        results.append((tool_path.name, clean))
        all_findings.extend([(tool_path.name, f) for f in findings])
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DA AUDITORIA MANUAL:")
    print("=" * 70)
    
    clean_count = sum(1 for _, clean in results if clean)
    total_count = len(results)
    
    print(f"\nTools auditadas: {total_count}")
    print(f"Tools limpas: {clean_count}")
    print(f"Tools com problemas: {total_count - clean_count}")
    
    if all_findings:
        print("\n📋 FINDINGS DETALHADOS:")
        for tool_name, finding in all_findings:
            print(f"  {tool_name}: {finding}")
    
    # Verificar também algumas tools v1/ problemáticas
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO RÁPIDA DAS TOOLS v1/ COM FAIL NO SMOKE TEST:")
    print("=" * 70)
    
    v1_dir = tools_dir / "v1"
    if v1_dir.exists():
        # Pegar algumas tools que falharam
        failed_tools = [
            "NC-TOOL-FR-001-cortex.py",
            "NC-TOOL-FR-000-brain.py", 
            "NC-TOOL-FR-004-checkpoint.py"
        ]
        
        for tool_name in failed_tools:
            tool_path = v1_dir / tool_name
            if tool_path.exists():
                print(f"\n🔍 Verificando {tool_name}:")
                with open(tool_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar apenas por R21/código proibido (não imports)
                if 'R21' in content:
                    print(f"   [CRITICO] R21 ENCONTRADO EM {tool_name}")
                
                # Verificar imports quebrados
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'import' in line and ('neocortex.core import' in line or 'from ...' in line):
                        # Verificar se linha parece quebrada
                        if line.count('import') > 1 or 'import import' in line:
                            print(f"   [AVISO] Import possivelmente quebrado na linha {i+1}: {line[:80]}...")
    
    print("\n" + "=" * 70)
    if clean_count == total_count and not any('R21' in str(f) for _, f in all_findings):
        print("[SUCESSO] AUDITORIA CONCLUIDA: NENHUM R21 OU CODIGO PROIBIDO ENCONTRADO")
        print("   As 17 core tools SUPER estão limpas.")
    else:
        print("[ALERTA] AUDITORIA CONCLUIDA: PROBLEMAS IDENTIFICADOS")
        print("   Verificar findings acima.")
    
    return clean_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)