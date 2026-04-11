# NC-BOOT-FR-001 — NeoCortex System Boot Manifest
# Este arquivo é a **instrução de boot universal** do sistema NeoCortex.
# Qualquer IA (Antigravity, OpenCode, Cursor, Claude, DeepSeek) deve ler este
# arquivo ANTES de qualquer outra ação no projeto.
#
# Localização: TURBOQUANT_V42/DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md
# Lobo MDC:   TURBOQUANT_V42/DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.mdc
# ─────────────────────────────────────────────────────────────────────────────

# NC-BOOT-FR-001 — NeoCortex System Boot Manifest

> **LEIA ESTE ARQUIVO PRIMEIRO.** Antes de qualquer análise, edição ou resposta sobre este projeto.

---

## 🧭 Identidade do Sistema

**Projeto:** NeoCortex MCP Framework
**Raiz:** `C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\`
**Framework:** `01_neocortex_framework\`
**Objetivo:** Servidor MCP local que reduz custo de API substituindo tokens de cloud caro por memória persistente (lobos) + modelos locais (Qwen 1.5B/3B via Ollama).

---

## ⚡ Boot em 60 Segundos

### Passo 1 — Checar/Iniciar o Host MCP

```powershell
# Checar se está ativo:
netstat -an | findstr 8765

# Se não estiver, iniciar:
cd C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42
.\start_neocortex_mcp.ps1
```

**Porta:** `ws://127.0.0.1:8765`
**Log esperado:** `INFO – MCP Server running on ws://127.0.0.1:8765`

### Passo 2 — Popular/Verificar Lobos

```bash
cd 01_neocortex_framework
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
# Se necessário (SSOT mudou), rodar sem --dry-run
```

### Passo 3 — Carregar Contexto via Lobo

```
# Via MCP (no chat do assistente):
Use neocortex_lobes com ação get e lobe_name=NC-LBE-FR-ARCHITECTURE-001
```

---

## 🗂️ Mapa de Lobos Ativos

| Lobo (`.mdc`) | Conteúdo | Usado por |
| :--- | :--- | :--- |
| `NC-LBE-FR-ARCHITECTURE-001` | Roadmap + Naming Convention + ADRs + Apêndice Técnico | T0, Engineer |
| `NC-LBE-FR-SECURITY-001` | Atomic Locks + Agent Policy + SOP de Sessão | Guardian, Sub-Servers |
| `NC-LBE-FR-DEVELOPMENT-001` | Auditorias + Alinhamentos de Arquitetura | Engineer, T0 |
| `NC-LBE-FR-PROFILES-001` | Schemas de developer/team | T0 |
| `NC-LBE-FR-WHITELABEL-001` | Templates white-label | Indexer |
| `NC-LBE-FR-BENCHMARKS-001` | Resultados de benchmark | Backend Dev |
| `NC-BOOT-FR-001-system-manifest` | Este manifesto | Qualquer IA |

---

## 🤖 Arquitetura de Agentes

```
T0 (DeepSeek/Claude) — Orquestrador
├── Courier (Qwen 1.5B) — lobes/courier/   — 24/7, tarefas braçais
├── Engineer (Qwen 3B)  — lobes/engineer/  — geração de código
└── Guardian (Qwen 1.5B)— lobes/guardian/  — validação e auditoria
```

**Regra de ouro:** T0 orquestra, nunca executa trabalho bruto. Trabalho bruto → Courier/Engineer (custo zero de API).

**Mentor Mode (AGENT-203):** Cada agente local lê o lobo de contexto via `mentor_step_0()` antes de executar qualquer tarefa. O prompt é prefixado com `[ORDEM DO SISTEMA]` + trechos relevantes dos lobos.

---

## 🏷️ Nomenclatura (Resumo Obrigatório)

**Arquivo:** `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`
**Pasta:**   `DIR-<TIPO>-<SIGLA>-<NUM>-<desc>/`

| TIPO | Uso |
| TOOL | Ferramenta MCP `/mcp/tools/` |
| SCR | Script `/scripts/` |
| DOC | Documentação `/docs-main/` |
| LBE | Lobo de memória `.mdc` |
| BOOT | Arquivos de boot `/bootup-main/` |
| ARC | Obsoleto → `DIR-ARC-FR` |

---

## 🛑 Proibições Absolutas

1. ❌ Nunca deletar arquivos — mover para `DIR-ARC-FR-001-archive-main/`
2. ❌ Nunca criar arquivo sem prefixo `NC-`
3. ❌ Nunca hardcodar caminhos — usar `ConfigProvider`
4. ❌ Nunca editar fora de `01_neocortex_framework/` sem autorização
5. ❌ Nunca commitar `*.db`, `*.wal`, `__pycache__/`, `.venv/`

---

## 📋 Tickets Críticos Abertos

| Ticket | Status | Descrição |
| AGENT-203 | ✅ Implementado | `mentor_step_0()` em `sub_server.py` |
| ORCH-301 | 🟡 Parcial | `spawn`/`stop`/`send_task` robustos |
| ORCH-302 | 🔴 Pendente | `execute` integrado com `LLMBackend` |
| SEC-401 | 🔴 Pendente | `neocortex_guardian` |
| SEC-403 | 🔴 Pendente | `limits.*` no config de cada agente |

---

## 📎 Arquivos SSOT (Leitura por Prioridade)

1. `NC-NAM-FR-001-naming-convention.md` — Mapa + Nomenclatura + Changelog
2. `NC-TODO-FR-001-project-roadmap-consolidated.md` — Roadmap oficial
3. `NC-APP-FR-001-technical-appendix.md` — Tools, libs, LLMs, mecanismos
4. `NC-SOP-FR-001-session-startup.md` — Procedimento de sessão
5. `NC-SEC-FR-001-atomic-locks.yaml` — O que os agentes não podem tocar
6. `NC-CFG-FR-001-agent-policy-template.yaml` — Políticas por agente
