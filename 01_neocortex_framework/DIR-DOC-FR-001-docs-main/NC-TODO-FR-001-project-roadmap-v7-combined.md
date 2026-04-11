# NC-TODO-FR-001 - NeoCortex Combined Stability Roadmap (v7.0)

> **Unified roadmap merging stability-first approach (v6.0) with comprehensive feature set (v5.0)**  
> **Analysis Date:** 2026-04-11  
> **Based on:** v6.0 Stability-First + v5.0 Evolution + Current Implementation State

---

## 🎯 Executive Summary

**Problem:** Advanced features (autonomous T0, vector search, multi-user) built on unstable foundation will cause systemic instability.

**Solution:** Prioritize completion of core infrastructure, configuration management, and agent isolation before proceeding to orchestration automation, while incorporating critical security and tooling enhancements from v5.0.

**Critical Path:** Complete ConfigProvider integration, factory audit, sanity tests → implement isolated local agents with mentor mode → basic manual orchestration → stabilization and security → comprehensive testing → advanced orchestration → hierarchy & connectivity.

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
- **Phase 2 (Partial):** Agent environments created, sub-server enhanced, tool filtering implemented

### ⚠️ **Partially Complete / Needs Attention**
- **Agent Isolation (Phase 2):** Courier & engineer environments created with STARTER cortex/ledger, but mentor mode pending
- **ConfigProvider Integration:** Configured and used by most services; file_utils uses config paths
- **HotCache:** Implemented but uses Python diskcache fallback (diskcache-rs optional)
- **Factory Pattern:** Services use stores via factories; singleton patterns audited
- **Task Execution:** `neocortex_task` integrated with AgentExecutor and MetricsStore
- **GPU/iGPU Optimization:** Qwen 3B should run on GPU, Qwen 1.5B on iGPU for memory efficiency (pending)
- **MCP Security:** Basic security tool exists but lacks authentication (JWT/API keys) and versioning

### ❌ **Missing / Critical for Stability**
- **Mentor Mode Implementation:** `mentor_step_0()` validation not yet implemented
- **Isolation Testing:** AGENT-205 tests for courier/engineer isolation pending
- **Manual Orchestration (Phase 3):** `neocortex_subserver` actions incomplete
- **Security Policies (Phase 4):** Usage limits, failsafe, auto-repair, authentication pending
- **Integration Testing (Phase 5):** Multi-agent stress tests pending
- **Tool Documentation & CLI:** Comprehensive docs, CLI client, IDE integration tests missing

---

## 🗺️ Combined Stability Roadmap (7 Phases)

| Phase | Name | Duration | Objective | Stability Impact |
| :--- | :--- | :---: | :--- | :--- |
| **PHASE 1** | **Core Infrastructure Completion** | 1-2 days | Complete ConfigProvider integration, audit factories, implement sanity tests | **CRITICAL** - Prevents configuration drift and hidden bugs |
| **PHASE 1.5** | **Metrics & Reporting** | 1-2 days | Implement DuckDB metrics storage and static report generation | **HIGH** - Monitoring, token economy, ROI validation |
| **PHASE 2** | **Local Agent Isolation & Mentor Mode** | 2-3 days | Implement isolated agents (1.5B, 3B) with mentor mode and tool restrictions | **HIGH** - Foundation for safe multi-agent execution |
| **PHASE 3** | **Manual Orchestration Basics** | 2-3 days | Complete MCP orchestration tools for spawn, task, monitoring | **MEDIUM** - Enables controlled multi-agent workflows |
| **PHASE 4** | **Stabilization & Security Policies** | 2-3 days | Add validation, failsafe, usage policies, error recovery, authentication | **HIGH** - Prevents runaway agents and resource exhaustion |
| **PHASE 5** | **Comprehensive Testing & Documentation** | 2-3 days | Execute integration/stress tests, produce white-label docs, CLI, IDE tests | **MEDIUM** - Ensures reliability and enables adoption |
| **PHASE 6** | **Multi-Agent Orchestration & Advanced Tools** | 3-5 days | Complete fire test validation, resilience testing, advanced orchestration | **MEDIUM** - Validates multi-agent architecture |
| **PHASE 7** | **Advanced Hierarchy & Network Connectivity** | 3-4 weeks | Hierarchical lobe architecture, multi-network connectivity, enterprise governance | **LOW** - Enterprise-scale features require stable foundation |

**Total:** 16-30 days for complete stable foundation (Phases 1-6) + future enterprise features (Phase 7)

---

## 📋 PHASE 1: Core Infrastructure Completion (1-2 days) - ✅ COMPLETED

**Objective:** Ensure configuration management is complete, factories are clean, and basic sanity tests pass.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **STAB-101** | **Complete ConfigProvider Integration (DONE)** | 1. Verify `PulseScheduler` uses `LedgerStore` (not direct filesystem)<br>2. Ensure all services get config via `get_config()`<br>3. Add config validation for critical paths<br>4. Test config reload without service restart | 3h | **CRITICAL** | ✅ **COMPLETED** - Prevents configuration drift |
| **STAB-102** | **Audit Factories & Singletons (DONE)** | 1. Review all `get_*_service()` functions for hidden globals<br>2. Ensure services are instantiated via factories<br>3. Remove any remaining global state variables<br>4. Document service lifecycle patterns | 2h | **CRITICAL** | ✅ **COMPLETED** - Hidden globals cause hardest-to-debug instability |
| **STAB-103** | **Implement Sanity Test Suite (DONE)** | 1. Create `test_sanity.py` with 10 essential tests<br>2. Test: MCP server starts, tools respond, config loads<br>3. Test: LedgerStore read/write, ManifestStore search<br>4. Test: Sub-server spawn and basic task execution | 2h | **CRITICAL** | ✅ **COMPLETED** - Early detection of systemic failures |
| **STAB-104** | **Fix LLM Factory Config Handling (DONE)** | 1. Fix `unhashable type: 'list'` in `LLMBackendFactory.create_from_config()`<br>2. Handle `fallback_chain` list in config properly<br>3. Ensure AgentExecutor works with current config | 1h | **HIGH** | ✅ **COMPLETED** - Blocks task execution in orchestration |
| **STAB-105** | **Enhance HotCache Robustness (DONE)** | 1. Install `diskcache-rs` if available (`pip install diskcache-rs`)<br>2. Add auto-repair for corrupted cache entries<br>3. Add metrics for cache hit/miss ratio | 1h | **MEDIUM** | ✅ **COMPLETED** - Performance optimization |

**Phase 1 Deliverables:**  ✅ **ALL DELIVERABLES MET**  
1. ✅ ConfigProvider fully integrated and validated  
2. ✅ Factory audit report with any issues fixed  
3. ✅ Sanity test suite passing (10+ tests)  
4. ✅ LLM factory working with `fallback_chain` config  
5. ✅ Optional: diskcache-rs installed for HotCache  

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

## 📋 PHASE 4: Stabilization & Security Policies (2-3 days) - ⏳ PENDING

**Objective:** Add validation, failsafe mechanisms, usage policies, error recovery, and authentication to prevent instability.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **SEC-401** | **Implement `neocortex_guardian` (Advanced Validation)** | 1. Actions: `validate_tool_call`, `audit_execution`, `enforce_constraints`<br>2. Integrate as optional middleware in sub-servers<br>3. Log all validation decisions to audit trail | 3h | **MEDIUM** | Additional safety layer |
| **SEC-402** | **Create `neocortex_failsafe` (Failure Recovery)** | 1. Actions: `detect_failure`, `rollback`, `switch_backend`<br>2. Used by orchestration to handle stuck agents<br>3. Automatic restart with exponential backoff | 2h | **MEDIUM** | Improves system resilience |
| **SEC-403** | **Configure Usage Policies per Agent** | 1. In `config.yaml`: `max_tokens_per_task`, `max_execution_time`<br>2. Sub-server interrupts tasks exceeding limits<br>3. Alert T0 interactive when limits approached | 2h | **MEDIUM** | Prevents resource exhaustion |
| **SEC-404** | **Implement Auto-Repair for Stores** | 1. Add checksum validation to LedgerStore, ManifestStore<br>2. Auto-repair corrupted entries with fallback to JSON<br>3. Notify administrator via pulse alerts | 2h | **HIGH** | Prevents data corruption cascades |
| **SEC-405** | **Implement Authentication & API Keys (from v5.0 T1-001)** | 1. Add JWT authentication for MCP server<br>2. API key management for external integrations<br>3. Secure tool calls with role-based permissions | 4h | **HIGH** | Critical for production security |
| **SEC-406** | **Implement Tool Versioning & Backward Compatibility (from v5.0 T1-006)** | 1. Add version field to tool manifests<br>2. Support multiple tool versions concurrently<br>3. Deprecation warnings and migration paths | 3h | **MEDIUM** | Ensures stable upgrades |

**Phase 4 Deliverables:**  
1. Guardian validation middleware  
2. Failsafe recovery mechanisms  
3. Configurable usage policies  
4. Auto-repair for corrupted stores  
5. Authentication and API key security  
6. Tool versioning support  

---

## 📋 PHASE 5: Comprehensive Testing & Documentation (2-3 days) - ⏳ PENDING

**Objective:** Execute rigorous tests, produce white-label documentation, CLI client, IDE integration tests, and tool manifest generation.

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **TEST-501** | **Integration Test Suite** | 1. Spawn courier and engineer simultaneously<br>2. Send 20 concurrent tasks, verify isolation<br>3. Simulate agent failure and verify recovery<br>4. Test configuration reload during operation | 4h | **HIGH** | Validates multi-agent stability |
| **TEST-502** | **Stress Test (Hybrid Titanomachy)** | 1. Run benchmark with 100 tasks using full architecture<br>2. Measure token economy and response time<br>3. Verify no memory leaks or resource exhaustion | 3h | **MEDIUM** | Performance validation |
| **DOC-503** | **White-Label Documentation** | 1. Update `white_label/README.md` with agent setup<br>2. Create `NC-DOC-WL-003-agent-setup.md`<br>3. Generate example `config.yaml` templates | 3h | **MEDIUM** | Enables adoption |
| **DOC-504** | **Final ROI Report** | 1. Update `BENCHMARKS_HYBRID.md` with real test data<br>2. Calculate token/cost savings from architecture<br>3. Publish summary for stakeholder review | 2h | **LOW** | Demonstrates value |
| **TOOL-505** | **Create CLI Client (from v5.0 T1-002)** | 1. Implement `neocortex_cli.py` with all MCP tool actions<br>2. Support local usage without IDE integration<br>3. Command completion and help system | 4h | **MEDIUM** | Improves developer experience |
| **TOOL-506** | **Test IDE Integration (from v5.0 T1-003)** | 1. Test with VS Code, Cursor, Antigravity<br>2. Verify tool discovery and execution<br>3. Document IDE-specific setup steps | 3h | **MEDIUM** | Ensures broad compatibility |
| **TOOL-507** | **Comprehensive Tool Documentation (from v5.0 T1-004)** | 1. Create complete API reference with usage examples<br>2. Generate interactive documentation site<br>3. Include troubleshooting guides | 4h | **MEDIUM** | Critical for adoption |
| **TOOL-508** | **Tool Manifest Generation (from v5.0 T1-005)** | 1. Automated manifest generation from tool definitions<br>2. Validation against JSON schema<br>3. Version-aware manifest updates | 3h | **MEDIUM** | Maintains manifest accuracy |

**Phase 5 Deliverables:**  
1. Integration and stress test results  
2. Complete white-label documentation  
3. Updated benchmarks with real data  
4. CLI client for local usage  
5. Verified IDE integration  
6. Comprehensive tool documentation  
7. Automated manifest generation  

---

## 📋 PHASE 6: Multi-Agent Orchestration & Advanced Tools (3-5 days) - ⏳ PENDING

**Objective:** Complete fire test validation, resilience testing, and advanced orchestration capabilities (v5.0 Phase 6).

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **ORCH-601** | **Create Isolated Lobes for Fire Test** | 1. Create guardian, backend_dev, indexer lobe directories<br>2. Dedicated `.agents/rules` files for each role<br>3. Configure isolated sub-servers for each lobe | 3h | **HIGH** | Foundation for fire test |
| **ORCH-602** | **Orchestrate Fire Test Execution** | 1. Spawn 3 sub-servers simultaneously<br>2. Send parallel tasks to each agent<br>3. Validate multi-agent coordination and isolation | 4h | **HIGH** | Validates multi-agent architecture |
| **ORCH-603** | **Validate Resilience & Failure Recovery** | 1. Simulate agent failure and verify recovery<br>2. Test isolation boundaries (data, process)<br>3. Measure concurrency handling under load | 3h | **HIGH** | Ensures system robustness |
| **ORCH-604** | **Advanced Orchestration Patterns** | 1. Implement task chaining across agents<br>2. Add result aggregation and synthesis<br>3. Create workflow templates for common patterns | 4h | **MEDIUM** | Enables complex workflows |
| **ORCH-605** | **Performance Benchmarking** | 1. Measure token economy with multiple agents<br>2. Compare performance vs single-agent baseline<br>3. Publish fire test results in benchmarks | 2h | **MEDIUM** | Quantifies multi-agent efficiency |

**Phase 6 Deliverables:**  
1. Fire test validation report  
2. Resilience and failure recovery proof  
3. Advanced orchestration patterns  
4. Performance benchmarks for multi-agent  
5. Ready for enterprise-scale deployment  

---

## 📋 PHASE 7: Advanced Hierarchy & Network Connectivity (3-4 weeks) - ⏳ FUTURE

**Objective:** Implement hierarchical lobe architecture, multi-network connectivity models, and enterprise-scale governance (v5.0 Phase 7).

| Ticket | Task | Micro Tasks | Est. | Priority | Notes |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **HIER-701** | **Audit Report Hierarchy** | 1. Inventory and analysis of existing components<br>2. Gap analysis for hierarchical architecture<br>3. Produce `AUDIT_REPORT_HIERARCHY.md` | 4h | **MEDIUM** | Foundation for hierarchy design |
| **HIER-702** | **Architecture Hierarchy Design** | 1. Define hierarchical lobe model with 5 levels<br>2. Establish inheritance rules and lateral isolation<br>3. Produce `ARCHITECTURE_HIERARCHY.md` | 5h | **MEDIUM** | Blueprint for hierarchical system |
| **HIER-703** | **Expand LobeService for Hierarchical Operations** | 1. Add parent_id, ancestor_ids to LobeIndex<br>2. Update `neocortex/core/lobe_service.py`<br>3. Implement inheritance and access control | 6h | **HIGH** | Core hierarchical functionality |
| **HIER-704** | **Create MCP Tool `neocortex_hierarchy`** | 1. Actions: `create_child`, `grant_access`, `inherit_rules`<br>2. Hierarchy visualization and management<br>3. Integration with existing lobe tools | 4h | **MEDIUM** | Management interface |
| **CONN-705** | **Implement mDNS Discovery for LAN Connectivity** | 1. Integrate zeroconf for service discovery<br>2. Create `neocortex/infra/discovery.py`<br>3. Test LAN connectivity between instances | 3h | **MEDIUM** | Enables local network collaboration |
| **CONN-706** | **Implement gRPC Server Stub** | 1. Create `.proto` definitions for high-performance communication<br>2. Implement `neocortex/infra/grpc_server.py`<br>3. Benchmark vs MCP protocol | 5h | **MEDIUM** | Foundation for high-performance networks |
| **CONN-707** | **Create Tailscale Network Setup Guide** | 1. Produce `white_label/NC-DOC-WL-002-tailscale-setup.md`<br>2. Test VPN connectivity across networks<br>3. Security best practices | 2h | **LOW** | Enables secure WAN connectivity |
| **CONN-708** | **Prepare MCP Gateway for Federation** | 1. Create `neocortex/infra/gateway.py` stub<br>2. Implement routing based on agent_id/lobe_id<br>3. Design for multi-tenant deployments | 4h | **MEDIUM** | Future-proofing for large scale |
| **TEST-709** | **Hierarchy & Connectivity Validation Tests** | 1. Test creation, inheritance, lateral isolation<br>2. Validate LAN, VPN, WAN connectivity modes<br>3. Security audit for unauthorized access | 6h | **HIGH** | Ensures architectural integrity |

**Phase 7 Deliverables:**  
1. Hierarchical lobe architecture implementation  
2. Multi-network connectivity (LAN/VPN/WAN)  
3. Enterprise governance and audit trails  
4. Ready for federated knowledge systems  

---

## 🔗 Dependencies & Critical Path

1. **STAB-101 → STAB-102 → STAB-103** (Core infrastructure must be stable first)
2. **STAB-104** (Fix LLM factory) required for **ORCH-302** (Task execution)
3. **AGENT-201 → AGENT-202 → AGENT-203** (Agent setup before orchestration)
4. **ORCH-301** (Orchestration tools) depends on **AGENT-202** (Enhanced sub-server)
5. **SEC-404** (Auto-repair) should follow **STAB-103** (Sanity tests)
6. **SEC-405** (Authentication) should precede **PHASE 6** (Multi-agent orchestration)
7. **PHASE 5** (Testing & Docs) depends on **PHASE 4** (Security) completion
8. **PHASE 6** (Multi-agent) depends on **PHASE 3** (Manual Orchestration) completion
9. **PHASE 7** (Hierarchy) requires **PHASE 6** (Multi-agent foundation)

**Critical Path Duration:** 14-25 days (Phases 1-6, excluding Phase 7)

---

## 🚨 Risk Assessment

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **ConfigProvider not fully integrated** | HIGH - Configuration drift causes unpredictable behavior | STAB-101 (complete integration) with validation |
| **Hidden global state in factories** | HIGH - Causes hardest-to-debug instability | STAB-102 (factory audit) with comprehensive review |
| **LLM factory config handling bug** | MEDIUM - Blocks task execution | STAB-104 (fix list handling) ✅ **COMPLETED** |
| **Agent isolation failure** | HIGH - Security breach, resource conflict | AGENT-205 (isolation tests) before orchestration |
| **No usage limits** | MEDIUM - Resource exhaustion, cost overruns | SEC-403 (usage policies) |
| **Lack of authentication** | HIGH - Unauthorized access to sensitive tools | SEC-405 (authentication implementation) |
| **Tool versioning conflicts** | MEDIUM - Breaking changes in production | SEC-406 (tool versioning) |
| **Inadequate testing** | MEDIUM - Undetected bugs in multi-agent scenarios | PHASE 5 (comprehensive testing) |

---

## 🏁 Success Criteria for Stability Milestone

1. ✅ Sanity test suite passes (10+ tests)
2. ✅ ConfigProvider used by all services, validated at runtime
3. ✅ Factory audit clean, no hidden globals
4. ✅ Courier (1.5B) and Engineer (3B) agents isolated with mentor mode
5. ✅ Manual orchestration via MCP tools functional
6. ✅ Usage policies enforced, failsafe mechanisms operational
7. ✅ Authentication and API key security implemented
8. ✅ Integration tests pass with concurrent agents
9. ✅ CLI client and IDE integration verified
10. ✅ Fire test validation successful (multi-agent resilience)

**When these are met, the foundation is stable for advanced features (Phases 6-7).**

---

**Version:** 7.0 (Combined Stability Roadmap)  
**Created:** 2026-04-11  
**Based on:** v6.0 Stability-First + v5.0 Evolution + Current Implementation State  
**Next Review:** After Phase 2 completion