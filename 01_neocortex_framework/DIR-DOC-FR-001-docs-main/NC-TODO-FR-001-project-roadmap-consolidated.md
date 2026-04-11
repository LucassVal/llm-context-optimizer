# NC-TODO-FR-001 - NeoCortex Combined Stability Roadmap (v7.0 Consolidated Master)

> **Unified Execution Roadmap:**
> This roadmap comprehensively combines the Stability-First methodology (from v6.0), the macro Vision roadmap (from v5.0), and includes the required English Executive Summary.
> **Warning**: *NO content has been lost from legacy roadmaps*. All macro tasks (T0-T6) and all micro STAB/METR/AGENT tickets are strictly preserved below.
> **Status Date**: 2026-04-11 (Atualizado: AGENT-203 ✅ DONE)

---

## 1. Visão Macro (v5.0 Evolution)

A visão V5 foca na transformação estrutural do framework em um produto final distribuído e resiliente. Abaixo está a relação de todos os F-Tickets originais preservados.

### Progressão Original (V5)
| Phase | Name | Final Status |
|---|---|---|
| **PHASE 1** | Foundation & Stabilization | **80%** |
| **PHASE 2** | MCP & Advanced Tools | **100%** |
| **PHASE 3** | Continuous Learning & Prediction | **0%** |
| **PHASE 4** | Collective Intelligence & Governance | **40%** |
| **PHASE 5** | Ecosystem & Distribution | **0%** |
| **PHASE 6** | Multi-Agent Orchestration | **50%** |
| **PHASE 7** | Advanced Hierarchy & Connectivity | **0%** |

### Fase 1: Fundação
- [x] **T0-001**: Refactor to modular architecture. ✅ (OK)
- [ ] **T0-002**: Create `requirements.txt` and `pyproject.toml` for pip installation.
- [ ] **T0-003**: Write complete `README.md`.
- [ ] **T0-004**: Create `white_label/NC-DOC-WL-001-readme.md`.
- [ ] **T0-005**: Add unit tests for helper functions.
- [ ] **T0-006**: Configure GitHub Actions for CI.
- [ ] **T0-007**: Run complete benchmark.
- [x] **OPT-001**: Implement `LedgerStore` optimized storage. ✅ (OK)
- [x] **OPT-002**: Implement `ManifestStore` for tool manifests. ✅ (OK)
- [x] **OPT-003**: Implement `LobeIndex` for lobe metadata. ✅ (OK)
- [x] **OPT-004**: Implement `SearchEngine` hybrid search. ✅ (OK)
- [x] **OPT-005**: Implement `HotCache`. ✅ (OK)
- [x] **OPT-006**: Integrate `LobeIndex` into `LobeService`. ✅ (OK)
- [x] **OPT-007**: Create MCP search tool. ✅ (OK)
- [x] **OPT-008**: Create migration script. ✅ (OK)
- [x] **OPT-009**: Implement `ConfigProvider`. ✅ (OK)
- [x] **OPT-010**: Integrate `PulseScheduler`. ✅ (OK)
- [ ] **OPT-011**: Implement `CacheBackend` abstraction.
- [ ] **OPT-012**: Implement `VectorStore` abstraction.
- [x] **LLM-001**: Design hybrid LLM mode. ✅ (OK)
- [x] **LLM-002**: Implement `LLMBackend` ABC. ✅ (OK)
- [x] **LLM-003**: Implement `OllamaBackend`. ✅ (OK)
- [x] **LLM-004**: Implement `DeepSeekBackend`. ✅ (OK)
- [x] **LLM-005**: Implement `OpenAIBackend`. ✅ (OK)
- [x] **LLM-006**: Implement `LLMFactory`. ✅ (OK)
- [x] **LLM-007**: Create `AgentExecutor`. ✅ (OK)
- [x] **LLM-008**: Add config action. ✅ (OK)
- [x] **LLM-009**: Add agent override. ✅ (OK)
- [x] **LLM-010**: Create hybrid doc. ✅ (OK)
- [x] **LLM-011**: Execute hybrid tests. ✅ (OK)
- [x] **LLM-012**: Publish hybrid mode benchmarks. ✅ (OK)

### Fase 2: MCP
- [ ] **T1-001**: Implement authentication and security (JWT).
- [ ] **T1-002**: Create CLI client for local usage.
- [ ] **T1-003**: Test IDE integration.
- [ ] **T1-004**: Create comprehensive tool documentation.
- [ ] **T1-005**: Add tool manifest generation.
- [ ] **T1-006**: Implement tool versioning.

### Fase 3 & 4: Learning & Intelligence
- [ ] **T2-001**: Create developer profiles.
- [ ] **T2-002**: Implement learning loop.
- [ ] **T2-003**: Add prediction capabilities.
- [ ] **T3-001**: Implement MCP Hub with WebSocket.
- [ ] **T3-002**: Add team governance features.
- [ ] **T3-003**: Implement peer discovery and synchronization.

### Fase 5, 6 & 7: Distribution & Advanced
- [ ] **T4-001**: Publish to PyPI.
- [ ] **T4-002**: Create documentation site.
- [ ] **T4-003**: Write technical article.
- [x] **ORCH-001**: Create sub-MCP server startup script. ✅ (OK)
- [x] **ORCH-002**: Create `neocortex_subserver` tool. ✅ (OK)
- [x] **ORCH-003**: Create `neocortex_task` tool. ✅ (OK)
- [x] **ORCH-004**: Create isolated lobes for fire test. ✅ (OK)
- [ ] **ORCH-005**: Orchestrate fire test execution.
- [ ] **ORCH-006**: Validate resilience.
- [ ] **HIER-001 to HIER-005**: Hierarchy planning and tooling.
- [ ] **CONN-001 to CONN-004**: mDNS, gRPC stubs, Tailscale setup, MCP gateway.
- [ ] **TEST-001 to TEST-003**: Hierarchy, connectivity and security validations.
- [ ] **DOC-001 to DOC-005**: Deliver final architecture audit reports.
- [ ] **VAL-001**: Final Validation Question.

---

## 2. Plano Tático de Estabilidade (v6.0 Stability / Implementation State)

A V6 foca em refinar os blocos que quebram o código e travar toda a fundação num regime estável isolado sem instâncias Singleton caóticas, com HotCache ativo via diskcache.

### Completados na Data de Hoje
- [x] **STAB-101**: Complete ConfigProvider Integration ✅ (OK)
- [x] **STAB-102**: Audit Factories & Singletons ✅ (OK)
- [x] **STAB-103**: Implement Sanity Test Suite ✅ (OK)
- [x] **STAB-104**: Fix LLM Factory Config Handling ✅ (OK)
- [x] **STAB-105**: Enhance HotCache Robustness ✅ (OK)
- [x] **METR-106**: Extend MetricsStore with Domain Tables ✅ (OK)
- [x] **METR-107**: Integrate MetricsStore with Core Components ✅ (OK)
- [x] **METR-108**: Create MCP Report Tool ✅ (OK)
- [x] **METR-109**: Validation & Sanity Integration ✅ (OK)
- [x] **AGENT-202**: Enhance Sub-Server with Role Configuration ✅ (OK)
- [x] **AGENT-204**: Configure Tool Allow/Deny Lists ✅ (OK)

### Em Andamento (Fase 2 Isolamento Local)
- [ ] **AGENT-201**: Create Isolated Agent Environments *(Diretórios de lobos OK, mas falta implementação e uso total pelo Sub-Server)*
- [x] **AGENT-203**: Implement Mentor Mode per Agent ✅ (OK) — `mentor_step_0()` real: `identify_relevant_lobes` + `extract_relevant_snippet` + prompt injection via LobeService. Logger `neocortex.mentor`.
- [ ] **AGENT-205**: Test Isolation & Mentor Enforcement *(depende AGENT-203 ✅ + ORCH-301)*


### Tarefas Pendentes Restritivas Críticas (Fase 3 & 4)
- [ ] **ORCH-301**: Complete `neocortex_subserver` MCP Tool
- [ ] **ORCH-302**: Complete `neocortex_task` in Sub-Server
- [ ] **ORCH-304**: Test Complete Manual Flow
- [ ] **SEC-401**: Implement `neocortex_guardian` (Advanced Validation)
- [ ] **SEC-402**: Create `neocortex_failsafe` (Failure Recovery)
- [ ] **SEC-403**: Configure Usage Policies per Agent
- [ ] **SEC-404**: Implement Auto-Repair for Stores
- [ ] **SEC-405**: Implement Authentication & API Keys (from v5.0 T1-001)

### Otimizações Testáveis Futuras (Fase 5 Docs)
- [ ] **TEST-501**: Integration Test Suite
- [ ] **TEST-502**: Stress Test (Hybrid Titanomachy)
- [ ] **DOC-503**: White-Label Documentation
- [ ] **DOC-504**: Final ROI Report

---

## 3. Resumo Executivo em Inglês (English Executive Summary)

**Platform Vision**
NeoCortex is transitioning from a localized AI tool wrapper into a robust, multi-agent orchestration architecture utilizing the Model Context Protocol (MCP). The main bottleneck historically has been an unstable foundation layer leading to config drifting and broken LLM state handoffs. 

**Current State (April 2026)**
The V6 refactoring has drastically stabilized the framework. The core system correctly separates services with singleton factories, leverages DuckDB efficiently as a ledger/metrics store, and establishes an active MCP Server capable of serving 22 tools over standard streams (STDIO) and active connections (SSE). 

**Immediate Blockers to Scalability**
While the backend operations (like data persistence, heartbeat ticks, automatic metrics, fallback logic) execute successfully, we are pending the completion of **Phase 2 (Agent Isolation)**. Specifically, enforcing `Mentor Mode` dynamically per agent based on `role` configs will prevent destructive overrides. Following that, **Phase 3 (Manual Orchestration)** requires polishing the remaining stubs inside tools like `subserver` to establish proper inter-process networking. Once these are solved securely, scaling up to autonomous networks will begin smoothly. All V5 legacy roadmap elements (T1 through T4, HIER features, etc.) remain in the backlog tracking system for future execution post-stability.
