# Anlise de Impacto de Renomeao

*Gerado em: 2026-04-15T23:33:12.129997*

## Resumo Executivo
- **Total de renomeaes:** 87
- **Arquivos com imports afetados:** 227
- **Referncias adicionais encontradas:** 101
- **Score de complexidade:** 30/100

> **Interpretao do Score:**
> - 0-30: Baixa complexidade (poucas dependncias)
> - 31-70: Mdia complexidade (algumas dependncias crticas)
> - 71-100: Alta complexidade (muitas dependncias, risco alto)

##  Renomeaes de Alto Impacto
| Arquivo Antigo | Arquivo Novo | Diretos | Indiretos | Risco |
|----------------|--------------|---------|-----------|-------|
| `neocortex/config.py` | `neocortex/NC-CORE-FR-001-config.py` | 45 | 37 | HIGH |
| `neocortex/core/file_utils.py` | `neocortex/core/NC-CORE-FR-014-file-utils.py` | 10 | 6 | HIGH |
| `neocortex/infra/llm/factory.py` | `neocortex/infra/llm/NC-INFRA-FR-009-factory.py` | 7 | 6 | HIGH |
| `neocortex/mcp/server.py` | `neocortex/mcp/NC-CORE-FR-026-server.py` | 18 | 13 | HIGH |

## Arquivos que Precisam de Atualizao
Total: 157 arquivos

### Arquivos Python
- `01_neocortex_framework/DIR-ARC-FR-001-archive-main/development_utilities/extract_all_tools.py`
- `01_neocortex_framework/DIR-ARC-FR-001-archive-main/development_utilities/extract_tools_final.py`
- `01_neocortex_framework/DIR-ARC-FR-001-archive-main/development_utilities/extract_tools_robust.py`
- `01_neocortex_framework/DIR-ARC-FR-001-archive-main/mcp_server_legacy/NC-MCP-FR-001-mcp-server.py`
- `01_neocortex_framework/DIR-ARC-FR-001-archive-main/scripts/verify_mcp.py`
- `01_neocortex_framework/DIR-BAK-FR-001-backup-main/backup_root/verify_mcp.py`
- `01_neocortex_framework/DIR-MCP-FR-001-mcp-server/NC-HUB-FR-001-mcp-hub.py`
- `01_neocortex_framework/DIR-MCP-FR-001-mcp-server/extract_tools.py`
- `01_neocortex_framework/DIR-MCP-FR-001-mcp-server/list_tools_simple.py`
- `01_neocortex_framework/DIR-MCP-FR-001-mcp-server/neocortex_mcp.py`
- `01_neocortex_framework/DIR-MCP-FR-001-mcp-server/test_tools.py`
- `01_neocortex_framework/DIR-MCP-FR-001-mcp-server/test_tools_simple.py`
- `01_neocortex_framework/DIR-TEST-FR-001-tests-main/fire_test.py`
- `01_neocortex_framework/DIR-TEST-FR-001-tests-main/test_config_reload.py`
- `01_neocortex_framework/DIR-TEST-FR-001-tests-main/test_mcp_responsive.py`
- `01_neocortex_framework/DIR-TEST-FR-001-tests-main/test_modular_server.py`
- `01_neocortex_framework/DIR-TEST-FR-001-tests-main/test_sanity.py`
- `01_neocortex_framework/DIR-TEST-FR-001-tests-main/test_tools.py`
- `01_neocortex_framework/neocortex/agent/executor.py`
- `01_neocortex_framework/neocortex/cli/main.py`
- `01_neocortex_framework/neocortex/core/NC-CFG-FR-001-logging-config.py`
- `01_neocortex_framework/neocortex/core/__init__.py`
- `01_neocortex_framework/neocortex/core/agent_service.py`
- `01_neocortex_framework/neocortex/core/akl_service.py`
- `01_neocortex_framework/neocortex/core/checkpoint_service.py`
- `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-004-project-config.py`
- `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-004-project-loader.py`
- `01_neocortex_framework/neocortex/core/config_service.py`
- `01_neocortex_framework/neocortex/core/consolidation_service.py`
- `01_neocortex_framework/neocortex/core/export_service.py`
- `01_neocortex_framework/neocortex/core/file_utils.py`
- `01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-002-simple-hook.py`
- `01_neocortex_framework/neocortex/core/kg_service.py`
- `01_neocortex_framework/neocortex/core/ledger_service.py`
- `01_neocortex_framework/neocortex/core/lobe_service.py`
- `01_neocortex_framework/neocortex/core/logging_config.py`
- `01_neocortex_framework/neocortex/core/manifest_service.py`
- `01_neocortex_framework/neocortex/core/peers_service.py`
- `01_neocortex_framework/neocortex/core/profile_manager.py`
- `01_neocortex_framework/neocortex/core/profile_service.py`
- `01_neocortex_framework/neocortex/core/pulse_scheduler.py`
- `01_neocortex_framework/neocortex/core/regression_service.py`
- `01_neocortex_framework/neocortex/core/review/NC-VAL-FR-005-async-thread-validator.py`
- `01_neocortex_framework/neocortex/core/security_service.py`
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-001-logging-service.py`
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-002-health-service.py`
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-004-cache-service.py`
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-010-kairos-service.py`
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-015-task-broker.py`
- `01_neocortex_framework/neocortex/core/utils/NC-UTL-FR-003-path-resolver.py`

*... e mais 107 arquivos Python.*

## Anlise Detalhada por Renomeao
Para detalhes completos, consulte o arquivo JSON:
`DIR-DOC-FR-001-docs-main\rename_impact_analysis.json`

### Exemplos de Impacto

#### 1. `neocortex/agent/executor.py`  `neocortex/agent/NC-AGENT-FR-001-executor.py`
- **Mdulo:** neocortex.agent.executor  neocortex.agent.NC-AGENT-FR-001-executor
- **Imports diretos:** 3
- **Referncias adicionais:** 2
- **Referncias crticas:**
  - `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_sanity.py` (python_import)
  - `01_neocortex_framework_RENAMED\DIR-TEST-FR-001-tests-main\test_sanity.py` (python_import)

#### 2. `neocortex/cli/main.py`  `neocortex/cli/NC-CLI-FR-001-main.py`
- **Mdulo:** neocortex.cli.main  neocortex.cli.NC-CLI-FR-001-main
- **Imports diretos:** 1
- **Referncias adicionais:** 0

#### 3. `neocortex/config.py`  `neocortex/NC-CORE-FR-001-config.py`
- **Mdulo:** neocortex.config  neocortex.NC-CORE-FR-001-config
- **Imports diretos:** 45
- **Referncias adicionais:** 37
- **Referncias crticas:**
  - `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_config_reload.py` (python_import)
  - `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_sanity.py` (python_import)
  - `01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_sanity.py` (python_import)
  *... e mais 34 referncias.*

#### 4. `neocortex/core/NC-CFG-FR-001-logging-config.py`  `neocortex/core/NC-CORE-FR-002-nc-cfg-fr-001-logging-config.py`
- **Mdulo:** neocortex.core.NC-CFG-FR-001-logging-config  neocortex.core.NC-CORE-FR-002-nc-cfg-fr-001-logging-config
- **Imports diretos:** 0
- **Referncias adicionais:** 0

#### 5. `neocortex/core/NC-CORE-FR-014-lock-guard.py`  `neocortex/core/NC-CORE-FR-003-nc-core-fr-014-lock-guard.py`
- **Mdulo:** neocortex.core.NC-CORE-FR-014-lock-guard  neocortex.core.NC-CORE-FR-003-nc-core-fr-014-lock-guard
- **Imports diretos:** 2
- **Referncias adicionais:** 0
