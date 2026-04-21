# NC-NAM-FR-001 - Convenes de Nomenclatura, Mapa e Changelog do Projeto NeoCortex

> **Documento Unificado Oficial:** Este artefato consolida a Arquitetura do Projeto (Project Map), o Catlogo Geral de Nomenclaturas e Prefixos, e o Histrico Central (Changelog) da plataforma NeoCortex.
> **Data Refncia:** 2026-04-11

---

##  1. Estrutura de Diretrios Proposta e Mapa do Projeto

O projeto utiliza um design de pastas modulares governado por prefixos restritos `DIR-<tipo>-FR`, abrigando o pacote central da framework `neocortex` rigidamente separado.

```
 TURBOQUANT_V42/
  README.md (descrio do propsito central)
  antigravity_neocortex_config.json (configurao IDE para MCP padro STDIO)
  start_neocortex_mcp.bat (Inicializador Windows WS do Host Principal)
  start_neocortex_mcp.ps1 (Inicializador Powershell WS do Host Principal)
  neocortex_framework/ (ncleo do framework isolado)
     __init__.py
     neocortex/ (cdigo fonte principal de rotas e agentes)
        config.py (ConfigProvider)
        core/ (servios de domnio - Services / Schedulers)
        infra/ (repositrios de conectividade com stores DB e Caches)
        agent/ (agentes autnomos internos isolados, eg. Courier / Engineer)
        mcp/ (servidor e conexo MCP via Transporte)
            server.py (Host principal em SSE)
            sub_server.py
            tools/ (17+ ferramentas de gesto T-0 conformadas como NC-TOOL)
     DIR-PRF-FR-001-profiles-main/ (perfis de usurio)
     DIR-DOC-FR-001-docs-main/ (documentao vital e roadmaps de arquitetura)
     DIR-ARC-FR-001-archive-main/ (arquivos obsoletos transferidos pelo OpenCode)
     DIR-BAK-FR-001-backup-main/ (backups antigos originados da raiz)
     DIR-CFG-FR-001-config-main/ (arquivos sensveis como config.yaml)
     DIR-TEST-FR-001-tests-main/ (suite de validao e testes de sanidade)
     DIR-TMP-FR-001-templates-main/ (templates resguardados)
     DIR-MCP-FR-001-mcp-server/ (scripts satlites da arquitetura Server principal)
  memory_lobes/ (lobos ativos / dados de persistncia viva)
  .agents/ (regras e workflows autnomos do OpenCode/Antigravity)
  white_label/ (templates para instanciamento modular)
```

---

##  2. Padro de Nomenclatura de Arquivos e Pastas

Formato Base: `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`  
Formato Diretrio Base: `DIR-<TIPO>-<SIGLA>-<NUM>-<desc>`

| Elemento | Descrio | Exemplos |
| :--- | :--- | :--- |
| **NC** | Prefixo fixo para Arquivos (NeoCortex) | NC |
| **DIR** | Prefixo fixo para Diretrios Estruturais | DIR |
| **<TIPO>** | Categoria base da operao do arquivo/pasta | MCP (Server), TOOL (Ferramenta), CORE (Servio), INFRA (Infra), DOC (Documentos), PRF (Perfil), TKT (Ticket), ARC (Arquivo Obsoleto), BAK (Backup), CFG (Configurao), TEST (Testes), TMP (Templates) |
| **<SIGLA>** | Abreviao do propsito contextual | FR (Framework Geral), WL (White Label), USR (Usurio) |
| **<NUM>** | Nmero sequencial (3 dgitos) por mdulo | 001, 002, 020 |
| **<desc>** | Descrio curta em kebab-case intuitiva | cortex-tool, mcp-server |

### Catlogo Primrio de Prefixos Praticados
- `NC-MCP-FR-001-*`: Componentes e rotas vitais do ncleo servidor Model Context Protocol.
- `NC-TOOL-FR-<NUM>-*`: Qualquer ferramenta legvel pela Interface MCP (Ex: `NC-TOOL-FR-000-brain.py`, `NC-TOOL-FR-008-ledger.py`).
- `NC-CORE-FR-001-*`: Servios e Orquestradores localizados em `/core`.
- `NC-DOC-FR-001-*`: Relatrios fixos, Checklists ou Planejamentos Estratgicos (Como este documento e Roadmaps).
- `NC-PRF-USR-XXX-*`: Profile rules localizados no `DIR-PRF-FR`.

### Regras Ouro para Manuteno
1. **Novas Ferramentas**: Se a ferramenta no puder ser consolidada num `NC-TOOL` englobador j existente, deve nascer sob a prxima numerao livre na pasta `/tools/`.
2. **Arquivos Obsoletos**: Devem ser arrastados para `DIR-ARC-FR-001-archive-main` no sofrendo *apenas* modificao e remoo direta da raiz pra precaver vazamento de dependncias escondidas.
3. **Logs**: Devem ser descartados perante limite da HotCache de 5. Backups temporais no geram commit, moram em `DIR-BAK-FR-001-backup-main`.

---

##  SSOT Geral do Sistema (Snapshot Local)
| Nome | Descrio | Local | Palavras Chaves |
|---|---|---|---|
| antigravity_neocortex_config.json | - | \antigravity_neocortex_config.json | - |
| README.md | - | \README.md | - |
| NC-SCR-FR-003-manifest-factory.py | Script factory: escaneia projeto e gera manifesto JSON/JSONL/MD com system_profile | \01_neocortex_framework\scripts\NC-SCR-FR-003-manifest-factory.py | manifest, factory, scan, boot_context |
| NC-TOOL-FR-019-project-manifest.py | Tool MCP: expe factory com 5 aes (generate, get_boot_context, get_nc_index, get_structure, get_ssot_files) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-019-project-manifest.py | mcp-tool, manifest, bootstrap |
| NC-TOOL-FR-020-categories.py | Tool Hub MCP: agrupa 22 tools em 5 super-tools por categoria (memory/session/agents/config/knowledge) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-020-categories.py | mcp-tool, categories, hub, aggregation |
| NC-MAN-FR-001-project-manifest.json | Manifesto completo do projeto (JSON 100 KB) com system_profile: MCP tools, lobes, governana | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-MAN-FR-001-project-manifest.json | manifest, bootstrap, system-profile |
| NC-MAN-FR-001-project-manifest.jsonl | Manifesto JSONL granular (1 entry por arquivo) para busca rpida | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-MAN-FR-001-project-manifest.jsonl | manifest, jsonl, search |
| NC-MAN-FR-001-project-manifest.md | Manifesto Markdown legvel para PR/GitHub e reviso humana | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-MAN-FR-001-project-manifest.md | manifest, markdown, docs |
| NeoCortex_HUD.bat | Launcher HUD v5  fix PYTHONUTF8, 100% ASCII, stderrlog | \NeoCortex_HUD.bat (Desktop) | launcher, hud, bat |
| NC-TOOL-FR-029-health.py | Tool MCP: neocortex_health  10 aes de observabilidade (server.status, agent.health_all, log.tail, log.purge, metrics.live) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-029-health.py | mcp-tool, health, observability, logs, metrics |
| NC-TOOL-FR-023-orchestration.py | Tool MCP: neocortex_orchestration  7 aes de orquestrao (agent.spawn, agent.heartbeat, agent.consume, agent.list_ephemeral, task.execute, task.get_result, peers.discover) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-023-orchestration.py | mcp-tool, orchestration, agent, task, peers |
| NC-TOOL-FR-024-governance.py | Tool MCP: neocortex_governance  8 aes de governana (policy.check, audit.replay, compliance.report, lock.validate, rule.list, session.contracts, violation.log, ssot.diff) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-024-governance.py | mcp-tool, governance, policy, audit, compliance, locks, ssot |
| NC-TOOL-FR-030-context.py | Tool MCP: neocortex_context  8 aes de economia de tokens (budget, estimate, compress, handoff, cache.stats) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-030-context.py | mcp-tool, context, budget, tokens, deepseek |
| NC-TOOL-FR-028-export.py | Tool MCP: neocortex_export  8 aes (to_markdown/json/graph, export_lobes/ssot/docker_compose/readme/obsidian) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-028-export.py | mcp-tool, export, docker, obsidian, white-label |
| NC-TOOL-FR-022-session.py | Tool MCP: neocortex_session  10 aes de sesso (checkpoint.get_current, checkpoint.set_current, checkpoint.complete_task, checkpoint.list_history, regression.check, regression.add_entry, regression.list_all, savepoint.list_active, savepoint.rollback, savepoint.discard) | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-022-session.py | mcp-tool, session, checkpoint, regression, savepoint |
| NC-PROMPT-DS-001-deepseek-subordinate.md | Prompt mestre T1: ciclo 6 fases, 9 regras, protocolo handoff YAML PENDING_REVIEW [2026-04-12] | \NC-PROMPT-DS-001-deepseek-subordinate.md | deepseek, t1, subordinate, prompt, handoff |
| NC-LBE-DS-001-deepseek-agent.mdc | Lobe isolado $DS_AGENT: identidade T1, 6 barreiras, ciclo 6 fases, workspace map, regression buffer [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-001-deepseek-agent.mdc | lobe, deepseek, agent, sandbox, t1 |
| NC-CFG-DS-001-agent-policy.yaml | Policy YAML agente T1: permissoes read/write/forbidden, limites tokens/rounds, handoff protocol [2026-04-12] | \01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-CFG-DS-001-agent-policy.yaml | policy, deepseek, t1, permissions, security |
| NC-DS-HANDOFF-TEMPLATE.yaml | Template correspondencia T1->T0: status PENDING_REVIEW/APPROVED/REJECTED/ESCALATED [2026-04-12] | \DIR-DS-001-tickets\NC-DS-HANDOFF-TEMPLATE.yaml | handoff, template, correspondence, t1-t0 |
| NC-DS-001-fr025-system.yaml | Ticket NC-DS-001: FR-025 neocortex_system 8 acoes  aguardando execucao T1 [2026-04-12] | \DIR-DS-001-tickets\NC-DS-001-fr025-system.yaml | ticket, fr-025, system, t1 |
| NC-PROMPT-DS-000-launcher.md | Launcher T1: 4 linhas  cole no OpenCode e DeepSeek le tudo sozinho [2026-04-12] | \NC-PROMPT-DS-000-launcher.md | launcher, deepseek, opencode, t1 |
| NC-CFG-DS-002-session-contract.yaml | Contrato de sessao T1: boot_sequence, ticket_discovery, stop_conditions, prohibited [2026-04-12] | \NC-CFG-DS-002-session-contract.yaml | contract, session, stop, deepseek, t1 |
| neocortex_config_dev.yaml | Config sandbox dev: porta 8766, lobe dir .neocortex_dev, cache reduzido (SAND-001) [2026-04-12] | \01_neocortex_framework\DIR-CFG-FR-001-config-main\neocortex_config_dev.yaml | config, sandbox, dev, porta-8766 |
| start_neocortex_dev.bat | SAND-002: launcher instancia dev isolada porta 8766 [2026-04-12] | \start_neocortex_dev.bat | sandbox, launcher, dev, porta-8766 |
| start_neocortex_mcp.bat | - | \start_neocortex_mcp.bat | - |
| start_neocortex_mcp.ps1 | - | \start_neocortex_mcp.ps1 | - |
| pyproject.toml | - | \01_neocortex_framework\pyproject.toml | - |
| requirements.txt | - | \01_neocortex_framework\requirements.txt | - |
| lobe_index.db | - | \01_neocortex_framework\.neocortex\cache\lobe_index.db | - |
| index.redb | - | \01_neocortex_framework\.neocortex\cache\hot_cache\index.redb | - |
| cache.db | - | \01_neocortex_framework\.neocortex\cache\ledger\cache.db | - |
| 7fd282bb51e2535a2323bf377a90.val | - | \01_neocortex_framework\.neocortex\cache\ledger\de\50\7fd282bb51e2535a2323bf377a90.val | - |
| cache.db | - | \01_neocortex_framework\.neocortex\cache\manifests\cache.db | - |
| metrics.db | - | \01_neocortex_framework\.neocortex\metrics\metrics.db | - |
| metrics.db.wal | - | \01_neocortex_framework\.neocortex\metrics\metrics.db.wal | - |
| 00-cortex-20260409.mdc | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\.agents\rules\00-cortex-20260409.mdc | - |
| clean_security.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\clean_security.py | - |
| extract_all_tools.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_all_tools.py | - |
| extract_tools_final.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_tools_final.py | - |
| extract_tools_robust.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\extract_tools_robust.py | - |
| fix_indentation.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\development_utilities\fix_indentation.py | - |
| NC-MCP-FR-001-mcp-server.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\mcp_server_legacy\NC-MCP-FR-001-mcp-server.py | - |
| add_root_sanitize_event.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\add_root_sanitize_event.py | - |
| update_antigravity_confirmation.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_antigravity_confirmation.py | - |
| update_ledger_status.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_ledger_status.py | - |
| update_phase3_progress.py | - | \01_neocortex_framework\DIR-ARC-FR-001-archive-main\scripts\update_phase3_progress.py | - |
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
| Sem ttulo.txt | - | \01_neocortex_framework\DIR-BAK-FR-001-backup-main\backup_root\Sem ttulo.txt | - |
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
| detalhamento_completo.md | - | \01_neocortex_framework\DIR-REF-FR-001-reference-main\Arquivos de referncia\detalhamento_completo.md | - |
| structured_elements.md | - | \01_neocortex_framework\DIR-REF-FR-001-reference-main\Arquivos de referncia\structured_elements.md | - |
| sumario.md | - | \01_neocortex_framework\DIR-REF-FR-001-reference-main\Arquivos de referncia\sumario.md | - |
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
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\__init__.py | - |
| executor.py | - | \01_neocortex_framework\neocortex\agent\executor.py | - |
| main.py | - | \01_neocortex_framework\neocortex\cli\main.py | - |
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\cli\__init__.py | - |
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
| security_service.py | NC-SVC-FR-SEC-001 | \01_neocortex_framework\neocortex\core\security_service.py | SEC-401 |
| NC-CORE-FR-014-lock-guard.py | NC-CORE-FR-014 | \01_neocortex_framework\neocortex\core\lock_guard.py | SEC-401 |
| NC-CORE-FR-017-policy-loader.py | NC-CORE-FR-017 | \01_neocortex_framework\neocortex\core\policy_loader.py | PRE-1 |
| NC-CORE-FR-022-save-point-service.py | NC-CORE-FR-022 | \01_neocortex_framework\neocortex\core\save_point_service.py | SAVE-002/003 |
| NC-SVC-FR-005-event-bus.py | NC-SVC-FR-005 | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-005-event-bus.py | ARCH-001 |
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\core\__init__.py | - |
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
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\mcp\__init__.py | - |
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
| NC-TOOL-FR-020-knowledge.py | - | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-020-knowledge.py | - |
| NC-TOOL-FR-031-savepoint.py | NC-TOOL-FR-031 | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-031-savepoint.py | SAVE-004 |
| NC-TOOL-FR-025-system.py | NC-TOOL-FR-025 | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-025-system.py | FR-025 |
| NC-TOOL-FR-026-intelligence.py | NC-TOOL-FR-026 | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-026-intelligence.py | FR-026 |
| NC-TOOL-FR-027-knowledge.py | NC-TOOL-FR-027 | \01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-027-knowledge.py | FR-027 |
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\mcp\tools\__init__.py | - |
| base.py | - | \01_neocortex_framework\neocortex\repositories\base.py | - |
| file_system_repository.py | - | \01_neocortex_framework\neocortex\repositories\file_system_repository.py | - |
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\repositories\__init__.py | - |
| a2a_message_schema.json | - | \01_neocortex_framework\neocortex\schemas\a2a_message_schema.json | - |
| ledger_schema.json | - | \01_neocortex_framework\neocortex\schemas\ledger_schema.json | - |
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\schemas\__init__.py | - |
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
| neocortex_hud.py | NC-HUD-FR-001 | \01_neocortex_framework\scripts\neocortex_hud.py | HUD-001 |
| populate_memory.py | - | \01_neocortex_framework\scripts\populate_memory.py | - |
| saneamento_raiz.py | - | \01_neocortex_framework\scripts\saneamento_raiz.py | - |
| test_llm_backends.py | - | \01_neocortex_framework\scripts\test_llm_backends.py | - |
| update_ledger_with_tools.py | - | \01_neocortex_framework\scripts\update_ledger_with_tools.py | - |
| update_mcp_config.py | - | \01_neocortex_framework\scripts\update_mcp_config.py | - |
| update_mcp_config2.py | - | \01_neocortex_framework\scripts\update_mcp_config2.py | - |
| update_phase3_progress.py | - | \01_neocortex_framework\scripts\update_phase3_progress.py | - |
| NC-DOC-WL-001-hybrid-mode.md | - | \03_white_label_templates\NC-DOC-WL-001-hybrid-mode.md | - |
| NC-DOC-WL-001-readme.md | - | \03_white_label_templates\NC-DOC-WL-001-readme.md | - |
| Aqui est o prompt ajustado exatamente c.txt | - | \04_user_docs\Aqui est o prompt ajustado exatamente c.txt | - |
| cruzar com o roadmap.txt | - | \04_user_docs\cruzar com o roadmap.txt | - |
| LLM e API .md | - | \04_user_docs\LLM e API .md | - |
|  SANITIZAO DA PASTA TURBOQUANT_V42 .txt | - | \04_user_docs\ SANITIZAO DA PASTA TURBOQUANT_V42 .txt | - |
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
| NC-SVC-FR-001-logging-service.py | Logging Service: Structured JSON logging wrapper for NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-001-logging-service.py | logging, json, service, structured |
| NC-CFG-FR-001-logging-config.py | Default logging configuration for NeoCortex | \01_neocortex_framework\neocortex\core\NC-CFG-FR-001-logging-config.py | logging, config, wrapper |
| NC-SVC-FR-002-health-service.py | Health Service: Health status and monitoring wrapper for NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-002-health-service.py | health, monitoring, service |
| NC-SVC-FR-005-event-bus.py | Event Bus: Synchronous event bus for inter-tool communication in NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-005-event-bus.py | event, bus, synchronous, service |
| NC-SVC-FR-004-cache-service.py | HotCache Service: In-memory cache with TTL and statistics for NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-004-cache-service.py | cache, ttl, memory, service, statistics |
| NC-SVC-FR-007-state-machine.py | Agent State Machine: Finite State Machine for T1 agent lifecycle in NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-007-state-machine.py | state machine, fsm, agent, service |
| NC-UTL-FR-001-yaml-safe-parser.py | YAML Safe Parser: Safe YAML loading/dumping with regex fallback for NeoCortex | \01_neocortex_framework\neocortex\core\utils\NC-UTL-FR-001-yaml-safe-parser.py | yaml, parser, utils, safe |
---

##  3. Histrico de Verses e Changelog Core

### [2026-04-12]  BOOT-001: System Manifest Update & Lobe Integration

#### Added
- `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md`  Atualizado com estado atual do sistema: Sprint-001 completo (9/10 tools MCP), lobes CC/DS ativos, frentes operacionais DSA/B/C/D, tickets pendentes, gaps crticos.
- `01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py`  Mapeamento SSOT_LOBE_MAP expandido com lobes CC002, CC003, DS001, DS002, DS003, DS004. Integrao ao LobeIndex para reconhecimento via `neocortex_lobes.list_all()`.

#### Changed
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`  Adicionada entrada BOOT-001 no changelog.
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md`  Ticket BOOT-001 marcado como %DONE.

Ticket: BOOT-001.

### [2026-04-12]  FR-021: neocortex_memory tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-021-memory.py`  MCP tool `neocortex_memory` com 18 aes (lobe.list_active, lobe.get_content, lobe.activate, lobe.deactivate, lobe.search, lobe.list_all, lobe.get_checkpoint_tree, cortex.get_full, cortex.get_section, cortex.get_aliases, cortex.get_workflows, cortex.validate_alias, manifest.generate, manifest.update, manifest.query, manifest.list, manifest.generate_all, search.advanced). Absorve funcionalidades de NC-TOOL-FR-001-cortex.py, NC-TOOL-FR-009-lobes.py, NC-TOOL-FR-014-search.py, NC-TOOL-FR-013-report.py (parcial) e NC-TOOL-FR-007-init.py (parcial). Ticket: FR-021.

### [2026-04-12]  CC-001-A: Claude Code Leak Analysis

#### Added
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-LBE-CC-002-memory-arch.mdc`  Lobe de anlise da arquitetura de memria do Claude Code (freecode/src/memdir/). Taxonomia de tipos, entrypoint MEMORY.md, busca de memrias relevantes.
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-LBE-CC-003-orchestration.mdc`  Lobe de anlise da orquestrao (coordinator mode, autoDream, tasks). Gates de consolidao, coordinator system prompt, worker isolation.
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-001-claw-python-engine.md`  Anlise do engine Python (clawcode). CLI, runtime simulada, query engine, parity audit.
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-002-tools-commands-schema.md`  Anlise dos schemas de tools/commands da Anthropic (snapshots). Inventrio de porting, categorias, mapeamento para NeoCortex.

Ticket: CC-001-A.

### [2026-04-12]  FR-025: neocortex_system tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-025-system.py`  MCP tool `neocortex_system` com 8 aes (config.get, config.reload, config.diff, system.diagnostics, system.env_check, pulse.status, pulse.schedule_custom, pulse.force). Absorve funcionalidades de NC-TOOL-FR-005-config.py e NC-TOOL-FR-011-pulse.py. Ticket: FR-025.

### [2026-04-12]  FR-026: neocortex_intelligence tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-026-intelligence.py`  MCP tool `neocortex_intelligence` com 5 aes (brain.think, brain.plan, brain.orchestrate, brain.critique, brain.feedback). Absorve funcionalidades de NC-TOOL-FR-000-brain.py. Ticket: FR-026.

### [2026-04-12]  FR-027: neocortex_knowledge tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-027-knowledge.py`  MCP tool `neocortex_knowledge` com 5 aes (knowledge.search, knowledge.get_documents, knowledge.project_manifest, knowledge.get_boot_context, knowledge.update_index). Absorve funcionalidades de NC-TOOL-FR-007-init.py e NC-TOOL-FR-019-project-manifest.py. Ticket: FR-027.

### [2026-04-12]  FR-022: neocortex_session tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-022-session.py`  MCP tool `neocortex_session` com 10 aes (checkpoint.get_current, checkpoint.set_current, checkpoint.complete_task, checkpoint.list_history, regression.check, regression.add_entry, regression.list_all, savepoint.list_active, savepoint.rollback, savepoint.discard). Absorve funcionalidades de NC-TOOL-FR-004-checkpoint.py, NC-TOOL-FR-012-regression.py e NC-TOOL-FR-031-savepoint.py. Ticket: FR-022.

### [2026-04-12]  AGENT-206: Health Service wrapper

#### Added
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-002-health-service.py`  Health Service wrapper with get_health_status(), check_mcp_alive(), format_health_response(), get_system_info(). Provides health status and monitoring for NeoCortex without touching @LOCKED files. Ticket: AGENT-206.

### [2026-04-12]  ARCH-001: Event Bus Service

#### Added
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py`  Event Bus service with NeoCortexEvent dataclass, EventBus singleton (subscribe/publish/unsubscribe), get_event_bus() convenience function, and predefined event types (TOOL_CALLED, TOOL_RESULT, AGENT_STATE_CHANGED, HANDOFF_SUBMITTED). Fully synchronous for MCP compatibility. Ticket: ARCH-001.

### [2026-04-11]  Camada 3: Confiabilidade Autnoma (SAVE-002/003/004 + SEC-402)

#### Added
- `neocortex/core/lock_guard.py` (NC-SVC-FR-LCK-001)  LockGuard DENY-by-default, leitura do NC-SEC-FR-001.yaml, hot-reload, violation log. Ticket: SEC-401.
- `neocortex/core/policy_loader.py` (NC-SVC-FR-POL-001)  PolicyLoader runtime YAML, token limits por role, hot-reload 120s, `record_token_usage`. Ticket: PRE-1.
- `neocortex/core/save_point_service.py` (NC-SVC-FR-SAV-001)  STEP -1 Save Point + STEP +1 Rollback. Singleton thread-safe (RLock), TTL 10min, 50 slots, integrado ao LockGuard, decorator `@with_save_point`, `get_compliance_status()` para HUD. Tickets: SAVE-002, SAVE-003.
- `neocortex/mcp/tools/NC-TOOL-FR-031-savepoint.py`  MCP tool `neocortex_savepoint` com 4 aes (list_active, rollback, discard, get_status). Auto-detectada pelo carregamento dinmico do server.py. Ticket: SAVE-004.
- `.git/hooks/pre-commit`  Hook SEC-402: bloqueia commit de arquivo sem prefixo NC- em zonas governadas (DIR-DOC/ARC/BAK/CFG/BOOT) e bloqueia arquivos *.db/*.wal/*.log/__pycache__/neocortex_config.yaml de lobes. Tickets: SEC-402, R01, R08.

#### Changed
- `neocortex/mcp/sub_server.py`  `handle_task` integrado com STEP -1 (capture antes do STEP 0 Mentor) e STEP +1 (rollback automtico no except). `save_id` retornado no output. Ticket: SAVE-003.
- `scripts/neocortex_hud.py` (NC-HUD-FR-001)  8 padro de governana adicionado ao Compliance Panel: ` STEP -1  Save Point ativo` com mtricas em tempo real (active/committed/rolled_back). Ticket: HUD-001.
- `DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md`  Roadmap v9.0: SAVE-002/003/004 e SEC-402 marcados como [x] DONE. Sanitizao marcada como CONCLUDA.
- `NC-NAM-FR-001-naming-convention.md` (este arquivo)  Tabela de mapeamento expandida com lock_guard.py, policy_loader.py, save_point_service.py, NC-TOOL-FR-031-savepoint.py, pre-commit hook, NC-HUD-FR-001. Cdigos NC- atribudos.

#### Added
- `NC-DOC-FR-001-ubiquitous-language-dictionary.md`  Dicionrio de Linguagem Ubqua com smbolos @$% (57 entradas). Inclui NC-READ-HASH de deduplicao.
- `NC-CFG-FR-002-rules-policy.yaml`  Policy-as-Code companion dos arquivos MDC. Machine-readable: `critical_rules`, `write_zones`, `read_dedup` checkpoints, `ubiquitous_language`, `llm_tiers`.
- `.agents/rules/NC-RULE-001-core-ssot.mdc`  Regras core, always-on, < 50 linhas. Inclui NC-READ-HASH para evitar re-leitura.
- `.agents/rules/NC-RULE-002-python-mcp.mdc`  Regras Python/MCP com globs `**/*.py`. Inclui exemplos de cdigo para importao, paths e logger.
- `.agents/rules/NC-RULE-003-lobes-memory.mdc`  Regras de lobos com globs `**/lobes/**`. Inclui mapa de lobos, isolamento, API LobeService.
- `.agents/rules/NC-RULE-004-filesystem.mdc`  Regras de filesystem com globs `**/DIR-*/**`. Inclui zonas de escrita, hierarquia numrica, checklist de criao.

#### Changed
- `.agents/rules/neocortexrules.md`  Reescrito como ndice master v3: mapa de mdulos MDC, tabelas @$% de linguagem ubqua, NC-READ-HASH dedup, 20 regras compactas com referncias @$%.

### [2026-04-11]  Sesso de Industrializao e Governana (Parte 2)

#### Added
- `NC-APP-FR-001-technical-appendix.md`  Apndice tcnico: inventrio de 30+ ferramentas, aes MCP, bibliotecas, LLMs, polticas de roteamento e fluxo de orquestrao. Ticket: OPT documentao.
- `NC-PROMPT-FR-001-master-context.md` (raiz)  Master Context Prompt v2 com mapa de lobos, comandos de busca, tiers LLM e princpio de economia de tokens.
- `NC-CFG-FR-001-agent-policy-template.yaml`  Template de poltica de agente: `allowed_tools`, `forbidden_actions`, `limits.*`, mentor mode, isolamento de lobe. Ticket: SEC-403.
- `NC-SEC-FR-001-atomic-locks.yaml`  Lista centralizada de arquivos protegidos para o SecurityService (6 categorias + excees por role). Ticket: SEC-401.
- `NC-SOP-FR-001-session-startup.md`  Procedimento Operacional Padro de inicializao de sesso NeoCortex (5 passos + checklist de encerramento).
- `NC-ARC-FR-001-decision-log.md`  Architecture Decision Records com 8 ADRs (pyspeedb, FTS5, DuckDB, diskcache-rs, FastMCP, Qwen 1.5B, msgspec, Arquitetura de Lobos).
- `NC-SCR-FR-001-populate-lobes-ssot.py` (scripts/)  Script de poblamento automtico dos lobos a partir dos arquivos SSOT via LobeService. Suporta `--dry-run`. 12 entradas mapeadas.
- `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md`  Manifesto universal de boot: qualquer IA deve ler antes de agir. Contm mapa de lobos, arquitetura de agentes, nomenclatura, proibies e tickets abertos.
- `NC-LBE-FR-ARCHITECTURE-001.mdc` (gerado via script)  Lobo de memria indexado: Roadmap + Naming Convention + Apndice Tcnico + ADRs.
- `NC-LBE-FR-SECURITY-001.mdc` (gerado via script)  Lobo de memria indexado: Atomic Locks + Agent Policy + SOP de Sesso + Sanitization Checklist.

#### Changed
- `neocortex/mcp/sub_server.py`  **AGENT-203 implementado**: `mentor_step_0()` com `identify_relevant_lobes` (mapeamento role+keyword  lobos), `extract_relevant_snippet` (scoring FTS5 por pargrafos), `handle_task` com logging detalhado via `neocortex.mentor` logger.
- `NC-APP-FR-001-technical-appendix.md`  Inventrio completo de 7 categorias (DB, Cache, Busca, LLM, Orquestrao, Dev, Aux) adicionado.
- `NC-SCR-FR-001-populate-lobes-ssot.py`  Mapeamento expandido com NC-CFG-FR-001, NC-SEC-FR-001, NC-SOP-FR-001, NC-ARC-FR-001.
- `NC-NAM-FR-001-naming-convention.md` (este arquivo)  Changelog duplicado removido; entrada expandida adicionada.

#### Fixed
- Duplicao do bloco de changelog removida (linhas 396-423 redundantes eliminadas).
- Stub `mentor_step_0()` substitudo pela implementao real com LobeService.

### [2026-04-11]  Sesso de Industrializao e Governana (Parte 2): HUD Fix + Manifest Factory + Tool Categories

#### Added
- `NC-SCR-FR-003-manifest-factory.py`: Factory standalone que escaneia 165 arquivos, 50 NC-named. Gera JSON (100KB), JSONL (48KB), MD (26KB). `system_profile` cobre: MCP tools por categoria, lobes, 8 padres de governana (score 7/8).
- `NC-TOOL-FR-019-project-manifest.py`: Tool MCP com 5 aes (`generate`, `get_boot_context`, `get_nc_index`, `get_structure`, `get_ssot_files`). Auto-registrada via glob dinmico do `server.py`.
- `NC-TOOL-FR-020-categories.py`: Hub que agrupa 22 tools individuais em 5 super-tools por categoria semntica. Reduz entrada no manifest de IA de 22 para 5 ferramentas visveis sem perder granularidade interna.
- `NC-MAN-FR-001-project-manifest.{json,jsonl,md}`: Trs formatos de manifesto gerados automaticamente. Suporte a bootstrap de IA via API em 1 leitura.

#### Fixed
- `NeoCortex_HUD.bat` v5: Causa raiz do crash identificada (`PYTHONUTF8=on` invlido herdado do ambiente). Fix: `set PYTHONUTF8=` antes de `start pythonw`. Salvo via PowerShell `Encoding::Default` (ASCII puro, sem BOM). stderr redirecionado para `NC-LOG-FR-001-hud-audit\hud_last_error.txt`.

### [2026-04-11]  Sesso de Industrializao e Governana (Parte 1)

#### Added
- Ferramenta MCP `neocortex_brain` para integrao com DeepSeek API como T-0 Assistente instalada.
- Documento-Mestre criado: Este documento passa agora a consolidar o changelog, Naming Convention e Project Map centralmente limitando fragmentao indesejada.
- Scripts de PowerShell e Batch `start_neocortex_mcp` regerados apontando para carregamento em mdulo do novo Host (ex: `-m neocortex.mcp.server`).
- Servidor MCP: varredura dinmica foi implantada com resilincia autnoma  mutao de diretorias.

#### Changed
- Consolidados todos os 3 roadmaps (v5.0 Macro, v6.0 Stability e Translation original) em um **nico** arquivo de roadmap inquebrvel (`NC-TODO-FR-001-project-roadmap-consolidated.md`).
- A estruturao da pasta `neocortex_framework/` foi refatorada e indexada segundo subdiretrios padro `DIR-*-FR-*`.

#### Fixed
- Erro fatal do servidor MCP na inicializao (`FastMCP.run() got an unexpected keyword argument 'host'`). Corrigido adaptando o modelo SSE nativo sobre protocolo WebSocket e implementando o objeto em instncia sincrnica.
- `RuntimeError` originado pelo pacote FastMCP por colises de pools do `asyncio` e bibliotecas AnyIO nativas.
- Erros de Windows Prompt charset originados da tentativa de codificao nativa CP1252 em Emojis.

| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\repositories\__init__.py | - |
| a2a_message_schema.json | - | \01_neocortex_framework\neocortex\schemas\a2a_message_schema.json | - |
| ledger_schema.json | - | \01_neocortex_framework\neocortex\schemas\ledger_schema.json | - |
| NC-LBE-DS-000-parent.mdc | Lobe-mae consolidado: estado global do sprint, gaps sistemicos, rate limiting hierarquico [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-000-parent.mdc | lobe, parent, sprint, ds |
| NC-LBE-DS-002-deepseek-agent-b.mdc | Lobe Frente B: NC-DS-005 session, barreira B7 anti-conflito com Frente A [2026-04-12] | \01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-LBE-DS-002-deepseek-agent-b.mdc | lobe, frente-b, session, ds |
| NC-CFG-DS-003-coordination.yaml | Coordenacao frentes paralelas: rate limiting 4 niveis, anti-conflito, gaps SAVE/WAL [2026-04-12] | \DIR-DS-000-agent-config\NC-CFG-DS-003-coordination.yaml | coordination, rate-limit, ds-a, ds-b || __init__.py | - | \01_neocortex_framework\neocortex\schemas\__init__.py | - |
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
| neocortex_hud.py | NC-HUD-FR-001 | \01_neocortex_framework\scripts\neocortex_hud.py | HUD-001 |
| populate_memory.py | - | \01_neocortex_framework\scripts\populate_memory.py | - |
| saneamento_raiz.py | - | \01_neocortex_framework\scripts\saneamento_raiz.py | - |
| test_llm_backends.py | - | \01_neocortex_framework\scripts\test_llm_backends.py | - |
| update_ledger_with_tools.py | - | \01_neocortex_framework\scripts\update_ledger_with_tools.py | - |
| update_mcp_config.py | - | \01_neocortex_framework\scripts\update_mcp_config.py | - |
| update_mcp_config2.py | - | \01_neocortex_framework\scripts\update_mcp_config2.py | - |
| update_phase3_progress.py | - | \01_neocortex_framework\scripts\update_phase3_progress.py | - |
| NC-DOC-WL-001-hybrid-mode.md | - | \03_white_label_templates\NC-DOC-WL-001-hybrid-mode.md | - |
| NC-DOC-WL-001-readme.md | - | \03_white_label_templates\NC-DOC-WL-001-readme.md | - |
| Aqui est o prompt ajustado exatamente c.txt | - | \04_user_docs\Aqui est o prompt ajustado exatamente c.txt | - |
| cruzar com o roadmap.txt | - | \04_user_docs\cruzar com o roadmap.txt | - |
| LLM e API .md | - | \04_user_docs\LLM e API .md | - |
|  SANITIZAO DA PASTA TURBOQUANT_V42 .txt | - | \04_user_docs\ SANITIZAO DA PASTA TURBOQUANT_V42 .txt | - |
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
| NC-SVC-FR-001-logging-service.py | Logging Service: Structured JSON logging wrapper for NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-001-logging-service.py | logging, json, service, structured |
| NC-CFG-FR-001-logging-config.py | Default logging configuration for NeoCortex | \01_neocortex_framework\neocortex\core\NC-CFG-FR-001-logging-config.py | logging, config, wrapper |
| NC-SVC-FR-002-health-service.py | Health Service: Health status and monitoring wrapper for NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-002-health-service.py | health, monitoring, service |
| NC-SVC-FR-005-event-bus.py | Event Bus: Synchronous event bus for inter-tool communication in NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-005-event-bus.py | event, bus, synchronous, service |
| NC-SVC-FR-004-cache-service.py | HotCache Service: In-memory cache with TTL and statistics for NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-004-cache-service.py | cache, ttl, memory, service, statistics |
| NC-SVC-FR-007-state-machine.py | Agent State Machine: Finite State Machine for T1 agent lifecycle in NeoCortex | \01_neocortex_framework\neocortex\core\services\NC-SVC-FR-007-state-machine.py | state machine, fsm, agent, service |
| NC-UTL-FR-001-yaml-safe-parser.py | YAML Safe Parser: Safe YAML loading/dumping with regex fallback for NeoCortex | \01_neocortex_framework\neocortex\core\utils\NC-UTL-FR-001-yaml-safe-parser.py | yaml, parser, utils, safe |
---

##  3. Histrico de Verses e Changelog Core

### [2026-04-12]  BOOT-001: System Manifest Update & Lobe Integration

#### Added
- `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md`  Atualizado com estado atual do sistema: Sprint-001 completo (9/10 tools MCP), lobes CC/DS ativos, frentes operacionais DSA/B/C/D, tickets pendentes, gaps crticos.
- `01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py`  Mapeamento SSOT_LOBE_MAP expandido com lobes CC002, CC003, DS001, DS002, DS003, DS004. Integrao ao LobeIndex para reconhecimento via `neocortex_lobes.list_all()`.

#### Changed
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`  Adicionada entrada BOOT-001 no changelog.
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md`  Ticket BOOT-001 marcado como %DONE.

Ticket: BOOT-001.

### [2026-04-12]  FR-021: neocortex_memory tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-021-memory.py`  MCP tool `neocortex_memory` com 18 aes (lobe.list_active, lobe.get_content, lobe.activate, lobe.deactivate, lobe.search, lobe.list_all, lobe.get_checkpoint_tree, cortex.get_full, cortex.get_section, cortex.get_aliases, cortex.get_workflows, cortex.validate_alias, manifest.generate, manifest.update, manifest.query, manifest.list, manifest.generate_all, search.advanced). Absorve funcionalidades de NC-TOOL-FR-001-cortex.py, NC-TOOL-FR-009-lobes.py, NC-TOOL-FR-014-search.py, NC-TOOL-FR-013-report.py (parcial) e NC-TOOL-FR-007-init.py (parcial). Ticket: FR-021.

### [2026-04-12]  CC-001-A: Claude Code Leak Analysis

#### Added
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-LBE-CC-002-memory-arch.mdc`  Lobe de anlise da arquitetura de memria do Claude Code (freecode/src/memdir/). Taxonomia de tipos, entrypoint MEMORY.md, busca de memrias relevantes.
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-LBE-CC-003-orchestration.mdc`  Lobe de anlise da orquestrao (coordinator mode, autoDream, tasks). Gates de consolidao, coordinator system prompt, worker isolation.
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-001-claw-python-engine.md`  Anlise do engine Python (clawcode). CLI, runtime simulada, query engine, parity audit.
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-a/NC-ANA-CC-002-tools-commands-schema.md`  Anlise dos schemas de tools/commands da Anthropic (snapshots). Inventrio de porting, categorias, mapeamento para NeoCortex.

Ticket: CC-001-A.

### [2026-04-12]  FR-025: neocortex_system tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-025-system.py`  MCP tool `neocortex_system` com 8 aes (config.get, config.reload, config.diff, system.diagnostics, system.env_check, pulse.status, pulse.schedule_custom, pulse.force). Absorve funcionalidades de NC-TOOL-FR-005-config.py e NC-TOOL-FR-011-pulse.py. Ticket: FR-025.

### [2026-04-12]  FR-026: neocortex_intelligence tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-026-intelligence.py`  MCP tool `neocortex_intelligence` com 5 aes (brain.think, brain.plan, brain.orchestrate, brain.critique, brain.feedback). Absorve funcionalidades de NC-TOOL-FR-000-brain.py. Ticket: FR-026.

### [2026-04-12]  FR-027: neocortex_knowledge tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-027-knowledge.py`  MCP tool `neocortex_knowledge` com 5 aes (knowledge.search, knowledge.get_documents, knowledge.project_manifest, knowledge.get_boot_context, knowledge.update_index). Absorve funcionalidades de NC-TOOL-FR-007-init.py e NC-TOOL-FR-019-project-manifest.py. Ticket: FR-027.

### [2026-04-12]  FR-022: neocortex_session tool

#### Added
- `neocortex/mcp/tools/NC-TOOL-FR-022-session.py`  MCP tool `neocortex_session` com 10 aes (checkpoint.get_current, checkpoint.set_current, checkpoint.complete_task, checkpoint.list_history, regression.check, regression.add_entry, regression.list_all, savepoint.list_active, savepoint.rollback, savepoint.discard). Absorve funcionalidades de NC-TOOL-FR-004-checkpoint.py, NC-TOOL-FR-012-regression.py e NC-TOOL-FR-031-savepoint.py. Ticket: FR-022.

### [2026-04-12]  AGENT-206: Health Service wrapper

#### Added
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-002-health-service.py`  Health Service wrapper with get_health_status(), check_mcp_alive(), format_health_response(), get_system_info(). Provides health status and monitoring for NeoCortex without touching @LOCKED files. Ticket: AGENT-206.

### [2026-04-12]  ARCH-001: Event Bus Service

#### Added
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py`  Event Bus service with NeoCortexEvent dataclass, EventBus singleton (subscribe/publish/unsubscribe), get_event_bus() convenience function, and predefined event types (TOOL_CALLED, TOOL_RESULT, AGENT_STATE_CHANGED, HANDOFF_SUBMITTED). Fully synchronous for MCP compatibility. Ticket: ARCH-001.

### [2026-04-11]  Camada 3: Confiabilidade Autnoma (SAVE-002/003/004 + SEC-402)

#### Added
- `neocortex/core/lock_guard.py` (NC-SVC-FR-LCK-001)  LockGuard DENY-by-default, leitura do NC-SEC-FR-001.yaml, hot-reload, violation log. Ticket: SEC-401.
- `neocortex/core/policy_loader.py` (NC-SVC-FR-POL-001)  PolicyLoader runtime YAML, token limits por role, hot-reload 120s, `record_token_usage`. Ticket: PRE-1.
- `neocortex/core/save_point_service.py` (NC-SVC-FR-SAV-001)  STEP -1 Save Point + STEP +1 Rollback. Singleton thread-safe (RLock), TTL 10min, 50 slots, integrado ao LockGuard, decorator `@with_save_point`, `get_compliance_status()` para HUD. Tickets: SAVE-002, SAVE-003.
- `neocortex/mcp/tools/NC-TOOL-FR-031-savepoint.py`  MCP tool `neocortex_savepoint` com 4 aes (list_active, rollback, discard, get_status). Auto-detectada pelo carregamento dinmico do server.py. Ticket: SAVE-004.
- `.git/hooks/pre-commit`  Hook SEC-402: bloqueia commit de arquivo sem prefixo NC- em zonas governadas (DIR-DOC/ARC/BAK/CFG/BOOT) e bloqueia arquivos *.db/*.wal/*.log/__pycache__/neocortex_config.yaml de lobes. Tickets: SEC-402, R01, R08.

#### Changed
- `neocortex/mcp/sub_server.py`  `handle_task` integrado com STEP -1 (capture antes do STEP 0 Mentor) e STEP +1 (rollback automtico no except). `save_id` retornado no output. Ticket: SAVE-003.
- `scripts/neocortex_hud.py` (NC-HUD-FR-001)  8 padro de governana adicionado ao Compliance Panel: ` STEP -1  Save Point ativo` com mtricas em tempo real (active/committed/rolled_back). Ticket: HUD-001.
- `DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md`  Roadmap v9.0: SAVE-002/003/004 e SEC-402 marcados como [x] DONE. Sanitizao marcada como CONCLUDA.
- `NC-NAM-FR-001-naming-convention.md` (este arquivo)  Tabela de mapeamento expandida com lock_guard.py, policy_loader.py, save_point_service.py, NC-TOOL-FR-031-savepoint.py, pre-commit hook, NC-HUD-FR-001. Cdigos NC- atribudos.

#### Added
- `NC-DOC-FR-001-ubiquitous-language-dictionary.md`  Dicionrio de Linguagem Ubqua com smbolos @$% (57 entradas). Inclui NC-READ-HASH de deduplicao.
- `NC-CFG-FR-002-rules-policy.yaml`  Policy-as-Code companion dos arquivos MDC. Machine-readable: `critical_rules`, `write_zones`, `read_dedup` checkpoints, `ubiquitous_language`, `llm_tiers`.
- `.agents/rules/NC-RULE-001-core-ssot.mdc`  Regras core, always-on, < 50 linhas. Inclui NC-READ-HASH para evitar re-leitura.
- `.agents/rules/NC-RULE-002-python-mcp.mdc`  Regras Python/MCP com globs `**/*.py`. Inclui exemplos de cdigo para importao, paths e logger.
- `.agents/rules/NC-RULE-003-lobes-memory.mdc`  Regras de lobos com globs `**/lobes/**`. Inclui mapa de lobos, isolamento, API LobeService.
- `.agents/rules/NC-RULE-004-filesystem.mdc`  Regras de filesystem com globs `**/DIR-*/**`. Inclui zonas de escrita, hierarquia numrica, checklist de criao.

#### Changed
- `.agents/rules/neocortexrules.md`  Reescrito como ndice master v3: mapa de mdulos MDC, tabelas @$% de linguagem ubqua, NC-READ-HASH dedup, 20 regras compactas com referncias @$%.

### [2026-04-11]  Sesso de Industrializao e Governana (Parte 2)

#### Added
- `NC-APP-FR-001-technical-appendix.md`  Apndice tcnico: inventrio de 30+ ferramentas, aes MCP, bibliotecas, LLMs, polticas de roteamento e fluxo de orquestrao. Ticket: OPT documentao.
- `NC-PROMPT-FR-001-master-context.md` (raiz)  Master Context Prompt v2 com mapa de lobos, comandos de busca, tiers LLM e princpio de economia de tokens.
- `NC-CFG-FR-001-agent-policy-template.yaml`  Template de poltica de agente: `allowed_tools`, `forbidden_actions`, `limits.*`, mentor mode, isolamento de lobe. Ticket: SEC-403.
- `NC-SEC-FR-001-atomic-locks.yaml`  Lista centralizada de arquivos protegidos para o SecurityService (6 categorias + excees por role). Ticket: SEC-401.
- `NC-SOP-FR-001-session-startup.md`  Procedimento Operacional Padro de inicializao de sesso NeoCortex (5 passos + checklist de encerramento).
- `NC-ARC-FR-001-decision-log.md`  Architecture Decision Records com 8 ADRs (pyspeedb, FTS5, DuckDB, diskcache-rs, FastMCP, Qwen 1.5B, msgspec, Arquitetura de Lobos).
- `NC-SCR-FR-001-populate-lobes-ssot.py` (scripts/)  Script de poblamento automtico dos lobos a partir dos arquivos SSOT via LobeService. Suporta `--dry-run`. 12 entradas mapeadas.
- `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md`  Manifesto universal de boot: qualquer IA deve ler antes de agir. Contm mapa de lobos, arquitetura de agentes, nomenclatura, proibies e tickets abertos.
- `NC-LBE-FR-ARCHITECTURE-001.mdc` (gerado via script)  Lobo de memria indexado: Roadmap + Naming Convention + Apndice Tcnico + ADRs.
- `NC-LBE-FR-SECURITY-001.mdc` (gerado via script)  Lobo de memria indexado: Atomic Locks + Agent Policy + SOP de Sesso + Sanitization Checklist.

#### Changed
- `neocortex/mcp/sub_server.py`  **AGENT-203 implementado**: `mentor_step_0()` com `identify_relevant_lobes` (mapeamento role+keyword  lobos), `extract_relevant_snippet` (scoring FTS5 por pargrafos), `handle_task` com logging detalhado via `neocortex.mentor` logger.
- `NC-APP-FR-001-technical-appendix.md`  Inventrio completo de 7 categorias (DB, Cache, Busca, LLM, Orquestrao, Dev, Aux) adicionado.
- `NC-SCR-FR-001-populate-lobes-ssot.py`  Mapeamento expandido com NC-CFG-FR-001, NC-SEC-FR-001, NC-SOP-FR-001, NC-ARC-FR-001.
- `NC-NAM-FR-001-naming-convention.md` (este arquivo)  Changelog duplicado removido; entrada expandida adicionada.

#### Fixed
- Duplicao do bloco de changelog removida (linhas 396-423 redundantes eliminadas).
- Stub `mentor_step_0()` substitudo pela implementao real com LobeService.

### [2026-04-11]  Sesso de Industrializao e Governana (Parte 2): HUD Fix + Manifest Factory + Tool Categories

#### Added
- `NC-SCR-FR-003-manifest-factory.py`: Factory standalone que escaneia 165 arquivos, 50 NC-named. Gera JSON (100KB), JSONL (48KB), MD (26KB). `system_profile` cobre: MCP tools por categoria, lobes, 8 padres de governana (score 7/8).
- `NC-TOOL-FR-019-project-manifest.py`: Tool MCP com 5 aes (`generate`, `get_boot_context`, `get_nc_index`, `get_structure`, `get_ssot_files`). Auto-registrada via glob dinmico do `server.py`.
- `NC-TOOL-FR-020-categories.py`: Hub que agrupa 22 tools individuais em 5 super-tools por categoria semntica. Reduz entrada no manifest de IA de 22 para 5 ferramentas visveis sem perder granularidade interna.
- `NC-MAN-FR-001-project-manifest.{json,jsonl,md}`: Trs formatos de manifesto gerados automaticamente. Suporte a bootstrap de IA via API em 1 leitura.

#### Fixed
- `NeoCortex_HUD.bat` v5: Causa raiz do crash identificada (`PYTHONUTF8=on` invlido herdado do ambiente). Fix: `set PYTHONUTF8=` antes de `start pythonw`. Salvo via PowerShell `Encoding::Default` (ASCII puro, sem BOM). stderr redirecionado para `NC-LOG-FR-001-hud-audit\hud_last_error.txt`.

### [2026-04-11]  Sesso de Industrializao e Governana (Parte 1)

#### Added
- Ferramenta MCP `neocortex_brain` para integrao com DeepSeek API como T-0 Assistente instalada.
- Documento-Mestre criado: Este documento passa agora a consolidar o changelog, Naming Convention e Project Map centralmente limitando fragmentao indesejada.
- Scripts de PowerShell e Batch `start_neocortex_mcp` regerados apontando para carregamento em mdulo do novo Host (ex: `-m neocortex.mcp.server`).
- Servidor MCP: varredura dinmica foi implantada com resilincia autnoma  mutao de diretorias.

#### Changed
- Consolidados todos os 3 roadmaps (v5.0 Macro, v6.0 Stability e Translation original) em um **nico** arquivo de roadmap inquebrvel (`NC-TODO-FR-001-project-roadmap-consolidated.md`).
- A estruturao da pasta `neocortex_framework/` foi refatorada e indexada segundo subdiretrios padro `DIR-*-FR-*`.

#### Fixed
- Erro fatal do servidor MCP na inicializao (`FastMCP.run() got an unexpected keyword argument 'host'`). Corrigido adaptando o modelo SSE nativo sobre protocolo WebSocket e implementando o objeto em instncia sincrnica.
- `RuntimeError` originado pelo pacote FastMCP por colises de pools do `asyncio` e bibliotecas AnyIO nativas.
- Erros de Windows Prompt charset originados da tentativa de codificao nativa CP1252 em Emojis.

### [2026-04-10]
#### Added
- Integrao pioneira do MetricsStore com backend em banco de dados DuckDB (OPT-010). Testado ativamente em suite `test_sanity.py` atestando 11 hits com sucesso transacional em memria e logs reportados.
- Inventrio MCP processado diagnosticando e documentando 22 ferramentas (STUBS e acionveis) passveis de deleque/restaurao arquitetural em fase.

### [2026-04-08]
#### Added
- Start tcnico oficial do branch de aprimoramento orgnico logstico do TurboQuant v4.2 instanciando as razes primrias MCP e consolidando o T-0 Assistant.

### [2026-04-12]
#### Added  Industrializao N-Workers & Software Factory distribuda

**DIR-DS-000-agent-config/**  Sistema de agentes distribudo:
- `NC-PROMPT-DS-002-worker-universal.md`  Prompt N-workers: STEP 0 learn mode, claim port-based (`worker-{PORT}-{HASH[:6]}`), Entry Locks EL-1EL-6, SHA-256 integridade de prompt, anti-spin. PROMPT_SHA12: cabealho auto-gerado por `stamp_prompt.py`.
- `NC-CFG-DS-004-task-queue.yaml`  Fila de tasks distribuda: atomic claim (5s wait + re-read), Progressive Lock Gates (GATE-001 a 005), Surgical Patches, status AVAILABLE/CLAIMED/ACTIVE/DONE/BLOCKED.

**DIR-DS-001-tickets/**  29 tickets NC-DS-001029: todos assinados com `integrity_hash` sha256[:16].

**DIR-DS-002-audit-logs/**  Handoffs YAML por worker (PENDING_REVIEW  APPROVED pelo NC-SCR-FR-005).

**DIR-DS-003-entry-locks/**  NEW:
- `active-zones.yaml`  Write-Zone Registry em tempo real. Workers registram write_zone antes de escrever.

**DIR-DS-004-patches/**  NEW: Surgical Patches para Progressive Lock Gates. T0 aplica manualmente; workers nunca tocam @LOCKS.

**01_neocortex_framework/scripts/**:
- `NC-SCR-FR-005-auto-approve.py`  Auto-aprovao handoffs (B1-B6, lines_added>5, files_created>0).
- `sign_tickets.py`  Assina batch de tickets com integrity_hash.
- `stamp_prompt.py`  Injeta PROMPT_SHA12 no topo do worker prompt; rodar aps cada edio.
- `fix_queue.py`  Reset de fila: BLOCKED/false-DONE  AVAILABLE; remove @LOCK de files_modified.

**NC-PROMPT-FR-002-pre-mcp-manual-checklist.md**  STEP 0 Regression Check + tabela REG-001005.

#### Architecture Notes
- **Progressive Lock Gates**: tickets aprovados  patches  T0 aplica cirurgicamente em @LOCKS.
- **Port-Based ID**: MY_CLAIM = `worker-{PORT}-{PROMPT_HASH[:6]}` elimina coliso de claims.
- **Regression Buffer MCP**: 5 erros crticos registrados (REG-001 a 005).

---
## Changelog [2026-04-14]  Merge Cruzado e Unificao Definitiva do Tool Manifest (NC-DS-053)

#### Added
- `01_neocortex_framework/scripts/NC-SCR-FR-002-tool-manifest-generator.py`  Script gerador master SSOT (frontmatter NC-RULE-007 compliant) que consolida todos os manifestos de ferramentas MCP num nico SSOT.

#### Changed
- `01_neocortex_framework/DIR-CORE-FR-001-core-central/NC-TLM-FR-001-tool-manifest.json`  Manifesto SSOT enriquecido com metadados de merge (`_meta`), total de 16 ferramentas, 61 aes, categorias expandidas.

#### Removed
- `01_neocortex_framework/neocortex/mcp/tools_manifest.json`  Manifesto redundante (gerado automaticamente).
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/mcp_tools_inventory.json`  Inventrio redundante.
- Scripts redundantes: `generate_tools_manifest.py`, `generate_official_tool_manifest.py`, `extract_tools_final.py`, `analyze_mcp_tools.py`, `merge_tool_manifests.py`.

#### Updated
- `01_neocortex_framework/scripts/update_ledger_with_tools.py`  Agora referencia o SSOT `NC-TLM-FR-001-tool-manifest.json`.
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-DS-001-roadmap-pre-mcp.md`  Ticket NC-DS-053 marcado como COMPLETED, DONE incrementado.

Ticket: NC-DS-053 | Sesso: T0 DeepSeek-Reasoner 2026-04-14.

---
## Changelog [2026-04-14]  Bblia Topolgica do NeoCortex

#### Added
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-DS-005-topological-taxonomy.md`  Documento SSOT mestre da taxonomia topolgica vetorial do NeoCortex. Lista exaustiva das 30 tags topolgicas vetoriais (domain, layer, type, tier, parent, children, dependence, codependence, criticality, risk, scope, lifecycle, etc.). Explica lgica e obrigatoriedade do formato YAML/Header (Ruamel) no topo de TODOS os arquivos do ecossistema. Demonstra exemplos cruis de como tags codependentes criam um RAG perfeito. Ticket: NC-DS-048 (Saneamento de Lobos e SSOT).

Ticket: NC-DS-048 | Sesso: T0 DeepSeek-Reasoner 2026-04-14.

---
## Changelog [2026-04-14]  Mission Control & Pixel Agents Integration Lobes

#### Added
- `02_memory_lobes/NC-LBE-INT-004-mission-control.mdc`  Lobe de integrao do Mission Control com suporte a webhooks, generic adapter e gerenciamento Kanban. Ticket: INT-004.
- `02_memory_lobes/NC-LBE-INT-005-pixel-agents.mdc`  Lobe de integrao do Pixel Agents com especificao para OpenCodeJSONL Bridge. Ticket: INT-005.

Ticket: INT-004, INT-005 | Sesso: T0 Antigravity 2026-04-14.

## Changelog [2026-04-13 15:30]  Lobe Antigravity Integration

#### Added
- `01_neocortex_framework/lobes/NC-LBE-INT-003-antigravity-integration.mdc`  Lobe de documentao do papel de T0 (Antigravity) como orquestrador central, hierarquia de agentes, 34 ferramentas MCP, protocolos de delegao e integrao com PicoClaw/OpenCode. Ticket: LOBE-INT-003.

Ticket: LOBE-INT-003 | Sesso: T0 Antigravity (agente C porta 32763) 2026-04-13.

---
## Changelog [2026-04-13]  Governana R21/STEP-0 + Saneamento do Workspace

#### Added
- `NC-PROMPT-FR-001-master-context.md` v4.0  Reescrito com R21 completo, Ground Truth deps (18 libs), mapa dos 5 sub-registros SSOT, estado frentes Sprint-002 (DS-A/B/C), toolchain de qualidade, flag MCP offline, checklist de sesso ampliado. Ticket: GOV-001.
- `01_neocortex_framework/scripts/NC-SCR-FR-013-validate-file.py` v2.0  Modos `--r11-fix` (printlogger em massa), `--f811-fix` (remove redefinies register_tool), `--missing-map` (auditoria de integridade), `--zone` (filtro por zona A/B/C). Ticket: GOV-001.
- `DIR-DS-000-agent-config/NC-CFG-DS-005-step0-environment.md`  Protocolo STEP-0 v2.0 com verificao de 18 dependncias reais via importlib. Injetado em NC-PROMPT-DS-004/005/006.
- `.agents/rules/NC-RULE-006-no-assumptions.mdc`  Regra R21 Anti-Suposio modular com globs alwaysApply.
- `DIR-DS-002-audit-logs/NC-INV-FR-001-workspace-inventory-20260413.txt`  Inventrio completo do workspace: 172 linhas, pastas corretas vs. orfas, 40 arquivos fora do padro identificados.
- `01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-001-env-quality.mdc`  Lobe de Qualidade: Ground Truth toolchain, STEP-0 v2 copivel, R21 checklist, regression buffer QUAL-001004, mapa de arquivos ausentes.

#### Changed
- `NC-PROMPT-DS-004-kairos-channel.md`  STEP-0 v2 injetado (seo 7-26). Template Brockman v1 adicionado (GOAL/RETURN FORMAT/WARNINGS/CONTEXT DUMP) [2026-04-13].
- `NC-PROMPT-DS-005-pathresolver-eventbus.md`  STEP-0 v2 injetado. Template Brockman v1 adicionado [2026-04-13].
- `NC-PROMPT-DS-006-metrics-statemachine.md`  STEP-0 v2 injetado. Template Brockman v1 adicionado [2026-04-13].
- `NC-PROMPT-FR-001-master-context.md`  v4.0: Template Brockman v1 integrado, R21 no topo, mapa de 9 SSOTs, frentes Sprint-002, toolchain de qualidade, flag MCP offline [2026-04-13].
- `.agents/rules/neocortexrules.md`  R21 adicionado ao ndice (ID R21, severity critical), @STEP0 adicionado s referncias.

#### Fixed  Saneamento do Workspace
- `raiz/`  11 arquivos orfaos movidos para `DIR-ARC-FR-001-archive-main/raiz-orphans-20260413/`: audit_entry.json, checkpoint_0.json, plan.json, filelist.txt, filelist2.txt, validation_report.json, temp_claim.py, test_*.py (4 arquivos).
- `raiz/audit_zone_b.ps1`  renomeado `NC-SCR-DS-001-audit-zone-b.ps1` e movido para `DIR-DS-000-agent-config/`.
- `DIR-DS-002-audit-logs/`  40 arquivos fora do padro movidos para `arc-sprint-001-pre-naming/`.

Ticket: GOV-001 | Sesso: T0 Antigravity 2026-04-13.

---
## Changelog [2026-04-13 11:52]  Saneamento Roadmaps + Reescrita DS-006

#### Archived
- `NC-TODO-DS-002-roadmap-full.md`  `DIR-ARC-FR-001-archive-main/raiz-orphans-20260413/`  Roadmap extra no solicitado, duplicao do NC-TODO-FR-001. SSOT de roadmaps agora tem apenas 2 documentos oficiais.

#### Changed
- `NC-PROMPT-DS-006-metrics-statemachine.md`  v2.0 reescrito do zero (Agente C se perdeu, sem entrega detectada). Inclui interfaces completas de MetricsCollector e FSM, STEP-0 v2, Brockman template, protocolo de entrega campo-a-campo.

#### State: Roadmaps oficiais vigentes
- `NC-TODO-FR-001-project-roadmap-consolidated.md` (479L)  Roadmap CONSOLIDADO (viso macro)
- `NC-TODO-DS-001-roadmap-pre-mcp.md` (344L)  Roadmap PR-MCP sprint ativo

Ticket: GOV-002 | Sesso: T0 Antigravity 2026-04-13.

---
## Changelog [2026-04-13]  Sntese Internet + Roadmaps
| Arquivo | Tipo | Path | Nota |
|---|---|---|---|
| NC-ANA-INT-001-synthesis-t0.md | ANA | DIR-RES-CC-001-claude-leak-workzone/ | Sntese T0 internet x NeoCortex, 6 CPs, APROVADO |
| NC-RES-CC-001-validation-hooks-worker-review.md | RES | DIR-RES-CC-001-claude-leak-workzone/ | 269L, pesquisa internet Fase 1 (agente 1) |
| NC-RES-CC-002-validation-buddy-config-plugin.md | RES | DIR-RES-CC-001-claude-leak-workzone/ | 191L, pesquisa internet Fase 1 (agente 2), NC-DS-042B APPROVED |
| NC-RES-CC-003-validation-scheduling-ttl-flags.md | RES | DIR-RES-CC-001-claude-leak-workzone/ | 297L + cdigo Python, pesquisa internet Fase 1 (agente 3) |
| NC-TODO-DS-001-roadmap-pre-mcp.md | TODO | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/ | Atualizado: @SYNTHESIS, 15 ajustes, mapa relacionamentos |
| NC-TODO-DS-002-roadmap-full.md | TODO | 01_neocortex_framework/DIR-DOC-FR-001-docs-main/ | Atualizado: Fase 1.5, backlog faseado, 5 fases totais |
