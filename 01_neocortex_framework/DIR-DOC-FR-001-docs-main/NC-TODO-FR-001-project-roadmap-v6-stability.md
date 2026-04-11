# NC-TODO-FR-001 - NeoCortex Stability-First Roadmap (v6.0)

> **Priority-focused implementation plan ensuring system stability before advanced features**  
> **Analysis Date:** 2026-04-10  
> **Based on:** v8.0 Orquestração Completa + Current v4.0 State + Audit Findings

---

## 🎯 Executive Summary

**Problem:** Advanced features (autonomous T0, vector search, multi-user) built on unstable foundation will cause systemic instability.

**Solution:** Prioritize completion of core infrastructure, configuration management, and agent isolation before proceeding to orchestration automation.

**Critical Path:** Complete ConfigProvider integration, factory audit, sanity tests, and robust HotCache → then implement isolated local agents with mentor mode → then basic manual orchestration → then stabilization and security.

---

## 📊 Current State Assessment (2026-04-11)

### ✅ **Already Stable & Completed**
- **Modular MCP Server:** 22 tools, 73+ actions, hexagonal architecture intact with MetricsStore integration
- **Optimized Stores:** LedgerStore, ManifestStore, LobeIndex, SearchEngine implemented and in use
- **MetricsStore with DuckDB:** Domain tables (daily_token_usage, cost_summary, agent_activity, pulse_health) + MCP report tool
- **Hybrid LLM Mode:** Operational with Ollama + fallback chain configuration
- **Sub-MCP Server Framework:** `sub_server.py` enhanced with role configuration, config.yaml reading, tool filtering
- **Basic Orchestration Tools:** `neocortex_subserver` and `neocortex_task` MCP tools implemented
- **LLM Model Sanitization & Configuration:** Models sanitized, Qwen 1.5B/3B configured as primary backends for agents
- **LLM Factory Bug Fix:** `unhashable type: 'list'` bug in LLMBackendFactory fixed
- **Sanity Test Suite:** 11/11 tests passing (includes metrics validation)
- **Phase 1.5 (Metrics & Reporting):** METR-106 to METR-109 completed

### ⚠️ **Partially Complete / Needs Attention**
- **Agent Isolation (Phase 2):** Courier & engineer environments created with STARTER cortex/ledger, but mentor mode pending
- **ConfigProvider Integration:** Configured and used by most services; file_utils uses config paths
- **HotCache:** Implemented but uses Python diskcache fallback (diskcache-rs optional)
- **Factory Pattern:** Services use stores via factories; singleton patterns audited
- **Task Execution:** `neocortex_task` integrated with AgentExecutor and MetricsStore
- **GPU/iGPU Optimization:** Qwen 3B should run on GPU, Qwen 1.5B on iGPU for memory efficiency (pending)

### ❌ **Missing / Critical for Stability**
- **Mentor Mode Implementation:** `mentor_step_0()` validation not yet implemented
- **Isolation Testing:** AGENT-205 tests for courier/engineer isolation pending
- **Manual Orchestration (Phase 3):** `neocortex_subserver` actions incomplete
- **Security Policies (Phase 4):** Usage limits, failsafe, auto-repair pending
- **Integration Testing (Phase 5):** Multi-agent stress tests pending

---

## 🗺️ Stability-First Roadmap (6 Phases)

| Phase | Name | Duration | Objective | Stability Impact |
| :--- | :--- | :---: | :--- | :--- |
| **PHASE 1** | **Core Infrastructure Completion** | 1-2 days | Complete ConfigProvider integration, audit factories, implement sanity tests | **CRITICAL** - Prevents configuration drift and hidden bugs |
| **PHASE 2** | **Local Agent Isolation & Mentor Mode** | 2-3 days | Implement isolated agents (1.5B, 3B) with mentor mode and tool restrictions | **HIGH** - Foundation for safe multi-agent execution |
| **PHASE 3** | **Manual Orchestration Basics** | 2-3 days | Complete MCP orchestration tools for spawn, task, monitoring | **MEDIUM** - Enables controlled multi-agent workflows |
| **PHASE 4** | **Stabilization & Security Policies** | 2-3 days | Add validation, failsafe, usage policies, and error recovery | **HIGH** - Prevents runaway agents and resource exhaustion |
| **PHASE 5** | **Comprehensive Testing & Documentation** | 2-3 days | Execute integration/stress tests and produce white-label docs | **MEDIUM** - Ensures reliability and enables adoption |
| **PHASE 6** | **Advanced Orchestration (Future)** | 3-5 days | Autonomous T0, vector search, analytics (after stable base) | **LOW** - Advanced features require stable foundation |

**Total:** 11-19 days for stable foundation (Phases 1-5)

---

## 📋 PHASE 1: Core Infrastructure Completion (1-2 days)

**Objective:** Ensure configuration management is complete, factories are clean, and basic sanity tests pass.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **STAB-101** | **Complete ConfigProvider Integration (DONE)** | 1. Verify `PulseScheduler` uses `LedgerStore` (not direct filesystem)<br>2. Ensure all services get config via `get_config()`<br>3. Add config validation for critical paths<br>4. Test config reload without service restart | 3h | **CRITICAL** | Prevents configuration drift; essential for dynamic scaling |
| **STAB-102** | **Audit Factories & Singletons (DONE)** | 1. Review all `get_*_service()` functions for hidden globals<br>2. Ensure services are instantiated via factories<br>3. Remove any remaining global state variables<br>4. Document service lifecycle patterns | 2h | **CRITICAL** | Hidden globals cause hardest-to-debug instability |
| **STAB-103** | **Implement Sanity Test Suite (DONE)** | 1. Create `test_sanity.py` with 10 essential tests<br>2. Test: MCP server starts, tools respond, config loads<br>3. Test: LedgerStore read/write, ManifestStore search<br>4. Test: Sub-server spawn and basic task execution | 2h | **CRITICAL** | Early detection of systemic failures |
| **STAB-104** | **Fix LLM Factory Config Handling** | 1. Fix `unhashable type: 'list'` in `LLMBackendFactory.create_from_config()`<br>2. Handle `fallback_chain` list in config properly<br>3. Ensure AgentExecutor works with current config | 1h | **HIGH** | Blocks task execution in orchestration **(DONE)** |
| **STAB-105** | **Enhance HotCache Robustness (DONE)** | 1. Install `diskcache-rs` if available (`pip install diskcache-rs`)<br>2. Add auto-repair for corrupted cache entries<br>3. Add metrics for cache hit/miss ratio | 1h | **MEDIUM** | Performance optimization, not stability-critical |

**Phase 1 Deliverables:**  
1. ConfigProvider fully integrated and validated  
2. Factory audit report with any issues fixed  
3. Sanity test suite passing (10+ tests)  
4. LLM factory working with `fallback_chain` config  
5. Optional: diskcache-rs installed for HotCache  

---

## 📋 PHASE 1.5: Metrics & Reporting (1-2 days) - ✅ COMPLETED 2026-04-11

**Objective:** Implement DuckDB-based metrics storage and static report generation for monitoring system health, token economy, and ROI validation.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **METR-106** | **Extend MetricsStore with Domain Tables** | 1. Add tables: `daily_token_usage`, `cost_summary`, `agent_activity`, `pulse_health`<br>2. Create helper methods for each domain (e.g., `record_token_usage`, `record_agent_activity`)<br>3. Ensure DuckDB fallback to SQLite works | 2h | **HIGH** | ✅ **COMPLETED** - Tables created, DuckDB/SQLite syntax fixed |
| **METR-107** | **Integrate MetricsStore with Core Components** | 1. Inject MetricsStore into `PulseScheduler`, `AgentExecutor`, `MCP server`<br>2. Record token usage from LLM backends<br>3. Record Pulse events (checkpoints, pruning, consolidation)<br>4. Record agent spawns, tasks, failures | 3h | **HIGH** | ✅ **COMPLETED** - All components integrated, metrics auto-recorded |
| **METR-108** | **Create MCP Report Tool** | 1. Create `neocortex/mcp/tools/report.py` with actions: `generate_daily_summary`, `generate_cost_report`, `generate_agent_report`<br>2. Generate Markdown, CSV, JSON reports in `reports/` directory<br>3. Format reports beautifully (like example in prompt) | 3h | **MEDIUM** | ✅ **COMPLETED** - Report tool with 3 actions, formatted output |
| **METR-109** | **Validation & Sanity Integration** | 1. Add metrics validation to sanity test suite<br>2. Generate sample report for today<br>3. Verify data consistency and report readability | 1h | **MEDIUM** | ✅ **COMPLETED** - Test #11 added, 11/11 tests passing |

**Phase 1.5 Deliverables:**  ✅ **ALL DELIVERABLES MET**  
1. ✅ Extended MetricsStore with domain‑specific tables  
2. ✅ Core components recording metrics automatically  
3. ✅ MCP report tool generating static Markdown/CSV/JSON reports  
4. ✅ Sample daily report showing token economy and system health  

---

## 📋 PHASE 2: Local Agent Isolation & Mentor Mode (2-3 days) - 🔄 IN PROGRESS

**Objective:** Create isolated Sub-MCP Servers for local LLMs (1.5B, 3B) with enforced mentor mode and tool restrictions.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **AGENT-201** | **Create Isolated Agent Environments** | 1. Create `lobes/courier/` and `lobes/engineer/` directories<br>2. Copy tailored Cortex/Ledger templates to each<br>3. Create agent-specific `config.yaml` with role, allowed_tools | 2h | **HIGH** | ✅ **PARTIAL** - Directories created, STARTER cortex/ledger templates copied, config.yaml with allowed_tools |
| **AGENT-202** | **Enhance Sub-Server with Role Configuration** | 1. Update `sub_server.py` to read `config.yaml` from lobe directory<br>2. Add `--role` parameter for agent identification<br>3. Register sub-server in central ledger on startup | 3h | **HIGH** | ✅ **COMPLETED** - Role config reading, tool filtering, --role parameter added |
| **AGENT-203** | **Implement Mentor Mode per Agent** | 1. Create `mentor_step_0(agent_role, tool_name, arguments)`<br>2. Courier: restrict to read-only actions only<br>3. Engineer: allow write actions with validation<br>4. Generate imperative instructions for LLM based on restrictions | 4h | **HIGH** | ❌ **PENDING** - Core validation function not yet implemented |
| **AGENT-204** | **Configure Tool Allow/Deny Lists** | 1. In `config.yaml`, define `allowed_tools` and `forbidden_actions`<br>2. Sub-server must reject calls to non-allowed tools<br>3. Log violations to audit trail | 2h | **MEDIUM** | ✅ **COMPLETED** - Integrated with sub_server.py tool filtering |
| **AGENT-205** | **Test Isolation & Mentor Enforcement** | 1. Start courier manually, attempt forbidden action (should be denied)<br>2. Verify `mentor_step_0()` generates correct imperative instructions<br>3. Test engineer with write permission validation | 2h | **HIGH** | ❌ **PENDING** - Requires AGENT-203 completion |

**Phase 2 Deliverables:**  🔄 **PARTIAL COMPLETION**  
1. ✅ Two isolated agent environments (courier 1.5B, engineer 3B)  
2. ✅ Role-aware sub-server with configuration support  
3. ❌ Working mentor mode with tool restrictions  
4. ✅ Allow/deny lists enforced at sub-server level  
5. ❌ Isolation tests passing  

---

## 📋 PHASE 3: Manual Orchestration Basics (2-3 days) - ⏳ PENDING

**Objective:** Complete MCP tools for manual orchestration, enabling OpenCode to spawn, task, and monitor agents.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **ORCH-301** | **Complete `neocortex_subserver` MCP Tool** | 1. Implement `spawn`, `stop`, `list`, `status`, `send_task` actions<br>2. `spawn`: start sub-server and register in central ledger<br>3. `send_task`: connect to sub-server and invoke `neocortex_task.execute` | 4h | **HIGH** | Core orchestration capability |
| **ORCH-302** | **Complete `neocortex_task` in Sub-Server** | 1. Action: `execute(prompt, context)` with mentor mode application<br>2. Apply `mentor_step_0()` before sending to LLM<br>3. Return structured response with metadata | 2h | **HIGH** | Task execution with safety |
| **ORCH-303** | **Integrate with LLMBackend Hybrid System** | 1. Sub-server uses `LLMBackendFactory` with agent-specific config<br>2. Support local fallback (1.5B → 3B) on failure<br>3. Log LLM usage per agent for analytics | 2h | **MEDIUM** | Leverages existing hybrid LLM infrastructure |
| **ORCH-304** | **Test Complete Manual Flow** | 1. Spawn courier via MCP tool<br>2. Send indexing task, verify result<br>3. Stop courier, verify resource cleanup<br>4. Test concurrent agents (courier + engineer) | 3h | **HIGH** | End-to-end validation |

**Phase 3 Deliverables:**  
1. Complete MCP orchestration toolset  
2. Task execution with mentor mode integration  
3. LLM backend integration per agent  
4. Working manual orchestration flow  

---

## 📋 PHASE 4: Stabilization & Security Policies (2-3 days)

**Objective:** Add validation, failsafe mechanisms, usage policies, and error recovery to prevent instability.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **SEC-401** | **Implement `neocortex_guardian` (Advanced Validation)** | 1. Actions: `validate_tool_call`, `audit_execution`, `enforce_constraints`<br>2. Integrate as optional middleware in sub-servers<br>3. Log all validation decisions to audit trail | 3h | **MEDIUM** | Additional safety layer |
| **SEC-402** | **Create `neocortex_failsafe` (Failure Recovery)** | 1. Actions: `detect_failure`, `rollback`, `switch_backend`<br>2. Used by orchestration to handle stuck agents<br>3. Automatic restart with exponential backoff | 2h | **MEDIUM** | Improves system resilience |
| **SEC-403** | **Configure Usage Policies per Agent** | 1. In `config.yaml`: `max_tokens_per_task`, `max_execution_time`<br>2. Sub-server interrupts tasks exceeding limits<br>3. Alert T0 interactive when limits approached | 2h | **MEDIUM** | Prevents resource exhaustion |
| **SEC-404** | **Implement Auto-Repair for Stores** | 1. Add checksum validation to LedgerStore, ManifestStore<br>2. Auto-repair corrupted entries with fallback to JSON<br>3. Notify administrator via pulse alerts | 2h | **HIGH** | Prevents data corruption cascades |

**Phase 4 Deliverables:**  
1. Guardian validation middleware  
2. Failsafe recovery mechanisms  
3. Configurable usage policies  
4. Auto-repair for corrupted stores  

---

## 📋 PHASE 5: Comprehensive Testing & Documentation (2-3 days)

**Objective:** Execute rigorous tests and produce white-label documentation for stable deployment.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **TEST-501** | **Integration Test Suite** | 1. Spawn courier and engineer simultaneously<br>2. Send 20 concurrent tasks, verify isolation<br>3. Simulate agent failure and verify recovery<br>4. Test configuration reload during operation | 4h | **HIGH** | Validates multi-agent stability |
| **TEST-502** | **Stress Test (Hybrid Titanomachy)** | 1. Run benchmark with 100 tasks using full architecture<br>2. Measure token economy and response time<br>3. Verify no memory leaks or resource exhaustion | 3h | **MEDIUM** | Performance validation |
| **DOC-503** | **White-Label Documentation** | 1. Update `white_label/README.md` with agent setup<br>2. Create `NC-DOC-WL-003-agent-setup.md`<br>3. Generate example `config.yaml` templates | 3h | **MEDIUM** | Enables adoption |
| **DOC-504** | **Final ROI Report** | 1. Update `BENCHMARKS_HYBRID.md` with real test data<br>2. Calculate token/cost savings from architecture<br>3. Publish summary for stakeholder review | 2h | **LOW** | Demonstrates value |

**Phase 5 Deliverables:**  
1. Integration and stress test results  
2. Complete white-label documentation  
3. Updated benchmarks with real data  
4. System ready for production use  

---

## 📋 PHASE 6: Advanced Orchestration (Future - After Stable Foundation)

**Objective:** Implement autonomous T0, vector search, and analytics on stable base.

| Ticket | Task | Est. | Priority |
| :--- | :--- | :---: | :--- |
| **ADV-601** | Autonomous T0 with DeepSeek API | 4h | Future |
| **ADV-602** | Vector Store implementation (LanceDB) | 3h | Future |
| **ADV-603** | Metrics Store with DuckDB analytics | 3h | Future |
| **ADV-604** | Multi-user collaboration gateway | 5h | Future |

---

## 🔗 Dependencies & Critical Path

1. **STAB-101 → STAB-102 → STAB-103** (Core infrastructure must be stable first)
2. **STAB-104** (Fix LLM factory) required for **ORCH-302** (Task execution)
3. **AGENT-201 → AGENT-202 → AGENT-203** (Agent setup before orchestration)
4. **ORCH-301** (Orchestration tools) depends on **AGENT-202** (Enhanced sub-server)
5. **SEC-404** (Auto-repair) should follow **STAB-103** (Sanity tests)

**Critical Path Duration:** 7-12 days (Phases 1-4, excluding documentation)

---

## 🚨 Risk Assessment

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **ConfigProvider not fully integrated** | HIGH - Configuration drift causes unpredictable behavior | STAB-101 (complete integration) with validation |
| **Hidden global state in factories** | HIGH - Causes hardest-to-debug instability | STAB-102 (factory audit) with comprehensive review |
| **LLM factory config handling bug** | MEDIUM - Blocks task execution | STAB-104 (fix list handling) |
| **Agent isolation failure** | HIGH - Security breach, resource conflict | AGENT-205 (isolation tests) before orchestration |
| **No usage limits** | MEDIUM - Resource exhaustion, cost overruns | SEC-403 (usage policies) |

---

## 🏁 Success Criteria for Stability Milestone

1. ✅ Sanity test suite passes (10+ tests)
2. ✅ ConfigProvider used by all services, validated at runtime
3. ✅ Factory audit clean, no hidden globals
4. ✅ Courier (1.5B) and Engineer (3B) agents isolated with mentor mode
5. ✅ Manual orchestration via MCP tools functional
6. ✅ Usage policies enforced, failsafe mechanisms operational
7. ✅ Integration tests pass with concurrent agents

**When these are met, the foundation is stable for advanced features.**

---

**Version:** 6.0 (Stability-First)  
**Created:** 2026-04-10  
**Based on:** v8.0 Orquestração Completa + v4.0 Current State  
**Next Review:** After Phase 1 completion