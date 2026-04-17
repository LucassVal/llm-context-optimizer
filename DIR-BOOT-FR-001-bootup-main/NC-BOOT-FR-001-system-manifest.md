<!-- NC-READ-HASH: NC-BOOT-FR-001-v4 -->
<!-- DEDUP: Se NC-BOOT-FR-001-v4 j est no teu contexto desta sesso, SALTE este bloco inteiro. -->

# NC-BOOT-FR-001  NeoCortex: Boot Universal Completo

> **LEIA ESTE ARQUIVO PRIMEIRO  e apenas este.** Ele contm TUDO.  
> Qualquer IA (Antigravity, OpenCode, Cursor, Claude, DeepSeek) comea aqui.  
> Última atualização: 2026-04-16 | **v4**  Arquitetura de Maturidade

---

## 1. IDENTIDADE DO SISTEMA

**Projeto:** NeoCortex MCP Framework  
**GitHub:** https://github.com/LucassVal/llm-context-optimizer  
**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`  
**Framework:** `01_neocortex_framework\`  
**Objetivo:** Servidor MCP local que reduz custo de API substituindo tokens de cloud por memria persistente (lobos) + orquestrao multi-agente via PicoClaw + integrao visual via Mission Control e Pixel Agents.  
**Dono:** Lucas Valrio  
**Fase atual:** PR-MCP  a fase termina quando Antigravity  NeoCortex  OpenCode/PicoClaw estiver 100% operacional via MCP stdio/SSE.

---

## 2. ARQUITETURA COMPLETA DE PORTAS (Mapa Maduro v4)

```
 COMANDO (entram ordens no core) 

  Antigravity (T0)            Mission Control
  IDE via MCP stdio/SSE        :3000 HTTP/WS (React app)
                                   
        
                    
 NEOCORTEX CORE (Domnio DDD) 
  Lobes  HookRegistry  Checkpoint  SSOT  TaskQueue  ProjectConfig

                                              
      despacha tasks              emite eventos (HookRegistry)
                                             
PicoClaw (:18790)                       bridge JSONL
gateway A2A                                   
                                             
                                      Pixel Agents (:8765)
OpenCode (:45132 / :32879)             visualizao pixel-art
DeepSeek T1 executor                   (obs. passivo)

 OBSERVABILIDADE 
  Mission Control activity feed  SSE/WS  HookRegistry (AuditHook)
  neocortex_hud.py              polling local  server.py
```

### Papis por componente

| Componente | Papel DDD | Porta | Direo |
|---|---|---|---|
| **Antigravity** | Adaptador primrio | MCP stdio |  Core (comanda) |
| **Mission Control** | Adaptador primrio | :3000 |  Core (comanda + observa) |
| **PicoClaw** | Adaptador secundrio (driven) | :18790 | Core  Agentes |
| **OpenCode** | Runtime dos agentes T1 | :45132/:32879 | Executa tasks do PicoClaw |
| **DeepSeek** | LLM executor | interno | Dentro do OpenCode |
| **Pixel Agents** | Adaptador secundrio (observer) | :8765 | Core  Visual |
| **neocortex_hud.py** | Dashboard local | GUI Tkinter | Read-only monitor |

### Regra de ouro
> T0 (Antigravity) **pensa e decide**. OpenCode/DeepSeek **executam**. PicoClaw **despacha**. Nunca inverter.  
> O Core **no sabe** que Mission Control ou Pixel Agents existem  DDD hexagonal.

---

## 3. COMO INICIAR (ordem obrigatria)

```powershell
# 1. Verificar MCP core:
netstat -an | findstr 8765

# 2. Se no estiver rodando:
cd C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42
.\start_neocortex_mcp.ps1

# 3. Verificar PicoClaw gateway:
netstat -an | findstr 18790

# 4. HUD local:
python 01_neocortex_framework\scripts\neocortex_hud.py

# 5. Verificar lobos (se SSOT mudou):
python 01_neocortex_framework\scripts\NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
```

---

## 4. MAPA DE LOBOS ATIVOS

| Smbolo | Lobo | Contedo |
|---|---|---|
| `$ARCH` | `NC-LBE-FR-ARCHITECTURE-001` | Roadmap + Naming + ADRs |
| `$SEC` | `NC-LBE-FR-SECURITY-001` | Locks + Policy + SOP |
| `$DEV` | `NC-LBE-FR-DEVELOPMENT-001` | Auditorias + Alinhamentos |
| `$DEEPSEEK` | `NC-LBE-FR-DEEPSEEK-001`  | API completa DeepSeek |
| `$DS_A` | `NC-LBE-DS-001-deepseek-agent.mdc` | Agente DS-A executor |
| `$DS_B` | `NC-LBE-DS-002-deepseek-agent-b.mdc` | Agente DS-B pesquisa |
| `$DS_C` | `NC-LBE-DS-003-deepseek-agent-c.mdc` | Agente DS-C tools |
| `$DS_D` | `NC-LBE-DS-004-deepseek-agent-d.mdc` | Agente DS-D observabilidade |
| `$WORKER_PATTERNS`  | `NC-LBE-DS-003-worker-patterns.mdc` | REG-001010, claim protocol |
| `$ANTIGRAVITY` | `NC-LBE-INT-003-antigravity-integration.mdc` | Papel T0, 38 tools MCP |
| `$MISSION_CTRL` | `NC-LBE-INT-004-mission-control.mdc` | Mission Control integrao |
| `$PIXEL_AGENTS` | `NC-LBE-INT-005-pixel-agents.mdc` | Pixel Agents + bridge spec |

---

## 5. MAPA SSOT  ONDE FICA CADA COISA

| Smbolo | Path | Funo |
|---|---|---|
| `@SSOT` | `DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md` | Naming + mapa + changelog |
| `@ROADMAP` | `DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` | Roadmap unificado (FR + DS) |
| `@LOCKS` | `DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` | Arquivos protegidos DENY |
| `@POLICY` | `DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.yaml` | Regras machine-readable |
| `@GOVERNANCE` | `DIR-DOC-FR-001-docs-main/NC-GOV-FR-003-ia-governance-rules.yaml` | 20 regras de governana de IA + auditoria |
| `@BOOT` | `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` | **Este arquivo** |
| `@SOP` | `DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md` | SOP de sesso |
| `@POPULATE` | `scripts/NC-SCR-FR-001-populate-lobes-ssot.py` | Popula lobos |
| `@APPENDIX` | `DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md` | Tools, libs, LLMs |
| `@ULQ` | `DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md` | Dicionrio @$% |
| `@PROMPT` | `NC-PROMPT-FR-001-master-context.md` (raiz) | Contexto master v8 |

---

## 6. FRENTES OPERACIONAIS ATIVAS (2026-04-17)

** FRENTE ATIVA:** Correes Crticas NeoCortex (Orquestrao T0)

1. **Tester  Correo testes VectorEngine (async/API)**
   - Handoff: NC-DS-048  COMPLETED
   - Resultado: Aplicação massiva de metadados de frontmatter (domain, layer, type, tags, hash) em todos os arquivos complementares (Testes, Templates, Scripts base, configurações raiz) conforme especificado no ticket.

1. **Outros  Tarefas diversas**
   - Handoff: NC-DS-116  COMPLETED
   - Resultado: SUCCESS

**Prximo passo:** Executar testes corrigidos (`pytest tests/test_vector_engine.py -v --asyncio-mode=auto`)

**MCP-WQUEUE:** Tickets YAML em `DIR-DS-001-tickets/`. Agentes OpenCode executam e geram handoffs em `DIR-DS-002-audit-logs/`. T0 (Antigravity) valida e aprova.

---
## 7. ESTADO ACUMULADO  O QUE FOI CONSTRUDO

| Grupo | Quantidade | Status |
|---|---|---|
| Serviços core (`NC-SVC-FR-*`) | 18 |  DONE |
| Utils (`NC-UTL-FR-*`) | 4 |  DONE |
| Tools MCP (`NC-TOOL-FR-000037`) | 38 |  DONE |
| Hooks core (`NC-HK-FR-001/002`) | 2 |  DONE |
| Config core (`NC-CFG-FR-004`) | 1 |  DONE |
| Lobes de integração (`NC-LBE-INT-004/005`) | 2 |  Em documentação |
| HUD Tkinter (5 abas) | 1 |  FUNCIONAL |
| PicoClaw gateway | 1 |  :18790 ativo |

**Serviços adicionados em 2026-04-16 (Ciclo 3):**

| Serviço | ID | Status | Descrição |
|---|---|---|---|
| CryptoHub | `NC-SVC-FR-017` |  ACTIVE | Fernet AES-128 + HMAC-SHA256. Key via PBKDF2(MASTER_KEY). Fallback hash-only. |
| TagNormalizer | `NC-SVC-FR-018` |  ACTIVE | Valida @/$/%  contra NC-DOC-FR-001 SSOT. scan(), normalize(), validate_lobe(). |

**Governança:** Compliance 44.9% → meta >80% (NC-DS-108 FAILED)

### Colisões resolvidas (2026-04-13)
FR-032, FR-033, FR-020-categories, FR-028-export  arquivados em `DIR-ARC-FR-001-archive-main/tools-duplicates-20260413/`

### SSOT + Tool Manifest Sync (2026-04-16)
- **SSOT**: Tabela NC-NAM-FR-001 atualizada com 17 NC-SVC, 35 NC-TOOL, 37 NC-SCR faltantes (drift corrigido).
- **Tool Manifest**: Regenerado com 38 tools + placeholders para hooks FR-003.
- **Registry**: NC-GOV-FR-004 atualizado com paths de todas as 35 tools físicas.
- **Boot Manifest**: Esta atualização (NC-DS-113) concluída.


## 8. CAMINHO CRTICO PR-MCP

```
FASE PR-MCP [ATUAL]:
   Antigravity ↔ MCP stdio ↔ NeoCortex Core — configurado
   PicoClaw ↔ OpenCode ↔ DeepSeek — operacional
   38 tools MCP físicos — criados e manifestados
   ORCH-301 — DONE (NC-DS-096, send_task() HTTP POST :18790)
   ORCH-302 — DONE (NC-DS-096, neocortex_task SSE polling)
   SAVE-005 — WIRED (dry-run preview middleware)

CRITÉRIO DE ENCERRAMENTO DA FASE PR-MCP:
  Antigravity chama tool MCP → Core recebe → PicoClaw despacha → OpenCode executa → resultado retorna
  = Loop completo Antigravity ↔ Core ↔ PicoClaw ↔ OpenCode via MCP

PRÓXIMOS PASSOS:
  [ ] Executar SAVE-005 (dry-run preview)
  [ ] Executar SCR-064 (catalog) + SCR-066 (bootup sync)
  [ ] Validar loop completo Antigravity → Core → PicoClaw → OpenCode
```


## 9. TICKETS CRTICOS (PR-MCP)

| Ticket | Status | Prxima ao |
|---|---|---|
| **INT-001** |  Entregue |  |

---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---
---

## 10. REGRAS OBRIGATRIAS

| ID | Regra |
|---|---|
| **R01** | `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`  SEMPRE |
| **R02** | Arquivo criado  atualizar `@SSOT` com changelog |
| **R04** | `@LOCKS` so IMUTVEIS: `server.py`, `sub_server.py`, `NC-NAM-FR-001`, `neocortex_config.yaml` |
| **R05** | NUNCA deletar  arquivar em `DIR-ARC-FR-001-archive-main/` |
| **R09** | NUNCA `import NC-SVC-*` direto  usar `importlib.util` |
| **R10** | NUNCA hardcodar paths  usar `get_config()` |
| **R11** | NUNCA `print()`  `logger = logging.getLogger(__name__)` |
| **R17** | T0 orquestra. OpenCode/DeepSeek executam. Nunca inverter. |
| **R21** |  ZERO suposies  verificar ambiente real antes de qualquer afirmao |

### Zonas de escrita

| Zona | Path | Quem |
|---|---|---|
| PROD | `01_neocortex_framework/neocortex/` | T0, T1 |
| DOCS | `DIR-DOC-FR-001-docs-main/` | T0 apenas |
| LOBES | `02_memory_lobes/` | T0 via `@POPULATE` |
| BOOT | `DIR-BOOT-FR-001-bootup-main/` | T0 apenas |
| TEST | `05_examples/` | T0, T1 |

---

## 10.5 GOVERNANA DE IA  20 REGRAS

**Framework**: `NCGOVFR003iagovernancerules.yaml` + auditoria `NCSCRFR080governanceauditor.py`

**Categorias**:
1. **Fundao** (R01R05): Inventrio, poltica, estrutura, nomenclatura, ambientes
2. **Controle de Acesso** (R06R09): Identidade, privilgio mnimo, atomic locks, zonas de escrita
3. **Rastreabilidade** (R10R13): Trilha de auditoria, versionamento, handoffs, checkpoints
4. **Execuo** (R14R17): STEP0 (mentor_step_0), STEP1 (save point), circuit breaker, rate limiting
5. **Ciclo de Vida** (R18R20): Tickets, rotina de 4 ciclos, reviso e arquivo

**Status**: 12 implementadas, 3 parciais, 5 pendentes (ver auditoria)

**Integrao**:
- **Mentor Mode**: STEP0 valida tarefas contra Regression Buffer e polticas
- **Atomic Locks**: Proteo proativa de arquivos crticos (@LOCKS)
- **Hooks Reativos**: HookRegistry (PreToolUse/PostToolUse/ToolError) complementa locks
- **Ciclo 4**: Auditoria de governana semanal via `NCSCRFR080`

**Prximos passos**:
1. Implementar verificaes completas para regras pendentes
2. Integrar hooks de segurana com atomic locks
3. Migrar configurao para por projeto (`.nc/config.yaml`)
4. Criar template de plugin para tools MCP

---

## 11. CHECKLIST FIM DE SESSO  R20

```
 @SSOT atualizado + changelog [YYYY-MM-DD]
 %DONE no @ROADMAP para cada ticket concludo
 @POPULATE rodado (se algum lobe mudou)
 @BOOT atualizado (frentes + tickets + status)    OBRIGATRIO
 Nenhum *.db / *.wal / __pycache__ commitado
```
