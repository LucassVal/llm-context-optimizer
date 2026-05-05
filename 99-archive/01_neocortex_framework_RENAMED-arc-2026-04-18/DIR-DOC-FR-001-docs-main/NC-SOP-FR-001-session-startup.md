# NC-SOP-FR-001  Procedimento Operacional Padro: Inicializao de Sesso NeoCortex

> **Classificao:** Procedimento Padro (SOP)
> **Aplica-se a:** Qualquer assistente AI (Antigravity, OpenCode, Cursor, Claude, DeepSeek)
> **Objetivo:** Garantir que NENHUM contexto seja perdido e que o host MCP esteja ativo antes de qualquer ao de desenvolvimento.

---

##  Checklist Rpido (2 minutos)

Execute nesta ordem exata. No pule etapas.

```
[ ] 1. Host MCP ativo?
[ ] 2. Lobos carregados/indexados?
[ ] 3. Roadmap lido? Sei qual ticket estou trabalhando?
[ ] 4. Regras do workspace relidas (.agents/rules)?
[ ] 5. Posso comear.
```

---

##  PASSO 1  Verificar e Iniciar o Host MCP

### 1.1 Checar se o servidor est ativo

```powershell
# Testar WebSocket (deve retornar 200 ou conectar sem erro):
curl http://127.0.0.1:8765/health
# Ou simplesmente verificar se h processo Python escutando:
netstat -an | findstr 8765
```

### 1.2 Se no estiver ativo, iniciar

```powershell
# Opo A  Batch (mais simples):
.\start_neocortex_mcp.bat

# Opo B  PowerShell:
.\start_neocortex_mcp.ps1

# Opo C  Manual (debug):
cd 01_neocortex_framework
python -m neocortex.mcp.server --transport websocket --host 127.0.0.1 --port 8765
```

**Sinais de sucesso nos logs:**
```
INFO - Sesso NeoCortex iniciada
INFO - LedgerStore initialized
INFO - MetricsStore initialized
INFO - MCP Server running on ws://127.0.0.1:8765
```

>  **Nunca inicie o trabalho sem o host MCP ativo.** Sem ele, cada chamada ao LLM envia o contexto completo, desperdiando tokens caros.

---

##  PASSO 2  Carregar / Atualizar os Lobos

### 2.1 Verificar se os lobos j esto populados

```bash
cd 01_neocortex_framework
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py --dry-run
```

Se o dry-run mostrar que os lobos j existem  **pule para o PASSO 3.**

### 2.2 Se os lobos precisarem ser atualizados (aps edio de SSOT)

```bash
python scripts/NC-SCR-FR-001-populate-lobes-ssot.py
```

### 2.3 Verificar ndice FTS5 (busca nos lobos)

Via MCP (usar no chat do Antigravity):
```
Use neocortex_lobes com ao list
```

Sada esperada: Lista com `NC-LBE-FR-ARCHITECTURE-001`, `NC-LBE-FR-SECURITY-001` etc.

---

##  PASSO 3  Carregar Contexto do Projeto

**Execute ANTES de falar qualquer coisa ao assistente:**

### 3.1 Ler o arquivo de roadmap (tickets abertos)

```
Use neocortex_lobes com ao get e lobe_name=NC-LBE-FR-ARCHITECTURE-001
```

Ou leia diretamente:
`01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md`

### 3.2 Identificar o ticket atual a trabalhar

Consulte a tabela de **Tickets Crticos Pendentes** no prompt master e escolha UM ticket para a sesso:

| Bloqueadores | Ao |
| :--- | :--- |
| AGENT-203 | Implementar `mentor_step_0()` |
| ORCH-301 | Tornar `spawn`/`stop`/`send_task` robustos |
| ORCH-302 | Integrar `execute` com `LLMBackend` |

> **Regra:** Uma sesso = Um ticket. No pulite entre tickets sem um checkpoint.

---

##  PASSO 4  Verificar Regras do Workspace

O assistente **deve** confirmar que leu as regras antes de escrever cdigo:

```
Verifique .agents/rules/NC-RULE-001-workspace-standards.mdc
e .agents/workflows/NC-WF-001-workspace-routine.md
```

**Resumo das proibies crticas:**
-  No crie arquivo sem prefixo `NC-`
-  No delete arquivos (mova para `DIR-ARC-FR`)
-  No escreva em pastas fora de `01_neocortex_framework/`
-  No faa import direto de mdulo com hfen
-  No hardcode caminhos  use `ConfigProvider`

---

##  PASSO 5  Criar Checkpoint de Incio de Sesso

Antes de iniciar qualquer modificao, crie um checkpoint:

```
Use neocortex_checkpoint com ao create, label=inicio-sessao-<data>
```

Isso garante rollback se algo der errado durante a sesso.

---

##  Ao Finalizar a Sesso

```
[ ] 1. Checkpoint criado com label=fim-sessao-<data>
[ ] 2. Novo arquivo criado  atualizar tabela SSOT em NC-NAM-FR-001
[ ] 3. Executar populate_lobes_from_ssot.py se SSOT foi atualizado
[ ] 4. Ticket concludo  atualizar status no roadmap NC-TODO-FR-001
[ ] 5. Registrar o que foi feito no changelog (seo 3 do NC-NAM-FR-001)
```

---

##  Referncias Rpidas

| Preciso de... | Onde olhar |
| :--- | :--- |
| Que ticket trabalhar | `NC-TODO-FR-001-project-roadmap-consolidated.md` |
| Nome correto de arquivo | `NC-NAM-FR-001-naming-convention.md` |
| Detalhes de implementao | `NC-APP-FR-001-technical-appendix.md` |
| Regras de segurana | `NC-SEC-FR-001-atomic-locks.yaml` |
| Poltica de um agente | `NC-CFG-FR-001-agent-policy-template.yaml` |
| Busca no conhecimento | `neocortex_lobes.search(query="...")` |
