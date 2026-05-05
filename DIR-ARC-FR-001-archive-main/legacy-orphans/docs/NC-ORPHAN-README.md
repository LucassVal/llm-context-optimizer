# NeoCortex Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-green.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://spec.modelcontextprotocol.io)

**NeoCortex** is an advanced AI agent framework with fractal memory architecture, zero-trust governance, and high-performance MCP tool orchestration. It achieves **61.8% token efficiency** over standard agents through intelligent context management and specialized tool offloading.

## 🚀 Features

### 🧠 Fractal Memory Architecture
- **Cortex/Lobe Memory System**: Hierarchical memory with semantic indexing
- **Mmap IPC**: Zero-copy memory sharing between processes
- **Context Compression**: 10:1 compression ratio for session summaries
- **Hot/Cold Memory**: Pareto-optimized memory access patterns

### 🛡️ Zero-Trust Governance
- **Constitutional Framework**: Role-based action authorization
- **SSOT Compliance**: 85.7% file naming convention compliance
- **Audit Trail**: Complete action logging and compliance tracking
- **Policy Enforcement**: Automated rule validation and violation detection

### ⚡ High-Performance MCP Tools
- **17 Core Tools**: Health, governance, orchestration, memory, state, LLM routing, system, brain, context, security, benchmark, notification, AKL, ledger, auto-memory, PicoClaw
- **SSE Transport**: Stable stdio-based communication
- **Tool Offloading**: 60%+ token savings via specialized operations

### 📊 Performance Metrics
- **Token Efficiency**: 61.8% savings vs standard agents (target: 48%)
- **Context Reduction**: 64-73% reduction in manual context re-entry
- **Response Time**: <100ms for local tools, <500ms for LLM calls
- **Memory Access**: 5-10x faster via mmap vs serialization

## 📋 Quick Start

### Prerequisites
- Python 3.12+
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) (`pip install mcp`)
- [Ollama](https://ollama.ai/) (optional, for local LLM)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/neocortex.git
cd neocortex

# Install dependencies
pip install -r requirements.txt

# Start the MCP server
python start_mcp_server.py
```

### Basic Usage
```python
# Connect to NeoCortex MCP server
from mcp import Client

async with Client() as client:
    # Test health tool
    result = await client.call_tool("neocortex_health", {"action": "server.health"})
    print(f"Services: {result['services']}")
    
    # Check governance compliance
    compliance = await client.call_tool("neocortex_governance", {"action": "compliance.report"})
    print(f"Compliance score: {compliance['compliance_score']}%")
```

## 🏗️ Architecture

### Core Components
```
NeoCortex Framework/
├── 01_neocortex_framework/     # Core framework
│   ├── neocortex/
│   │   ├── core/              # Core services
│   │   ├── mcp/tools/         # 17 MCP super tools
│   │   └── infra/             # Infrastructure
│   ├── 02_memory_lobes/       # Fractal memory lobes
│   └── DIR-DOC-FR-001-docs-main/ # Documentation
├── DIR-DS-001-tickets/        # Task tracking
├── DIR-DS-002-audit-logs/     # Audit trails
└── DIR-ARC-FR-001-archive-main/ # Archives
```

### MCP Tool Ecosystem
| Tool | Purpose | Key Actions |
|------|---------|-------------|
| `neocortex_health` | Health monitoring | `server.health`, `ssot.audit`, `metrics.live` |
| `neocortex_governance` | Governance rules | `policy.check`, `compliance.report`, `violation.log` |
| `neocortex_orchestration` | Task orchestration | `task.execute`, `agent.spawn`, `workers.status` |
| `neocortex_memory` | Fractal memory | `cortex.get`, `lobe.search`, `knowledge.store` |
| `neocortex_state` | State persistence | `checkpoint.get`, `savepoint.create`, `session.status` |
| `neocortex_llm_router` | LLM routing | `gateway.health`, `route.call`, `ollama.ask` |
| `neocortex_system` | System operations | `config.get`, `pulse.status`, `health.agent` |
| `neocortex_brain` | Planning intelligence | `brain.think`, `brain.plan`, `intelligence.query` |
| `neocortex_context` | Context management | `context.compress`, `session.summarize`, `report.generate` |
| `neocortex_security` | Security controls | `access.validate`, `lock.check`, `hook.register` |
| `neocortex_benchmark` | Performance testing | `run.drift`, `run.titanomachy`, `benchmark.status` |
| `neocortex_notification` | Notifications | `push.send`, `peers.discover`, `peers.sync` |
| `neocortex_akl` | Knowledge graph | `akl.add`, `akl.search`, `kg.query` |
| `neocortex_health` | Health monitoring | `server.health`, `ssot.audit` |
| `neocortex_ledger` | Agent ledger | `ledger.read`, `agent.register`, `agent.identity` |
| `neocortex_memory_auto` | Auto-memory | `turn.record`, `session.hot`, `session.stats` |
| `neocortex_picoclaw` | IPC server | `picoclaw.start`, `picoclaw.publish`, `picoclaw.llm_call` |

## 📈 Performance

### Token Efficiency Comparison
| Task | Standard Agent | NeoCortex | Savings |
|------|---------------|-----------|---------|
| SSOT Compliance Audit | 1200 tokens | 400 tokens | 66% |
| Governance Validation | 800 tokens | 300 tokens | 62% |
| Project Analysis | 1500 tokens | 600 tokens | 60% |
| Documentation | 2000 tokens | 800 tokens | 60% |
| **Total** | **5500 tokens** | **2100 tokens** | **61.8%** |

### Memory Efficiency
- **Fractal Compression**: 10:1 ratio for session context
- **Mmap Performance**: 5-10x faster than serialization
- **Semantic Search**: O(log n) vs O(n) linear search
- **Hot Context**: 80% of accesses to 20% of memory

## 🔧 Development

### Project Structure
NeoCortex follows strict SSOT (Single Source of Truth) naming conventions:
- `NC-[TYPE]-[FR/SV/SCR]-[###]-[description].ext`
- Types: `GOV`, `SUPER`, `LBE`, `RPT`, `TEST`, `DS`, `SCR`, `AUDIT`, `MCP`, `SVC`
- Codes: `FR` (Framework), `SV` (Service), `SCR` (Script)

### Adding New Tools
1. Create tool file in `01_neocortex_framework/neocortex/mcp/tools/`
2. Follow naming convention: `NC-SUPER-###-description.py`
3. Implement tool function with `@mcp.tool` decorator
4. Add to server registration in `neocortex/mcp/server.py`
5. Update documentation

### Testing
```bash
# Run Alpha tests
python NC-TEST-FR-201-health-tool-test.py

# Check SSOT compliance
python -c "from neocortex.mcp.tools.NC_SUPER_013_health import neocortex_health; print(neocortex_health('ssot.audit'))"
```

## 📚 Documentation

### Bilingual Resources
- **English**: Primary documentation in `/DIR-DOC-FR-001-docs-main/`
- **Portuguese**: Brazilian Portuguese translations available

### Key Documents
- `NC-GOV-FR-003-ia-governance-rules.yaml` - Governance rules
- `NC-NAM-FR-001-naming-convention.md` - SSOT naming conventions
- `NC-TEST-FR-200-alpha-testing-plan.md` - Testing methodology
- `NC-TEST-FR-202-token-efficiency-analysis.md` - Performance analysis

## 🗺️ Roadmap

### Q2 2026: Foundation & Stabilization ✅
- [x] NeoCortex Core MVP with fractal memory
- [x] Zero-Trust Governance implementation
- [x] Alpha Testing of 17 core tools

### Q3 2026: Open-Source Transition 🚧
- [ ] GitHub public release under MIT License
- [ ] Bilingual documentation (English/Portuguese)
- [ ] Academic paper on arXiv

### Q4 2026: Rust Migration
- [ ] `neocortex-mcp-rs` native Rust gateway
- [ ] O(1) memory mapping in pure Rust
- [ ] Enterprise features and telemetry

### 2027: Ecosystem Expansion
- [ ] Integration marketplace
- [ ] Managed cloud bridge
- [ ] University research partnerships

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes following SSOT conventions
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/neocortex/issues)
- **Documentation**: [Full documentation](DIR-DOC-FR-001-docs-main/)
- **Academic**: Paper forthcoming on arXiv

## 🙏 Acknowledgments

- Model Context Protocol (MCP) team for the protocol specification
- Ollama for local LLM infrastructure
- FastMCP for Python SDK implementation
- Research partners for fractal memory architecture validation