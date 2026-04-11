# NC-TODO-FR-001 - NeoCortex Project Roadmap (v5.0 Evolution)

> **Definitive Implementation Plan for NeoCortex - Transforming vision into progressive, validated reality**

---

## Overview of Phases (Status: 2026-04-10)

| Phase | Name | Status | Progress | Main Objective |
|---|---|---|---|---|
| **PHASE 1** | Foundation & Stabilization | **80%** | 25/31 tasks | Consolidate code, document, prepare distribution + high-performance infrastructure + hybrid LLM mode |
| **PHASE 2** | MCP & Advanced Tools | **100%** | 6/6 tasks | Operational MCP server with 20 tools, 70+ actions |
| **PHASE 3** | Continuous Learning & Prediction | **0%** | 0/3 tasks | Personal profiles, predictions, learning assistant |
| **PHASE 4** | Collective Intelligence & Governance | **40%** | 2/3 tasks | Knowledge sharing, security, teams |
| **PHASE 5** | Ecosystem & Distribution | **0%** | 0/3 tasks | PyPI, documentation, community, technical article |
| **PHASE 6** | Multi-Agent Orchestration with Sub-MCP Servers | **50%** | 3/6 tasks | Isolated sub-MCP servers, fire test validation, multi-agent resilience |
| **PHASE 7** | Advanced Hierarchy & Network Connectivity | **0%** | 0/18 tasks | Hierarchical lobe architecture, multi-network connectivity, enterprise-scale governance |

---

## Ticket System

> **Reference:** All detailed tickets are documented in **[NC-TKT-FR-001-tickets.md](NC-TKT-FR-001-tickets.md)**

| Priority | Tickets | Description | Estimate |
|----------|---------|-------------|----------|
| **T0 (Essential)** | 31 tickets | Framework foundation (packaging, tests, docs) + high-performance infrastructure optimization + hybrid LLM mode | 78-92 hours |
| **T1 (Priority)** | 4 tickets | MCP server finalization (CLI, authentication, IDE tests) | 11-14 hours |
| **T2 (Important)** | 4 tickets | Continuous learning (profiles, predictions, learning loop) | 12-16 hours |
| **T3 (Complementary)** | 3 tickets | Multi-user collaboration (hub, governance) | 13-17 hours |
| **T4 (Ecosystem)** | 3 tickets | Distribution (PyPI, community, article) | 13-17 hours |
| **T5 (Advanced Capability)** | 6 tickets | Multi-agent orchestration with sub-MCP servers | 15-20 hours |
| **T6 (Enterprise Architecture)** | 18 tickets | Hierarchical lobe architecture, multi-network connectivity, enterprise governance | 45-60 hours |

**Total:** 69 tickets • ~187-236 hours • Timeline: 7-9 weeks

---

## Progress by Phase

### **PHASE 1: Foundation & Stabilization** (1-2 weeks)
**Objective:** Transform current code into a distributable, reliable product with architectural foundations for future evolution.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F1.1** | T0-001 | Refactor `NC-MCP-FR-001-mcp-server.py` to modular architecture (separate tools into modules) with architectural separation (business logic vs adapters, Repository Pattern, JSON Schemas). | ✅ | Structure `neocortex/mcp/tools/`, `neocortex/mcp/server.py`, 16 tools modularized + Repository Pattern + JSON Schemas |
| **F1.2** | T0-002 | Create `requirements.txt` and `pyproject.toml` for pip installation. |  | `pip install -e .` functional |
| **F1.3** | T0-003 | Write complete `README.md` for root repository. |  | Installation and quick usage documentation |
| **F1.4** | T0-004 | Create `white_label/NC-DOC-WL-001-readme.md` with 5-minute guide. |  | Ready template for new projects |
| **F1.5** | T0-005 | Add unit tests for helper functions (`read_cortex`, `write_ledger`, etc.). |  | Coverage >70% |
| **F1.6** | T0-006 | Configure GitHub Actions for CI (lint, tests, build). |  | Green pipeline on push |
| **F1.7** | T0-007 | Run complete benchmark (`Titanomachy`, `Drift`) and publish in `BENCHMARKS.md`. |  | Official metrics of savings (-38% tokens, -80% drift) |
| **F1.8** | OPT-001 | Implement `LedgerStore` optimized storage (msgspec, diskcache, SQLite). | ✅ | `neocortex/infra/ledger_store.py` with 10x faster reads |
| **F1.9** | OPT-002 | Implement `ManifestStore` for tool manifests (Xapian FTS5). | ✅ | `neocortex/infra/manifest_store.py` with full-text search |
| **F1.10** | OPT-003 | Implement `LobeIndex` for lobe metadata and search. | ✅ | `neocortex/infra/lobe_index.py` with fast lookup |
| **F1.11** | OPT-004 | Implement `SearchEngine` for semantic search across cortex. | ✅ | `neocortex/infra/search_engine.py` with hybrid search |
| **F1.12** | OPT-005 | Implement `HotCache` for hot context caching (LRU, TTL). | ✅ | `neocortex/infra/hot_cache.py` with configurable limits |
| **F1.13** | OPT-006 | Integrate `LobeIndex` into `LobeService.search_lobes()`. | ✅ | Search functionality using optimized index |
| **F1.14** | OPT-007 | Create MCP tool `neocortex_search` for fast cortex search. | ✅ | `neocortex/mcp/tools/search.py` with semantic and keyword search |
| **F1.15** | OPT-008 | Create and execute migration script to transition existing data to new stores. | ✅ | `scripts/migrate_to_stores.py` with data integrity validation |
| **F1.16** | OPT-009 | Implement `ConfigProvider` with sections for cache, scheduler, LLM backends. | ✅ | Dynamic configuration with environment overrides |
| **F1.17** | OPT-010 | Integrate `PulseScheduler` with `ConfigProvider` for dynamic scheduling. | ✅ | `neocortex/core/pulse_scheduler.py` using configurable intervals |
| **F1.18** | OPT-011 | Implement `CacheBackend` abstraction (Redis, Memcached, diskcache). |  | `neocortex/infra/cache_backend.py` stub ready for implementation |
| **F1.19** | OPT-012 | Implement `VectorStore` abstraction (Infinity, LanceDB, Qdrant). |  | `neocortex/infra/vector_store.py` stub ready for implementation |
| **F1.20** | LLM-001 | Design hybrid LLM mode architecture (local Ollama + cloud OpenAI/Anthropic). | ✅ | Architecture document and interface definitions |
| **F1.21** | LLM-002 | Implement `LLMBackend` abstract base class. | ✅ | `neocortex/infra/llm/backend.py` with unified interface |
| **F1.22** | LLM-003 | Implement `OllamaBackend` for local model inference. | ✅ | `neocortex/infra/llm/ollama_backend.py` with streaming support |
| **F1.23** | LLM-004 | Implement `DeepSeekBackend` for cloud API inference. | ✅ | `neocortex/infra/llm/deepseek_backend.py` with rate limiting |
| **F1.24** | LLM-005 | Implement `OpenAIBackend` for GPT models. | ✅ | `neocortex/infra/llm/openai_backend.py` with function calling |
| **F1.25** | LLM-006 | Implement `LLMFactory` with automatic backend selection. | ✅ | `neocortex/infra/llm/factory.py` with configuration-based routing |
| **F1.26** | LLM-007 | Create `AgentExecutor` for task execution with backend override. | ✅ | `neocortex/agent/executor.py` with hybrid LLM support |
| **F1.27** | LLM-008 | Add `set_agent_backend` action to MCP `config` tool. | ✅ | MCP tool `neocortex_config` updated |
| **F1.28** | LLM-009 | Add `backend_override` parameter to MCP `agent` tool. | ✅ | MCP tool `neocortex_agent` updated |
| **F1.29** | LLM-010 | Create hybrid mode documentation. | ✅ | `white_label/NC-DOC-WL-001-hybrid-mode.md` |
| **F1.30** | LLM-011 | Execute hybrid mode integration tests. | ✅ | Test results in `BENCHMARKS_HYBRID.md` |
| **F1.31** | LLM-012 | Publish hybrid mode benchmarks. | ✅ | `BENCHMARKS_HYBRID.md` with performance metrics |

### **PHASE 2: MCP & Advanced Tools** (1-2 weeks)
**Objective:** Deliver a fully operational MCP server with comprehensive toolset for IDE integration.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F2.1** | T1-001 | Implement authentication and security integration (JWT, API keys). |  | Secure MCP server with token validation |
| **F2.2** | T1-002 | Create CLI client for local usage without IDE integration. |  | `neocortex_cli.py` with all MCP tool actions |
| **F2.3** | T1-003 | Test IDE integration (VS Code, Cursor, Antigravity). |  | Verified working in all supported IDEs |
| **F2.4** | T1-004 | Create comprehensive tool documentation and examples. |  | Complete API reference with usage examples |
| **F2.5** | T1-005 | Add tool manifest generation and validation. |  | Automated manifest generation from tool definitions |
| **F2.6** | T1-006 | Implement tool versioning and backward compatibility. |  | Version-aware tool routing and deprecation warnings |

### **PHASE 3: Continuous Learning & Prediction** (1-2 weeks)
**Objective:** Enable personalized developer profiles and predictive assistance.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F3.1** | T2-001 | Create developer profiles with hierarchical access levels. |  | Profile system with skill tracking |
| **F3.2** | T2-002 | Implement learning loop and pattern extraction from interactions. |  | Automated pattern discovery and rule generation |
| **F3.3** | T2-003 | Add prediction capabilities for common development tasks. |  | Predictive suggestions based on context |

### **PHASE 4: Collective Intelligence & Governance** (1-2 weeks)
**Objective:** Enable knowledge sharing and team collaboration.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F4.1** | T3-001 | Implement MCP Hub with WebSocket support for real-time collaboration. |  | Central hub for multi-user coordination |
| **F4.2** | T3-002 | Add team and project governance features. |  | Team collaboration with role-based access |
| **F4.3** | T3-003 | Implement peer discovery and synchronization. |  | P2P knowledge sharing across instances |

### **PHASE 5: Ecosystem & Distribution** (1-2 weeks)
**Objective:** Package, distribute, and build community around NeoCortex.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F5.1** | T4-001 | Publish to PyPI as `neocortex-framework`. |  | Official Python package |
| **F5.2** | T4-002 | Create comprehensive documentation site. |  | User guides, API reference |
| **F5.3** | T4-003 | Write technical article and share with community. |  | Medium/Dev.to publication |

### **PHASE 6: Multi-Agent Orchestration with Sub-MCP Servers** (1-2 weeks)
**Objective:** Validate multi-agent architecture resilience with isolated sub-MCP servers, fire test validation, and autonomous agent orchestration.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F6.1** | ORCH-001 | Create sub-MCP server startup script (`neocortex/mcp/sub_server.py`). | ✅ | Script accepts --port, --lobe-dir, --tools arguments |
| **F6.2** | ORCH-002 | Create MCP tool `neocortex_subserver` (orchestrator). | ✅ | `neocortex/mcp/tools/subserver.py` with spawn, stop, list_active, send_task |
| **F6.3** | ORCH-003 | Create MCP tool `neocortex_task` (sub-server task receiver). | ✅ | `neocortex/mcp/tools/task.py` with execute() method |
| **F6.4** | ORCH-004 | Create isolated lobes for fire test (guardian, backend_dev, indexer). | ✅ | Three lobe directories with dedicated .agents/rules files |
| **F6.5** | ORCH-005 | Orchestrate fire test execution (spawn 3 sub-servers, send parallel tasks). |  | Validation of multi-agent coordination and isolation |
| **F6.6** | ORCH-006 | Validate resilience (failure detection, isolation, concurrency handling). |  | Test report with failure recovery and isolation verification |

**Prerequisites:** PHASE 1 high-performance infrastructure + hybrid LLM mode must be complete (provides data layer + AgentExecutor).

### **PHASE 7: Advanced Hierarchy & Network Connectivity** (3-4 weeks)
**Objective:** Implement hierarchical lobe architecture, multi-network connectivity models, and enterprise-scale governance for federated knowledge systems.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F7.1** | HIER-001 | Audit Report Hierarchy - Inventory and analysis of existing components. |  | `AUDIT_REPORT_HIERARCHY.md` with gap analysis |
| **F7.2** | HIER-002 | Architecture Hierarchy Design - Define hierarchical lobe model with 5 levels. |  | `ARCHITECTURE_HIERARCHY.md` with inheritance rules |
| **F7.3** | HIER-003 | Expand LobeService and LobeIndex for hierarchical operations. |  | Updated `neocortex/core/lobe_service.py` with parent_id, ancestor_ids |
| **F7.4** | HIER-004 | Create MCP tool `neocortex_hierarchy` for hierarchy management. |  | `neocortex/mcp/tools/hierarchy.py` with create_child, grant_access, etc. |
| **F7.5** | HIER-005 | Implement AuditTrail for hierarchical events. |  | Expanded `neocortex/core/audit_service.py` with HIERARCHY events |
| **F7.6** | CONN-001 | Implement mDNS Discovery for LAN connectivity. |  | `neocortex/infra/discovery.py` with zeroconf integration |
| **F7.7** | CONN-002 | Implement gRPC Server stub for high-performance communication. |  | `neocortex/infra/grpc_server.py` with .proto definitions |
| **F7.8** | CONN-003 | Create Tailscale Network Setup Guide. |  | `white_label/NC-DOC-WL-002-tailscale-setup.md` |
| **F7.9** | CONN-004 | Prepare MCP Gateway for future federation. |  | `neocortex/infra/gateway.py` stub with routing capabilities |
| **F7.10** | TEST-001 | Hierarchy Validation Tests - creation, inheritance, lateral isolation. |  | Test suite with automated validation |
| **F7.11** | TEST-002 | Connectivity Validation Tests - Local, LAN, VPN, WAN modes. |  | Test reports for each connectivity mode |
| **F7.12** | TEST-003 | Security Validation Tests - unauthorized access, privilege escalation. |  | Security audit report |
| **F7.13** | DOC-001 | Deliver Audit Report (F7.1 output). |  | `AUDIT_REPORT_HIERARCHY.md` finalized |
| **F7.14** | DOC-002 | Deliver Architecture Documentation (F7.2 output). |  | `ARCHITECTURE_HIERARCHY.md` finalized |
| **F7.15** | DOC-003 | Deliver Tailscale Setup Guide (F7.8 output). |  | `white_label/NC-DOC-WL-002-tailscale-setup.md` finalized |
| **F7.16** | DOC-004 | Deliver Hierarchy User Guide. |  | `white_label/NC-DOC-WL-003-hierarchy-guide.md` |
| **F7.17** | DOC-005 | Deliver Test Reports (F7.10-12 outputs). |  | `TEST_REPORT_HIERARCHY.md` consolidated |
| **F7.18** | VAL-001 | Final Validation Question - confirm all objectives met. |  | Validation confirmation and readiness assessment |

**Prerequisites:** PHASE 6 multi-agent orchestration foundation must be complete.

---

## Local AI Assistance & Mentor Protocol

### Current Capabilities (Implemented)
- **Hybrid LLM Mode**: Local Ollama, DeepSeek, OpenAI backends via `AgentExecutor`
- **Sub-MCP Servers**: Isolated execution environments with own ledger and regression buffers
- **MCP Tools**: `neocortex_subserver` (spawn, stop, list), `neocortex_task` (execute tasks)
- **AgentExecutor**: "Courier protocol" for dispatching tasks to appropriate backends

### Missing Pieces for Fluid "Mentor" Experience
1. **Task Queue & Monitoring**: Central task queue with heartbeat monitoring for sub-servers
2. **Result Aggregation**: Standardized format for sub-servers to report progress and results
3. **Automatic Spawning**: Dynamic sub-server creation based on task requirements
4. **Integrated IDE Experience**: Seamless delegation from OpenCode to local AI assistants

### Immediate Next Steps (Phase 6 Completion)
1. **Complete ORCH-005**: Fire test execution with 3 sub-servers
2. **Complete ORCH-006**: Resilience validation and failure recovery
3. **Enhance `neocortex_task`**: Add progress reporting and heartbeat mechanism
4. **Create `neocortex_orchestrator`**: Central coordination tool for multi-agent workflows

### Long-term Vision (Phase 7+)
- **Hierarchical Mentorship**: Parent lobes mentoring child lobes with rule inheritance
- **Federated Learning**: Knowledge sharing across network-connected NeoCortex instances
- **Enterprise Governance**: Compliance and audit trails for regulated environments

---

## Architectural Evolution & Future-Proofing

### Architectural Foundations Being Established Now:
1. **Hexagonal Architecture (Ports & Adapters)**
   - Business logic isolated in `neocortex/core/` (domain layer)
   - Adapters in `neocortex/mcp/tools/` (MCP-specific implementations)
   - Future adapters for WebSocket, HTTP, A2A protocols

2. **Repository Pattern for Storage Abstraction**
   - `CortexRepository`, `LedgerRepository`, `ProfileRepository` interfaces
   - Current: File system implementation
   - Future: Hub-based implementation via WebSocket/REST

3. **JSON Schema Contracts**
   - `NC-TLM-FR-001-tool-manifest-schema.json` (Tool Manifest)
   - `NC-LED-FR-001-ledger-schema.json` (Ledger state)
   - `NC-SCH-FR-001-a2a-message-schema.json` (A2A messaging)
   - Ensures language-agnostic data exchange

4. **Composable Entry Points**
   - `create_mcp_server()` function for different modes (stdio, hub, etc.)
   - Preparation for Rust/Go implementations sharing same contracts

5. **Hierarchical Lobe Architecture** (PHASE 7 Foundation)
   - Multi-level lobe hierarchy with inheritance and lateral isolation
   - Parent-child relationships and cumulative rule inheritance
   - Preparation for federated knowledge systems with granular governance

### Preparations for Future Integrations:

| Future Technology | Current Preparation | Benefit |
| :--- | :--- | :--- |
| **Rust/Go Hub** | Clear JSON schemas, repository interfaces | Can reimplement business logic while keeping same contracts |
| **A2A Protocol** | Message schema definition, adapter pattern | Easy addition of A2A adapter without rewriting business logic |
| **WebSocket Hub** | Composable server creation, separation of concerns | MCP server can connect to hub instead of running standalone |
| **Multi-language SDKs** | Tool Manifest as universal API description | Any language can generate clients from Tool Manifest |
| **Hierarchical Networks** | Lobe hierarchy model, mDNS discovery, gRPC stubs | Scalable federated systems with LAN/VPN/WAN connectivity |
| **MCP Gateway** | Gateway stub with routing based on agent_id/lobe_id | Future-proofing for large-scale multi-tenant deployments |

---

## Critical Path & Dependencies

1. **Complete T0-001 with architectural refinements** (separate business logic, add repositories, define schemas)
2. **Implement high-performance infrastructure optimization** (OPT-001 to OPT-009) - critical for scalability
3. **Execute migration script** (OPT-008) to transition existing data
4. **Implement hybrid LLM mode foundation** (LLM-001 to LLM-007) - enables local Ollama backends for testing with 2+ LLMs
5. **Add T0-005 (tests)** to ensure stability with new infrastructure and LLM backends
6. **Execute T0-007 (benchmarks)** for proof of effectiveness including performance metrics
7. **Proceed to T1 tickets** for MCP finalization
8. **Future: T6 Enterprise Architecture** (hierarchical lobes, network connectivity, enterprise governance) - after core framework stabilization

**Total Critical Path:** ~60-75 hours (including optimization + hybrid LLM)
**Total Extended Roadmap:** ~187-236 hours (including T6 Enterprise Architecture)

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Token reduction** | 96.6% vs stateless |  |
| **Context drift errors** | 0 in 100 tasks |  |
| **Rule adherence** | 100% compact encoding |  |
| **Session continuity** | 100% checkpoint resume |  |
| **MCP tool coverage** | 16 tools with 61+ actions | 20 tools, 70+ actions (with Pulse Scheduler) |
| **Test coverage** | >70% | 0% |
| **CI/CD pipeline** | Green on push | Not configured |
| **Read latency** | <50ms for ledger operations | To be measured |
| **Search latency** | <100ms for 10k documents | To be measured |
| **Cache hit ratio** | >90% for hot_context | To be measured |
| **Data migration success** | 100% data integrity | To be measured |
| **Hybrid LLM mode** | Seamless backend switching | ✅ Implemented and tested |
| **Sub-MCP isolation** | Complete process and data isolation | ✅ Implemented |
| **Multi-agent coordination** | Fire test validation successful | Pending ORCH-005/006 |

---

## Update Process

This roadmap should be updated:
1. **After each session** - Update completion status
2. **When priorities change** - Reorder tasks
3. **When new requirements emerge** - Add tasks
4. **Weekly review** - Assess progress and blockers

---

**Version:** 4.0 (Consolidated English)  
**Last Updated:** 2026-04-10  
**Next Review:** 2026-04-11  
**Language:** English (project standard)