# Auditoria SSOT vs Materialidade (KGS)

**Data:** 2026-04-14
O relatrio cruza os 258 arquivos materiais da Teia KGS com as 275 entradas na tabela oficial em `NC-NAM-FR-001`.

** Resumo Executivo**
- **Arquivos Fsicos Indexados:** 258
- **Entradas na Tabela SSOT:** 275
- ** Arquivos Fantasmas (Fsicos NO listados no SSOT):** 150
- ** Links Mortos (Listados no SSOT, mas no existem no disco):** 155

---

##  Links Mortos (SSOT Defasado)
Estes arquivos constam na Bblia, mas no foram encontrados materialmente pela KGS.
- `requirements.txt`
- `index.redb`
- `NC-LBE-DS-002-deepseek-agent-b.mdc`
- `test_tools.py`
- `test_config_reload.py`
- `metrics.db.wal`
- `NC-LBE-FR-BENCHMARKS-001.mdc`
- `NC-PROMPT-DS-001-deepseek-subordinate.md`
- `NC-DS-001-fr025-system.yaml`
- `PKG-INFO`
- `NC-CFG-DS-002-session-contract.yaml`
- `start_neocortex_dev.bat`
- `TEST_INDEX_13aa6e78.mdc`
- `NC-TOOL-FR-028-export.py`
- `Aqui est o prompt ajustado exatamente c.txt`
- `NC-MCP-FR-001-mcp-server.py`
- `Sem ttulo.txt`
- `README_MCP_NEOCORTEX.md`
- `example_architecture.py`
- `benchmark_master_suite.py`
- `LLM e API .md`
- `NC-LBE-FR-LEGACY-001.mdc`
- `NC-LBE-FR-WHITELABEL-001.mdc`
- `NC-TLM-FR-001-tool-manifest-schema.json`
- `DEEPSEEK_API_SUMMARY.md`
- `install.sh`
- `TEST_INDEX_19948498.mdc`
- `start_neocortex_mcp.bat`
- `test_server_start.py`
- `NC-LBE-FR-002-claude-assistant.mdc`
- `neocortex_mcp.py`
- `test_mcp_simple.py`
- `requires.txt`
- `sumario.md`
- `memory-ledger-TEMPLATE.json`
- `ledger_20260410_203605.json`
- `generate_tools_manifest.py`
- `list_tools_simple.py`
- `NC-LBE-FR-MCP-001.mdc`
- `NC-CTX-FR-001-cortex-central-20260410-0140.mdc`
- `test_modular_server.py`
- `add_root_sanitize_event.py`
- `NC-LBE-FR-SECURITY-001.mdc`
- `analyze_mcp_tools.py`
- `lobe_index.db`
- `NC-LBE-FR-PROFILES-001.mdc`
- `update_antigravity_confirmation.py`
- `update_ledger_status.py`
- `NC-TODO-FR-001-project-roadmap-v7-combined.md`
- `phase-lobe-TEMPLATE.mdc`
- `extract_tools_final.py`
- `NC-LBE-FR-MONITORING-001.mdc`
- `7fd282bb51e2535a2323bf377a90.val`
- `ledger_20260410_212708.json`
- `NC-LBE-FR-INTEGRATION-001.mdc`
- `extract_tools.py`
- `NC-LBE-FR-KNOWLEDGE-001.mdc`
- `ledger_20260410_174028.json`
- `test_mcp_responsive.py`
- `package.json`
- `TEST_INDEX_8f76b831.mdc`
- `test_tools_simple.py`
- `NC-HUB-FR-001-mcp-hub.py`
- `NC-SCR-FR-064-orchestration-agent-fixes.ps1`
- `migration.log`
- `NC-CFG-DS-001-agent-policy.yaml`
- `NC-DS-HANDOFF-TEMPLATE.yaml`
- `list_tools.py`
- `server.js`
- `migration_report.json`
- `00-cortex-20260409.mdc`
- `NC-LED-FR-001-framework-ledger.json`
- `entry_points.txt`
- `NC-TMP-WL-001-cortex-template.mdc`
- `memory_neocortex_framework-20260409.json`
- `backup_manifest.json`
- `STATUS.md`
- `NC-LBE-DS-001-deepseek-agent.mdc`
- `ledger_20260410_174150.json`
- `NC-PLN-FR-001-optimization-plan.mdc`
- `install.ps1`
- `NC-LBE-FR-PULSE-001.mdc`
- `SOURCES.txt`
- `QUICK_TEST.py`
- `SANITIZATION_CHECKLIST.md`
- `NC-LBE-FR-DOCUMENTATION-001.mdc`
- `cache.db`
- `neocortex_config_dev.yaml`
- `CONTINUE.md`
- `NC-TLM-FR-001-tool-manifest.json`
- `NC-DOC-FR-003-turboquant-prompt.md`
- `NC-LBE-FR-CORE-001.mdc`
- `mcp_tools_inventory.json`
- `antigravity_neocortex_config.json`
- `NC-DOC-WL-001-readme.md`
- `ledger_20260410_173853.json`
- `migration_debug.log`
- `NC-TODO-FR-001-project-roadmap.md.bak`
- `tools_manifest.json`
- `dependency_links.txt`
- `cruzar com o roadmap.txt`
- `extract_all_tools.py`
- `NC-DOC-WL-001-hybrid-mode.md`
- `NC-TODO-FR-001-project-roadmap.md.backup`
- `NC-LBE-FR-TESTING-001.mdc`
- `NC-LBE-DS-000-parent.mdc`
- `checkpoint_tree_phase1.json`
- `top_level.txt`
- `NC-AUD-FR-001-audit-findings-2026-04-10.md`
- `NC-TOOL-FR-020-categories.py`
- `ledger_backup_20260410_001233.json`
- `benchmark_fractal_gauntlet.py`
- `start_neocortex_mcp.ps1`
- `NC-LBE-FR-PERFORMANCE-001.mdc`
- `server.py.backup`
- `NC-LED-FR-001-framework-ledger-20260410-0140.json`
- `metrics.db`
- `pyproject.toml`
- `NC-CFG-DS-003-coordination.yaml`
- `restart-session.md`
- `NC-TKT-FR-001-tickets.md`
- `00-cortex-FULL.mdc`
- `NC-LBE-FR-DEVELOPMENT-001.mdc`
- `clean_utf0.py`
- `test_task.py`
- `structured_elements.md`
- `BENCHMARKS.md`
- `NC-LED-FR-001-framework-ledger.json.backup`
- `ledger_20260410_173805.json`
- `generate_official_tool_manifest.py`
- `test_security_integration.py`
- `update_ledger.py`
- `ledger_20260410_173509.json`
- `clean_security.py`
- `NC-LBE-FR-CLI-001.mdc`
- `NC-TODO-FR-001-project-roadmap.md`
- `fire_test.py`
- `NC-TODO-FR-001-project-roadmap-v6-stability.md`
- `NC-CTX-FR-001-cortex-central.mdc`
- `NC-PROMPT-DS-000-launcher.md`
- `NC-SES-FR-001-session-status-2026-04-10.md`
- `NC-LBE-FR-DEPLOYMENT-001.mdc`
- `detalhamento_completo.md`
- `AGENTS.md`
- `NC-MAN-FR-001-project-manifest.jsonl`
- `BENCHMARKS_HYBRID.md`
- `rules.txt`
- `CHECKPOINT_AUDIT_2026-04-10.md`
- `README.md`
- `NC_SEC_FR_001_security_utils.py`
- `SANITIZAO DA PASTA TURBOQUANT_V42 .txt`
- `test_sanity.py`
- `NC-LBE-FR-ARCHITECTURE-001.mdc`
- `verify_mcp.py`
- `NeoCortex_HUD.bat`

---

##  Arquivos Fantasmas (Trabalho Sujo)
Estes arquivos *existem materialmente* e esto na Teia Semntica, mas **no tm registro no SSOT NC-NAM-FR-001**.
Agrupados por Pasta:

### ` C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\02_memory_lobes`
- `NC-LBE-INT-004-mission-control.mdc`
- `NC-LBE-INT-005-pixel-agents.mdc`

### ` DIR-DOC-FR-001-docs-main`
- `courier_progress.json`
- `coverage_report.json`
- `coverage_report.md`
- `discrepancy_report.json`
- `extraction_audit.json`
- `NC-ANALYSIS-FR-001-renaming-plan-review.yaml`
- `NC-APP-FR-001-technical-appendix.md`
- `NC-ARC-FR-001-decision-log.md`
- `NC-AUD-FR-001-timestamp-audit.md`
- `NC-CFG-FR-001-agent-policy-template.yaml`
- `NC-CFG-FR-002-rules-policy.md`
- `NC-CFG-FR-002-rules-policy.yaml`
- `NC-CYC-FR-001-4-cycle-validation.md`
- `NC-DOC-DS-005-topological-taxonomy.md`
- `NC-DOC-FR-001-ubiquitous-language-dictionary.md`
- `NC-DOC-FR-002-dev-environment-standard.md`
- `NC-GOV-FR-001-nworker-protocol.md`
- `NC-GOV-FR-002-ticket-lifecycle.md`
- `NC-GOV-FR-002-ticket-lifecycle.yaml`
- `NC-GOV-FR-003-ia-governance-rules.md`
- `NC-GOV-FR-003-ia-governance-rules.yaml`
- `NC-GOV-FR-004-fr-artifacts-registry.yaml`
- `NC-GOV-FR-005-governance-ecosystem.yaml`
- `NC-NAM-FR-001a-tools-registry.md`
- `NC-NAM-FR-001b-lobes-registry.md`
- `NC-NAM-FR-001c-config-registry.md`
- `NC-NAM-FR-001d-prompts-registry.md`
- `NC-REPORT-FR-001-consolidated-results.md`
- `NC-SEC-FR-001-atomic-locks.md`
- `NC-SEC-FR-001-atomic-locks.yaml`
- `NC-SEC-FR-002-entry-lock-protocol.md`
- `NC-SOP-FR-001-session-startup.md`
- `NC-TODO-DS-001-roadmap-pre-mcp.md`
- `orchestration_report_20260414-132918.md`
- `PROJECT_MAP.md`
- `renaming_analysis_summary.yaml`
- `renaming_plan.yaml`
- `renaming_plan_v2.yaml`
- `renaming_plan_v2_dedup.yaml`
- `ssot_audit_report.json`
- `ssot_audit_report.md`
- `structural_audit_report.md`
- `symbolic_map.json`
- `test_coverage_checklist.md`

### ` lobes`
- `NC-LBE-DS-003-worker-patterns.mdc`
- `NC-LBE-FR-QUALITY-001-env-quality.mdc`
- `NC-LBE-FR-QUALITY-002-context-compaction.mdc`
- `NC-LBE-INT-001-picoclaw-architecture.mdc`
- `NC-LBE-INT-002-opencode-architecture.mdc`
- `NC-LBE-INT-003-antigravity-integration.mdc`

### ` lobes\backend_dev`
- `NC-LBE-FR-DEEPSEEK-001.md`

### ` lobes\cc-leak`
- `NC-LBE-CC-002-hooks-system.mdc`
- `NC-LBE-CC-003-persistent-worker.mdc`
- `NC-LBE-CC-004-confidence-review.mdc`
- `NC-LBE-CC-005-session-mate.mdc`
- `NC-LBE-CC-006-project-config.mdc`
- `NC-LBE-CC-007-plugin-template.mdc`
- `NC-LBE-CC-008-pulse-daemon.mdc`
- `NC-LBE-CC-009-ttl-session-manager.mdc`
- `NC-LBE-CC-010-feature-flags-channels.mdc`

### ` neocortex`
- `__init__.py`

### ` neocortex\cli`
- `__init__.py`

### ` neocortex\core`
- `logging_config.py`
- `__init__.py`

### ` neocortex\core\adapters`
- `NC-ADP-FR-001-mission-control.py`
- `__init__.py`

### ` neocortex\core\config`
- `NC-CFG-FR-002-feature-flags.py`
- `NC-CFG-FR-004-project-config-schema.yaml`
- `NC-CFG-FR-004-project-config.py`
- `NC-CFG-FR-004-project-loader.py`

### ` neocortex\core\hooks`
- `NC-HK-FR-001-hook-registry.py`
- `NC-HK-FR-002-simple-hook.py`
- `__init__.py`

### ` neocortex\core\review`
- `NC-REV-FR-001-confidence-review.py`
- `NC-VAL-FR-005-async-thread-validator.py`
- `__init__.py`

### ` neocortex\core\review\validators`
- `NC-VAL-FR-001-naming-validator.py`
- `NC-VAL-FR-002-compile-validator.py`
- `NC-VAL-FR-003-locks-validator.py`
- `__init__.py`

### ` neocortex\core\services`
- `NC-SVC-FR-003-savepoint-stub.py`
- `NC-SVC-FR-006-metrics-collector.py`
- `NC-SVC-FR-008-config-validator.py`
- `NC-SVC-FR-009-session-buddy.py`
- `NC-SVC-FR-010-kairos-service.py`
- `NC-SVC-FR-011-ttl-manager.py`
- `NC-SVC-FR-012-channel-notifier.py`
- `NC-SVC-FR-014-dry-run-preview.py`
- `NC-SVC-FR-015-task-broker.py`

### ` neocortex\core\utils`
- `NC-UTL-FR-002-hash-utils.py`
- `NC-UTL-FR-003-path-resolver.py`
- `NC-UTL-FR-004-id-validator.py`
- `__init__.py`

### ` neocortex\core\workers`
- `NC-WKR-FR-001-persistent-worker.py`

### ` neocortex\infra`
- `symbolic_compressor.py`
- `vector_engine.py`
- `vector_engine_example.py`
- `__init__.py`

### ` neocortex\mcp`
- `__init__.py`

### ` neocortex\mcp\tools`
- `NC-TOOL-FR-018-push-notification.py`
- `NC-TOOL-FR-021-memory.py`
- `NC-TOOL-FR-034-dry-run.py`
- `NC-TOOL-FR-035-task.py`
- `NC-TOOL-FR-036-picoclaw.py`
- `NC-TOOL-FR-037-hooks.py`
- `__init__.py`

### ` neocortex\repositories`
- `__init__.py`

### ` neocortex\schemas`
- `__init__.py`

### ` scripts`
- `approve_handoffs.py`
- `audit_reader.py`
- `batch_approve.py`
- `dep_scanner.py`
- `fix_approve_022_023.py`
- `fix_queue.py`
- `NC-SCR-FR-001-populate-lobes-ssot.py`
- `NC-SCR-FR-002-tool-manifest-generator.py`
- `NC-SCR-FR-004-governance-validator.py`
- `NC-SCR-FR-005-auto-approve.py`
- `NC-SCR-FR-006-ticket-validator.py`
- `NC-SCR-FR-007-queue-monitor.py`
- `NC-SCR-FR-008-queue-repair.py`
- `NC-SCR-FR-010-sync-ticket-status.py`
- `NC-SCR-FR-011-sanitize-handoffs.py`
- `NC-SCR-FR-012-new-tool.py`
- `NC-SCR-FR-013-validate-file.py`
- `NC-SCR-FR-017-visual-server.py`
- `NC-SCR-FR-020-yaml-injector.py`
- `NC-SCR-FR-021-lexicon-extractor.py`
- `NC-SCR-FR-022-coverage-auditor.py`
- `NC-SCR-FR-023-ssot-auditor.py`
- `NC-SCR-FR-024-structural-auditor.py`
- `NC-SCR-FR-051-knowledge-graph-builder.py`
- `NC-SCR-FR-060-courier-saneamento.py`
- `NC-SCR-FR-061-courier-discrepancy-fix.py`
- `NC-SCR-FR-061-engineer-documentacao.py`
- `NC-SCR-FR-062-engineer-encoding-fix.py`
- `NC-SCR-FR-062-tester-vector.py`
- `NC-SCR-FR-063-tester-vector-fix.py`
- `NC-SCR-FR-064-artifact-catalog.py`
- `NC-SCR-FR-065-rename-impact-analyzer.py`
- `NC-SCR-FR-066-bootup-sync.py`
- `NC-SCR-FR-075-genealogy-injector.py`
- `NC-SCR-FR-080-governance-auditor.py`
- `NC-SCR-FR-081-config-migrator.py`
- `NC-TST-FR-001-test-rag-search.py`
- `reset_ds018.py`
- `sign_tickets.py`
- `stamp_prompt.py`

---
*Relatrio gerado por NC-SCR-FR-023-ssot-auditor.py*