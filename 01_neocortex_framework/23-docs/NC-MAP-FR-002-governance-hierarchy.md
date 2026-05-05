# 🏛️ NeoCortex Governance Hierarchy (P0-P4)
**NC-MAP-FR-002 | v1.0 | 2026-05-05**

---

## 🗺️ Mapa de Cadeia de Comando
Esta hierarquia garante que o sistema opere sob a lente analítica (RCA/SWOT/KISS) e respeite a regra R21 (Zero Suposições).

### 🥇 P0: ESTRATÉGICO (Supremo)
*Onde reside a inteligência analítica e os ciclos de decisão.*

| ID | Nome | Localização | Função |
| :--- | :--- | :--- | :--- |
| **NC-WF-002** | Master Governance Workflow | `.agents/workflows/NC-WF-002-master-governance.md` | Lente Analítica (RCA/SWOT/3W/KISS) + 4 Ciclos Operacionais. |
| **NC-PRF-FR-001** | Master Governance Prompt | `01_neocortex_framework/23-docs/prompts/NC-PRF-FR-001-master-prompt.md` | Prompt de contexto para T1+ agentes orquestradores. |

---

### 📜 P1: CONSTITUCIONAL (Core)
*Regras fundamentais e inegociáveis.*

| ID | Nome | Localização | Função |
| :--- | :--- | :--- | :--- |
| **NC-RULE-001** | Core SSOT Rules | `.agents/rules/NC-RULE-001-core-ssot.mdc` | Naming, SSOT Update, Roadmaps e Atomic Locks. |
| **NC-RULE-006** | Zero Assumptions (R21) | `.agents/rules/NC-RULE-006-no-assumptions.mdc` | Proibição de inferência. Verificação obrigatória antes da ação. |

---

### 🛠️ P2: DOMÍNIO (Técnico)
*Padrões por área de atuação.*

| ID | Nome | Localização | Função |
| :--- | :--- | :--- | :--- |
| **NC-RULE-002** | Python & MCP Patterns | `.agents/rules/NC-RULE-002-python-mcp.mdc` | Padrões de codificação, imports NC- e registro de tools. |
| **NC-RULE-003** | Memory & Lobes | `.agents/rules/NC-RULE-003-lobes-memory.mdc` | Governança de armazenamento semântico e acesso a Lobos. |
| **NC-RULE-004** | Filesystem & Governance | `.agents/rules/NC-RULE-004-filesystem.mdc` | Zonas de escrita, backups e regras de arquivamento. |

---

### 📦 P3: OPERACIONAL (Chão de Fábrica)
*Contexto vivo e estado atual.*

| ID | Nome | Localização | Função |
| :--- | :--- | :--- | :--- |
| **NC-BOOT-FR-001** | System Manifest | `06-boot/NC-BOOT-FR-001-system-manifest.md` | Mapa de portas, serviços e caminhos SSOT ativos. |
| **@ROADMAP** | Unified Roadmap | `01_neocortex_framework/23-docs/NC-TODO-FR-001-project-roadmap-consolidated.md` | Tickets e backlog do projeto. |
| **@LOCKS** | Atomic Locks | `01_neocortex_framework/23-docs/NC-SEC-FR-001-atomic-locks.yaml` | Arquivos protegidos contra escrita automática. |

---

### 👤 P4: ESPECIALIZADO (Personas/Schemas)
*Contextos específicos de usuário e tipos de dados.*

| ID | Nome | Localização | Função |
| :--- | :--- | :--- | :--- |
| **NC-PRF-USR** | User Profiles | `01_neocortex_framework/27-profiles/users/` | Preferências e hierarquias de usuários individuais. |
| **NC-PRF-TMP** | Profile Templates | `01_neocortex_framework/27-profiles/templates/` | Blueprints para novos perfis e agentes. |

---

## 🔗 Cadeia de Ativação (Flow)
1. **Trigger:** Um novo ticket é identificado em `@ROADMAP`.
2. **P0 Activation:** O agente carrega `NC-WF-002` e aplica **RCA** (Por que o ticket existe?).
3. **P1 Validation:** Antes de qualquer `view_file`, o agente aplica **R21** (Verificar se o arquivo existe realmente).
4. **P2 Execution:** O código é escrito seguindo `NC-RULE-002` (Ruff/Mypy/Hyphenated imports).
5. **P3 Cleanup:** O agente atualiza `@SSOT` e o manifesto de boot se necessário.
6. **Final Audit:** O agente executa a Seção 15 do `NC-PRF-FR-001` (Checklist de Fim de Sessão).
