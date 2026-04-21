#!/usr/bin/env python3
"""
Script para aplicar frontmatter em arquivos Markdown, Python e JSON
no Core (neocortex) e Lobos (memory_lobes) conforme NC-DS-047-GLOBAL-SANE-001.
"""

import os
import re
import json
import sys
from pathlib import Path

# Configuraes
BASE_DIR = Path(__file__).parent
CORE_DIR = BASE_DIR / "01_neocortex_framework" / "neocortex"
LOBES_DIR = BASE_DIR / "02_memory_lobes"

# Mapeamento de caminho para domain/layer/type
PATH_MAPPINGS = [
    (r".*mcp/tools/.*\.py$", {"domain": "orchestration", "layer": "core", "type": "tool"}),
    (r".*core/services/.*\.py$", {"domain": "core", "layer": "core", "type": "service"}),
    (r".*core/config/.*\.py$", {"domain": "configuration", "layer": "core", "type": "config"}),
    (r".*core/hooks/.*\.py$", {"domain": "hooks", "layer": "core", "type": "hook"}),
    (r".*core/utils/.*\.py$", {"domain": "utils", "layer": "core", "type": "utility"}),
    (r".*core/.*\.py$", {"domain": "core", "layer": "core", "type": "service"}),
    (r".*infra/.*\.py$", {"domain": "infrastructure", "layer": "infra", "type": "service"}),
    (r".*repositories/.*\.py$", {"domain": "persistence", "layer": "infra", "type": "repository"}),
    (r".*schemas/.*\.py$", {"domain": "schemas", "layer": "core", "type": "schema"}),
    (r".*schemas/.*\.json$", {"domain": "schemas", "layer": "core", "type": "schema"}),
    (r".*cli/.*\.py$", {"domain": "cli", "layer": "core", "type": "cli"}),
    (r".*agent/.*\.py$", {"domain": "agent", "layer": "core", "type": "service"}),
    (r".*mcp/.*\.py$", {"domain": "orchestration", "layer": "core", "type": "service"}),
    (r".*\.mdc$", {"domain": "integration", "layer": "lobe", "type": "documentation"}),
]

# Tags baseadas em palavras-chave no nome do arquivo
KEYWORDS = {
    "tool": ["tool"],
    "service": ["service", "svc"],
    "config": ["config", "cfg"],
    "hook": ["hook", "hk"],
    "schema": ["schema"],
    "ledger": ["ledger"],
    "task": ["task"],
    "agent": ["agent"],
    "orchestration": ["orchestration"],
    "security": ["security", "sec"],
    "health": ["health"],
    "metrics": ["metrics"],
    "cache": ["cache"],
    "search": ["search"],
    "export": ["export"],
    "import": ["import"],
    "init": ["init"],
    "brain": ["brain"],
    "cortex": ["cortex"],
    "knowledge": ["knowledge"],
    "memory": ["memory"],
    "lobes": ["lobes"],
    "session": ["session"],
    "project": ["project"],
    "manifest": ["manifest"],
    "benchmark": ["benchmark"],
    "checkpoint": ["checkpoint"],
    "regression": ["regression"],
    "pulse": ["pulse"],
    "peers": ["peers"],
    "subserver": ["subserver"],
    "governance": ["governance"],
    "intelligence": ["intelligence"],
    "system": ["system"],
    "dry-run": ["dry-run", "dryrun"],
    "savepoint": ["savepoint"],
    "context": ["context"],
    "push-notification": ["push-notification", "pushnotification"],
    "picoclaw": ["picoclaw"],
    "hooks": ["hooks"],
}

def get_metadata(filepath: Path):
    """Determina domain, layer, type e tags baseados no caminho e nome do arquivo."""
    rel_path = filepath.relative_to(BASE_DIR) if filepath.is_relative_to(BASE_DIR) else filepath
    path_str = str(rel_path).lower()
    name = filepath.stem.lower()
    
    # Aplicar mapeamento de caminho
    metadata = {"domain": "core", "layer": "core", "type": "file", "tags": []}
    for pattern, mapping in PATH_MAPPINGS:
        if re.match(pattern, str(filepath), re.IGNORECASE):
            metadata.update(mapping)
            break
    
    # Coletar tags baseadas em palavras-chave
    tags = set()
    for keyword, patterns in KEYWORDS.items():
        for pat in patterns:
            if pat in name or pat in path_str:
                tags.add(keyword)
    
    # Adicionar tags de nome de arquivo (partes do nome)
    # Remover prefixos como nc-*, fr-*, ds-*
    clean_name = re.sub(r'^(nc|fr|ds|int|svc|cfg|hk|utl|tool|scr|arc|bak|boot|aln|aud|tst|dpl|api|lib|prf|nam)-', '', name)
    parts = re.split(r'[-_.]', clean_name)
    for part in parts:
        if len(part) > 2 and part not in ['py', 'json', 'md', 'mdc']:
            tags.add(part)
    
    metadata["tags"] = list(tags)[:10]  # Limitar a 10 tags
    metadata["hash"] = "auto-generated"
    return metadata

def has_frontmatter(content: str, ext: str) -> bool:
    """Verifica se o arquivo j tem frontmatter."""
    lines = content.splitlines()
    if not lines:
        return False
    if ext in ('.md', '.mdc'):
        # Verificar se as primeiras linhas so --- ... ---
        if len(lines) >= 3 and lines[0] == '---':
            for i in range(1, min(10, len(lines))):
                if lines[i] == '---':
                    return True
    elif ext == '.py':
        # Verificar se comea com \"\"\"--- ... ---\"\"\"
        if content.startswith('\"\"\"---'):
            return True
        # Ou se h um bloco de comentrio frontmatter
        if content.lstrip().startswith('\"\"\"---'):
            return True
    elif ext == '.json':
        # Verificar se h chave \"_meta\" no objeto raiz
        try:
            data = json.loads(content)
            if \"_meta\" in data:
                return True
        except:
            pass
    return False

def add_frontmatter_to_md(content: str, metadata: dict) -> str:
    \"\"\"Adiciona frontmatter a arquivos Markdown/MDC.\"\"\"
    lines = content.splitlines()
    # Se j tem frontmatter, vamos atualizar/adicionar campos faltantes
    if lines and lines[0] == '---':
        # Encontrar fim do frontmatter
        end_idx = 1
        while end_idx < len(lines) and lines[end_idx] != '---':
            end_idx += 1
        if end_idx < len(lines):
            # Extrair frontmatter existente
            frontmatter_lines = lines[1:end_idx]
            # Parse YAML simples (no implementado completo)
            # Vamos apenas adicionar campos faltantes no final do frontmatter
            new_frontmatter_lines = []
            existing_fields = set()
            for line in frontmatter_lines:
                if ':' in line:
                    field = line.split(':', 1)[0].strip()
                    existing_fields.add(field)
                new_frontmatter_lines.append(line)
            
            # Adicionar campos faltantes
            for field in ['domain', 'layer', 'type', 'hash']:
                if field not in existing_fields:
                    new_frontmatter_lines.append(f\"{field}: {json.dumps(metadata[field])}\")
            # Tags - adicionar se no existir
            if 'tags' not in existing_fields:
                new_frontmatter_lines.append(f\"tags: {json.dumps(metadata['tags'])}\")
            
            # Reconstruir contedo
            new_content = ['---'] + new_frontmatter_lines + ['---'] + lines[end_idx+1:]
            return '\\n'.join(new_content)
    
    # Se no tem frontmatter, adicionar novo
    frontmatter = ['---']
    frontmatter.append(f\"domain: {json.dumps(metadata['domain'])}\")
    frontmatter.append(f\"layer: {json.dumps(metadata['layer'])}\")
    frontmatter.append(f\"type: {json.dumps(metadata['type'])}\")
    frontmatter.append(f\"tags: {json.dumps(metadata['tags'])}\")
    frontmatter.append(f\"hash: {json.dumps(metadata['hash'])}\")
    frontmatter.append('---')
    frontmatter.append('')
    return '\\n'.join(frontmatter + lines)

def add_frontmatter_to_py(content: str, metadata: dict) -> str:
    \"\"\"Adiciona frontmatter a arquivos Python.\"\"\"
    # Verificar se j tem frontmatter
    lines = content.splitlines()
    if lines and lines[0].startswith('\"\"\"---'):
        # Encontrar fim do frontmatter
        end_idx = 0
        while end_idx < len(lines) and not lines[end_idx].endswith('---\"\"\"'):
            end_idx += 1
        if end_idx < len(lines):
            # Atualizar frontmatter (simplificado: substituir)
            # Vamos substituir o bloco inteiro por um novo
            # Mantendo o restante do contedo
            rest = lines[end_idx+1:] if end_idx+1 < len(lines) else []
            # Gerar novo frontmatter
            frontmatter = ['\"\"\"---']
            frontmatter.append(f'domain: {json.dumps(metadata[\"domain\"])}')
            frontmatter.append(f'layer: {json.dumps(metadata[\"layer\"])}')
            frontmatter.append(f'type: {json.dumps(metadata[\"type\"])}')
            frontmatter.append(f'tags: {json.dumps(metadata[\"tags\"])}')
            frontmatter.append(f'hash: {json.dumps(metadata[\"hash\"])}')
            frontmatter.append('---\"\"\"')
            frontmatter.append('')
            return '\\n'.join(frontmatter + rest)
    
    # Se no tem frontmatter, adicionar antes de qualquer docstring existente
    # Procurar por docstring no incio
    if lines and (lines[0].startswith('\"\"\"') or lines[0].startswith(\"'''\")):
        # H docstring na primeira linha
        # Inserir frontmatter antes dela
        frontmatter = ['\"\"\"---']
        frontmatter.append(f'domain: {json.dumps(metadata[\"domain\"])}')
        frontmatter.append(f'layer: {json.dumps(metadata[\"layer\"])}')
        frontmatter.append(f'type: {json.dumps(metadata[\"type\"])}')
        frontmatter.append(f'tags: {json.dumps(metadata[\"tags\"])}')
        frontmatter.append(f'hash: {json.dumps(metadata[\"hash\"])}')
        frontmatter.append('---\"\"\"')
        frontmatter.append('')
        return '\\n'.join(frontmatter + lines)
    else:
        # Adicionar frontmatter no topo
        frontmatter = ['\"\"\"---']
        frontmatter.append(f'domain: {json.dumps(metadata[\"domain\"])}')
        frontmatter.append(f'layer: {json.dumps(metadata[\"layer\"])}')
        frontmatter.append(f'type: {json.dumps(metadata[\"type\"])}')
        frontmatter.append(f'tags: {json.dumps(metadata[\"tags\"])}')
        frontmatter.append(f'hash: {json.dumps(metadata[\"hash\"])}')
        frontmatter.append('---\"\"\"')
        frontmatter.append('')
        return '\\n'.join(frontmatter + lines)

def add_frontmatter_to_json(content: str, metadata: dict) -> str:
    \"\"\"Adiciona chave _meta a arquivos JSON.\"\"\"
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print(f\"  AVISO: JSON invlido, ignorando\")
        return content
    
    # Se j tem _meta, atualizar
    if \"_meta\" in data:
        data[\"_meta\"].update({
            \"domain\": metadata[\"domain\"],
            \"layer\": metadata[\"layer\"],
            \"type\": metadata[\"type\"],
            \"tags\": metadata[\"tags\"],
            \"hash\": metadata[\"hash\"]
        })
    else:
        # Adicionar _meta como primeira chave (para manter ordem)
        new_data = {\"_meta\": {
            \"domain\": metadata[\"domain\"],
            \"layer\": metadata[\"layer\"],
            \"type\": metadata[\"type\"],
            \"tags\": metadata[\"tags\"],
            \"hash\": metadata[\"hash\"]
        }}
        new_data.update(data)
        data = new_data
    
    # Retornar JSON formatado com indentao 2
    return json.dumps(data, indent=2, ensure_ascii=False)

def process_file(filepath: Path):
    \"\"\"Processa um nico arquivo.\"\"\"
    ext = filepath.suffix.lower()
    if ext not in ('.md', '.mdc', '.py', '.json'):
        return False
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f\"  ERRO: No pude ler {filepath}: {e}\")
        return False
    
    metadata = get_metadata(filepath)
    
    # Verificar se j tem frontmatter completo (todos os campos obrigatrios)
    # Para simplificar, vamos sempre aplicar/atualizar
    print(f\"  Processando: {filepath.relative_to(BASE_DIR)}\")
    print(f\"    Metadata: {metadata}\")
    
    new_content = content
    if ext in ('.md', '.mdc'):
        new_content = add_frontmatter_to_md(content, metadata)
    elif ext == '.py':
        new_content = add_frontmatter_to_py(content, metadata)
    elif ext == '.json':
        new_content = add_frontmatter_to_json(content, metadata)
    
    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        print(f\"     Frontmatter aplicado/atualizado\")
        return True
    else:
        print(f\"      Nenhuma alterao necessria\")
        return False

def main():
    print(\"NC-DS-047-GLOBAL-SANE-001: Aplicando frontmatter massivamente\")
    print(\"=\" * 60)
    
    # Coletar arquivos
    files = []
    
    # Core: Python, JSON
    for ext in ('*.py', '*.json'):
        files.extend(CORE_DIR.rglob(ext))
    
    # Lobos: MDC (e possivelmente MD, JSON, Python)
    for ext in ('*.mdc', '*.md', '*.py', '*.json'):
        files.extend(LOBES_DIR.rglob(ext))
    
    # Remover arquivos em __pycache__ e outros diretrios de sistema
    files = [f for f in files if '__pycache__' not in str(f) and '.git' not in str(f)]
    
    print(f\"Encontrados {len(files)} arquivos para processar\")
    
    modified_count = 0
    for filepath in files:
        if process_file(filepath):
            modified_count += 1
    
    print(\"=\" * 60)
    print(f\"Concludo. {modified_count} arquivos modificados.\")
    
    # Validar arquivos Python com py_compile
    print(\"\\nValidando arquivos Python com py_compile...\")
    import subprocess
    errors = []
    for filepath in files:
        if filepath.suffix == '.py':
            result = subprocess.run([sys.executable, '-m', 'py_compile', str(filepath)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                errors.append((filepath, result.stderr))
    
    if errors:
        print(\" Erros de compilao encontrados:\")
        for filepath, err in errors:
            print(f\"  {filepath.relative_to(BASE_DIR)}: {err[:200]}\")
        return 1
    else:
        print(\" Todos os arquivos Python compilam corretamente.\")
        return 0

if __name__ == '__main__':
    sys.exit(main())