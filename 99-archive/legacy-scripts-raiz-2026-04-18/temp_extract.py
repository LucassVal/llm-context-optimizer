import re
from pathlib import Path

report_path = Path(
    "01_neocortex_framework/DIR-DOC-FR-001-docs-main/structural_audit_report.md"
)
content = report_path.read_text(encoding="utf-8")

# Padro para capturar caminhos entre crases
pattern = r"`(neocortex\\.+?)`"
matches = re.findall(pattern, content)

# Remover duplicatas
unique_matches = sorted(set(matches))

print(f"Total de arquivos extrados: {len(unique_matches)}")
for path in unique_matches:
    print(path)

# Salvar lista em arquivo
output_path = Path("01_neocortex_framework/DIR-DOC-FR-001-docs-main/legacy_files.txt")
output_path.write_text("\n".join(unique_matches), encoding="utf-8")
print(f"\nLista salva em: {output_path}")
