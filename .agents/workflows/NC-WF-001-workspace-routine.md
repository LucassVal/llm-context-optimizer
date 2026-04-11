---
description: NeoCortex Workspace Routine Standards
---

# Fluxo de Trabalho (Workspace Routine)

Sempre que atuar no ambiente `TURBOQUANT_V42`, o Agente AI (Antigravity ou outro via Cursor/VSCode) deve seguir estritamente as convenções arquiteturais.

## Validações Obrigatórias antes de Escrita:
1. **Verificação de Diretório**: Todo o projeto está numerado por nível raiz (`01_neocortex_framework`, `02_memory_lobes`, `03_white_label_templates`, `04_user_docs`, `05_examples`).
2. **Naming Convention Check**: Todo código-fonte deve ser nomeado via SSOT: `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`.
3. **Resguardo de Caminho**: Nunca apagar arquivos sem antes fazer merge ou mover para a pasta `DIR-ARC...` (Archive).

## Como criar nova Ferramenta (Tool):
1. Crie o arquivo respeitando a convenção em `01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-<NUM>-<novaferramenta>.py`.
2. Mapeie o arquivo recém-criado em `sub_server.py` caso ele deva estar exposto aos LLMs isolados.
3. Catalogue-o adicionando a descrição no SSOT Document (`NC-NAM-FR-001-naming-convention.md`).
