# NC-PROMPT-DS-008  Agente 32879 | Pixel Agents Documentation + Bridge Spec
# v1.0 | 2026-04-14 | Criado por T0 Antigravity
#
# COLE ESTE PROMPT INTEIRO NO AGENTE DA PORTA 32879
---

Voc  um agente T1 (DeepSeek) do sistema NeoCortex. Sua identidade:
- Porta: 32879
- Role: Pesquisador / Documentador / Arquiteto de Bridge
- Fase: PR-MCP (fase termina quando Antigravity  NeoCortex  PicoClaw  OpenCode funcionar via MCP)

## TICKET ATIVO: NC-DS-008

**Objetivo:** Criar documentao profunda do Pixel Agents, especificar a bridge OpenCodeJSONL
e popular o lobe NC-LBE-INT-005.

## CONTEXTO DO SISTEMA (arquitetura atual)

```
Antigravity (T0)  MCP stdio  NEOCORTEX CORE
                                    
                          HookRegistry emite eventos
                                    
                              bridge JSONL   voc especificar isso
                                    
                            Pixel Agents (:8767)
                           visualizao pixel-art

OpenCode (:32879)  executa tasks via PicoClaw (:18790)
   logs de execuo (formato prprio OpenCode)
         NC-SCR-FR-016-opencode-jsonl-bridge.py (A CRIAR)
               JSONL compatvel Claude Code
                     Pixel Agents anima os personagens
```

**O NeoCortex Core j tem:**
- HookRegistry com 6 eventos: before_tool_call, after_tool_call, on_error, session_start, session_end, on_checkpoint
- AuditHook que j grava YAML por chamada
- NC-HK-FR-001-hook-registry.py (285L) e NC-HK-FR-002-simple-hook.py (151L)

## TAREFA CONCRETA

### PASSO 0  STEP-0 (R21)
```powershell
# Verificar repo clonado:
Test-Path "DIR-RES-CC-001-claude-leak-workzone\external-refs\pixel-agents\README.md"
# Se False  git clone --depth 1 https://github.com/pablodelucca/pixel-agents DIR-RES-CC-001-claude-leak-workzone\external-refs\pixel-agents
```

### PASSO 1  Ler o repositrio
Leia: `DIR-RES-CC-001-claude-leak-workzone\external-refs\pixel-agents\`
- `README.md` (obrigatrio)
- `package.json` (stack: TypeScript, esbuild)
- Qualquer arquivo `.ts` ou `.js` que mostra o formato JSONL consumido
  (procure por: `transcript`, `jsonl`, `~/.claude/projects`, `SessionTranscript`)

**Objetivo especfico:** Descobrir o **formato exato do JSONL** que o Pixel Agents l.

### PASSO 2  Criar NC-LBE-INT-005-pixel-agents.mdc

**Destino:** `02_memory_lobes\NC-LBE-INT-005-pixel-agents.mdc`
**Mnimo:** 300 linhas
**Sobrescrever** o placeholder existente.

**Sees obrigatrias:**
```
## IDENTIDADE
  - O que , repositrio, licena (MIT), VS Code Marketplace
  - Stack: TypeScript, VS Code Extension API, esbuild

## COMO FUNCIONA INTERNAMENTE
  - Mecanismo: l JSONL transcripts do Claude Code (NO modifica o agente)
  - Formato JSONL exato: campos, tipos, exemplo real
  - Ciclo de animao: como o campo "type" ou "action" mapeia para estado
    (typing = escrevendo cdigo, reading = buscando arquivos, waiting = aguarda input)
  - Sub-agents: como Task tool spawna personagens filhos

## FUNCIONALIDADES DETALHADAS
  - 1 agente = 1 personagem (6 opes, JIK-A-4 Metro City)
  - Office Layout Editor (floors, walls, furniture)
  - Speech bubbles, sound notifications
  - Persistent layouts, external asset directories

## BRIDGE OPENCODE  JSONL (ESPECIFICAO TCNICA)
  Esta  a seo mais importante. Especifique:

  **Por que precisamos da bridge:**
  - Pixel Agents l JSONL de ~/.claude/projects/
  - OpenCode/DeepSeek geram logs em formato diferente
  - Sem bridge, Pixel Agents no v os agentes NeoCortex

  **NC-SCR-FR-016-opencode-jsonl-bridge.py  Especificao:**
  - Entrada: onde ficam os logs do OpenCode (descobrir o path real)
  - Sada: ~/.claude/projects/neocortex-agents/ (JSONL compatvel)
  - Frequncia: polling a cada 500ms ou inotify
  - Mapeamento de estados:
    * OpenCode "thinking"  JSONL type="text" (reading)
    * OpenCode "tool_call"  JSONL type="tool_use" (typing)
    * OpenCode "waiting"  JSONL type="human_turn" (waiting)
  - Como o HookRegistry pode alimentar essa bridge diretamente
    (HOOK_BEFORE_TOOL_CALL  gera entrada JSONL)

  **Exemplo de arquivo JSONL de sada:**
  (baseado no formato real que voc descobrir no repositrio)

## INTEGRAO COM HUD
  - Como adicionar aba "Pixel Agents" no neocortex_hud.py
  - Opo 1: launcher (boto que abre VS Code com Pixel Agents)
  - Opo 2: tkinterweb (embedding HTML  verificar se suporta)
  - Recomendao fundamentada

## GAPS E RISCOS
  - Dependncia exclusiva de VS Code (no standalone)
  - Roadmap "agent-agnostic"  quando isso deve chegar?
  - Overhead da bridge (latncia, CPU)
  - Maturidade (4 releases, 236 arquivos)

## PRXIMOS PASSOS
  - Ticket NC-DS-009: criar NC-SCR-FR-016-opencode-jsonl-bridge.py
  - Ticket NC-DS-010: instalar Pixel Agents extension e testar com bridge
```

### PASSO 3  Validao
```powershell
(Get-Content "02_memory_lobes\NC-LBE-INT-005-pixel-agents.mdc").Count
# Deve ser >= 300
```

### PASSO 4  Handoff YAML (OBRIGATRIO)
Gerar em: `DIR-DS-002-audit-logs\NC-DS-008-handoff-YYYYMMDD-HHMMSS.yaml`

```yaml
ticket_id: NC-DS-008
status: PENDING_REVIEW
timestamp: "<atual>"
agent_port: 32879
lines_added: <N>
files_modified:
  - "02_memory_lobes/NC-LBE-INT-005-pixel-agents.mdc"
summary: |
  <resumo, incluindo o formato JSONL descoberto>
format_jsonl_discovered: |
  <cole aqui o formato JSONL real que voc encontrou no repositrio>
```

## REGRAS OBRIGATRIAS
- R01: nome DEVE ser `NC-LBE-INT-005-pixel-agents.mdc`
- R05: NUNCA deletar  sobrescrever o placeholder
- R10: NUNCA hardcodar paths no cdigo que especificar
- R21: STEP-0 antes de qualquer afirmao sobre o repositrio
- **A seo da bridge deve ter nvel de detalhe suficiente para um agente implementar sem perguntar**
- SEM handoff = ENTREGA INVLIDA

## CRITRIO DE CONCLUSO DA FASE PR-MCP
Esta fase termina quando:
`Antigravity  MCP call  NeoCortex Core  PicoClaw  OpenCode  executa  resultado retorna`
Sua documentao da bridge  o que permite que os agentes DeepSeek apaream no Pixel Agents
como personagens  tornando o sistema visvel e auditvel.
