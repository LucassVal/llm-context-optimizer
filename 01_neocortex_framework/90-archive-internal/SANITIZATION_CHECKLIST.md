# Checklist de Sanitizao Mestre - NeoCortex (SSOT Auditado)

**Status de Auditoria:** 100% EXECUTADO e RESGUARDADO 
**Data:** 2026-04-11

##  1. Sanitizao Fsica Executada (Ferramentas Integradas e Renomeadas)
O mapeamento fsico na arquitetura ocorreu obedecendo estritamente ao SSOT da nomenclatura. As ferramentas MCP legadas foram convertidas e centralizadas:

- [x] `neocortex/mcp/server.py`  `NC-MCP-FR-001-server.py` (Referncia mantida estvel para bootloaders)
- [x] `neocortex/mcp/tools/cortex.py`  `NC-TOOL-FR-001-cortex.py`
- [x] `neocortex/mcp/tools/agent.py`  `NC-TOOL-FR-002-agent.py`
- [x] `neocortex/mcp/tools/benchmark.py`  `NC-TOOL-FR-003-benchmark.py`
- [x] `neocortex/mcp/tools/checkpoint.py`  `NC-TOOL-FR-004-checkpoint.py`
- [x] `neocortex/mcp/tools/config.py`  `NC-TOOL-FR-005-config.py`
- [x] `neocortex/mcp/tools/export.py`  `NC-TOOL-FR-006-export.py`
- [x] `neocortex/mcp/tools/init.py`  `NC-TOOL-FR-007-init.py`
- [x] `neocortex/mcp/tools/ledger.py`  `NC-TOOL-FR-008-ledger.py`
- [x] `neocortex/mcp/tools/lobes.py`  `NC-TOOL-FR-009-lobes.py`
- [x] `neocortex/mcp/tools/peers.py`  `NC-TOOL-FR-010-peers.py`
- [x] `neocortex/mcp/tools/pulse.py`  `NC-TOOL-FR-011-pulse.py`
- [x] `neocortex/mcp/tools/regression.py`  `NC-TOOL-FR-012-regression.py`
- [x] `neocortex/mcp/tools/report.py`  `NC-TOOL-FR-013-report.py`
- [x] `neocortex/mcp/tools/search.py`  `NC-TOOL-FR-014-search.py`
- [x] `neocortex/mcp/tools/security.py`  `NC-TOOL-FR-015-security.py`
- [x] `neocortex/mcp/tools/subserver.py`  `NC-TOOL-FR-016-subserver.py`
- [x] `neocortex/mcp/tools/task.py`  `NC-TOOL-FR-017-task.py`
- [x] **CONSOLIDAO KNOWLEDGE STUBS:** `akl.py`, `consolidation.py`, `kg.py`, e `manifest.py` foram apensados num arquivo blindado s:  `NC-TOOL-FR-020-knowledge.py`
- [x] `neocortex/mcp/tools/NC-TOOL-FR-000-brain.py`  (J convertido p/ NC).

##  2. Precaues Tomadas e Anlise de Danos / Referncias

### Impacto Avaliado 1: O Quebra de Importao do "server.py"
*   **Ameaa:** Ao mudar o nome dos arquivos para `NC-TOOL-FR-*`, o loop original do `server.py` poderia falhar por causa dos hfens no suportados em instncias estticas do python (eg: `import NC-TOOL-FR-000`).
*   **Precauo & Soluo:** O design foi confirmado inquebrvel por usar a classe Python nativa **`importlib.import_module()`** que suporta hfens no modo de varredura dinmica do `glob()`.
*   **Status de Sanidade:** O servidor `server.py` segue bootando dinamicamente sem perdas. Nenhuma string em `server.py` precisou ser substituda.

### Impacto Avaliado 2: Loop Seguro e Crash no "sub_server.py"
*   **Ameaa:** O script vital `sub_server.py` continha um dicionrio mestre esttico `TOOL_MODULE_MAP = { "cortex": "cortex", ... }` que injetaria erros diretos de `ModuleNotFoundError` pois apontavam para referncias mortas / apagadas.
*   **Precauo & Soluo:** O sistema inteiro de mapeamento foi refatorado. As strings das ferramentas (esquerda) permaneceram originais (assegurando que regras .yaml do sistema funcionem limpas), enquanto o carregamento da direita (os mdulos brutos) foi repontado para a conveno NC explcita: `"cortex": "NC-TOOL-FR-001-cortex"`. Tudo resolvido *in-context*.

### Impacto Avaliado 3: O Fantasma da Perda de Contexto
*   **Ameaa:** Delees acidentais em arquivos originais ou perda de roadmap antigo.
*   **Precauo & Soluo:** Nenhuma remoo local foi feita na raz ou em `/neocortex` sem arquivado prvio, as mesclagens do knowledge foram commitadas e podem ser espelhadas caso haja regresso, e todo changelog est unificado conforme Naming Convention. 

---
>  *O Ecossistema TurboQuant/NeoCortex est oficialmente protegido, documentado, catalogado em SSOT reestruturado para ser rodado sem conflitos.*
