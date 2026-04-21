# NC-PROMPT-FR-002  Pre-MCP Session Checklist v6
<!-- Atualizado: 2026-04-12 | v6: Adiciona verificao de correspondncia $DS_AGENT -->

> **PROPSITO:** Checklist operacional de sesso. Nada de roadmap aqui  veja `@ROADMAP`.
> **LEIA NO INCIO DE CADA SESSO.**

---

## ARQUITETURA DE AGENTES (viso rpida)

```
T0 = Antigravity    Orquestra, revisa, valida, aprova handoffs
T1 = DeepSeek-chat  Executa tickets NC-DS-XXX (~USD 0.007/tool, via OpenCode)
T2 = Qwen 1.5B      Trabalho braal massivo (local, grtis)
T3 = Qwen 3B        Cdigo mdio (local, grtis)
T4 = Mission Ctrl   Generic Adapter para gesto Kanban
T5 = Pixel Agents   JSONL Bridge visual
```

`$DS_AGENT` lobe: `DIR-TMP-FR-001-templates-main/NC-LBE-DS-001-deepseek-agent.mdc`
`$DS_PROMPT`:     `NC-PROMPT-DS-001-deepseek-subordinate.md` + ticket YAML

---

##  STEP 0  REGRESSION CHECK (1a coisa a fazer nesta sesso)

> Verificar se os erros registrados de sesses anteriores no vo se repetir.

```bash
# Via MCP (se ativo):
neocortex_regression  action=list_all
# Sem MCP: ler DIR-DS-002-audit-logs/ e lembrar das lies abaixo:
```

**Lies crticas registradas (2026-04-12):**

| REG | Erro | Preveno |
|---|---|---|
| REG-001 | Ticket com `@LOCK` em `files_modified`  workers BLOCKED | Tickets s listam write_zone, SSOT = T0 |
| REG-002 | Worker em loop infinito quando fila 100% CLAIMED | Prompt tem max 3 retries  PARA |
| REG-003 | task.file no existe  EL-3 BLOCKS todos workers | Criar YAMLs ANTES de enfileirar |
| REG-004 | Handoff DONE com 0 linhas, 0 arquivos (false DONE) | Auto-approve exige `lines_added > 5` + `files_created > 0` |
| REG-005 | PS heredoc falha silenciosamente em batch | Usar Python script para criar arquivos em batch |

---

## PR-SESSO (executar nesta ordem)

**1. Verificar correspondncias DS em aberto**  NOVO  SEMPRE PRIMEIRO
```powershell
# Verificar handoffs PENDING_REVIEW (T1  T0)
Select-String -Path "DIR-DS-002-audit-logs\*.yaml" -Pattern "PENDING_REVIEW" -List
# Verificar tickets em aberto sem handoff correspondente
Get-ChildItem "DIR-DS-001-tickets\NC-DS-*.yaml" | Where-Object {
    $id = ($_.BaseName -split "-")[0..2] -join "-"
    -not (Test-Path "DIR-DS-002-audit-logs\$id-handoff-*.yaml")
}
```
> SE houver PENDING_REVIEW  revisar ANTES de emitir novos tickets (ver seo "Reviso de Handoffs")

**2. Verificar MCP ativo**
```powershell
netstat -an | findstr 8765
# Se no ativo: .\start_neocortex_mcp.ps1
# Instncia DEV (sandbox): .\start_neocortex_dev.bat (porta 8766)
```

**3. Carregar @BOOT e $DS_AGENT lobe**
```
# MCP ativo:
neocortex_lobes  action=get_content  lobe_name=NC-LBE-FR-ARCHITECTURE-001
neocortex_lobes  action=get_content  lobe_name=NC-LBE-DS-001-deepseek-agent
# Sem MCP: abrir manualmente DIR-TMP-FR-001-templates-main/NC-LBE-DS-001-deepseek-agent.mdc
```

**4. Verificar @LOCKS**
```
NC-SEC-FR-001-atomic-locks.yaml
Protegidos: neocortex_config.yaml | server.py | sub_server.py | NC-NAM-FR-001 | NC-TODO-FR-001
```

**5. Identificar ticket no @ROADMAP**
```
NC-TODO-FR-001-project-roadmap-consolidated.md
NUNCA implemente sem ticket vinculado.
```

**6. Naming NC- obrigatrio (R01)**
```
Formato: NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext
Tipos: TOOL SCR DOC TODO LBE CFG SEC SOP ARC BAK BOOT PROMPT MAN DS
```

**7.  SSOT UPDATE  OBRIGATRIO A CADA ARQUIVO CRIADO (R02)**
> [!CAUTION]
> **SSOT desatualizado = coliso garantida.** Outro agente pode criar um arquivo com o mesmo nome sem saber que j existe. Isso j aconteceu em 2026-04-12 (REG-006).

```
NC-NAM-FR-001-naming-convention.md  tabela + changelog [YYYY-MM-DD]
MOMENTO: logo aps criar/mover arquivo  NO deixar para o final da sesso.
VERIFICAO: grep NC-NAM-FR-001 para confirmar que o novo arquivo consta.
```

**8. Regenerar manifesto aps alterar NC-***
```powershell
$env:PYTHONPATH = "C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\01_neocortex_framework"
python -X utf8 ".\scripts\NC-SCR-FR-003-manifest-factory.py" --format all
```

**9. Popular lobes aps atualizar SSOT**
```powershell
python ".\scripts\NC-SCR-FR-001-populate-lobes-ssot.py"
```

---

## REVISO DE HANDOFFS DS (quando houver PENDING_REVIEW)

```powershell
# 1. Ler handoff
Get-Content "DIR-DS-002-audit-logs\NC-DS-XXX-handoff-*.yaml"

# 2. Validar independente (T0 no confia  verifica por si)
python -X utf8 -m py_compile "01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-0XX-*.py"
Get-ChildItem "neocortex\mcp\tools\" | Where-Object { $_.Name -notmatch "^NC-" }
Select-String -Path "DIR-DOC-FR-001-docs-main\NC-NAM-FR-001*" -Pattern "\[2026-"

# 3. Aprovar: alterar status para APPROVED + preencher t0_review
# 4. Rejeitar: alterar status para REJECTED + criar NC-DS-{NUM+1} para correo

# 5. Aps aprovao:
python ".\scripts\NC-SCR-FR-001-populate-lobes-ssot.py"
# Marcar %DONE no @ROADMAP (FR-XXX + NC-DS-XXX)
```

---

## SE EMITIR NOVO TICKET PARA DEEPSEEK

```
 Criar DIR-DS-001-tickets/NC-DS-XXX-{desc}.yaml (copiar NC-DS-HANDOFF-TEMPLATE.yaml)
 Preencher entry_state, exit_state, active_locks, write_zone
 Verificar roadmap_ticket no @ROADMAP
 write_zone NO est em @LOCKS
 Abrir OpenCode  colar NC-PROMPT-DS-001-deepseek-subordinate.md + ticket YAML
```

---

## PS-SESSO  R20 (obrigatrio sempre)

```
 @SSOT (NC-NAM-FR-001) atualizado + changelog [YYYY-MM-DD]
 %DONE no @ROADMAP (FR-XXX e NC-DS-XXX se houver)
 NC-SCR-FR-003 rodado (manifesto regenerado)
 NC-SCR-FR-001 rodado (lobes populados  incluindo $DS_AGENT)
 @BOOT atualizado (NC-BOOT-FR-001)
 DIR-DS-002-audit-logs sem PENDING_REVIEW em aberto
 Nenhum *.db / *.wal / __pycache__ no git
```

---

## REFERNCIA RPIDA

| Smbolo | Arquivo |
|---|---|
| `@SSOT` | `DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md` |
| `@ROADMAP` | `DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` |
| `@LOCKS` | `DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` |
| `@BOOT` | `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` |
| `@MANIFEST` | `DIR-DOC-FR-001-docs-main/NC-MAN-FR-001-project-manifest.json` |
| `@POLICY_T1` | `DIR-DOC-FR-001-docs-main/NC-CFG-DS-001-agent-policy.yaml` |
| `@ENTRY_LOCK` | `DIR-DOC-FR-001-docs-main/NC-SEC-FR-002-entry-lock-protocol.md` |
| `$DS_AGENT` | `DIR-TMP-FR-001-templates-main/NC-LBE-DS-001-deepseek-agent.mdc` |
| `$DS_PROMPT` | `NC-PROMPT-DS-001-deepseek-subordinate.md`  per-frente |
| `$WK_PROMPT` | `DIR-DS-000-agent-config/NC-PROMPT-DS-002-worker-universal.md`  N workers |
| `$QUEUE` | `DIR-DS-000-agent-config/NC-CFG-DS-004-task-queue.yaml` |
| `$DS_TICKETS` | `DIR-DS-001-tickets/` |
| `$DS_LOGS` | `DIR-DS-002-audit-logs/` |
| `$ENTRY_LOCKS` | `DIR-DS-003-entry-locks/` |
| `@AUTO_APPROVE` | `scripts/NC-SCR-FR-005-auto-approve.py` |
| `@FACTORY` | `scripts/NC-SCR-FR-003-manifest-factory.py` |
| `@POPULATE` | `scripts/NC-SCR-FR-001-populate-lobes-ssot.py` |
| `$MISSION_CTRL` | `02_memory_lobes/NC-LBE-INT-004-mission-control.mdc` |
| `$PIXEL_AGENTS` | `02_memory_lobes/NC-LBE-INT-005-pixel-agents.mdc` |

---

##  SCHEDULE T0  Verificao Automtica (rodar a cada ~15 min ou quando worker finaliza)

> **T0 deve executar este bloco periodicamente durante sesses com N workers ativos.**

```powershell
# 1. AUTO-APPROVE  aprovar handoffs elegveis sem interao manual
python "01_neocortex_framework\scripts\NC-SCR-FR-005-auto-approve.py"

# 2. STATUS DA FILA  quantas tasks AVAILABLE / DONE / CLAIMED
$q = Get-Content "DIR-DS-000-agent-config\NC-CFG-DS-004-task-queue.yaml" -Raw
[regex]::Matches($q, 'status: (\w+)') | Group-Object {$_.Groups[1].Value} |
  Select-Object Name, Count | Format-Table

# 3. HANDOFFS PENDENTES (que no passaram no auto-approve)
Select-String -Path "DIR-DS-002-audit-logs\*.yaml" -Pattern "PENDING_REVIEW" -List |
  Select-Object -ExpandProperty Path

# 4. WORKERS OCIOSOS (claims expirados > 300s)
$now = Get-Date
Get-Content "DIR-DS-000-agent-config\NC-CFG-DS-004-task-queue.yaml" |
  Select-String "claimed_at" | ForEach-Object {
    if ($_ -match '"(.+)"') {
      $age = ($now - [DateTime]$Matches[1]).TotalSeconds
      if ($age -gt 300) { "CLAIM EXPIRADO: $_ ($([int]$age)s)" }
    }
  }
```

### Ao por resultado:

| Resultado | Ao T0 |
|---|---|
| Handoffs PENDING_REVIEW restantes | Revisar manualmente (ESCALATED ou locks) |
| Tasks AVAILABLE = 0 | Criar novas tasks em NC-CFG-DS-004 |
| Claims expirados | Resetar `status: AVAILABLE` + `claimed_by: null` |
| Worker ocioso (sem task claimed) | Verificar se leu NC-PROMPT-DS-002 corretamente |

---

## PROTEO NC-PROMPT-DS-002 (worker universal)

`NC-PROMPT-DS-002-worker-universal.md` e `NC-CFG-DS-004-task-queue.yaml` so **SSOT crticos**.
- Apenas T0 edita estes arquivos
- Adicionar em @LOCKS se sistema escalar para >10 workers simultneos
- Workers s LEEM estes arquivos  nunca escrevem

