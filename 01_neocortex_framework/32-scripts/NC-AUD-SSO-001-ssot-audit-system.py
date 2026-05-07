# @UBL @UBL @AUD-SSO | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
NC-AUD-SSO-001: Sistema de Auditoria SSOT para Arquivos Renomeados
---
"""

"""---
NC-AUD-SSO-001: Sistema de Auditoria SSOT para Arquivos Renomeados
---
"""

"""
NC-AUD-SSO-001: Sistema de Auditoria SSOT para Arquivos Renomeados

SISTEMA COMPLETO de Single Source of Truth para:
1. Auditoria de arquivos renomeados durante migração NC-
2. Rastreabilidade de mudanças
3. Validação de integridade
4. Relatórios de conformidade

SSOT = Single Source of Truth (Fonte Única da Verdade)
"""

import os
import re
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil

# ============================================================================
# CONFIGURAÇÃO DO SISTEMA SSOT
# ============================================================================

class SSOTDatabase:
    """Banco de dados SQLite para SSOT"""
    
    def __init__(self, db_path: str = "nc_ssot.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Inicializa estrutura do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de arquivos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            current_name TEXT NOT NULL,
            original_name TEXT,
            file_hash TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            category TEXT NOT NULL,
            compliance_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(filename)
        )
        ''')
        
        # Tabela de histórico de renomeações
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rename_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            old_name TEXT NOT NULL,
            new_name TEXT NOT NULL,
            rename_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            performed_by TEXT DEFAULT 'system',
            FOREIGN KEY (file_id) REFERENCES files (id)
        )
        ''')
        
        # Tabela de auditorias
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_files INTEGER NOT NULL,
            compliant_files INTEGER NOT NULL,
            non_compliant_files INTEGER NOT NULL,
            compliance_rate REAL NOT NULL,
            report_path TEXT
        )
        ''')
        
        # Tabela de exceções
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            exception_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            granted_by TEXT,
            granted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_file(self, file_info: Dict) -> int:
        """Adiciona ou atualiza arquivo no SSOT"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verifica se já existe
        cursor.execute(
            "SELECT id FROM files WHERE filename = ?",
            (file_info["filename"],)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Atualiza
            cursor.execute('''
            UPDATE files SET
                current_name = ?,
                file_hash = ?,
                file_size = ?,
                file_type = ?,
                category = ?,
                compliance_status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE filename = ?
            ''', (
                file_info.get("current_name", file_info["filename"]),
                file_info["file_hash"],
                file_info["file_size"],
                file_info["file_type"],
                file_info["category"],
                file_info["compliance_status"],
                file_info["filename"]
            ))
            file_id = existing[0]
        else:
            # Insere novo
            cursor.execute('''
            INSERT INTO files (
                filename, current_name, original_name, file_hash,
                file_size, file_type, category, compliance_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_info["filename"],
                file_info.get("current_name", file_info["filename"]),
                file_info.get("original_name"),
                file_info["file_hash"],
                file_info["file_size"],
                file_info["file_type"],
                file_info["category"],
                file_info["compliance_status"]
            ))
            file_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return file_id
    
    def record_rename(self, file_id: int, old_name: str, new_name: str, reason: str = ""):
        """Registra histórico de renomeação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO rename_history (file_id, old_name, new_name, reason)
        VALUES (?, ?, ?, ?)
        ''', (file_id, old_name, new_name, reason))
        
        conn.commit()
        conn.close()
    
    def get_file_history(self, filename: str) -> List[Dict]:
        """Obtém histórico completo de um arquivo"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT f.*, rh.old_name, rh.new_name, rh.rename_date, rh.reason
        FROM files f
        LEFT JOIN rename_history rh ON f.id = rh.file_id
        WHERE f.filename = ? OR f.original_name = ?
        ORDER BY rh.rename_date DESC
        ''', (filename, filename))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_compliance_stats(self) -> Dict:
        """Obtém estatísticas de conformidade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN compliance_status = 'COMPLIANT' THEN 1 ELSE 0 END) as compliant,
            SUM(CASE WHEN compliance_status = 'NON_COMPLIANT' THEN 1 ELSE 0 END) as non_compliant,
            SUM(CASE WHEN compliance_status = 'EXCEPTION' THEN 1 ELSE 0 END) as exceptions,
            SUM(CASE WHEN compliance_status = 'CRITICAL' THEN 1 ELSE 0 END) as critical
        FROM files
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            total, compliant, non_compliant, exceptions, critical = row
            compliance_rate = (compliant / total * 100) if total > 0 else 0
            
            return {
                "total_files": total,
                "compliant_files": compliant,
                "non_compliant_files": non_compliant,
                "exception_files": exceptions,
                "critical_files": critical,
                "compliance_rate": f"{compliance_rate:.1f}%"
            }
        
        return {}

# ============================================================================
# AUDITORIA SSOT
# ============================================================================

class SSOTAuditor:
    """Auditor SSOT para verificação de integridade"""
    
    def __init__(self):
        self.db = SSOTDatabase()
        self.backup_dir = Path("ssot_audit_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calcula hash SHA256 do arquivo"""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def analyze_file(self, filepath: Path) -> Dict:
        """Analisa arquivo para registro no SSOT"""
        from NC-HLP-VAL-001-naming-validator import validate_file
        
        filename = filepath.name
        is_valid, reason, category = validate_file(filename, filepath)
        
        # Determina status de conformidade
        if category == "CRITICAL":
            compliance_status = "CRITICAL"
        elif category == "EXCEPTION":
            compliance_status = "EXCEPTION"
        elif category == "NC_COMPLIANT":
            compliance_status = "COMPLIANT"
        else:
            compliance_status = "NON_COMPLIANT"
        
        # Calcula hash
        file_hash = self.calculate_file_hash(filepath)
        
        return {
            "filename": filename,
            "filepath": str(filepath),
            "file_hash": file_hash,
            "file_size": filepath.stat().st_size,
            "file_type": filepath.suffix[1:] if filepath.suffix else "unknown",
            "category": category,
            "compliance_status": compliance_status,
            "validation_reason": reason,
            "is_valid": is_valid,
            "last_modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        }
    
    def perform_full_audit(self) -> Dict:
        """Realiza auditoria completa do sistema"""
        print("🔍 AUDITORIA SSOT COMPLETA")
        print("=" * 80)
        
        current_dir = Path(".")
        all_files = []
        
        # Coleta todos os arquivos relevantes
        for ext in ["*.py", "*.md", "*.yaml", "*.yml", "*.json"]:
            all_files.extend(list(current_dir.rglob(ext)))
        
        print(f"Arquivos encontrados: {len(all_files)}")
        
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(all_files),
            "files_analyzed": [],
            "summary": {},
            "issues": []
        }
        
        # Analisa cada arquivo
        for filepath in sorted(all_files, key=lambda x: x.name):
            print(f"Analisando: {filepath.name}")
            
            file_info = self.analyze_file(filepath)
            audit_results["files_analyzed"].append(file_info)
            
            # Registra no SSOT
            file_id = self.db.add_file(file_info)
            
            # Verifica problemas
            if not file_info["is_valid"] and file_info["compliance_status"] == "NON_COMPLIANT":
                audit_results["issues"].append({
                    "filename": file_info["filename"],
                    "issue": file_info["validation_reason"],
                    "severity": "MEDIUM"
                })
        
        # Gera estatísticas
        stats = self.db.get_compliance_stats()
        audit_results["summary"] = stats
        
        # Salva relatório
        self.save_audit_report(audit_results)
        
        # Exibe resultados
        self.display_audit_results(audit_results)
        
        return audit_results
    
    def save_audit_report(self, audit_results: Dict):
        """Salva relatório de auditoria"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"NC-RPT-AUD-{timestamp}-ssot-audit.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo: {report_file}")
        
        # Também salva no banco de dados
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO audits (total_files, compliant_files, non_compliant_files, compliance_rate, report_path)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            audit_results["summary"].get("total_files", 0),
            audit_results["summary"].get("compliant_files", 0),
            audit_results["summary"].get("non_compliant_files", 0),
            float(audit_results["summary"].get("compliance_rate", "0%").rstrip('%')),
            str(report_file)
        ))
        
        conn.commit()
        conn.close()
    
    def display_audit_results(self, audit_results: Dict):
        """Exibe resultados da auditoria"""
        print("\n" + "=" * 80)
        print("📊 RESULTADOS DA AUDITORIA SSOT")
        print("=" * 80)
        
        summary = audit_results["summary"]
        
        print(f"📁 Total de arquivos: {summary.get('total_files', 0)}")
        print(f"✅ Conformes (NC-): {summary.get('compliant_files', 0)}")
        print(f"🚫 Não conformes: {summary.get('non_compliant_files', 0)}")
        print(f"⚠️  Exceções: {summary.get('exception_files', 0)}")
        print(f"🔧 Críticos: {summary.get('critical_files', 0)}")
        print(f"📈 Taxa de conformidade: {summary.get('compliance_rate', '0%')}")
        
        if audit_results["issues"]:
            print(f"\n🚨 PROBLEMAS ENCONTRADOS ({len(audit_results['issues'])}):")
            for issue in audit_results["issues"]:
                print(f"  • {issue['filename']}: {issue['issue']}")
        
        # Distribuição por tipo
        print(f"\n📋 DISTRIBUIÇÃO POR TIPO:")
        file_types = {}
        for file_info in audit_results["files_analyzed"]:
            file_type = file_info["file_type"]
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        for file_type, count in sorted(file_types.items()):
            percentage = (count / len(audit_results["files_analyzed"])) * 100
            print(f"  {file_type:10} {count:4} ({percentage:.1f}%)")
    
    def verify_integrity(self) -> List[Dict]:
        """Verifica integridade dos arquivos vs SSOT"""
        print("🔍 VERIFICAÇÃO DE INTEGRIDADE SSOT")
        print("=" * 80)
        
        issues = []
        
        # Obtém todos os arquivos do SSOT
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM files")
        db_files = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for db_file in db_files:
            filename = db_file["filename"]
            filepath = Path(db_file.get("current_name", filename))
            
            if not filepath.exists():
                issues.append({
                    "filename": filename,
                    "issue": "Arquivo não encontrado no sistema",
                    "severity": "HIGH"
                })
                continue
            
            # Verifica hash
            current_hash = self.calculate_file_hash(filepath)
            if current_hash != db_file["file_hash"]:
                issues.append({
                    "filename": filename,
                    "issue": f"Hash modificado (era: {db_file['file_hash'][:8]}..., agora: {current_hash[:8]}...)",
                    "severity": "MEDIUM"
                })
        
        if issues:
            print(f"🚨 {len(issues)} problema(s) de integridade encontrado(s):")
            for issue in issues:
                print(f"  • {issue['filename']}: {issue['issue']}")
        else:
            print("✅ Todos os arquivos estão íntegros!")
        
        return issues
    
    def generate_migration_report(self) -> Dict:
        """Gera relatório de migração NC-"""
        print("📊 RELATÓRIO DE MIGRAÇÃO NC-")
        print("=" * 80)
        
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Arquivos renomeados
        cursor.execute('''
        SELECT COUNT(DISTINCT file_id) as total_renamed,
               MIN(rename_date) as first_rename,
               MAX(rename_date) as last_rename
        FROM rename_history
        ''')
        rename_stats = dict(cursor.fetchone())
        
        # Distribuição temporal
        cursor.execute('''
        SELECT DATE(rename_date) as rename_day,
               COUNT(*) as count
        FROM rename_history
        GROUP BY DATE(rename_date)
        ORDER BY rename_day
        ''')
        daily_renames = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "migration_summary": {
                "total_files_renamed": rename_stats.get("total_renamed", 0),
                "migration_period": {
                    "start": rename_stats.get("first_rename"),
                    "end": rename_stats.get("last_rename")
                },
                "daily_progress": daily_renames
            },
            "current_status": self.db.get_compliance_stats(),
            "recommendations": self.generate_recommendations()
        }
        
        # Salva relatório
        report_file = Path(f"NC-RPT-MIG-{datetime.now().strftime('%Y%m%d_%H%M%S')}-migration-report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório de migração salvo: {report_file}")
        
        # Exibe resumo
        print(f"\n📈 RESUMO DA MIGRAÇÃO:")
        print(f"  Arquivos renomeados: {rename_stats.get('total_renamed', 0)}")
        if daily_renames:
            print(f"  Período: {daily_renames[0]['rename_day']} a {daily_renames[-1]['rename_day']}")
            print(f"  Dias com atividade: {len(daily_renames)}")
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas no estado atual"""
        stats = self.db.get_compliance_stats()
        recommendations = []
        
        total = stats.get("total_files", 0)
        non_compliant = stats.get("non_compliant_files", 0)
        
        if non_compliant > 0:
            compliance_rate = (stats.get("compliant_files", 0) / total * 100) if total > 0 else 0
            
            if compliance_rate < 80:
                recommendations.append("Priorizar renomeação de arquivos não conformes críticos")
            elif compliance_rate < 90:
                recommendations.append("Estabelecer plano para atingir 90% de conformidade")
            else:
                recommendations.append("Manter conformidade acima de 90% com auditorias regulares")
        
        if stats.get("exception_files", 0) > 10:
            recommendations.append("Revisar exceções automáticas - algumas podem ser convertidas para NC-")
        
        return recommendations

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NC-AUD-SSO-001: Sistema de Auditoria SSOT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --audit           # Auditoria completa
  %(prog)s --integrity       # Verificação de integridade
  %(prog)s --migration-report # Relatório de migração
  %(prog)s --stats           # Estatísticas atuais
        """
    )
    
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Realiza auditoria completa do sistema"
    )
    
    parser.add_argument(
        "--integrity",
        action="store_true",
        help="Verifica integridade dos arquivos vs SSOT"
    )
    
    parser.add_argument(
        "--migration-report",
        action="store_true",
        help="Gera relatório de migração NC-"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Exibe estatísticas atuais de conformidade"
    )
    
    parser.add_argument(
        "--history",
        metavar="FILENAME",
        help="Mostra histórico de um arquivo específico"
    )
    
    args = parser.parse_args()
    
    auditor = SSOTAuditor()
    
    if args.audit:
        auditor.perform_full_audit()
    elif args.integrity:
        auditor.verify_integrity()
    elif args.migration_report:
        auditor.generate_migration_report()
    elif args.history:
        db = SSOTDatabase()
        history = db.get_file_history(args.history)
        if history:
            print(f"\n📜 HISTÓRICO DE {args.history}:")
            for record in history:
                print(f"\n  Nome atual: {record.get('current_name')}")
                print(f"  Hash: {record.get('file_hash', '')[:16]}...")
                print(f"  Status: {record.get('compliance_status')}")
                if record.get('old_name'):
                    print(f"  Renomeado de: {record.get('old_name')} em {record.get('rename_date')}")
        else:
            print(f"Arquivo '{args.history}' não encontrado no SSOT")
    elif args.stats:
        db = SSOTDatabase()
        stats = db.get_compliance_stats()
        print("\n📊 ESTATÍSTICAS ATUAIS DO SSOT:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        # Modo padrão: auditoria completa
        print("NC-AUD-SSO-001: Sistema de Auditoria SSOT")
        print("Use --help para ver opções disponíveis")

if __name__ == "__main__":
    main()
