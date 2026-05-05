#!/usr/bin/env python3
"""
Classifica tickets rfos em categorias: template, ativo, obsoleto.
"""

import yaml
import re
from pathlib import Path

TICKETS_DIR = Path("DIR-DS-001-tickets")
HANDOFFS_DIR = Path("DIR-DS-002-audit-logs")


def extract_ticket_id_from_filename(filename):
    match = re.match(r"(NC-DS-\d{2,3})", filename)
    return match.group(1) if match else None


def classify_ticket(filepath):
    """Classifica um ticket YAML em categorias."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # Verifica se  template/exemplo
            if "Ticket de Exemplo" in content or "Copie e adapte" in content:
                return "template"
            # Verifica se task est vazio ou placeholder
            if "task:" in content and "description:" in content:
                # Extrai a seo task via YAML
                data = yaml.safe_load(content)
                if data and "task" in data:
                    task = data["task"]
                    if isinstance(task, str) and task.strip() in ["", "TODO", "TBD"]:
                        return "placeholder"
                    if isinstance(task, dict) and "description" in task:
                        desc = task["description"]
                        if isinstance(desc, str) and desc.strip() in [
                            "",
                            "TODO",
                            "TBD",
                        ]:
                            return "placeholder"
                # Verifica se tem integrity_hash (indica ticket vlido)
                if data and "integrity_hash" in data:
                    return "ativo"
                else:
                    return "sem_hash"
            # Se no tem task, pode ser incompleto
            return "incompleto"
    except Exception as e:
        return f"erro: {e}"


def main():
    print("=== CLASSIFICAO DE TICKETS RFOS ===\n")

    # Carregar IDs de handoffs
    handoff_ids = set()
    for hf in HANDOFFS_DIR.glob("*.yaml"):
        try:
            with open(hf, "r", encoding="utf-8") as f:
                # Lidar com mltiplos documentos
                docs = list(yaml.safe_load_all(f))
                for doc in docs:
                    if doc and "ticket_id" in doc:
                        handoff_ids.add(doc["ticket_id"])
        except Exception as e:
            print(f"Erro ao ler {hf}: {e}")

    print(f"IDs de handoffs encontrados: {len(handoff_ids)}")

    # Processar tickets
    ticket_files = list(TICKETS_DIR.glob("*.yaml"))
    orphaned = []
    classified = {
        "template": 0,
        "ativo": 0,
        "placeholder": 0,
        "incompleto": 0,
        "sem_hash": 0,
        "erro": 0,
    }

    for tf in ticket_files:
        ticket_id = extract_ticket_id_from_filename(tf.name)
        if not ticket_id:
            continue
        if ticket_id in handoff_ids:
            continue  # Ignorar tickets com handoff

        category = classify_ticket(tf)
        classified[category] = classified.get(category, 0) + 1
        orphaned.append((ticket_id, tf.name, category))

    print(f"\nTotal de tickets rfos: {len(orphaned)}")
    print("\nDistribuio por categoria:")
    for cat, count in classified.items():
        if count > 0:
            print(f"  {cat}: {count}")

    print("\nDetalhamento por ticket:")
    for ticket_id, filename, category in sorted(orphaned):
        print(f"  {ticket_id} ({filename})  {category}")

    # Salvar relatrio
    report_path = Path("DIR-DS-002-audit-logs/ticket_classification_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Relatrio de Classificao: Tickets rfos\n\n")
        f.write(f"Total de tickets rfos: {len(orphaned)}\n\n")
        f.write("## Categorias\n\n")
        for cat, count in classified.items():
            if count > 0:
                f.write(f"- **{cat}**: {count}\n")
        f.write("\n## Lista Detalhada\n\n")
        f.write("| ID | Arquivo | Categoria |\n")
        f.write("|----|---------|-----------|\n")
        for ticket_id, filename, category in sorted(orphaned):
            f.write(f"| {ticket_id} | {filename} | {category} |\n")
        f.write("\n## Aes Recomendadas\n\n")
        f.write(
            "1. **Templates**: Manter como referncia, mas no considerar rotinas ativas.\n"
        )
        f.write(
            "2. **Placeholders/Incompletos**: Avaliar se devem ser descartados ou completados.\n"
        )
        f.write(
            "3. **Ativos**: So rotinas inertes que precisam de handoff ou fechamento.\n"
        )
        f.write("4. **Sem hash**: Verificar integridade e adicionar hash.\n")

    print(f"\nRelatrio salvo em: {report_path}")


if __name__ == "__main__":
    main()
