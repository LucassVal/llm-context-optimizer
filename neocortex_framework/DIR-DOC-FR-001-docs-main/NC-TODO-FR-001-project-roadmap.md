# NC-TODO-FR-001 - NeoCortex Project Roadmap (v5.0 Evolution)

> **Definitive Implementation Plan for NeoCortex - Transforming vision into progressive, validated reality**

---

## Overview of Phases (Status: 2026-04-10)

| Phase | Name | Status | Progress | Main Objective |
|---|---|---|---|---|
| **PHASE 1** | Foundation & Stabilization | **45%** | 14/31 tasks | Consolidate code, document, prepare distribution + high-performance infrastructure + hybrid LLM mode |
| **PHASE 2** | MCP & Advanced Tools | **100%** | 6/6 tasks | Operational MCP server with 17 tools, 65 actions |
| **PHASE 3** | Continuous Learning & Prediction | **0%** | 0/3 tasks | Personal profiles, predictions, learning assistant |
| **PHASE 4** | Collective Intelligence & Governance | **40%** | 2/3 tasks | Knowledge sharing, security, teams |
| **PHASE 5** | Ecosystem & Distribution | **0%** | 0/3 tasks | PyPI, documentation, community, technical article |
| **PHASE 6** | Multi-Agent Orchestration with Sub-MCP Servers | **0%** | 0/6 tasks | Isolated sub-MCP servers, fire test validation, multi-agent resilience |

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

**Total:** 51 tickets • ~142-176 hours • Timeline: 5-6 weeks

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
| **F1.8** | OPT-001 | **High-Performance Infrastructure**: LedgerStore com Speedb + msgspec | ✅ | `neocortex/infra/ledger_store.py` |
| **F1.9** | OPT-002 | **High-Performance Infrastructure**: ManifestStore com Speedb + msgspec | ✅ | `neocortex/infra/manifest_store.py` |
| **F1.10** | OPT-003 | **High-Performance Infrastructure**: LobeIndex com SQLite + FTS5 | ✅ | `neocortex/infra/lobe_index.py` + índice SQLite |
| **F1.11** | OPT-004 | **High-Performance Infrastructure**: SearchEngine com SQLite FTS5 + Tantivy | ✅ | `neocortex/infra/search_engine.py` |
| **F1.12** | OPT-005 | **High-Performance Infrastructure**: HotCache com diskcache_rs | ✅ | `neocortex/infra/hot_cache.py` |
| **F1.13** | OPT-006 | **High-Performance Infrastructure**: Unificar busca no LobeService |  | Método `search_lobes()` em `lobe_service.py` |
| **F1.14** | OPT-007 | **High-Performance Infrastructure**: MCP tools para busca |  | `neocortex/mcp/tools/search.py` + extensão `lobes.py` |
| **F1.15** | OPT-008 | **High-Performance Infrastructure**: Script de migração de dados | ✅ | `scripts/migrate_to_stores.py` com validação |
| **F1.16** | OPT-009 | **High-Performance Infrastructure**: Integrar e configurar (ConfigProvider + PulseScheduler) |  | Configurações atualizadas, Pulse usando HotCache |
| **F1.17** | OPT-010 | **Stub Preparatório**: Analytics DuckDB | ✅ | `neocortex/infra/metrics_store.py` (implementado) |
| **F1.18** | OPT-011 | **Stub Preparatório**: Cache Backend abstrato |  | `neocortex/infra/cache_backend.py` (DiskCache + Redis stubs) |
| **F1.19** | OPT-012 | **Stub Preparatório**: VectorStore Infinity/LanceDB |  | `neocortex/infra/vector_store.py` (stubs para busca vetorial) |
| **F1.20** | LLM-001 | **Hybrid LLM Mode**: Interface abstrata `LLMBackend` | ✅ | `neocortex/infra/llm/backend.py` (classe abstrata) |
| **F1.21** | LLM-002 | **Hybrid LLM Mode**: Backend local Ollama | ✅ | `neocortex/infra/llm/ollama_backend.py` (implementado) |
| **F1.22** | LLM-003 | **Hybrid LLM Mode**: Backend cloud DeepSeek | ✅ | `neocortex/infra/llm/deepseek_backend.py` (API compatível) |
| **F1.23** | LLM-004 | **Hybrid LLM Mode**: Backend adicional OpenAI | ✅ | `neocortex/infra/llm/openai_backend.py` (implementado) |
| **F1.24** | LLM-005 | **Hybrid LLM Mode**: Fábrica de Backends `LLMBackendFactory` | ✅ | `neocortex/infra/llm/factory.py` (configuração por string) |
| **F1.25** | LLM-006 | **Hybrid LLM Mode**: Expandir `ConfigProvider` para LLM | ✅ | `neocortex/config.py` com chaves LLM, API keys |
| **F1.26** | LLM-007 | **Hybrid LLM Mode**: Integrar com `AgentExecutor` |  | `neocortex/agent/executor.py` usa backend apropriado por role |
| **F1.27** | LLM-008 | **Hybrid LLM Mode**: Ação `set_agent_backend` no MCP config |  | `neocortex/mcp/tools/config.py` (atualização em tempo real) |
| **F1.28** | LLM-009 | **Hybrid LLM Mode**: Parâmetro `backend_override` no `spawn_agent` |  | `neocortex/mcp/tools/agent.py` (override por agente) |
| **F1.29** | LLM-010 | **Hybrid LLM Mode**: Documentação de configuração híbrida |  | `white_label/NC-DOC-WL-001-hybrid-mode.md` (guia cliente) |
| **F1.30** | LLM-011 | **Hybrid LLM Mode**: Testar cenário híbrido real (2 LLMs locais) |  | Guardian Ollama local + Backend Dev DeepSeek cloud |
| **F1.31** | LLM-012 | **Hybrid LLM Mode**: Relatório de economia híbrida |  | `BENCHMARKS_HYBRID.md` (caso de uso, custos) |

**Completion Criteria:** Stable, documented, tested code with published metrics + high-performance hybrid infrastructure foundation + hybrid LLM mode with local and cloud backends.

### **PHASE 2: MCP & Advanced Tools** (100% complete)
**Objective:** Operational MCP server with multi-action tools for IDEs, with preparation for future architectural evolution.

**Current Progress:** 17 tools implemented, 65 actions, validation in simulation, modularized server, Pulse Scheduler for autonomous maintenance.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F2.1** | — | Implement 16 MCP multi-action tools | ✅ | 16 tools, 61 actions |
| **F2.2** | — | Validate integration with FastMCP and Antigravity IDE | ✅ | Server operational in simulation |
| **F2.3** | — | Implement Pulse Scheduler for autonomous maintenance | ✅ | `neocortex_pulse` tool, automatic pruning/consolidation |
| **F2.4** | T1-001 | Add authentication and validation to MCP tools |  | Integrated security |
| **F2.5** | T1-002 | Create CLI client (`NC-CLI-FR-001-cli-tool.py`) |  | Command-line interface |
| **F2.6** | T1-003 | Test MCP integration with VS Code/Cursor/Antigravity |  | Integration guide |
| **F2.7** | T1-004 | Document all 17 MCP tools with examples |  | Complete API reference |

**Tools Implemented:**
1. `neocortex_cortex` - Central cortex management
2. `neocortex_lobes` - Lobes/phase management
3. `neocortex_checkpoint` - Checkpoints and continuity
4. `neocortex_regression` - Regression validation and STEP 0
5. `neocortex_ledger` - State ledger operations
6. `neocortex_benchmark` - Performance benchmarking
7. `neocortex_agent` - Agent automation
8. `neocortex_init` - Project initialization
9. `neocortex_config` - Configuration management
10. `neocortex_export` - Data export
11. `neocortex_manifest` - Content manifest management
12. `neocortex_kg` - Knowledge graph operations
13. `neocortex_consolidation` - Learning consolidation
14. `neocortex_akl` - Adaptive knowledge lifecycle
15. `neocortex_peers` - Peer-to-peer collaboration
16. `neocortex_security` - Security and access control
17. `neocortex_pulse` - Pulse Scheduler control and monitoring

### **PHASE 3: Continuous Learning & Prediction** (1-2 weeks)
**Objective:** Personalization, predictions, and a learning assistant that evolves with usage.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F3.1** | T2-001 | Create personal developer profile system with hierarchical access |  | Profile JSON with skill tracking |
| **F3.2** | T2-002 | Implement learning loop (STEP 0, regression buffer, pattern extraction) |  | Self-improving system |
| **F3.3** | T2-003 | Add prediction capabilities (next action, task estimation) |  | Predictive analytics |
| **F3.4** | T2-004 | Create Tool Manifest system for tool discovery and metadata |  | `NC-TLM-FR-001-tool-manifest.json` |

### **PHASE 4: Collective Intelligence & Governance** (40% complete)
**Objective:** Multi-user collaboration, knowledge sharing, and governance mechanisms.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F4.1** | — | Implement basic hierarchical access control | ✅ | `can_access()` function |
| **F4.2** | — | Create profile manager for multi-user support | ✅ | `profile_manager.py` |
| **F4.3** | T3-001 | Implement MCP Hub prototype with WebSocket support |  | Multi-user MCP server |
| **F4.4** | T3-002 | Add team and project governance features |  | Team collaboration |
| **F4.5** | T3-003 | Implement peer discovery and synchronization |  | P2P knowledge sharing |

### **PHASE 5: Ecosystem & Distribution** (1-2 weeks)
**Objective:** Package, distribute, and build community around NeoCortex.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F5.1** | T4-001 | Publish to PyPI as `neocortex-framework` |  | Official Python package |
| **F5.2** | T4-002 | Create comprehensive documentation site |  | User guides, API reference |
| **F5.3** | T4-003 | Write technical article and share with community |  | Medium/Dev.to publication |

### **PHASE 6: Multi-Agent Orchestration with Sub-MCP Servers** (1-2 weeks)
**Objective:** Validate multi-agent architecture resilience with isolated sub-MCP servers, fire test validation, and autonomous agent orchestration.

| Task ID | Ticket | Description | Status | Deliverable |
| :--- | :--- | :---: | :---: | :--- |
| **F6.1** | ORCH-001 | Create sub-MCP server startup script (`neocortex/mcp/sub_server.py`) |  | Script accepts --port, --lobe-dir, --tools arguments |
| **F6.2** | ORCH-002 | Create MCP tool `neocortex_subserver` (orchestrator) |  | `neocortex/mcp/tools/subserver.py` with spawn, stop, list_active, send_task |
| **F6.3** | ORCH-003 | Create MCP tool `neocortex_task` (sub-server task receiver) |  | `neocortex/mcp/tools/task.py` with execute() method |
| **F6.4** | ORCH-004 | Create isolated lobes for fire test (guardian, backend_dev, indexer) |  | Three lobe directories with dedicated .agents/rules files |
| **F6.5** | ORCH-005 | Orchestrate fire test execution (spawn 3 sub-servers, send parallel tasks) |  | Validation of multi-agent coordination and isolation |
| **F6.6** | ORCH-006 | Validate resilience (failure detection, isolation, concurrency handling) |  | Test report with failure recovery and isolation verification |

**Prerequisites:** PHASE 1 high-performance infrastructure + hybrid LLM mode must be complete (provides data layer + AgentExecutor).

---

## **Architectural Evolution & Future-Proofing (Critical Adjustments)**

### **Architectural Foundations Being Established Now:**

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

### **Preparations for Future Integrations:**

| Future Technology | Current Preparation | Benefit |
| :--- | :--- | :--- |
| **Rust/Go Hub** | Clear JSON schemas, repository interfaces | Can reimplement business logic while keeping same contracts |
| **A2A Protocol** | Message schema definition, adapter pattern | Easy addition of A2A adapter without rewriting business logic |
| **WebSocket Hub** | Composable server creation, separation of concerns | MCP server can connect to hub instead of running standalone |
| **Multi-language SDKs** | Tool Manifest as universal API description | Any language can generate clients from Tool Manifest |

---

## **Implementation Tiers (Revised)**

### **T0 - Foundation & Architecture** (Essential)
- Modular architecture with clear separation of concerns
- Packaging and distribution (`pyproject.toml`, `requirements.txt`)
- Unit tests and CI/CD pipeline
- Official benchmarks and metrics
- **Architectural preparation for future evolution**

### **T1 - MCP Server Finalization** (Priority)
- Authentication and security integration
- CLI client for local usage
- IDE integration testing (VS Code, Cursor, Antigravity)
- Comprehensive tool documentation

### **T2 - Learning & Personalization** (Important)
- Developer profiles with hierarchical access
- Learning loop and pattern extraction
- Prediction capabilities
- Tool Manifest system for tool discovery

### **T3 - Collaboration & Governance** (Complementary)
- MCP Hub with WebSocket support
- Team and project governance
- Peer discovery and synchronization

### **T4 - Ecosystem & Distribution** (Ecosystem)
- PyPI publication
- Documentation site
- Community building and technical article

### **T5 - Multi-Agent Orchestration** (Advanced Capability)
- Isolated sub-MCP servers for agent specialization
- Fire test validation of multi-agent resilience
- Autonomous agent coordination and failure recovery

---

## **Critical Path & Dependencies**

1. **Complete T0-001 with architectural refinements** (separate business logic, add repositories, define schemas)
2. **Implement high-performance infrastructure optimization** (OPT-001 to OPT-009) - critical for scalability
3. **Execute migration script** (OPT-008) to transition existing data
4. **Implement hybrid LLM mode foundation** (LLM-001 to LLM-007) - enables local Ollama backends for testing with 2+ LLMs
5. **Add T0-005 (tests)** to ensure stability with new infrastructure and LLM backends
6. **Execute T0-007 (benchmarks)** for proof of effectiveness including performance metrics
7. **Proceed to T1 tickets** for MCP finalization

**Total Critical Path:** ~60-75 hours (including optimization + hybrid LLM)

---

## **Success Metrics**

| Metric | Target | Current |
|--------|--------|---------|
| **Token reduction** | 96.6% vs stateless |  |
| **Context drift errors** | 0 in 100 tasks |  |
| **Rule adherence** | 100% compact encoding |  |
| **Session continuity** | 100% checkpoint resume |  |
| **MCP tool coverage** | 16 tools with 61+ actions | 17 tools, 65 actions (with Pulse Scheduler) |
| **Test coverage** | >70% | 0% |
| **CI/CD pipeline** | Green on push | Not configured |
| **Read latency** | <50ms for ledger operations | To be measured |
| **Search latency** | <100ms for 10k documents | To be measured |
| **Cache hit ratio** | >90% for hot_context | To be measured |
| **Data migration success** | 100% data integrity | To be measured |

---

## **Update Process**

This roadmap should be updated:
1. **After each session** - Update completion status
2. **When priorities change** - Reorder tasks
3. **When new requirements emerge** - Add tasks
4. **Weekly review** - Assess progress and blockers

---

**Version:** 2.0 (English)  
**Last Updated:** 2026-04-10  
**Next Review:** 2026-04-11  
**Language:** English (project standard)  