# NC-NAM-FR-001 - Convenções de Nomenclatura + Registro .py

> **Data:** 2026-05-05 | **Versão:** v2.0 | **LEXICO:** v4.5 (114 serviços)
> **ADR-008 ativo:** Paths resolvidos via `#LEXICO` e `@UBL` (ULQ-TAG-INDEX v2.0)
> **DDD:** Constitution (Shared Kernel) → ULQ-TAG-INDEX → LEXICO → MANIFEST

## REGISTRO .py (306 arquivos — 2026-05-05)

| Categoria | Path | Qtd | LEXICO |
|-----------|------|-----|--------|
| NC-CORE-FR-* | `01_neocortex_framework/neocortex/core/` | 78 | #CORE |
| NC-SUPER-* | `01_neocortex_framework/neocortex/mcp/tools/` | 19 | #TOOLS |
| NC-MCP/TOOL-FR-* | `01_neocortex_framework/neocortex/mcp/tools/` | 3 | #TOOLS |
| NC-INFRA-FR-* | `01_neocortex_framework/neocortex/infra/` | 5 | #INFRA |
| NC-REP-FR-* | `01_neocortex_framework/neocortex/repositories/` | 2 | #REPOS |
| NC-LLM-FR-* | `01_neocortex_framework/neocortex/infra/llm/` | 6 | #LLM |
| NC-SVC-FR-* | `01_neocortex_framework/neocortex/core/services/` | 21 | #SERVICES |
| NC-HK-FR-* | `01_neocortex_framework/neocortex/core/hooks/` | 7 | #HOOKS |
| NC-UTL-FR-* | `01_neocortex_framework/neocortex/core/utils/` | 9 | #UTILS |
| NC-SCR-FR-* | `01_neocortex_framework/32-scripts/` | 87 | #SCRIPTS |
| NC-TEST-FR-* | `01_neocortex_framework/33-tests/` | 7 | #TESTS |
| Strangler wrappers | `01_neocortex_framework/neocortex/core/` | 19 | #STRANGLER |
| NC-*-FR-* (outros) | Diversos | 23 | #OTHER |
| `__init__.py` + configs | Diversos | 20 | — |

**Total: 306 .py files catalogados. 114 serviços no LEXICO v4.5.**

---

## 🗺️ 1. Estrutura de Diretórios Proposta e Mapa do Projeto

O projeto utiliza um design de pastas modulares governado por prefixos restritos `DIR-<tipo>-FR`, abrigando o pacote central da framework `neocortex` rigidamente separado.

```
📁 TURBOQUANT_V42/
├── 📄 README.md (descrição do propósito central)
├── 📄 antigravity_neocortex_config.json (configuração IDE para MCP padrão STDIO)
├── 📄 start_neocortex_mcp.bat (Inicializador Windows WS do Host Principal)
├── 📄 start_neocortex_mcp.ps1 (Inicializador Powershell WS do Host Principal)
├── 📁 neocortex_framework/ (núcleo do framework isolado)
│   ├── 📄 __init__.py
│   ├── 📁 neocortex/ (código fonte principal de rotas e agentes)
│   │   ├── 📄 config.py (ConfigProvider)
│   │   ├── 📁 core/ (serviços de domínio - Services / Schedulers)
│   │   ├── 📁 infra/ (repositórios de conectividade com stores DB e Caches)
│   │   ├── 📁 agent/ (agentes autônomos internos isolados, eg. Courier / Engineer)
│   │   └── 📁 mcp/ (servidor e conexão MCP via Transporte)
│   │       ├── 📄 server.py (Host principal em SSE)
│   │       ├── 📄 sub_server.py
│   │       └── 📁 tools/ (17+ ferramentas de gestão T-0 conformadas como NC-TOOL)
│   ├── 📁 DIR-PRF-FR-001-profiles-main/ (perfis de usuário)
│   ├── 📁 DIR-DOC-FR-001-docs-main/ (documentação vital e roadmaps de arquitetura)
│   ├── 📁 DIR-ARC-FR-001-archive-main/ (arquivos obsoletos transferidos pelo OpenCode)
│   ├── 📁 DIR-BAK-FR-001-backup-main/ (backups antigos originados da raiz)
│   ├── 📁 DIR-CFG-FR-001-config-main/ (arquivos sensíveis como config.yaml)
│   ├── 📁 DIR-TEST-FR-001-tests-main/ (suite de validação e testes de sanidade)
│   ├── 📁 DIR-TMP-FR-001-templates-main/ (templates resguardados)
│   └── 📁 DIR-MCP-FR-001-mcp-server/ (scripts satélites da arquitetura Server principal)
├── 📁 02_memory_lobes/ (lobos ativos / dados de persistência viva)
├── 📁 .agents/ (regras e workflows autônomos do OpenCode/Antigravity)
└── 📁 white_label/ (templates para instanciamento modular)
```

---

## 🏷️ 2. Padrão de Nomenclatura de Arquivos e Pastas

Formato Base: `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`  
Formato Diretório Base: `DIR-<TIPO>-<SIGLA>-<NUM>-<desc>`

| Elemento | Descrição | Exemplos |
| :--- | :--- | :--- |
| **NC** | Prefixo fixo para Arquivos (NeoCortex) | NC |
| **DIR** | Prefixo fixo para Diretórios Estruturais | DIR |
| **<TIPO>** | Categoria base da operação do arquivo/pasta | MCP (Server), TOOL (Ferramenta), SUPER (Super-Tool MCP consolidada multi-action), CORE (Serviço), INFRA (Infra), DOC (Documentos), PRF (Perfil), TKT (Ticket), ARC (Arquivo Obsoleto), BAK (Backup), CFG (Configuração), TEST (Testes), TMP (Templates) |
| **<SIGLA>** | Abreviação do propósito contextual | FR (Framework Geral), WL (White Label), USR (Usuário) |
| **<NUM>** | Número sequencial (3 dígitos) por módulo | 001, 002, 020 |
| **<desc>** | Descrição curta em kebab-case intuitiva | cortex-tool, mcp-server |

### Catálogo Primário de Prefixos Praticados
- `NC-MCP-FR-001-*`: Componentes e rotas vitais do núcleo servidor Model Context Protocol.
- `NC-TOOL-FR-<NUM>-*`: Qualquer ferramenta legível pela Interface MCP (Ex: `NC-TOOL-FR-000-brain.py`, `NC-TOOL-FR-008-ledger.py`).
- `NC-CORE-FR-001-*`: Serviços e Orquestradores localizados em `/core`.
- `NC-DOC-FR-001-*`: Relatórios fixos, Checklists ou Planejamentos Estratégicos (Como este documento e Roadmaps).
- `NC-PRF-USR-XXX-*`: Profile rules localizados no `DIR-PRF-FR`.

### Regras Ouro para Manutenção
1. **Novas Ferramentas**: Se a ferramenta não puder ser consolidada num `NC-TOOL` englobador já existente, deve nascer sob a próxima numeração livre na pasta `/tools/`.
2. **Arquivos Obsoletos**: Devem ser arrastados para `DIR-ARC-FR-001-archive-main` não sofrendo *apenas* modificação e remoção direta da raiz pra precaver vazamento de dependências escondidas.
3. **Logs**: Devem ser descartados perante limite da HotCache de 5. Backups temporais não geram commit, moram em `DIR-BAK-FR-001-backup-main`.
4. **Versionamento SSOT**: Todo SSOT deve incluir versão/hash no formato `NC-<TIPO>-<SIGLA>-<NUM>-vX.Y-YYYYMMDD-hash` para rastreabilidade.

---

## 📂 SSOT Geral do Sistema (Snapshot Local)
| Nome | Descrição | Local | Palavras Chaves | SSOT Relacionado |
|---|---|---|---|---|
| antigravity_neocortex_config.json | Configuração IDE MCP STDIO | \antigravity_neocortex_config.json | mcp, config | NC-CFG-FR-001-config-main |
| README.md | Documentação raiz do projeto | \README.md | docs | NC-DOC-FR-001-ubiquitous-language-dictionary.md |
| start_neocortex_mcp.bat | Inicializador Windows | \start_neocortex_mcp.bat | startup, windows | NC-SCR-FR-103-start-with-mc.ps1 |
| start_neocortex_mcp.ps1 | Inicializador PowerShell | \start_neocortex_mcp.ps1 | startup, powershell | NC-SCR-FR-103-start-with-mc.ps1 |
| pyproject.toml | Configuração Python | \01_neocortex_framework\pyproject.toml | python, config | NC-CFG-FR-001-config-main |
| requirements.txt | Dependências Python | \01_neocortex_framework\requirements.txt | python, dependencies | NC-CFG-FR-001-config-main |
| deepseek.exe | CLI DeepSeek | C:\Program Files\Python312\Scripts\deepseek.exe | deepseek, cli, ai | NC-TOOL-FR-000-brain.py |
| lobe_index.db | Cache de lobes | \01_neocortex_framework\.neocortex\cache\lobe_index.db | cache, lobes | NC-LBE-FR-001-lobe-manager.py |
| index.redb | Hot cache | \01_neocortex_framework\.neocortex\cache\hot_cache\index.redb | cache, hot | NC-SVC-FR-006-metrics-collector.py |
| cache.db | Cache ledger | \01_neocortex_framework\.neocortex\cache\ledger\cache.db | cache, ledger | NC-TOOL-FR-008-ledger.py |
| 7fd282bb51e2535a2323bf377a90.val | Cache value | \01_neocortex_framework\.neocortex\cache\ledger\de\50\7fd282bb51e2535a2323bf377a90.val | cache, ledger | NC-TOOL-FR-008-ledger.py |
| cache.db | Cache manifests | \01_neocortex_framework\.neocortex\cache\manifests\cache.db | cache, manifests | NC-TOOL-FR-008-ledger.py |
| metrics.db | Métricas DuckDB | \01_neocortex_framework\.neocortex\metrics\metrics.db | metrics, duckdb | NC-SVC-FR-006-metrics-collector.py |
| metrics.db.wal | WAL métricas | \01_neocortex_framework\.neocortex\metrics\metrics.db.wal | metrics, wal | NC-SVC-FR-006-metrics-collector.py |
| 00-cortex-20260409.mdc | Lobe archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\.agents\rules\00-cortex-20260409.mdc | archive, lobe | NC-LBE-FR-001-lobe-manager.py |
| clean_security.py | Utility archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\clean_security.py | archive, utility | NC-SCR-FR-080-governance-auditor.py |
| extract_all_tools.py | Utility archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_all_tools.py | archive, utility | NC-TOOL-FR-000-brain.py |
| extract_tools_final.py | Utility archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_tools_final.py | archive, utility | NC-TOOL-FR-000-brain.py |
| extract_tools_robust.py | Utility archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_tools_robust.py | archive, utility | NC-TOOL-FR-000-brain.py |
| fix_indentation.py | Utility archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\fix_indentation.py | archive, utility | NC-SCR-FR-009-sanitize-yamls.py |
| _INDEX.yaml | Índice Canônico de Lobos | \02_memory_lobes\_INDEX.yaml | ddd, lobes, mapping | NC-SCR-FR-001-populate-lobes-ssot.py |
| 01_architecture | Domínio DDD Arquitetura | \02_memory_lobes\01_architecture | ddd, architecture | NC-LBE-FR-ARCHITECTURE-001 |
| 06_governance | Domínio DDD Governança | \02_memory_lobes\06_governance | ddd, governance | NC-LBE-CEREBRAL-FRONTAL-001 |
| update_antigravity_confirmation.py | Script archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_antigravity_confirmation.py | archive, script | NC-SCR-FR-080-governance-auditor.py |
| update_ledger_status.py | Script archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_ledger_status.py | archive, script | NC-TOOL-FR-008-ledger.py |
| update_phase3_progress.py | Script archive | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_phase3_progress.py | archive, script | NC-TODO-FR-001-project-roadmap-consolidated.md |
| verify_mcp.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\verify_mcp.py | - |
| memory_neocortex_framework-20260409.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\memory_neocortex_framework-20260409.json | - |
| migration.log | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration.log | - |
| migration_debug.log | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_debug.log | - |
| NC-CTX-FR-001-cortex-central-20260410-0140.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\NC-CTX-FR-001-cortex-central-20260410-0140.mdc | - |
| NC-LED-FR-001-framework-ledger-20260410-0140.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\NC-LED-FR-001-framework-ledger-20260410-0140.json | - |
| add_root_sanitize_event.py | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\add_root_sanitize_event.py | - |
| CHEATSHEET.md | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\CHEATSHEET.md | - |
| install.ps1 | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\install.ps1 | - |
| install.sh | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\install.sh | - |
| Sem título.txt | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\Sem título.txt | - |
| update_antigravity_confirmation.py | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\update_antigravity_confirmation.py | - |
| update_ledger_status.py | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\update_ledger_status.py | - |
| verify_mcp.py | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\verify_mcp.py | - |
| benchmark_fractal_gauntlet.py | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\benchmarks_archive\benchmark_fractal_gauntlet.py | - |
| benchmark_master_suite.py | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\benchmarks_archive\benchmark_master_suite.py | - |
| README.md | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\benchmarks_archive\README.md | - |
| ledger_backup_20260410_001233.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\old_backup\backup\ledger_backup_20260410_001233.json | - |
| 00-cortex-FULL.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\templates\00-cortex-FULL.mdc | - |
| 00-cortex-STARTER.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\templates\00-cortex-STARTER.mdc | - |
| memory-ledger-TEMPLATE.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\templates\memory-ledger-TEMPLATE.json | - |
| phase-lobe-TEMPLATE.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\templates\phase-lobe-TEMPLATE.mdc | - |
| backup_manifest.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\backup_manifest.json | - |
| ledger_20260410_173509.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_173509.json | - |
| ledger_20260410_173805.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_173805.json | - |
| ledger_20260410_173853.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_173853.json | - |
| ledger_20260410_174028.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_174028.json | - |
| ledger_20260410_174150.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_174150.json | - |
| ledger_20260410_203605.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_203605.json | - |
| ledger_20260410_212708.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\ledger_20260410_212708.json | - |
| migration_report.json | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\migration_report.json | - |
| NC-CTX-FR-001-cortex-central.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-CTX-FR-001-cortex-central.mdc | - |
| NC-LBE-FR-002-claude-assistant.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-002-claude-assistant.mdc | - |
| NC-LBE-FR-ARCHITECTURE-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-ARCHITECTURE-001.mdc | - |
| NC-LBE-FR-BENCHMARKS-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-BENCHMARKS-001.mdc | - |
| NC-LBE-FR-CLI-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-CLI-001.mdc | - |
| NC-LBE-FR-CORE-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-CORE-001.mdc | - |
| NC-LBE-FR-DEPLOYMENT-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-DEPLOYMENT-001.mdc | - |
| NC-LBE-FR-DEVELOPMENT-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-DEVELOPMENT-001.mdc | - |
| NC-LBE-FR-DOCUMENTATION-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-DOCUMENTATION-001.mdc | - |
| NC-LBE-FR-INTEGRATION-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-INTEGRATION-001.mdc | - |
| NC-LBE-FR-KNOWLEDGE-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-KNOWLEDGE-001.mdc | - |
| NC-LBE-FR-LEGACY-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-LEGACY-001.mdc | - |
| NC-LBE-FR-MCP-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-MCP-001.mdc | - |
| NC-LBE-FR-MONITORING-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-MONITORING-001.mdc | - |
| NC-LBE-FR-PERFORMANCE-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-PERFORMANCE-001.mdc | - |
| NC-LBE-FR-PROFILES-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-PROFILES-001.mdc | - |
| NC-LBE-FR-PULSE-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-PULSE-001.mdc | - |
| NC-LBE-FR-SECURITY-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-SECURITY-001.mdc | - |
| NC-LBE-FR-TESTING-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-TESTING-001.mdc | - |
| NC-LBE-FR-WHITELABEL-001.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\NC-LBE-FR-WHITELABEL-001.mdc | - |
| TEST_INDEX_13aa6e78.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\TEST_INDEX_13aa6e78.mdc | - |
| TEST_INDEX_19948498.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\TEST_INDEX_19948498.mdc | - |
| TEST_INDEX_8f76b831.mdc | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\migration_backup\mdc_files\.agents\rules\TEST_INDEX_8f76b831.mdc | - |
| neocortex_config.yaml | - | \01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config.yaml | - |
| checkpoint_tree_phase1.json | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\checkpoint_tree_phase1.json | - |
| NC-LED-FR-001-framework-ledger.json | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-LED-FR-001-framework-ledger.json | - |
| NC-LED-FR-001-framework-ledger.json.backup | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-LED-FR-001-framework-ledger.json.backup | - |
| NC-TLM-FR-001-tool-manifest-schema.json | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-TLM-FR-001-tool-manifest-schema.json | - |
| NC-TLM-FR-001-tool-manifest.json | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\NC-TLM-FR-001-tool-manifest.json | - |
| NC_SEC_FR_001_security_utils.py | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\NC_SEC_FR_001_security_utils.py | - |
| test_security_integration.py | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\test_security_integration.py | - |
| update_ledger.py | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\update_ledger.py | - |
| AGENTS.md | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\AGENTS.md | - |
| NC-CTX-FR-001-cortex-central.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-CTX-FR-001-cortex-central.mdc | - |
| NC-LBE-FR-002-claude-assistant.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-002-claude-assistant.mdc | - |
| NC-LBE-FR-ARCHITECTURE-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-ARCHITECTURE-001.mdc | - |
| NC-LBE-FR-BENCHMARKS-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-BENCHMARKS-001.mdc | - |
| NC-LBE-FR-CLI-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-CLI-001.mdc | - |
| NC-LBE-FR-CORE-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-CORE-001.mdc | - |
| NC-LBE-FR-DEPLOYMENT-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-DEPLOYMENT-001.mdc | - |
| NC-LBE-FR-DEVELOPMENT-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-DEVELOPMENT-001.mdc | - |
| NC-LBE-FR-DOCUMENTATION-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-DOCUMENTATION-001.mdc | - |
| NC-LBE-FR-INTEGRATION-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-INTEGRATION-001.mdc | - |
| NC-LBE-FR-KNOWLEDGE-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-KNOWLEDGE-001.mdc | - |
| NC-LBE-FR-LEGACY-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-LEGACY-001.mdc | - |
| NC-LBE-FR-MCP-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-MCP-001.mdc | - |
| NC-LBE-FR-MONITORING-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-MONITORING-001.mdc | - |
| NC-LBE-FR-PERFORMANCE-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-PERFORMANCE-001.mdc | - |
| NC-LBE-FR-PROFILES-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-PROFILES-001.mdc | - |
| NC-LBE-FR-PULSE-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-PULSE-001.mdc | - |
| NC-LBE-FR-SECURITY-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-SECURITY-001.mdc | - |
| NC-LBE-FR-TESTING-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-TESTING-001.mdc | - |
| NC-LBE-FR-WHITELABEL-001.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\NC-LBE-FR-WHITELABEL-001.mdc | - |
| TEST_INDEX_13aa6e78.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\TEST_INDEX_13aa6e78.mdc | - |
| TEST_INDEX_19948498.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\TEST_INDEX_19948498.mdc | - |
| TEST_INDEX_8f76b831.mdc | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\rules\TEST_INDEX_8f76b831.mdc | - |
| restart-session.md | - | \01_neocortex_framework\DIR-CORE-FR-001-core-central\.agents\workflows\restart-session.md | - |
| BENCHMARKS.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\BENCHMARKS.md | - |
| BENCHMARKS_HYBRID.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\BENCHMARKS_HYBRID.md | - |
| CHECKPOINT_AUDIT_2026-04-10.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\CHECKPOINT_AUDIT_2026-04-10.md | - |
| DEEPSEEK_API_SUMMARY.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\DEEPSEEK_API_SUMMARY.md | - |
| mcp_tools_inventory.json | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\mcp_tools_inventory.json | - |
| NC-ALN-FR-001-arquitetural-alignment.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ALN-FR-001-arquitetural-alignment.md | - |
| NC-AUD-FR-001-audit-findings-2026-04-10.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-AUD-FR-001-audit-findings-2026-04-10.md | - |
| NC-AUD-FR-002-checklist-validation.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-AUD-FR-002-checklist-validation.md | - |
| NC-DOC-FR-002-directory-convention.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-DOC-FR-002-directory-convention.md | - |
| NC-DOC-FR-003-turboquant-prompt.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-DOC-FR-003-turboquant-prompt.md | - |
| NC-NAM-FR-001-naming-convention.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-NAM-FR-001-naming-convention.md | - |
| NC-PLN-FR-001-optimization-plan.mdc | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-PLN-FR-001-optimization-plan.mdc | - |
| NC-SES-FR-001-session-status-2026-04-10.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-SES-FR-001-session-status-2026-04-10.md | - |
| NC-TKT-FR-001-tickets.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TKT-FR-001-tickets.md | - |
| NC-TODO-FR-001-project-roadmap-consolidated.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TODO-FR-001-project-roadmap-consolidated.md | - |
| NC-TODO-FR-001-project-roadmap-v6-stability.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TODO-FR-001-project-roadmap-v6-stability.md | - |
| NC-TODO-FR-001-project-roadmap-v7-combined.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TODO-FR-001-project-roadmap-v7-combined.md | - |
| NC-TODO-FR-001-project-roadmap.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TODO-FR-001-project-roadmap.md | - |
| NC-TODO-FR-001-project-roadmap.md.backup | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TODO-FR-001-project-roadmap.md.backup | - |
| NC-TODO-FR-001-project-roadmap.md.bak | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-TODO-FR-001-project-roadmap.md.bak | - |
| README_MCP_NEOCORTEX.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\README_MCP_NEOCORTEX.md | - |
| SANITIZATION_CHECKLIST.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\SANITIZATION_CHECKLIST.md | - |
| STATUS.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\STATUS.md | - |
| CHEATSHEET.md | - | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\legacy\CHEATSHEET.md | - |
| clean_utf0.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\clean_utf0.py | - |
| extract_tools.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\extract_tools.py | - |
| list_tools.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\list_tools.py | - |
| list_tools_simple.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\list_tools_simple.py | - |
| NC-HUB-FR-001-mcp-hub.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-HUB-FR-001-mcp-hub.py | - |
| neocortex_mcp.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\neocortex_mcp.py | - |
| test_mcp_simple.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_mcp_simple.py | - |
| test_server_start.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_server_start.py | - |
| test_tools.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_tools.py | - |
| test_tools_simple.py | - | \01_neocortex_framework\DIR-MCP-FR-001-mcp-server\test_tools_simple.py | - |
| NC-PRF-FR-001-developer-schema.md | - | \01_neocortex_framework\DIR-PRF-FR-001-profiles-main\NC-PRF-FR-001-developer-schema.md | - |
| NC-PRF-FR-002-team-schema.md | - | \01_neocortex_framework\DIR-PRF-FR-001-profiles-main\NC-PRF-FR-002-team-schema.md | - |
| NC-PRF-FR-003-profile-loader.py | - | \01_neocortex_framework\DIR-PRF-FR-001-profiles-main\NC-PRF-FR-003-profile-loader.py | - |
| profile_manager.py | - | \01_neocortex_framework\DIR-PRF-FR-001-profiles-main\profile_manager.py | - |
| NC-PRF-TMP-001-dev-profile-template.json | - | \01_neocortex_framework\DIR-PRF-FR-001-profiles-main\templates\NC-PRF-TMP-001-dev-profile-template.json | - |
| NC-PRF-USR-001-profile.json | - | \01_neocortex_framework\DIR-PRF-FR-001-profiles-main\users\lucas_valerio\NC-PRF-USR-001-profile.json | - |
| detalhamento_completo.md | - | \01_neocortex_framework\DIR-REF-FR-001-reference-main\Arquivos de referência\detalhamento_completo.md | - |
| structured_elements.md | - | \01_neocortex_framework\DIR-REF-FR-001-reference-main\Arquivos de referência\structured_elements.md | - |
| sumario.md | - | \01_neocortex_framework\DIR-REF-FR-001-reference-main\Arquivos de referência\sumario.md | - |
| fire_test.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\fire_test.py | - |
| test_config_reload.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_config_reload.py | - |
| test_mcp_responsive.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_mcp_responsive.py | - |
| test_modular_server.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_modular_server.py | - |
| test_sanity.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_sanity.py | - |
| test_task.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_task.py | - |
| test_tools.py | - | \01_neocortex_framework\DIR-TEST-FR-001-tests-main\test_tools.py | - |
| 00-cortex-FULL.mdc | - | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\00-cortex-FULL.mdc | - |
| 00-cortex-STARTER.mdc | - | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\00-cortex-STARTER.mdc | - |
| memory-ledger-TEMPLATE.json | - | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\memory-ledger-TEMPLATE.json | - |
| NC-TMP-WL-001-cortex-template.mdc | - | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TMP-WL-001-cortex-template.mdc | - |
| phase-lobe-TEMPLATE.mdc | - | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\phase-lobe-TEMPLATE.mdc | - |
| rules.txt | - | \01_neocortex_framework\lobes\backend_dev\rules.txt | - |
| neocortex_config.yaml | - | \01_neocortex_framework\lobes\courier\neocortex_config.yaml | - |
| memory_ledger_courier.json | - | \01_neocortex_framework\lobes\courier\DIR-CORE-FR-001-core-central\memory_ledger_courier.json | - |
| 00-cortex-STARTER.mdc | - | \01_neocortex_framework\lobes\courier\DIR-CORE-FR-001-core-central\.agents\rules\00-cortex-STARTER.mdc | - |
| neocortex_config.yaml | - | \01_neocortex_framework\lobes\engineer\neocortex_config.yaml | - |
| memory_ledger_engineer.json | - | \01_neocortex_framework\lobes\engineer\DIR-CORE-FR-001-core-central\memory_ledger_engineer.json | - |
| 00-cortex-STARTER.mdc | - | \01_neocortex_framework\lobes\engineer\DIR-CORE-FR-001-core-central\.agents\rules\00-cortex-STARTER.mdc | - |
| rules.txt | - | \01_neocortex_framework\lobes\guardian\rules.txt | - |
| config.py | - | \01_neocortex_framework\neocortex\config.py | - |
| __init__.py | - | \01_neocortex_framework\neocortex\__init__.py | - |
| executor.py | - | \01_neocortex_framework\neocortex\agent\executor.py | - |
| main.py | - | \01_neocortex_framework\neocortex\cli\main.py | - |
| __init__.py | - | \01_neocortex_framework\neocortex\cli\__init__.py | - |
| agent_service.py | - | \01_neocortex_framework\neocortex\core\agent_service.py | - |
| akl_service.py | - | \01_neocortex_framework\neocortex\core\akl_service.py | - |
| benchmark_service.py | - | \01_neocortex_framework\neocortex\core\benchmark_service.py | - |
| checkpoint_service.py | - | \01_neocortex_framework\neocortex\core\checkpoint_service.py | - |
| config_service.py | - | \01_neocortex_framework\neocortex\core\config_service.py | - |
| consolidation_service.py | - | \01_neocortex_framework\neocortex\core\consolidation_service.py | - |
| cortex_service.py | - | \01_neocortex_framework\neocortex\core\cortex_service.py | - |
| export_service.py | - | \01_neocortex_framework\neocortex\core\export_service.py | - |
| file_utils.py | - | \01_neocortex_framework\neocortex\core\file_utils.py | - |
| init_service.py | - | \01_neocortex_framework\neocortex\core\init_service.py | - |
| kg_service.py | - | \01_neocortex_framework\neocortex\core\kg_service.py | - |
| ledger_service.py | - | \01_neocortex_framework\neocortex\core\ledger_service.py | - |
| lobe_service.py | - | \01_neocortex_framework\neocortex\core\lobe_service.py | - |
| manifest_service.py | - | \01_neocortex_framework\neocortex\core\manifest_service.py | - |
| peers_service.py | - | \01_neocortex_framework\neocortex\core\peers_service.py | - |
| profile_manager.py | - | \01_neocortex_framework\neocortex\core\profile_manager.py | - |
| profile_service.py | - | \01_neocortex_framework\neocortex\core\profile_service.py | - |
| pulse_scheduler.py | - | \01_neocortex_framework\neocortex\core\pulse_scheduler.py | - |
| regression_service.py | - | \01_neocortex_framework\neocortex\core\regression_service.py | - |
| security_service.py | - | \01_neocortex_framework\neocortex\core\security_service.py | - |
| __init__.py | - | \01_neocortex_framework\neocortex\core\__init__.py | - |
| backup_restore.py | - | \01_neocortex_framework\neocortex\infra\backup_restore.py | - |
| cache_backend.py | - | \01_neocortex_framework\neocortex\infra\cache_backend.py | - |
| config_validation.py | - | \01_neocortex_framework\neocortex\infra\config_validation.py | - |
| health_metrics.py | - | \01_neocortex_framework\neocortex\infra\health_metrics.py | - |
| hot_cache.py | - | \01_neocortex_framework\neocortex\infra\hot_cache.py | - |
| ledger_store.py | - | \01_neocortex_framework\neocortex\infra\ledger_store.py | - |
| lobe_index.py | - | \01_neocortex_framework\neocortex\infra\lobe_index.py | - |
| manifest_store.py | - | \01_neocortex_framework\neocortex\infra\manifest_store.py | - |
| metrics_store.py | - | \01_neocortex_framework\neocortex\infra\metrics_store.py | - |
| profiler.py | - | \01_neocortex_framework\neocortex\infra\profiler.py | - |
| search_engine.py | - | \01_neocortex_framework\neocortex\infra\search_engine.py | - |
| task_queue.py | - | \01_neocortex_framework\neocortex\infra\task_queue.py | - |
| vector_store.py | - | \01_neocortex_framework\neocortex\infra\vector_store.py | - |
| backend.py | - | \01_neocortex_framework\neocortex\infra\llm\backend.py | - |
| deepseek_backend.py | - | \01_neocortex_framework\neocortex\infra\llm\deepseek_backend.py | - |
| factory.py | - | \01_neocortex_framework\neocortex\infra\llm\factory.py | - |
| ollama_backend.py | - | \01_neocortex_framework\neocortex\infra\llm\ollama_backend.py | - |
| openai_backend.py | - | \01_neocortex_framework\neocortex\infra\llm\openai_backend.py | - |
| server.py | - | \01_neocortex_framework\neocortex\mcp\server.py | - |
| server.py.backup | - | \01_neocortex_framework\neocortex\mcp\server.py.backup | - |
| sub_server.py | - | \01_neocortex_framework\neocortex\mcp\sub_server.py | - |
| tools_manifest.json | - | \01_neocortex_framework\neocortex\mcp\tools_manifest.json | - |
| __init__.py | - | \01_neocortex_framework\neocortex\mcp\__init__.py | - |
| NC-TOOL-FR-000-brain.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-000-brain.py | - |
| NC-TOOL-FR-001-cortex.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-001-cortex.py | - |
| NC-TOOL-FR-002-agent.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-002-agent.py | - |
| NC-TOOL-FR-003-benchmark.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-003-benchmark.py | - |
| NC-TOOL-FR-004-checkpoint.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-004-checkpoint.py | - |
| NC-TOOL-FR-005-config.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-005-config.py | - |
| NC-TOOL-FR-006-export.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-006-export.py | - |
| NC-TOOL-FR-007-init.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-007-init.py | - |
| NC-TOOL-FR-008-ledger.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-008-ledger.py | - |
| NC-TOOL-FR-009-lobes.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-009-lobes.py | - |
| NC-TOOL-FR-010-peers.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-010-peers.py | - |
| NC-TOOL-FR-011-pulse.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-011-pulse.py | - |
| NC-TOOL-FR-012-regression.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-012-regression.py | - |
| NC-TOOL-FR-013-report.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-013-report.py | - |
| NC-TOOL-FR-014-search.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-014-search.py | - |
| NC-TOOL-FR-015-security.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-015-security.py | - |
| NC-TOOL-FR-016-subserver.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-016-subserver.py | - |
| NC-TOOL-FR-017-task.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-017-task.py | - |
| NC-TOOL-FR-020-openclaude-bridge.py | Bridge gRPC industrializada para controle do OpenClaude | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-020-openclaude-bridge.py | bridge, grpc, openclaude | NC-TOD-FR-001 |
| openclaude_pb2.py | Stub gRPC gerado para mensagens OpenClaude | \01_neocortex_framework\neocortex\mcp\tools\stubs\openclaude_pb2.py | grpc, stub, proto | NC-TOOL-FR-020 |
| openclaude_pb2_grpc.py | Stub gRPC gerado para serviços OpenClaude | \01_neocortex_framework\neocortex\mcp\tools\stubs\openclaude_pb2_grpc.py | grpc, stub, proto | NC-TOOL-FR-020 |
| __init__.py | - | \01_neocortex_framework\neocortex\mcp\tools\__init__.py | - |
| base.py | - | \01_neocortex_framework\neocortex\repositories\base.py | - |
| file_system_repository.py | - | \01_neocortex_framework\neocortex\repositories\file_system_repository.py | - |
| __init__.py | - | \01_neocortex_framework\neocortex\repositories\__init__.py | - |
| a2a_message_schema.json | - | \01_neocortex_framework\neocortex\schemas\a2a_message_schema.json | - |
| ledger_schema.json | - | \01_neocortex_framework\neocortex\schemas\ledger_schema.json | - |
| __init__.py | - | \01_neocortex_framework\neocortex\schemas\__init__.py | - |
| dependency_links.txt | - | \01_neocortex_framework\neocortex_framework.egg-info\dependency_links.txt | - |
| entry_points.txt | - | \01_neocortex_framework\neocortex_framework.egg-info\entry_points.txt | - |
| PKG-INFO | - | \01_neocortex_framework\neocortex_framework.egg-info\PKG-INFO | - |
| requires.txt | - | \01_neocortex_framework\neocortex_framework.egg-info\requires.txt | - |
| SOURCES.txt | - | \01_neocortex_framework\neocortex_framework.egg-info\SOURCES.txt | - |
| top_level.txt | - | \01_neocortex_framework\neocortex_framework.egg-info\top_level.txt | - |
| analyze_mcp_tools.py | - | \01_neocortex_framework\scripts\analyze_mcp_tools.py | - |
| create_lobes.py | - | \01_neocortex_framework\scripts\create_lobes.py | - |
| exhaustive_population.py | - | \01_neocortex_framework\scripts\exhaustive_population.py | - |
| extract_tools_final.py | - | \01_neocortex_framework\scripts\extract_tools_final.py | - |
| extract_tools_robust.py | - | \01_neocortex_framework\scripts\extract_tools_robust.py | - |
| fix_indentation.py | - | \01_neocortex_framework\scripts\fix_indentation.py | - |
| generate_all_manifests.py | - | \01_neocortex_framework\scripts\generate_all_manifests.py | - |
| generate_official_tool_manifest.py | - | \01_neocortex_framework\scripts\generate_official_tool_manifest.py | - |
| generate_tools_manifest.py | - | \01_neocortex_framework\scripts\generate_tools_manifest.py | - |
| inspect_config.py | - | \01_neocortex_framework\scripts\inspect_config.py | - |
| migrate_to_stores.py | - | \01_neocortex_framework\scripts\migrate_to_stores.py | - |
| neocortex_hud.py | - | \01_neocortex_framework\scripts\neocortex_hud.py | - |
| populate_memory.py | - | \01_neocortex_framework\scripts\populate_memory.py | - |
| saneamento_raiz.py | - | \01_neocortex_framework\scripts\saneamento_raiz.py | - |
| test_llm_backends.py | - | \01_neocortex_framework\scripts\test_llm_backends.py | - |
| update_ledger_with_tools.py | - | \01_neocortex_framework\scripts\update_ledger_with_tools.py | - |
| update_mcp_config.py | - | \01_neocortex_framework\scripts\update_mcp_config.py | - |
| update_mcp_config2.py | - | \01_neocortex_framework\scripts\update_mcp_config2.py | - |
| update_phase3_progress.py | - | \01_neocortex_framework\scripts\update_phase3_progress.py | - |
| NC-DOC-WL-001-hybrid-mode.md | - | \03_white_label_templates\NC-DOC-WL-001-hybrid-mode.md | - |
| NC-DOC-WL-001-readme.md | - | \03_white_label_templates\NC-DOC-WL-001-readme.md | - |
| Aqui está o prompt ajustado exatamente c.txt | - | \04_user_docs\Aqui está o prompt ajustado exatamente c.txt | - |
| cruzar com o roadmap.txt | - | \04_user_docs\cruzar com o roadmap.txt | - |
| LLM e API .md | - | \04_user_docs\LLM e API .md | - |
| 📁 SANITIZAÇÃO DA PASTA TURBOQUANT_V42 –.txt | - | \04_user_docs\📁 SANITIZAÇÃO DA PASTA TURBOQUANT_V42 –.txt | - |
| example_architecture.py | - | \05_examples\example_architecture.py | - |
| package.json | - | \05_examples\demo-api\package.json | - |
| README.md | - | \05_examples\demo-api\README.md | - |
| server.js | - | \05_examples\demo-api\src\server.js | - |
| benchmark_fractal_gauntlet.py | - | \05_examples\ollama-benchmark\benchmark_fractal_gauntlet.py | - |
| benchmark_master_suite.py | - | \05_examples\ollama-benchmark\benchmark_master_suite.py | - |
| README.md | - | \05_examples\ollama-benchmark\README.md | - |
| CONTINUE.md | - | \05_examples\ollama-benchmark\protocol\CONTINUE.md | - |
| QUICK_TEST.py | - | \05_examples\ollama-benchmark\protocol\QUICK_TEST.py | - |
| STATUS.md | - | \05_examples\ollama-benchmark\protocol\STATUS.md | - |

| NC-SVC-FR-011-ttl-manager.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-011-ttl-manager.py | - |
| NC-SVC-FR-009-session-buddy.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-009-session-buddy.py | - |
| NC-SVC-FR-018-tag-normalizer.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-018-tag-normalizer.py | - |
| NC-SVC-FR-016-wal-service.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-016-wal-service.py | - |
| NC-SVC-FR-010-kairos-service.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-010-kairos-service.py | - |
| NC-SVC-FR-007-state-machine.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-007-state-machine.py | - |
| NC-SVC-FR-017-crypto-hub.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-017-crypto-hub.py | - |
| NC-SVC-FR-012-channel-notifier.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-012-channel-notifier.py | - |
| NC-SVC-FR-015-task-broker.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-015-task-broker.py | - |
| NC-SVC-FR-005-event-bus.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-005-event-bus.py | - |
| NC-SVC-FR-004-cache-service.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-004-cache-service.py | - |
| NC-SVC-FR-006-metrics-collector.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-006-metrics-collector.py | - |
| NC-SVC-FR-014-dry-run-preview.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-014-dry-run-preview.py | - |
| NC-SVC-FR-003-savepoint-stub.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-003-savepoint-stub.py | - |
| NC-SVC-FR-008-config-validator.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-008-config-validator.py | - |
| NC-SVC-FR-002-health-service.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-002-health-service.py | - |
| NC-SVC-FR-001-logging-service.py | - | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-001-logging-service.py | - |
| NC-SCR-FR-061-engineer-documentacao.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-061-engineer-documentacao.py | - |
| NC-SCR-FR-066-bootup-sync.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-066-bootup-sync.py | - |
| NC-SCR-FR-003-manifest-factory.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-003-manifest-factory.py | - |
| NC-SCR-FR-001-populate-lobes-ssot.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-001-populate-lobes-ssot.py | - |
| NC-SCR-FR-017-visual-server.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-017-visual-server.py | - |
| NC-SCR-FR-023-ssot-auditor.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-023-ssot-auditor.py | - |
| NC-SCR-FR-005-auto-approve.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-005-auto-approve.py | - |
| NC-SCR-FR-060-courier-saneamento.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-060-courier-saneamento.py | - |
| NC-SCR-FR-008-queue-repair.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-008-queue-repair.py | - |
| NC-SCR-FR-061-courier-discrepancy-fix.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-061-courier-discrepancy-fix.py | - |
| NC-SCR-FR-007-queue-monitor.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-007-queue-monitor.py | - |
| NC-SCR-FR-080-governance-auditor.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-080-governance-auditor.py | - |
| NC-SCR-FR-062-engineer-encoding-fix.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-062-engineer-encoding-fix.py | - |
| NC-SCR-FR-024-structural-auditor.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-024-structural-auditor.py | - |
| NC-SCR-FR-011-sanitize-handoffs.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-011-sanitize-handoffs.py | - |
| NC-SCR-FR-062-tester-vector.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-062-tester-vector.py | - |
| NC-SCR-FR-081-config-migrator.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-081-config-migrator.py | - |
| NC-SCR-FR-006-ticket-validator.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-006-ticket-validator.py | - |
| NC-SCR-FR-002-tool-manifest-generator.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-002-tool-manifest-generator.py | - |
| NC-SCR-FR-064-artifact-catalog.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-064-artifact-catalog.py | - |
| NC-SCR-FR-098-health-wrapper.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-098-health-wrapper.py | - |
| NC-SCR-FR-022-coverage-auditor.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-022-coverage-auditor.py | - |
| NC-SCR-FR-021-lexicon-extractor.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-021-lexicon-extractor.py | - |
| NC-SCR-FR-013-validate-file.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-013-validate-file.py | - |
| NC-SCR-FR-009-sanitize-all-yamls.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-009-sanitize-all-yamls.py | - |
| NC-SCR-FR-004-governance-validator.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-004-governance-validator.py | - |
| NC-SCR-FR-012-new-tool.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-012-new-tool.py | - |
| NC-SCR-FR-063-tester-vector-fix.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-063-tester-vector-fix.py | - |
| NC-SCR-FR-010-sync-ticket-status.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-010-sync-ticket-status.py | - |
| NC-SCR-FR-075-genealogy-injector.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-075-genealogy-injector.py | - |
| NC-SCR-FR-020-yaml-injector.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-020-yaml-injector.py | - |
| NC-SCR-FR-051-knowledge-graph-builder.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-051-knowledge-graph-builder.py | - |
| NC-SCR-FR-103-mc-startup-hook.py | Mission Control startup hook — integra MC com NeoCortex MCP Server | \01_neocortex_framework\scripts\NC-SCR-FR-103-mc-startup-hook.py | NC-DS-103, AGENTE-B1 (deepseek-v4-flash), 2026-04-16 |
| NC-SCR-FR-103-start-with-mc.ps1 | PowerShell wrapper: Inicia NeoCortex MCP Server + Mission Control startup hook como jobs background | \01_neocortex_framework\scripts\NC-SCR-FR-103-start-with-mc.ps1 | NC-DS-103, AGENTE-B1 (deepseek-v4-flash), 2026-04-16, parent: NC-SCR-FR-103-mc-startup-hook.py |
| NC-SCR-FR-065-rename-impact-analyzer.py | - | \01_neocortex_framework\scripts\NC-SCR-FR-065-rename-impact-analyzer.py | - |
| NC-SCR-FR-113-kg-populate-lobes.py | Knowledge Graph population — popula KG a partir dos lobes/AKL (NC-DS-133 KG-002) | \01_neocortex_framework\scripts\NC-SCR-FR-113-kg-populate-lobes.py | kg, knowledge-graph, lobes |
| NC-SCR-FR-114-auto-categorize-lobes.py | Auto-categorização de lobes .mdc com Qwen 1.5b (NC-DS-148 SemanticCataloger) | \01_neocortex_framework\scripts\NC-SCR-FR-114-auto-categorize-lobes.py | semantic, categorize, qwen, lobes |
| NC-SCR-FR-115-guardian-daemon.py | Guardian Daemon — 7 módulos automáticos (Ciclo3: 5 steps/hora, Ciclo4: 6 steps/dia) | \01_neocortex_framework\scripts\NC-SCR-FR-115-guardian-daemon.py | guardian, daemon, automação, ciclos |
| NC-SCR-FR-116-guardian-service-installer.bat | Instalador do Guardian como serviço Windows (NSSM) | \01_neocortex_framework\scripts\NC-SCR-FR-116-guardian-service-installer.bat | guardian, windows-service, nssm |
| NC-SCR-FR-134-smoke-test-tools.py | Smoke test 40 MCP tools via MockMCP — score e relatório JSON (NC-DS-134 P1) | \01_neocortex_framework\scripts\NC-SCR-FR-134-smoke-test-tools.py | smoke-test, mcp, tools, validação |
| NC-SUPER-001-governance.py | Super-Tool governance: rule.list, compliance.report, cycle.archive_handoffs, yaml.sanitize, governance.full_audit, catalog.refresh, bootup.sync | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-001-governance.py | governance, compliance, audit |
| NC-SUPER-002-orchestration.py | Super-Tool orchestration: task.execute, agent.spawn, dispatch.create, workers.spawn | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-002-orchestration.py | orchestration, agent, task |
| NC-SUPER-003-memory.py | Super-Tool memory: cortex, lobes, knowledge, manifest, lexico.build/search/stats, semantic.categorize | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-003-memory.py | memory, lobes, lexico, semantic |
| NC-SUPER-004-state.py | Super-Tool state: checkpoint, regression, savepoint.create/list/rollback/diff (filesystem real), session, ledger | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-004-state.py | state, savepoint, rollback, checkpoint |
| NC-SUPER-005-llm-router.py | Super-Tool LLM router: gateway, route.call, ollama.ask, budget | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-005-llm-router.py | llm, router, ollama, budget |
| NC-SUPER-006-system.py | Super-Tool system: config, pulse, health, export, init | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-006-system.py | system, config, pulse, health |
| NC-SUPER-007-brain.py | Super-Tool brain: brain.think, brain.plan, brain.critique, brain.orchestrate | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-007-brain.py | brain, think, plan |
| NC-SUPER-008-context.py | Super-Tool context: context.budget_status, compress, prune, session.summarize | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-008-context.py | context, compress, budget |
| NC-SUPER-009-security.py | Super-Tool security: access.validate, lock.check, hook.register/trigger, audit.log | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-009-security.py | security, locks, hooks, audit |
| NC-SUPER-010-benchmark.py | Super-Tool benchmark: run.drift, run.titanomachy, run.omni, benchmark.status | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-010-benchmark.py | benchmark, drift, omni |
| NC-SUPER-011-notification.py | Super-Tool notification: push.send, push.list, push.clear, peers | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-011-notification.py | notification, push, peers |
| NC-SUPER-012-akl.py | Super-Tool AKL/KG: akl.add/search/export, kg.query/enrich/stats, consolidate | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-012-akl.py | akl, knowledge-graph, consolidate |
| NC-SUPER-013-health.py | Super-Tool health: server.health, log.errors, metrics.live, watchdog | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-013-health.py | health, metrics, watchdog |
| NC-SUPER-014-ledger.py | Super-Tool ledger: ledger.read/write/stats, agent.register/identity | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-014-ledger.py | ledger, agent, identity |
| NC-SUPER-015-memory-auto.py | Super-Tool memory-auto: turn.record, session.hot/stats/end, lobe.auto, catalog.now | \01_neocortex_framework\neocortex\mcp\tools\NC-SUPER-015-memory-auto.py | memory-auto, turn, session, catalog |
---

## 📜 3. Histórico de Versões e Changelog Core

### 🏗️ [2026-04-28 TARDE] — 7 Motores + 115 Regras + Tripla Auditoria

#### Novos Motores (FR-154 a FR-158)
- `NC-CORE-FR-154-corporate-engines.py`: KPIs (R56), ROI (R57), Compliance (R58). Health score 88.5 (B).
- `NC-CORE-FR-155-resiliency-engine.py`: Bulkhead, CQRS, FeatureToggle, GracefulDegradation, Backpressure (R65-R72).
- `NC-CORE-FR-156-ai-governance.py`: ModelCards, XAI, HITL, BiasDetector, RedTeam, AIAuditor (R74-R79).
- `NC-CORE-FR-157-bsc-swot.py`: BalancedScorecard + SWOTAnalyzer (R54-R55). 4 perspectivas.
- `NC-CORE-FR-158-system-integrity.py`: YAML, MDC Header, Secret Scan, Dead Code (R112-R115).

#### Gateway v3.0 + MULTILAYER 115 Regras
- Gateway: `ACTION_RULES` dict com 30+ mapeamentos para 11 ferramentas MCP.
- MULTILAYER: 133 regras (R01-R133) — v4.0, 10 blocos, 4 mordaças (H/C/S/U), 27 regras de governança integradas
- Matriz HONESTA: H 18/115, C 9/115, S 93/115, U 110/115.

#### Auditoria Tripla (ruff+mypy+pyright)
- RUFF 100% (80/80), MYPY PASS, PYRIGHT PASS — dupla segurança de type check.
- `audit.full`: 18 seções, scan completo em 80 arquivos .py.

#### Auto-Governança
- PulseScheduler `_auto_governance`: compliance+KPI+ruff+mypy automático a cada 300s.
- Pipeline FAIL-FAST: ruff + 3W + YAML + Secrets + handoff + RCA + catalog.
- 21 novas ações MCP: kpi.report, roi.analyze, bsc.report, swot.analyze, yaml.validate, secret.scan, etc.

#### Infra Final
- MCP: 21 tools, SSE :8766 | GW: 16/18 | Lobes: 70 (16 domínios) | Audit: 80.0% (72/90)

#### 15 Técnicas de Qualidade (FR-150 + FR-151)
- `NC-CORE-FR-150-techniques-audit.py`: Mapeamento 15 técnicas ↔ Conceitos Jurídicos
- `NC-CORE-FR-151-missing-techniques.py`: 5 motores — ThreeWEngine, EisenhowerEngine, ParetoEngine, OKREngine, IdempotencyGuard
- Técnicas ✅ (10/15): 5 Porquês, 4 Porquês Estratégico, RCA, 3 W's, PDCA, Eisenhower, Pareto, OKRs, Kaizen, Idempotência, RAG, Zero Trust
- Técnicas ⚠️ (5/15): DRY, KISS, Fail-Fast → implementados nesta sessão

#### FAIL-FAST (Prisão em Flagrante)
- `pyproject.toml`: Ruff expandido (E,F,I,B,C4,W → +SIM,UP,RUF,N,PLC,PLE), 1107→57 erros
- `NC-CORE-FR-148-submission-pipeline.py`: FAIL_FAST_ENABLED gate — ruff errors BLOCK submission
- Pipeline STEP 1 agora é GATE bloqueante + STEP 2 inclui 3 W's check

#### KISS (Art. 5º CF)
- `NC-CORE-FR-129-shared-kernel-gateway.py`: 6 blocos importlib → 1 helper `ConstitutionGateway._load()`

#### GATEWAY Expansion
- 8 tools wired: governance, orchestration, state, system, security, memory-auto, replication, evolution
- 16/18 tools com Gateway | 2 stubs (llm-router, picoclaw) → Fase 5 / MVP 1.0

#### Conectores Reais (FR-152 + FR-153)
- `NC-CORE-FR-152-eisenhower-real.py`: Eisenhower ↔ 163 tickets `DIR-DS-001-tickets/`
- `NC-CORE-FR-153-pareto-real.py`: Pareto ↔ WAL DB real `neocortex_wal.db`

#### SSOT (FR-149 expandido)
- 4 novas seções: calendar_ulq, performance, data_quality, token_cache, techniques
- 17 seções totais | Score 72.3% (60/83)

#### Lobes + Domínios
- `NC-LBE-FR-OKR-001.mdc` (06_governance): 5 KRs Q2 2026 com progresso
- `NC-LBE-FR-PDCA-001.mdc` (06_governance): CICLO 0-4 como PDCA formal
- `NC-LBE-FR-MEMORY-DOMAIN-001.mdc` (02_memory_lobes): Index do domínio (era vazio)
- `NC-LBE-FR-MACHINE-MEMORY-001.mdc` (05_machine_memory): Artifact registry (era vazio)

#### Scripts
- `NC-SCR-FR-inject-three-ws.py`: Auto-Injeção de 3 W's em 408 arquivos

#### Infraestrutura
- MCP: 21 ferramentas carregadas, SSE :8766 estável
- Checkpoints: 5 ativos | Lobes: 60→66 (2 domínios vazios populados)
- Enforcement: 4/4 camadas (H/C/S/U) | Rules: 42/42
- Gateway: 16/18 tools wired | Pipeline: FAIL-FAST active

---

## 🏗️ SSOT ESTRUTURAL — Mapas, Blueprints, Hierarquia e Organogramas

Documentos que capturam a arquitetura hierárquica, relações entre componentes e organograma do sistema.

| Nome | Descrição | Local | Tipo SSOT | Hierarquia |
|---|---|---|---|---|
| NC-MAP-FR-001-structural-maps.yaml | 6 mapas estruturais: organograma agentes, fluxo dados, 6 orbitais, rotinas pensamento, pipeline execução, hierarquia pastas | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-MAP-FR-001-structural-maps.yaml` | MAP | @MAPS |
| NC-ARC-FR-002-architecture-blueprint.yaml | Blueprint DDD 6 orbitais (STF, STJ, TJ, FÓRUM, EXECUTIVO, LEGISLATIVO) + Shared Kernel | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ARC-FR-002-architecture-blueprint.yaml` | ARC | @VISION |
| NC-ARC-FR-001-decision-log.md | 7 ADRs: MCP SSE, PYTHONPATH, PulseScheduler, ToolGuard, Super Tools, DDD 6 camadas, SSOT junction | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ARC-FR-001-decision-log.md` | ARC | @ADR |
| NC-ARC-COMPLIANCE-REPORT.md | Auditoria de conformidade arquitetural (20/30 conformes) | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-ARC-COMPLIANCE-REPORT.md` | ARC | — |
| NC-TODO-FR-001-roadmap.yaml | Roadmap v5.0 (YAML) — CICLO_1_5 (COMPLETED) + CICLO_6 (IN_PROGRESS) + CICLO_7+8 (PLANNED) | `\DIR-DS-000-agent-config\NC-TODO-FR-001-roadmap.yaml` | ROADMAP | @ROADMAP (v5.0) |
| NC-CFG-DS-001-agent-policy.yaml | Política de agente: roles, permissões, tiers | `\DIR-DS-000-agent-config\NC-CFG-DS-001-agent-policy.yaml` | CFG | @POLICY |
| NC-CFG-DS-002-session-contract.yaml | Contrato de sessão: handoff, TTL, checkpoint | `\DIR-DS-000-agent-config\NC-CFG-DS-002-session-contract.yaml` | CFG | — |
| NC-CFG-DS-003-coordination.yaml | Coordenação multi-agente: filas, locks, dispatch | `\DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml` | CFG | — |
| NC-CFG-DS-004-task-queue.yaml | Task queue: prioridades, retry, dead letter | `\DIR-DS-000-agent-config\NC-CFG-DS-004-task-queue.yaml` | CFG | — |
| NC-CORE-FR-125-tool-guard.py | Middleware 6 etapas: STEP0, LockGuard, Naming, SavePoint, CryptoSign, Audit | `\01_neocortex_framework\neocortex\core\NC-CORE-FR-125-tool-guard.py` | CORE | — |
| NC-CFG-FR-004-project-config-schema.yaml | Schema de configuração por projeto (.nc/config.yaml) | `\01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-config-schema.yaml` | CFG | — |
| NC-CFG-FR-004-project-config.py | Config loader com herança (global → .nc/local) | `\01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-config.py` | CORE | — |
| NC-CFG-FR-004-project-loader.py | Project loader: descobre .nc/config.yaml | `\01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-loader.py` | CORE | — |

### 🧬 HIERARQUIA VERTICAL — Organograma de Agentes

```
T0 (Supremo Juiz) ─── orquestra ───► GUARDIAN (T1, Supervisão)
                    ├── orquestra ──► ENGINEER (T2, Técnico)
                    │                  └── delega ──► COURIER (T2, Braçal)
                    ├── dispatch ───► DEEPSEEK T1 (via PicoClaw :18790)
                    └── reports ◄─── PULSE SCHEDULER (T2, auto 300s)
```

### 🔄 HIERARQUIA HORIZONTAL — 6 Orbitais DDD

```
SHARED KERNEL (Gateway: validate_action → STEP0 → LOCKS → ZONES → NAMING)
    │
    ├── STF (MODERADOR) — brain.think/plan/critique/orchestrate
    ├── STJ (SUPERIOR)  — llm_router.gateway/route/ollama
    ├── TJ  (JUSTIÇA)   — memory, state, context, memory_auto
    ├── FÓRUM (ADMIN)   — system, security, health, benchmark, notification, akl, ledger
    ├── EXECUTIVO       — orchestration (PicoClaw :18790 — OFFLINE)
    └── LEGISLATIVO     — governance (define regras para TODOS)
```

### 🧠 REGIÕES CEREBRAIS (Lobes → Domínios)

```
$FRONTAL   (planejamento)   → roadmap, tickets, governance, ADR
$TEMPORAL  (mem. semântica) → lexico, knowledge-graph, akl, ubiquitous-language
$PARIETAL  (integração)     → mcp-patterns, health, integrations, profiles
$OCCIPITAL (padrões)        → naming, manifests, architecture, cc-patterns
$CEREBELO  (automação)      → guardian, automation, benchmark, deployment
$HIPOCAMPO (mem. episódica) → sessions, savepoints, handoffs, audit
```

### 📦 REGISTROS COMPLEMENTARES SSOT

| Registro | Local | Conteúdo |
|----------|-------|----------|
| NC-NAM-FR-001-tools-registry.md | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main` | Catálogo de 21 tools MCP |
| NC-NAM-FR-001-lobes-registry.md | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main` | Registro de 75 lobes |
| NC-NAM-FR-001-config-registry.md | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main` | Registro de configurações |
| NC-NAM-FR-001-prompts-registry.md | `\01_neocortex_framework\DIR-DOC-FR-001-docs-main` | Registro de prompts de agente |

---

### 🛠️ [2026-05-03 23:20] — Fix merge config OpenCode + checkpoint sessão
- **Conflito resolvido**: `opencode.json` (local stdio) vs `opencode.jsonc` (remote :8770 SSE)
- **Unificado**: único `opencode.json` com local stdio + timeout 60000 + model deepseek
- **.jsonc removido**: config duplicado eliminado
- **SSOT atualizado**: NC-MAP-FR-001, NC-ARC-FR-002, NC-TODO-FR-001-roadmap.yaml incluídos como entradas SSOT
- **Hierarquia adicionada**: organograma vertical, 6 orbitais horizontais, regiões cerebrais
- **UBL @MAPS e @VISION**: agora referenciam corretamente NC-MAP-FR-001 e NC-ARC-FR-002
- **OpenCode docs**: 34/34 seções da documentação armazenadas no knowledge store

### 📐 [2026-05-03] — SSOT Estrutural: mapas, hierarquia e organogramas adicionados
- **NC-MAP-FR-001**: Adicionado como SSOT tipo MAP (6 mapas estruturais)
- **NC-ARC-FR-002**: Adicionado como SSOT tipo ARC (blueprint 6 orbitais DDD)
- **NC-TODO-FR-001-roadmap.yaml**: Adicionado como SSOT TODO ativo
- **NC-CFG-DS-001..004**: Adicionados como SSOT CFG (agent policies)
- **HIERARQUIA VERTICAL**: Organograma de agentes (T0 → Guardian → Engineer → Courier)
- **HIERARQUIA HORIZONTAL**: 6 orbitais DDD (STF, STJ, TJ, FÓRUM, EXECUTIVO, LEGISLATIVO)
- **REGIÕES CEREBRAIS**: Mapeamento $FRONTAL..$HIPOCAMPO → domínios
- **REGISTROS**: tools-registry, lobes-registry, config-registry, prompts-registry referenciados
- **Hash**: NC-NAM-FR-001-v1.3-20260503-9f8e2b1

### 🧬 [2026-04-27 23:59] - Sessão de Governança Intensiva — MCP estabilizado + 25 bugs + ToolGuard + Blueprint + Factory Vision

#### Correções (25 bugs)
- `NC-CORE-FR-102-agent-service.py`: import relativo → try/except absoluto
- `neocortex/mcp/server.py`: 4 prints stdout removidos, logging respeita env var, PulseScheduler/SessionManager desabilitados
- `NC-SUPER-009-security.py`: lock.list chave `locked_files` → `atomic_locks` (7 categorias)
- `neocortex/infra/metrics_store.py`: UUID para `metrics.id` (NOT NULL constraint)
- `NC-CORE-FR-108-config-service.py`: método `set()` adicionado
- `NC-CORE-FR-123-regression-service.py`: métodos `check()`, `set_baseline()` adicionados
- `NC-CORE-FR-117-lobe-service.py`: aliases `activate()`, `deactivate()` adicionados
- `NC-SUPER-001-governance.py`: rule.list 14→21, policy.check handler, G8 bootup.sync com ssot+compliance
- `NC-SUPER-004-state.py`: session.start handler, session.heartbeat pass-through, ToolGuard wire-up
- `NC-SUPER-006-system.py`: config.set handler, ToolGuard wire-up
- `NC-SUPER-003-memory.py`: search.advanced + knowledge.search com fallback real
- `NC-SUPER-013-health.py`: tools_count Path scope fix, metrics.live import fix
- `NC-SC-FR-104-neocortex-launcher.bat`: porta 8765→8766, Mission Control removido

#### Novos arquivos (14)
- `NC-CORE-FR-125-tool-guard.py`: middleware 6 etapas (STEP 0, LockGuard, Naming, SavePoint, CryptoSign, Audit)
- `NC-CORE-FR-126-search-service.py`: busca real em disco (lobes + docs)
- `NC-CORE-FR-127-knowledge-service.py`: store/search real
- `NC-CORE-FR-128-session-memory-writer.py`: substitui stub SessionMemoryWriter
- `NC-ARC-FR-002-architecture-blueprint.yaml`: Nível 0-1 DDD com 6 domínios
- `NC-ARC-COMPLIANCE-REPORT.md`: auditoria de conformidade (20/30 conformes)
- `NC-GRAND-PLAN-001-unified-master-plan.md`: 321 regras, 5 fases, genome
- `NC-FACTORY-SPEC-001.md`: 200 regras + 50 ideias para fábrica de software
- `NC-SOP-FR-001-session-startup.md`: SOP de início de sessão
- `NC-ARC-FR-001-decision-log.md`: 7 decisões arquiteturais (ADR)
- `NC-DS-IMPL-001-governance-sprint.yaml`: plano de implementação Bloco A
- `NC-LBE-FR-FACTORY-001.mdc`: lobe de memória da Factory
- `NC-LBE-FR-EVOLUTION-001.mdc`: lobe de memória da Evolução (DNA/RNA/replicação)
- `NC-LEXICO-LATEST.json`: catálogo semântico (40 lobes, 14 domínios)

#### Infraestrutura
- MCP: stdio→SSE remoto na porta 8766 (20 super tools estáveis)
- Junction `C:\TQ` → `C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42`
- OpenCode config: `~\.config\opencode\opencode.jsonc` → `http://localhost:8766/sse`
- Compliance: 93.8% (15/16) | Score: 62%→82%
- Checkpoints: 2093 | Lobes: 40 em 14 domínios
- Active track: EVOLUTION (resilience_first)

### 🚀 [2026-04-27] - Industrialização DDD + DeepSeek v4 + Bridge gRPC
- **_INDEX.yaml**: Criado mapeamento canônico para 8 domínios de lobes em `02_memory_lobes/`.
- **Directory Junctions**: Implementado `mklink /J` no script `@POPULATE` para vincular $brain_tags às pastas DDD.
- **DeepSeek v4**: Backend atualizado com suporte a `thinking_mode` e `multi_round_chat`.
- **OpenClaude gRPC Bridge**: Industrializada conectividade 100% operacional com a "Janela Lateral" via porta 50051 (NC-DS-202).
- **Governança**: Atualizado `@BOOT` e `@SSOT` com a nova arquitetura semântica e ativos gRPC.

### [2026-04-21] — Correção Crítica de Bypass de Governança MCP

#### Problema Identificado
- **Bypass Crítico**: Servidor mock `NC-SVC-FR-100-mcp-server.py` retornava "✅ Sucesso" fake para TODAS as ferramentas
- **Governança Ignorada**: Agentes HTTP (:8765/8766) podiam ignorar completamente regras .mdc
- **Sistema Duplo**: Mock server vs FastMCP real criavam inconsistência

#### Correções Aplicadas
1. **Mock Server Corrigido** (`NC-SVC-FR-100-mcp-server.py`):
   - Bypass "sucesso fake" ELIMINADO
   - Agora carrega regras .mdc do diretório `.agents/rules/`
   - Expõe ferramenta `neocortex_governance` com regras R01-R133
   - Mantém compatibilidade com clientes existentes

2. **FastMCP Real Patchado** (`neocortex/mcp/server.py`):
   - `mdc_loader.py` criado para carregamento automático de regras
   - Regras .mdc injetadas via `inject_rules_into_fastmcp()`
   - Log confirmado: "✅ Regras de governança .mdc injetadas no FastMCP"

#### Arquivos Criados/Modificados
| Nome | Descrição | Local | Status |
|---|---|---|---|
| NC-SCR-FR-151-compliance-audit.py | Auditoria inicial de compliance | antigravity/brain/ | CRIADO |
| NC-SCR-FR-152-fix-mcp-governance.py | Análise e plano de correção | antigravity/brain/ | CRIADO |
| NC-SCR-FR-157-final-fix.py | Correção final aplicada | antigravity/brain/ | CRIADO |
| NC-SCR-FR-158-test-mock-corrected.py | Testes do mock corrigido | antigravity/brain/ | CRIADO |
| NC-SCR-FR-159-test-fastmcp-real.py | Testes do FastMCP real | antigravity/brain/ | CRIADO |
| NC-SCR-FR-160-audit-compliance.py | Auditoria completa de compliance | antigravity/brain/ | CRIADO |
| mdc_loader.py | Carregador de regras .mdc | neocortex/mcp/ | CRIADO |
| server.py (patch) | Servidor FastMCP com regras | neocortex/mcp/ | MODIFICADO |
| NC-SVC-FR-100-mcp-server.py | Mock server corrigido | DIR-MCP-FR-001-mcp-server/ | MODIFICADO |

### [2026-04-20] — Automação Total e Alinhamento de Governança

#### Added
- **`NC-SCR-FR-134-smoke-test-tools.py`** — Smoke test 40 MCP Super-Tools via MockMCP. Valida 2-3 actions por tool, gera score e relatório JSON em `.neocortex/smoke_test_report.json` (P1 NC-DS-134).
- **`NC-SCR-FR-115-guardian-daemon.py`** expandido: `Ciclo3Runner` (5 steps/hora: catalog, bootup, yaml, lexico.build, cascade) e `Ciclo4Runner` (6 steps/dia: governance.full_audit, archive, lobe.populate, kg.enrich, semantic.categorize, smoke_test).
- **`savepoint.create`** — Snapshot filesystem real (ledger.json + cortex.json + guardian_state.json) salvo em `.neocortex/savepoints/{name}.json`.
- **`savepoint.rollback`** — Restore real dos snapshots com auto-backup pré-rollback (P4 NC-DS-100 SEC-402).
- **`savepoint.diff`** — Comparação estado atual vs snapshot para auditoria pré-rollback.
- **`semantic.categorize`** (NC-SUPER-003) — Action MCP que dispara NC-SCR-FR-114 via subprocess para categorizar todos os lobes com Qwen 1.5b (P3 NC-DS-148).
- **SSOT atualizado** — 15 NC-SUPER-001..015 + NC-SCR-FR-113/114/115/116/134 registrados na tabela SSOT.

#### Changed
- **`NC-SUPER-003-memory.py`** — Adicionados `import json`, `semantic.categorize` action. F401 lobe_result removido.
- **`NC-SUPER-004-state.py`** — savepoint.create/list/rollback/diff reescritos com filesystem primeiro (sem depender de get_savepoint_service). F401 List removido.

#### Notes
- **Cobertura automação Guardian**: Ciclo3 5 steps/hora + Ciclo4 6 steps/dia = 11 processos automáticos diários.
- **STEP-0 limpo**: py_compile 0 + ruff F 0 em todos os 4 arquivos modificados.
- **Fase LEXICO-001 concluída**: LexicoService 1041 termos, 27 lobes, integrado ao Ciclo3 (step 4).

### [2026-04-17] — Resolução Conflito de Portas e Orquestração Unitária

#### Added
- **Mapeamento de portas NeoCortex (16 portas)** — Definido orquestrador unitário com 8 portas para serviços core e 8 portas para comunicação A2A, documentado em NC-BOOT-FR-001.
- **Health wrapper (NC-SCR-FR-098)** — Implementado e handoff aprovado (NC-DS-098).

#### Changed
- **Pixel Agents porta alterada** — De `:8765` para `:8767` para liberar porta core MCP Server. Atualizado em NC-BOOT-FR-001, NC-WF-001, NC-LBE-INT-005 e NC-GOV-FR-004.
- **Registro de handoff NC-DS-098** — Ticket de health wrapper marcado %DONE no roadmap.

#### Fixed
- **Conflito de portas 8765** — NeoCortex MCP Server mantém porta 8765; Pixel Agents movido para 8767, permitindo operação simultânea.
- **Documentação de acesso no Ciclo 1** — NC-WF-001 atualizado com porta correta para Pixel Agents.

### [2026-04-16] — Ciclo 1 Conclusão, Protocolo T0 e Handoffs

#### Added
- **Protocolo T0 de auditoria de handoff** (NC-DS-116) — Adicionado bloco obrigatório de 7 passos ao NC-WF-001 v3.6 para validação técnica (py_compile, ruff) antes de marcar %DONE.
- **Handoffs para tickets pendentes** — NC-DS-099, 100, 101, 102, 114 (APPROVED), 108, 110 (FAILED) com validação de conformidade.
- **Correção de importação de tools MCP** — Recriação dinâmica de `neocortex/mcp/tools/__init__.py` para mapear nomes curtos (cortex, ledger, etc.) para módulos NC-TOOL-FR-*.

#### Changed
- **Script de inicialização NC-SCR-FR-103b** — Substituído `Start-Job` por `Start-Process` com redirecionamento de logs separados (stdout/stderr) para monitoramento robusto.
- **Servidor MCP (`server.py`)** — Comentadas importações estáticas problemáticas (linhas 25-44) e ajustada lógica de transporte (websocket → SSE fallback).
- **NC-WF-001 (Workspace Routine)** — Atualizado para v3.6 com protocolo T0 integrado no Ciclo 2.

#### Fixed
- **Erros de lint (F401, I001)** em 3 arquivos Python via `ruff --fix`: NC-TOOL-FR-034-dry-run.py, NC-SVC-FR-003-savepoint-stub.py, NC-SCR-FR-101-tools-smoke-test.py.
- **Validação de handoffs** — Aplicado protocolo T0 para garantir `compile_ok: true` e `ruff_ok: true` antes de aprovação.

#### Notes
- **PicoClaw desativado** conforme solicitação — porta 18790 fechada, processo terminado.
- **Mission Control ativo** na porta 3000 — hook de startup executado.
- **Servidor MCP hospedado** (PID 32736) mas porta 8765 não respondendo — diagnóstico pendente.
- **Catálogo de artefatos atualizado** — 529 arquivos .py, 403 .yaml (gerado em 2026-04-16T18:41:47).

### [2026-04-11] — Sessão de Modularização de Regras e Linguagem Ubíqua (Parte 3)

#### Added
- `NC-DOC-FR-001-ubiquitous-language-dictionary.md` — Dicionário de Linguagem Ubíqua com símbolos @$% (57 entradas). Inclui NC-READ-HASH de deduplicação.
- `NC-CFG-FR-002-rules-policy.yaml` — Policy-as-Code companion dos arquivos MDC. Machine-readable: `critical_rules`, `write_zones`, `read_dedup` checkpoints, `ubiquitous_language`, `llm_tiers`.
- `.agents/rules/NC-RULE-001-core-ssot.mdc` — Regras core, always-on, < 50 linhas. Inclui NC-READ-HASH para evitar re-leitura.
- `.agents/rules/NC-RULE-002-python-mcp.mdc` — Regras Python/MCP com globs `**/*.py`. Inclui exemplos de código para importação, paths e logger.
- `.agents/rules/NC-RULE-003-lobes-memory.mdc` — Regras de lobos com globs `**/lobes/**`. Inclui mapa de lobos, isolamento, API LobeService.
- `.agents/rules/NC-RULE-004-filesystem.mdc` — Regras de filesystem com globs `**/DIR-*/**`. Inclui zonas de escrita, hierarquia numérica, checklist de criação.

#### Changed
- `.agents/rules/neocortexrules.md` — Reescrito como índice master v3: mapa de módulos MDC, tabelas @$% de linguagem ubíqua, NC-READ-HASH dedup, 20 regras compactas com referências @$%.

### [2026-04-11] — Sessão de Industrialização e Governança (Parte 2)

#### Added
- `NC-APP-FR-001-technical-appendix.md` — Apêndice técnico: inventário de 30+ ferramentas, ações MCP, bibliotecas, LLMs, políticas de roteamento e fluxo de orquestração. Ticket: OPT documentação.
- `NC-PROMPT-FR-001-master-context.md` (raiz) — Master Context Prompt v2 com mapa de lobos, comandos de busca, tiers LLM e princípio de economia de tokens.
- `NC-CFG-FR-001-agent-policy-template.yaml` — Template de política de agente: `allowed_tools`, `forbidden_actions`, `limits.*`, mentor mode, isolamento de lobe. Ticket: SEC-403.
- `NC-SEC-FR-001-atomic-locks.yaml` — Lista centralizada de arquivos protegidos para o SecurityService (6 categorias + exceções por role). Ticket: SEC-401.
- `NC-SOP-FR-001-session-startup.md` — Procedimento Operacional Padrão de inicialização de sessão NeoCortex (5 passos + checklist de encerramento).
- `NC-ARC-FR-001-decision-log.md` — Architecture Decision Records com 8 ADRs (pyspeedb, FTS5, DuckDB, diskcache-rs, FastMCP, Qwen 1.5B, msgspec, Arquitetura de Lobos).
- `NC-SCR-FR-001-populate-lobes-ssot.py` (scripts/) — Script de poblamento automático dos lobos a partir dos arquivos SSOT via LobeService. Suporta `--dry-run`. 12 entradas mapeadas.
- `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` — Manifesto universal de boot: qualquer IA deve ler antes de agir. Contém mapa de lobos, arquitetura de agentes, nomenclatura, proibições e tickets abertos.
- `NC-LBE-FR-ARCHITECTURE-001.mdc` (gerado via script) — Lobo de memória indexado: Roadmap + Naming Convention + Apêndice Técnico + ADRs.
- `NC-LBE-FR-SECURITY-001.mdc` (gerado via script) — Lobo de memória indexado: Atomic Locks + Agent Policy + SOP de Sessão + Sanitization Checklist.

#### Changed
- `neocortex/mcp/sub_server.py` — **AGENT-203 implementado**: `mentor_step_0()` com `identify_relevant_lobes` (mapeamento role+keyword → lobos), `extract_relevant_snippet` (scoring FTS5 por parágrafos), `handle_task` com logging detalhado via `neocortex.mentor` logger.
- `NC-APP-FR-001-technical-appendix.md` — Inventário completo de 7 categorias (DB, Cache, Busca, LLM, Orquestração, Dev, Aux) adicionado.
- `NC-SCR-FR-001-populate-lobes-ssot.py` — Mapeamento expandido com NC-CFG-FR-001, NC-SEC-FR-001, NC-SOP-FR-001, NC-ARC-FR-001.
- `NC-NAM-FR-001-naming-convention.md` (este arquivo) — Changelog duplicado removido; entrada expandida adicionada.

#### Fixed
- Duplicação do bloco de changelog removida (linhas 396-423 redundantes eliminadas).
- Stub `mentor_step_0()` substituído pela implementação real com LobeService.

### [2026-04-11] — Sessão de Industrialização e Governança (Parte 1)

#### Added
- Ferramenta MCP `neocortex_brain` para integração com DeepSeek API como T-0 Assistente instalada.
- Documento-Mestre criado: Este documento passa agora a consolidar o changelog, Naming Convention e Project Map centralmente limitando fragmentação indesejada.
- Scripts de PowerShell e Batch `start_neocortex_mcp` regerados apontando para carregamento em módulo do novo Host (ex: `-m neocortex.mcp.server`).
- Servidor MCP: varredura dinâmica foi implantada com resiliência autônoma à mutação de diretorias.

#### Changed
- Consolidados todos os 3 roadmaps (v5.0 Macro, v6.0 Stability e Translation original) em um **único** arquivo de roadmap inquebrável (`NC-TODO-FR-001-project-roadmap-consolidated.md`).
- A estruturação da pasta `neocortex_framework/` foi refatorada e indexada segundo subdiretórios padrão `DIR-*-FR-*`.

#### Fixed
- Erro fatal do servidor MCP na inicialização (`FastMCP.run() got an unexpected keyword argument 'host'`). Corrigido adaptando o modelo SSE nativo sobre protocolo WebSocket e implementando o objeto em instância sincrônica.
- `RuntimeError` originado pelo pacote FastMCP por colisões de pools do `asyncio` e bibliotecas AnyIO nativas.
- Erros de Windows Prompt charset originados da tentativa de codificação nativa CP1252 em Emojis.

### [2026-04-10]
#### Added
- Integração pioneira do MetricsStore com backend em banco de dados DuckDB (OPT-010). Testado ativamente em suite `test_sanity.py` atestando 11 hits com sucesso transacional em memória e logs reportados.
- Inventário MCP processado diagnosticando e documentando 22 ferramentas (STUBS e acionáveis) passíveis de deleque/restauração arquitetural em fase.

### [2026-04-08]
#### Added
- Start técnico oficial do branch de aprimoramento orgânico logístico do TurboQuant v4.2 instanciando as raízes primárias MCP e consolidando o T-0 Assistant.

## NC-DS-122 — Novas Entradas core/ (2026-04-20)

| Nome | Descrição | Local | Tags |
|---|---|---|---|
| NC-CORE-FR-101-agent-policy-enforcer.py | Agent policy enforcement service | neocortex/core/ | core,policy,agent |
| NC-CORE-FR-102-agent-service.py | Agent lifecycle management service | neocortex/core/ | core,agent,lifecycle |
| NC-CORE-FR-103-akl-service.py | AKL (Adaptive Knowledge Layer) service | neocortex/core/ | core,akl,knowledge |
| NC-CORE-FR-104-benchmark-service.py | Benchmark execution and reporting service | neocortex/core/ | core,benchmark |
| NC-CORE-FR-105-cascade-consolidator.py | Cascade consolidation orchestrator | neocortex/core/ | core,consolidation |
| NC-CORE-FR-106-checkpoint-service.py | Checkpoint save/restore service | neocortex/core/ | core,checkpoint,state |
| NC-CORE-FR-107-circuit-breaker.py | Circuit breaker pattern implementation | neocortex/core/ | core,circuit-breaker,reliability |
| NC-CORE-FR-108-config-service.py | Configuration management service | neocortex/core/ | core,config |
| NC-CORE-FR-109-consolidation-service.py | Data consolidation service | neocortex/core/ | core,consolidation |
| NC-CORE-FR-110-cortex-service.py | Cortex state management service | neocortex/core/ | core,cortex,state |
| NC-CORE-FR-111-export-service.py | Data export service | neocortex/core/ | core,export |
| NC-CORE-FR-112-file-utils.py | File utility helpers (13 importers) | neocortex/core/ | core,utils,files |
| NC-CORE-FR-113-init-service.py | System initialization service | neocortex/core/ | core,init |
| NC-CORE-FR-114-kg-service.py | Knowledge graph service | neocortex/core/ | core,kg,knowledge-graph |
| NC-CORE-FR-115-ledger-service.py | Ledger tracking service (12 importers) | neocortex/core/ | core,ledger,tracking |
| NC-CORE-FR-116-lexico-service.py | Lexico semantic service | neocortex/core/ | core,lexico,semantic |
| NC-CORE-FR-117-lobe-service.py | Memory lobe management service (10 importers) | neocortex/core/ | core,lobes,memory |
| NC-CORE-FR-118-manifest-service.py | Manifest generation service | neocortex/core/ | core,manifest |
| NC-CORE-FR-119-peers-service.py | Peer discovery and sync service | neocortex/core/ | core,peers,network |
| NC-CORE-FR-120-profile-manager.py | User profile manager | neocortex/core/ | core,profile,user |
| NC-CORE-FR-121-profile-service.py | Profile CRUD service | neocortex/core/ | core,profile |
| NC-CORE-FR-122-pulse-scheduler.py | Pulse heartbeat scheduler (6 importers) | neocortex/core/ | core,pulse,scheduler |
| NC-CORE-FR-123-regression-service.py | Regression testing service | neocortex/core/ | core,regression,testing |
 | NC-CORE-FR-124-security-service.py | Security validation service | neocortex/core/ | core,security |

## NC-SCR-FR-157 — Correção de Bypass de Governança (2026-04-21)

### [2026-04-21] — Correção Crítica de Bypass de Governança MCP

#### Problema Identificado
- **Bypass Crítico**: Servidor mock `NC-SVC-FR-100-mcp-server.py` retornava "✅ Sucesso" fake para TODAS as ferramentas
- **Governança Ignorada**: Agentes HTTP (:8765/8766) podiam ignorar completamente regras .mdc
- **Sistema Duplo**: Mock server vs FastMCP real criavam inconsistência

#### Correções Aplicadas
1. **Mock Server Corrigido** (`NC-SVC-FR-100-mcp-server.py`):
   - Bypass "sucesso fake" ELIMINADO
   - Agora carrega regras .mdc do diretório `.agents/rules/`
   - Expõe ferramenta `neocortex_governance` com regras R01-R133
   - Mantém compatibilidade com clientes existentes

2. **FastMCP Real Patchado** (`neocortex/mcp/server.py`):
   - `mdc_loader.py` criado para carregamento automático de regras
   - Regras .mdc injetadas via `inject_rules_into_fastmcp()`
   - Log confirmado: "✅ Regras de governança .mdc injetadas no FastMCP"

3. **Arquitetura Unificada**:
   ```
   [ANTES] Mock Server → Bypass total
   [AGORA] Mock Server Corrigido → Carrega regras .mdc
           ↓
          FastMCP Real → Regras injetadas (stdio)
   ```

#### Arquivos Criados/Modificados
| Nome | Descrição | Local | Status |
|---|---|---|---|
| NC-SCR-FR-151-compliance-audit.py | Auditoria inicial de compliance | antigravity/brain/ | CRIADO |
| NC-SCR-FR-152-fix-mcp-governance.py | Análise e plano de correção | antigravity/brain/ | CRIADO |
| NC-SCR-FR-157-final-fix.py | Correção final aplicada | antigravity/brain/ | CRIADO |
| NC-SCR-FR-158-test-mock-corrected.py | Testes do mock corrigido | antigravity/brain/ | CRIADO |
| NC-SCR-FR-159-test-fastmcp-real.py | Testes do FastMCP real | antigravity/brain/ | CRIADO |
| NC-SCR-FR-160-audit-compliance.py | Auditoria completa de compliance | antigravity/brain/ | CRIADO |
| mdc_loader.py | Carregador de regras .mdc | neocortex/mcp/ | CRIADO |
| server.py (patch) | Servidor FastMCP com regras | neocortex/mcp/ | MODIFICADO |
| NC-SVC-FR-100-mcp-server.py | Mock server corrigido | DIR-MCP-FR-001-mcp-server/ | MODIFICADO |

#### Resultados da Auditoria
- ✅ **Regras .mdc**: 8 arquivos carregados (NC-RULE-001 a 008)
- ✅ **Mock Server**: Bypass eliminado, regras expostas
- ✅ **FastMCP Real**: Patches aplicados, regras injetadas
- ⚠️ **Config Antigravity**: JSON corrompido (necessita correção)
- ⚠️ **OpenCode Naming**: 1 arquivo fora do padrão

#### Próximos Passos
1. Corrigir configuração do Antigravity (JSON corrompido)
2. Renomear `NC-DS-FR-122-lobe-migration-report.md` para padrão NC-SCR
3. Testar Antigravity com servidores corrigidos
4. Validar fluxo completo de governança

> **Executor**: OpenCode (T1) com supervisão T0  
> **Status**: Bypass ELIMINADO, Governança ATIVADA  
> **Referência**: @BOOT R01-R133, @SSOT, @LOCKS, @RULES-MULTILAYER (NC-LBE-FR-RULES-MULTILAYER-001 v4.0, 10 blocos, 4 mordaças, 27 regras de governança)
| NC-SCR-FR-147-nc-ds-122-executor.py | Script executor seguro NC-DS-122 (rename+shim) | scripts/ | scripts,rename,core,nc-ds-122 |

#### Novos Motores (FR-161 a FR-165)
- NC-CORE-FR-161-regulatory-compliance.py: R104-R111 — EU AI Act, NIST, Singapore, RDI, Layered Translation
- NC-CORE-FR-162-strangler-fig.py: R68 — Migration tracker de ferramentas
- NC-CORE-FR-163-ssot-reporter.py: R117 — Gera header SSOT dinamico do estado do sistema
- NC-CORE-FR-164-claim-validator.py: R21+R41+R42+R53 — Valida claims do assistente contra evidencia
- NC-CORE-FR-165-semantic-router.py: Coracao do sistema — roteador universal baseado no catalogo semantico

- NC-CORE-FR-166-domain-routers.py: R118 — Domain Routers (DDD 2-level semantic index)

- NC-CORE-FR-167-semantic-guardian.py: R119 — Semantic Guardian (lobe/catalog/memory health agent)
- NC-CORE-FR-168-semantic-audit.py: Deep Semantic Cross-Reference Audit (redundancias, orfaos, fragmentacao)
- ALCOA++ (R83): WAL integrity check — Attributable, Legible, Contemporaneous, Original, Accurate

---

## 🎯 GUIA OPERACIONAL POR TIER (UBL # → 3W + RCA + KISS)

> **Path resolver:** `NC-LEXICO-LATEST.json` v4.0 (69 serviços `#`).  
> **Rotinas:** `NC-MAP-FR-001` (R0-R8). **Regras:** NC-RULE-009 (R01-R117).  
> **Modelo:** T0=DeepSeek V4 Pro, T2=Qwen 3B/1.5B (Ollama :11434), TG=Qwen 1.5B.

### 🟣 T0 — JUIZ SUPREMO (DeepSeek V4 Pro)

| 3W | RCA | KISS |
|----|-----|------|
| **WHAT:** Orquestrar, auditar, aprovar | **5 Porquês** em toda divergência | Delegar braçal ao Courier |
| **WHY:** Evidência do Regression Buffer + WAL | Se score <70%: RCA urgente | Uma aprovação por vez |
| **WHERE:** @SSOT + @BOOT + NC-LEXICO | Causa raiz → ticket NC-DS-* | Não reimplementar o que já existe |

| # Serviços | Propósito | STEP 0 |
|-----------|-----------|--------|
| `#GATEWAY` | validate_action() — barreira central | Verificar se todos os 15 checks passam |
| `#TOOLGUARD` | Pipeline: STEP0→LockGuard→Naming→SavePoint→CryptoSign→Audit | Rodar em modo `--dry-run` antes |
| `#SECURITY` | Atomic locks + Write Zones | Verificar @LOCKS antes de autorizar |
| `#GOV` | 46 ações MCP de governança | `rule.list` → `compliance.report` |
| `#AUDIT3L` | Auditoria 3 camadas (compile+runtime+operational) | `ruff check` + `mypy` + `py_compile` |
| `#DOMROUTER` | Roteador semântico (8 domínios, 763 itens) | Verificar catálogo < 24h |
| `#BRAIN` | Pensamento estratégico (think/plan/critique) | Delegar ações ao #ORCH |

**Rotina T0:** `R0_BOOT → R1_3W → R2_EISENHOWER → R5_PDCA → R7_HANDOFF → R8_OKR_ROI`

### 🟢 T2 COURIER — BRAÇAL (Qwen 1.5B)

| 3W | RCA | KISS |
|----|-----|------|
| **WHAT:** Renomear, povoar, arquivar, handoff | Se falhar: reportar ao T0 com log | 1 tarefa por invocação |
| **WHY:** SSOT desatualizado — seguir @SSOT | Não repetir erro do Regression Buffer | nc-validate ANTES de entregar |
| **WHERE:** machine_memory, DIR-ARC, DIR-DS-002 | Causa visível no stdout | Não criar — só mover/renomear |

| # Serviços | Propósito | STEP 0 |
|-----------|-----------|--------|
| `#POPULATE` (NC-SCR-FR-001) | Povoar lobes com conteúdo SSOT | `python --version` + `ruff --version` |
| `#SSOTREP` | Gerar header SSOT do estado atual | `neocortex_state regression.check` |
| `#SAVEPOINT` | Snapshot antes de escrever | `savepoint.create` antes de qq alteração |
| `#WATCHER` | Registrar toda ação no CentralWatcher | Verificar se watcher está ativo |
| `#ULQREG` | Cross-reference ULQ tags → paths | `Auto-Registry: true` |

**Rotina Courier:** `R0_BOOT → R5_EXECUTE → R6_VERIFY(ruff+py_compile) → R7_HANDOFF`

### 🟡 T2 ENGINEER — TÉCNICO (Qwen 3B)

| 3W | RCA | KISS |
|----|-----|------|
| **WHAT:** Analisar, propor refatoração, depurar | 5 Porquês em toda análise | Propor diff, NUNCA aplicar sem T0 |
| **WHY:** Regressão detectada? Código duplicado? | Rastrear causa até módulo origem | Menos de 2500 chars na proposta |
| **WHERE:** neocortex/core/, services/, hooks/ | Documentar achado no handoff | Reutilizar # existentes |

| # Serviços | Propósito | STEP 0 |
|-----------|-----------|--------|
| `#RCA` | Root Cause Analysis (5 Porquês) | Verificar Regression Buffer antes |
| `#PIPELINE` | Pipeline de submissão (FAIL-FAST) | `ruff check` + `py_compile` |
| `#INTEGRITY` | YAML, MDC, Secrets, DeadCode scan | Rodar scan completo |
| `#EISENHOWER` | Priorização de 163 tickets | `neocortex_state regression.check` |
| `#PARETO` | 80/20 análise de causas | Cruzar com WAL DB real |
| `#REGRESSION` | Buffer de regressão | Verificar baseline antes de propor |

**Rotina Engineer:** `R0_BOOT → R1_3W → R4_KISS_DRY → R5_PDCA → R6_VERIFY → R7_DELIVER(diff+T0 aprova)`

### 🔵 TG GUARDIAN — VALIDAÇÃO (Qwen 1.5B)

| 3W | RCA | KISS |
|----|-----|------|
| **WHAT:** Fiscalizar @LOCKS, zonas, naming | Se violação: investigar PADRÃO | Reportar PASS/FAIL com evidência |
| **WHY:** Prevenir corrupção de estado | RCA nos 5 Porquês | Não corrigir — só reportar |
| **WHERE:** Todos os arquivos tocados na sessão | Documentar no WAL + Regression | 1 relatório por ciclo |

| # Serviços | Propósito | STEP 0 |
|-----------|-----------|--------|
| `#HOOKS` | HookRegistry — PreToolUse/PostToolUse/ToolError | `neocortex_governance lock.validate` |
| `#LOCKGUARD` | Bloquear escrita em @LOCKS | Verificar server.py, sub_server.py, NC-NAM-FR-001 |
| `#SEMGUARD` | Saúde semântica (lobes/catalog/memory a cada 300s) | `neocortex_memory lobe.auto` |
| `#BASHGUARD` | Bloquear comandos perigosos (rm, del) | Validar regex de comandos |
| `#DELGUARD` | Bloquear qualquer deleção (R05) | Interceptar antes do filesystem |
| `#WALSVC` | Write-Ahead Log — toda ação registrada | Verificar WAL integrity |

**Rotina Guardian:** `R0_BOOT → R6_VERIFY(4 mordaças: H/C/S/U) → R7_DELIVER(PASS/FAIL)`

### ⚪ AUDITOR — COMPLIANCE (DeepSeek V4 Pro)

| # Serviços | Propósito | Ciclo |
|-----------|-----------|-------|
| `#CLAIM` | Validar claims do assistente contra evidência real | Toda sessão |
| `#INTEGRITY` | YAML + MDC + Secret + DeadCode scan | CICLO 4 (semanal) |
| `#CRYPTO` | Hash SHA-256 de integridade + encoding scan | CICLO 4 |
| `#SEMANTIC` | Deep Semantic Cross-Reference Audit | Mensal |
| `#GENOME` | Replicação governada de agentes | Sob demanda |

### 🔗 RESOLUÇÃO DE PATHS (UBL como fonte única)

```
Agente referencia:     #TOOLGUARD
         ↓
NC-LEXICO-LATEST.json: services."#TOOLGUARD".path
         ↓
Resolve para:           neocortex/core/NC-CORE-FR-125-tool-guard.py
```

**Regra:** NENHUM código, ticket, agente ou documento deve hardcodar paths. SEMPRE usar `#` + resolver via LEXICO.
