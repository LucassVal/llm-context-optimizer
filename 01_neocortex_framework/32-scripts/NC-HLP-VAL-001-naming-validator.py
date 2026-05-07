# @UBL @UBL @HLP-VAL | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
NC-HLP-VAL-001: Validador de Convenção de Nomenclatura NC-
---
"""

"""---
NC-HLP-VAL-001: Validador de Convenção de Nomenclatura NC-
---
"""

"""
NC-HLP-VAL-001: Validador de Convenção de Nomenclatura NC-

VALIDADOR OFICIAL para pre-commit hooks.
Rejeita arquivos que não seguem padrão NC- (exceto exceções).

USO:
1. Como pre-commit hook: valida automaticamente
2. Como auditoria manual: python NC-HLP-VAL-001-naming-validator.py --audit
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURAÇÕES OFICIAIS (da Resolução NC-POL-NAM-001)
# ============================================================================

# Arquivos CRÍTICOS isentos (não podem ser renomeados)
CRITICAL_FILES = {
    # Configurações essenciais
    ".pre-commit-config.yaml",
    "opencode.json",
    
    # Ferramentas de validação/correção
    "validate_yaml.py",
    "pre_commit_hook.py",
    "test_sanitization.py",
    "fix_tickets_yaml.py",
    
    # Este validador
    "NC-HLP-VAL-001-naming-validator.py",
}

# Exceções automáticas (padrões permitidos)
AUTO_EXCEPTIONS = [
    # Arquivos temporários de debug
    r"^C_Temp_.*\.py$",
    
    # Rascunhos/notas temporárias
    r"^scratchpad_.*\.md$",
    
    # Metadados gerados automaticamente
    r".*\.metadata\.json$",
    
    # Relatórios de naming (durante transição)
    r"^naming_.*\.json$",
    r"^naming_.*\.py$",
    
    # Arquivos de compliance/checkpoint
    r"^compliance_check_.*\.json$",
    r"^CP_.*\.json$",
    r"^HANDOFF_.*\.json$",
    
    # Logs do sistema
    r"^checkpoints_log\.json$",
    r"^handoffs_log\.json$",
    r"^monitoring_log\.json$",
    r"^ticket_fix_report\.json$",
    r"^master_decision\.json$",
    
    # Scripts de migração/naming (durante transição)
    r"^safe_naming_.*\.py$",
    r"^analyze_naming_.*\.py$",
    r"^apply_naming_.*\.py$",
    r"^fix_json_conflicts\.py$",
    r"^check_naming_hook\.py$",
    r"^final_validation\.py$",
    r"^test_system_after_rename\.py$",
    r"^safe_rename_markdown\.py$",
]

# Tipos oficiais (TIPO)
OFFICIAL_TYPES = {
    "SCR", "SVC", "CFG", "DOC", "RPT", "POL", "AUD", "TST", "PLN", "HLP",
    "CHK", "HOF", "CMP", "MCP", "EXM", "INT", "SET", "TKT", "PCL", "MTD",
    "BAT", "GEN", "FIL", "DS", "TODO", "FR", "SYS", "VAL", "BKP", "RNM"
}

# Siglas oficiais (SIGLA)
OFFICIAL_SIGLAS = {
    "ANL", "AUD", "MCP", "TST", "VAL", "NAM", "SYS", "CMP", "CHK", "HOF",
    "AUT", "MD", "TKT", "PCL", "INT", "SET", "ACT", "EXM", "BAT", "GEN",
    "FIN", "MON", "SUM", "LEG", "EXC", "REV", "GOV", "BKP", "RNM", "FR"
}

# ============================================================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================================================

def is_critical_file(filename):
    """Verifica se arquivo é crítico (isento)"""
    return filename in CRITICAL_FILES

def is_auto_exception(filename):
    """Verifica se arquivo se encaixa em exceção automática"""
    for pattern in AUTO_EXCEPTIONS:
        if re.match(pattern, filename):
            return True
    return False

def validate_nc_format(filename):
    """
    Valida formato NC- completo:
    NC-<TIPO>-<SIGLA>-<NUM>-<desc>.<ext>
    """
    # Padrão regex completo
    pattern = r'^NC-([A-Z]{3})-([A-Z]{3,4})-(\d{3,})-([a-z0-9-]+)\.([a-z]+)$'
    match = re.match(pattern, filename)
    
    if not match:
        return False, "Formato NC- inválido"
    
    tipo, sigla, num, desc, ext = match.groups()
    
    # Valida TIPO oficial
    if tipo not in OFFICIAL_TYPES:
        return False, f"TIPO '{tipo}' não é oficial"
    
    # Valida SIGLA oficial
    if sigla not in OFFICIAL_SIGLAS:
        return False, f"SIGLA '{sigla}' não é oficial"
    
    # Valida NUM (mínimo 3 dígitos)
    if len(num) < 3:
        return False, f"NUM '{num}' muito curto (mínimo 3 dígitos)"
    
    # Valida descrição (kebab-case)
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', desc):
        return False, f"Descrição '{desc}' não está em kebab-case"
    
    # Valida extensão
    valid_extensions = {"py", "md", "yaml", "yml", "json", "txt", "sh", "bat"}
    if ext not in valid_extensions:
        return False, f"Extensão '.{ext}' não suportada"
    
    return True, "OK"

def validate_file(filename, filepath=None):
    """
    Valida um arquivo individualmente.
    Retorna (is_valid, reason, category)
    """
    # Verifica se é arquivo crítico
    if is_critical_file(filename):
        return True, "Arquivo crítico (isento)", "CRITICAL"
    
    # Verifica exceções automáticas
    if is_auto_exception(filename):
        return True, "Exceção automática", "EXCEPTION"
    
    # Verifica se já tem NC-
    if filename.startswith("NC-"):
        is_valid, reason = validate_nc_format(filename)
        if is_valid:
            return True, "Formato NC- válido", "NC_COMPLIANT"
        else:
            return False, f"NC- mal formatado: {reason}", "NC_INVALID"
    
    # Arquivo sem NC- e sem exceção
    return False, "Não segue padrão NC-", "NON_COMPLIANT"

# ============================================================================
# AUDITORIA SSOT (SINGLE SOURCE OF TRUTH)
# ============================================================================

def load_ssot_registry():
    """Carrega ou cria registro SSOT de arquivos"""
    ssot_file = Path("NC-RPT-LEG-001-legacy-files.json")
    
    if ssot_file.exists():
        try:
            with open(ssot_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Cria estrutura inicial
    return {
        "metadata": {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "policy": "NC-POL-NAM-001"
        },
        "legacy_files": [],
        "audit_history": []
    }

def save_ssot_registry(registry):
    """Salva registro SSOT"""
    ssot_file = Path("NC-RPT-LEG-001-legacy-files.json")
    
    # Garante que metadata está atualizada
    registry["metadata"]["updated"] = datetime.now().isoformat()
    
    with open(ssot_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def audit_files():
    """Realiza auditoria completa de todos os arquivos"""
    print("🔍 AUDITORIA SSOT DE CONFORMIDADE NC-")
    print("=" * 80)
    
    registry = load_ssot_registry()
    current_dir = Path(".")
    
    # Encontra todos os arquivos
    all_files = []
    for ext in ["*.py", "*.md", "*.yaml", "*.yml", "*.json", "*.txt"]:
        all_files.extend(list(current_dir.rglob(ext)))
    
    print(f"Total de arquivos encontrados: {len(all_files)}")
    
    # Realiza auditoria
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(all_files),
        "by_category": {},
        "files": []
    }
    
    categories_count = {
        "CRITICAL": 0,
        "EXCEPTION": 0,
        "NC_COMPLIANT": 0,
        "NC_INVALID": 0,
        "NON_COMPLIANT": 0
    }
    
    for file_path in sorted(all_files, key=lambda x: x.name):
        filename = file_path.name
        is_valid, reason, category = validate_file(filename, file_path)
        
        # Contagem por categoria
        categories_count[category] = categories_count.get(category, 0) + 1
        
        # Resultado detalhado
        file_result = {
            "filename": filename,
            "path": str(file_path.relative_to(current_dir)),
            "is_valid": is_valid,
            "reason": reason,
            "category": category,
            "size_kb": file_path.stat().st_size / 1024
        }
        
        audit_results["files"].append(file_result)
        
        # Exibe resultado
        status = "✅" if is_valid else "❌"
        print(f"{status} {category:15} {filename}")
        if not is_valid and reason:
            print(f"   └─ {reason}")
    
    # Estatísticas
    audit_results["by_category"] = categories_count
    
    total_valid = (categories_count["CRITICAL"] + categories_count["EXCEPTION"] + 
                   categories_count["NC_COMPLIANT"])
    compliance_rate = (total_valid / len(all_files)) * 100 if all_files else 0
    
    audit_results["compliance_rate"] = f"{compliance_rate:.1f}%"
    
    print("\n" + "=" * 80)
    print("📊 ESTATÍSTICAS DA AUDITORIA")
    print("=" * 80)
    print(f"Total de arquivos: {len(all_files)}")
    print(f"✅ Conformes: {total_valid}")
    print(f"❌ Não conformes: {categories_count['NON_COMPLIANT'] + categories_count['NC_INVALID']}")
    print(f"📈 Taxa de conformidade: {compliance_rate:.1f}%")
    print()
    print("📁 Distribuição por categoria:")
    for category, count in categories_count.items():
        percentage = (count / len(all_files)) * 100 if all_files else 0
        print(f"  {category:15} {count:4} ({percentage:.1f}%)")
    
    # Atualiza registro SSOT
    registry["audit_history"].append(audit_results)
    
    # Mantém apenas últimos 10 audits
    if len(registry["audit_history"]) > 10:
        registry["audit_history"] = registry["audit_history"][-10:]
    
    save_ssot_registry(registry)
    
    # Salva relatório completo
    report_file = Path(f"NC-RPT-AUD-{datetime.now().strftime('%Y%m%d%H%M')}-compliance-report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    print(f"📋 Registro SSOT atualizado: NC-RPT-LEG-001-legacy-files.json")
    
    return audit_results

# ============================================================================
# PRE-COMMIT HOOK MODE
# ============================================================================

def pre_commit_mode():
    """
    Modo para pre-commit hook.
    Recebe lista de arquivos via stdin ou args.
    """
    # Obtém arquivos staged
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Lê da stdin (formato git)
        files = [line.strip() for line in sys.stdin if line.strip()]
    
    if not files:
        print("⚠️  Nenhum arquivo para validar")
        return 0
    
    print("🔍 VALIDAÇÃO NC- (pre-commit hook)")
    print("=" * 80)
    
    invalid_files = []
    
    for file_arg in files:
        # Extrai apenas o nome do arquivo do path
        filename = Path(file_arg).name
        
        is_valid, reason, category = validate_file(filename)
        
        if not is_valid:
            invalid_files.append((filename, reason))
            print(f"❌ {filename}")
            print(f"   └─ {reason}")
        else:
            print(f"✅ {filename} ({category})")
    
    print("=" * 80)
    
    if invalid_files:
        print(f"🚫 {len(invalid_files)} arquivo(s) não conforme(s):")
        for filename, reason in invalid_files:
            print(f"  • {filename}: {reason}")
        
        print("\n💡 CORREÇÃO:")
        print("1. Renomear para padrão NC-: NC-<TIPO>-<SIGLA>-<NUM>-desc.ext")
        print("2. Solicitar exceção via NC-TKT-EXC-001-exception-request.yaml")
        print("3. Verificar se é arquivo crítico (lista em NC-POL-NAM-001)")
        
        return 1  # Código de erro para pre-commit
    
    print("🎉 Todos os arquivos estão conformes com NC-!")
    return 0

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--audit":
        # Modo auditoria completa
        audit_files()
        return 0
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        # Ajuda
        print("NC-HLP-VAL-001: Validador de Convenção de Nomenclatura NC-")
        print("\nUso:")
        print("  python NC-HLP-VAL-001-naming-validator.py          # Modo pre-commit")
        print("  python NC-HLP-VAL-001-naming-validator.py --audit  # Auditoria completa")
        print("  python NC-HLP-VAL-001-naming-validator.py --help   # Esta ajuda")
        return 0
    else:
        # Modo pre-commit (default)
        return pre_commit_mode()

if __name__ == "__main__":
    sys.exit(main())
