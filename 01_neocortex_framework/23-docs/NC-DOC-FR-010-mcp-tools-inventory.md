# NC-DOC-FR-010 — MCP Tools Inventory

Gerado: 2026-04-18 21:48 | Arquitetura: CF-v0.2

| # | Arquivo | Tool Name | Actions |
|---|---------|-----------|---------|
| 1 | NC-SUPER-001-governance.py | `neocortex_governance` | audit.replay · bootup.sync · catalog.refresh · cf.pre_check · cf.status · compliance.report · cycle.check · handoff.create · handoff.list · lock.validate · naming.check · roadmap.done · rule.list · ssot.diff · ticket.close · ticket.create · ticket.list · violation.log |
| 2 | NC-SUPER-002-orchestration.py | `neocortex_orchestration` | agent.consume · agent.heartbeat · agent.list · agent.list_ephemeral · agent.spawn · dispatch.create · dispatch.status · task.cancel · task.execute · task.get_result · task.list · task.status · workers.spawn · workers.status |
| 3 | NC-SUPER-003-memory.py | `neocortex_memory` | cortex.get · cortex.get_aliases · cortex.get_full · cortex.get_section · cortex.get_workflows · cortex.reset · cortex.update · cortex.validate_alias · knowledge.search · knowledge.store · lobe.activate · lobe.deactivate · lobe.get · lobe.get_content · lobe.list · lobe.list_active · lobe.list_all · lobe.search · manifest.generate · manifest.generate_all · manifest.list · manifest.query · manifest.update · search.advanced |
| 4 | NC-SUPER-004-state.py | `neocortex_state` | checkpoint.get · checkpoint.list · checkpoint.set · ledger.read · ledger.stats · ledger.update · regression.add_entry · regression.baseline · regression.check · regression.list_all · savepoint.create · savepoint.list · savepoint.rollback · session.end · session.heartbeat · session.status |
| 5 | NC-SUPER-005-llm-router.py | `neocortex_llm_router` | budget.status · gateway.health · gateway.models · gateway.start · gateway.stop · ollama.ask · ollama.list · ollama.pull · route.call · workers.spawn · workers.status |
| 6 | NC-SUPER-006-system.py | `neocortex_system` | config.diff · config.get · config.list · config.list_models · config.reload · config.set_agent_backend · config.set_model · export.list · export.snapshot · health.agent · health.full · health.tools_count · init.workspace · pulse.force · pulse.schedule_custom · pulse.status · system.diagnostics · system.env_check |
| 7 | NC-SUPER-007-brain.py | `neocortex_brain` | brain.critique · brain.feedback · brain.orchestrate · brain.plan · brain.think · intelligence.query · intelligence.synthesize |
| 8 | NC-SUPER-008-context.py | `neocortex_context` | cache.stats · context.budget_status · context.compress · context.estimate · context.prune · context.smart_prune · context.window_used · report.compliance · report.generate · report.list · session.handoff · session.hot · session.summarize |
| 9 | NC-SUPER-009-security.py | `neocortex_security` | access.validate · audit.log_event · gateway.status · hook.list · hook.register · hook.remove · hook.trigger · lock.check · lock.list |
| 10 | NC-SUPER-010-benchmark.py | `neocortex_benchmark` | benchmark.last_report · benchmark.status · run.drift · run.omni · run.titanomachy |
| 11 | NC-SUPER-011-notification.py | `neocortex_notification` | peers.discover · peers.heartbeat · peers.list · peers.sync · push.clear · push.list · push.send · push.status |
| 12 | NC-SUPER-012-akl.py | `neocortex_akl` | akl.add · akl.export · akl.search · consolidate.run · consolidate.session · kg.enrich · kg.query · kg.stats · knowledge.get_boot_context · knowledge.get_documents · knowledge.project_manifest · knowledge.update_index |
| 13 | NC-SUPER-013-health.py | `neocortex_health` | log.errors · log.purge · log.search · log.tail · metrics.live · metrics.tool_stats · server.health · server.status · server.tools_count · watchdog.start · watchdog.status |
| 14 | NC-SUPER-014-ledger.py | `neocortex_ledger` | agent.identity · agent.register · agent.token_budget · ledger.metrics · ledger.read · ledger.stats · ledger.write |
| 15 | NC-SUPER-015-memory-auto.py | `neocortex_memory_auto` | catalog.now · lobe.auto · session.end · session.hot · session.stats · turn.record |
