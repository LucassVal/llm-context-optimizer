# NC-SOP-FR-001 — Procedimento Operacional Padrão: Inicialização de Sessão NeoCortex

> **Classificação:** Procedimento Padrão (SOP)
> **Aplica-se a:** Qualquer assistente AI (Antigravity, OpenCode, Cursor, Claude, DeepSeek)
> **Objetivo:** Garantir que NENHUM contexto seja perdido e que o host MCP esteja ativo antes de qualquer ação de desenvolvimento.

---

## ⚡ Checklist Rápido (2 minutos)

Execute nesta ordem exata. Não pule etapas.

```
[ ] 1. Host MCP ativo?
[ ] 2. Lobos carregados/indexados?
[ ] 3. Roadmap lido? Sei qual ticket estou trabalhando?
[ ] 4. Regras do workspace relidas (.agents/rules)?
[ ] 5. Posso começar.
```

---

## 📋 PASSO 1 — Verificar e Iniciar o Host MCP

### 1.1 Checar se o servidor está ativo

```powershell
# Testar WebSocket (deve retornar 200 ou conectar sem erro):
curl http://127.0.0.1:8765/health
# Ou simplesmente verificar se há processo Python escutando:
netstat -an | findstr 8765
```

### 1.2 Se não estiver ativo, iniciar

```powershell
# Opção A — Batch (mais simples):
.\start_neocortex_mcp.bat

# Opção B — PowerShell:
.\start_neocortex_mcp.ps1

# Opção C — Manual (debug):
cd 01_neocortex_framework
python -m neocortex.mcp.server --transport websocket --host 127.0.0.1 --port 8765
```

**Sinais de sucesso nos logs:**
```
INFO - Sessão NeoCortex iniciada
INFO - LedgerStore initialized
INFO - MetricsStore initialized
INFO - MCP Server running on ws://127.0.0.1:8765
```

> ⚠️ **Nunca inicie o trabalho sem o host MCP ativo.** Sem ele, cada chamada ao LLM envia o contexto completo, desperdiçando tokens caros.

---

## 📋 PASSO 2 — Carregar / Atualizar os Lobos

### 2.1 Verificar se os lobos já estão populados

```bash
cd 01_neocortex_framework
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
```

Se o dry-run mostrar que os lobos já existem → **pule para o PASSO 3.**

### 2.2 Se os lobos precisarem ser atualizados (após edição de SSOT)

```bash
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py
```

### 2.3 Verificar índice FTS5 (busca nos lobos)

Via MCP (usar no chat do Antigravity):
```
Use neocortex_lobes com ação list
```

Saída esperada: Lista com `NC-LBE-FR-ARCHITECTURE-001`, `NC-LBE-FR-SECURITY-001` etc.

---

## 📋 PASSO 3 — Carregar Contexto do Projeto

**Execute ANTES de falar qualquer coisa ao assistente:**

### 3.1 Ler o arquivo de roadmap (tickets abertos)

```
Use neocortex_lobes com ação get e lobe_name=NC-LBE-FR-ARCHITECTURE-001
```

Ou leia diretamente:
`01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md`

### 3.2 Identificar o ticket atual a trabalhar

Consulte a tabela de **Tickets Críticos Pendentes** no prompt master e escolha UM ticket para a sessão:

| Bloqueadores | Ação |
| :--- | :--- |
| AGENT-203 | Implementar `mentor_step_0()` |
| ORCH-301 | Tornar `spawn`/`stop`/`send_task` robustos |
| ORCH-302 | Integrar `execute` com `LLMBackend` |

> **Regra:** Uma sessão = Um ticket. Não pulite entre tickets sem um checkpoint.

---

## 📋 PASSO 4 — Verificar Regras do Workspace

O assistente **deve** confirmar que leu as regras antes de escrever código:

```
Verifique .agents/rules/NC-RULE-001-workspace-standards.mdc
e .agents/workflows/NC-WF-001-workspace-routine.md
```

**Resumo das proibições críticas:**
- ❌ Não crie arquivo sem prefixo `NC-`
- ❌ Não delete arquivos (mova para `DIR-ARC-FR`)
- ❌ Não escreva em pastas fora de `01_neocortex_framework/`
- ❌ Não faça import direto de módulo com hífen
- ❌ Não hardcode caminhos — use `ConfigProvider`

---

## 📋 PASSO 5 — Criar Checkpoint de Início de Sessão

Antes de iniciar qualquer modificação, crie um checkpoint:

```
Use neocortex_checkpoint com ação create, label=inicio-sessao-<data>
```

Isso garante rollback se algo der errado durante a sessão.

---

## 🏁 Ao Finalizar a Sessão

```
[ ] 1. Checkpoint criado com label=fim-sessao-<data>
[ ] 2. Novo arquivo criado → atualizar tabela SSOT em NC-NAM-FR-001
[ ] 3. Executar populate_lobes_from_ssot.py se SSOT foi atualizado
[ ] 4. Ticket concluído → atualizar status no roadmap NC-TODO-FR-001
[ ] 5. Registrar o que foi feito no changelog (seção 3 do NC-NAM-FR-001)
```

---

## 📎 Referências Rápidas

| Preciso de... | Onde olhar |
| :--- | :--- |
| Que ticket trabalhar | `NC-TODO-FR-001-project-roadmap-consolidated.md` |
| Nome correto de arquivo | `NC-NAM-FR-001-naming-convention.md` |
| Detalhes de implementação | `NC-APP-FR-001-technical-appendix.md` |
| Regras de segurança | `NC-SEC-FR-001-atomic-locks.yaml` |
| Política de um agente | `NC-CFG-FR-001-agent-policy-template.yaml` |
| Busca no conhecimento | `neocortex_lobes.search(query="...")` |
