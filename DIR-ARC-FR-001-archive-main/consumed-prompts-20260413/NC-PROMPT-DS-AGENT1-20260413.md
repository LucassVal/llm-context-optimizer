# AGENT 1  Batch Sprint Pr-MCP [2026-04-13]
<!-- Tickets: NC-DS-029, NC-DS-031, NC-DS-033 -->
<!-- Base: NC-ANA-INT-001 @SYNTHESIS | Contexto: ~30k tokens estimado -->

## CONTEXTO OBRIGATRIO (leia antes de qualquer coisa)

**Projeto:** NeoCortex Multi-Agent Framework
**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
**Sua identidade:** Agent 1  sprint Fase 1 Pr-MCP

**Arquivos SSOT a consultar antes de comear:**
- `@LOCKS` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`
- `@SSOT` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
- `@SYNTHESIS` = `DIR-RES-CC-001-claude-leak-workzone/NC-ANA-INT-001-synthesis-t0.md`
- `@RES001` = `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-001-validation-hooks-worker-review.md`
- `$WORKER_PATTERNS` = `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc`

**PROIBIDO MODIFICAR:** `server.py`, `sub_server.py`, `NC-NAM-FR-001` (@LOCKS)

---

## TAREFA A  NC-DS-029: PersistentWorker (Worker em Loop Contnuo)

**Ticket:** WORKER-001
**Esforo:** ~150L
**Write zone:** `DIR-DS-000-agent-config/`
**Arquivo a gerar:** `DIR-DS-000-agent-config/NC-PROMPT-DS-003-persistent-worker.md`

### O que entregar
Um **prompt de sistema** (no cdigo Python diretamente) para configurar um agent como worker persistente em loop contnuo. O prompt deve instruir o worker a:

1. **Loop sncrono** com `time.sleep(10)`  adequado para MCP sncrono
2. **Backoff exponencial:** 10s  20s  40s aps erros consecutivos (mximo 3 tentativas antes de reportar)
3. **Classe PersistentWorker** com mtodos: `start()`, `stop()`, `pause()`
4. **Protocolo FILE_LOCK** (j existe em NC-PROMPT-DS-002  reutilizar)
5. **Heartbeat interno** a cada 60s (registrar em log)
6. **EXIT_CODE_PERMANENT = 42** para erros no-retentveis (importar de IDValidator quando existir)

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- Separar em classe com `start()`, `stop()`, `pause()`  API limpa
- Backoff exponencial 102040s aps erros consecutivos
- Migrar para `asyncio` quando MCP-WQUEUE (SQLite) for implementado (Fase 2)  anotar como TODO

### Referncias a ler ANTES de implementar
- `@RES001` seo "PersistentWorker" (pontos 7-9)  padres validados pela internet
- `$WORKER_PATTERNS`  protocolo atual de workers
- `DIR-DS-000-agent-config/NC-PROMPT-DS-002-worker-universal.md`  prompt universal atual (adaptar, no substituir)

### Estrutura do arquivo a gerar
```
NC-PROMPT-DS-003-persistent-worker.md
 Identidade do worker (Ralph-Wiggum mode)
 Loop principal com backoff exponencial
 Protocolo FILE_LOCK (copiar de NC-PROMPT-DS-002)
 Checklist pr-entrega (R20 adaptado)
 Handoff template
```

---

## TAREFA B  NC-DS-031: HookRegistry (Sistema de Hooks Reativos)

**Ticket:** HOOK-001
**Esforo:** ~250L
**Write zone:** `01_neocortex_framework/neocortex/core/hooks/`
**Arquivos a gerar:**
- `01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-001-hook-registry.py`
- `01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-002-example-hook.py`
- `05_examples/.nc/hooks/ssot-guard.yaml` (exemplo de hook YAML)

### O que entregar
Sistema de hooks reativos ps-ao seguindo padro MCP:

**Nomenclatura obrigatria dos eventos (padro MCP):**
- `PreToolUse`  antes de executar uma tool
- `PostToolUse`  aps executar uma tool com sucesso
- `ToolError`  quando uma tool retorna erro

**HookRegistry deve ter:**
```python
class HookRegistry:
    def register(self, event: str, hook_fn: Callable, timeout: float = 2.0) -> None
    def fire(self, event: str, context: dict) -> list[HookResult]
    def list_hooks(self) -> dict[str, list]
    def load_from_yaml(self, path: Path) -> None  # .nc/hooks/*.yaml
```

**Regras crticas:**
- Timeout de **2 segundos** por hook (evitar bloqueio de MCP)
- Suporte a hooks assncronos via `asyncio.wait_for`
- Log de execuo: qual hook rodou, durao, resultado
- Auto-discovery via `importlib.metadata` para hooks em pacotes

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- `PreToolUse`, `PostToolUse`, `ToolError`  nomenclatura padro MCP (no mudar)
- Timeout 2s obrigatrio
- Log: `hook_name`, `event`, `duration_ms`, `result`, `error`

### Referncias a ler ANTES de implementar
- `@RES001` sees 1 e 2  padres hookery + pre-commit
- `@SYNTHESIS` seo A (MentorHooks/GuardHooks)
- `NC-SEC-FR-001-atomic-locks.yaml`  criar guard hook para SSOT

---

## TAREFA C  NC-DS-033: PluginTemplate (NC-TOOL-FR-TEMPLATE)

**Ticket:** PLUGIN-001
**Esforo:** ~300L (10 arquivos template)
**Write zone:** `01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TOOL-FR-TEMPLATE/`
**Arquivos a gerar:**
```
NC-TOOL-FR-TEMPLATE/
 NC-CFG-FR-001-plugin.json           metadados do plugin
 commands/NC-CMD-EXAMPLE.md          template de comando
 hooks/NC-HK-EXAMPLE.py              template de hook
 README.md                           instrues de uso
 tests/test_example.py               template de teste

scripts/NC-SCR-FR-012-new-tool.py       scaffolding script (raiz scripts/)
```

### plugin.json obrigatrio
```json
{
  "name": "NC-TOOL-FR-XXX-example",
  "version": "0.1.0",
  "neocortex_min_version": "1.0.0",
  "hooks": ["PreToolUse", "PostToolUse"],
  "commands": ["example-command"],
  "write_zones": ["DIR-EXAMPLE/"],
  "author": "NeoCortex Agent"
}
```

**Campo `neocortex_min_version`  obrigatrio** (confirmado pela pesquisa  versioning de plugins)

### NC-SCR-FR-012-new-tool.py
Script CLI que recebe nome do tool e gera a estrutura acima:
```
python NC-SCR-FR-012-new-tool.py NC-TOOL-FR-031-my-tool
```
Usa scanner de diretrio (`pathlib.glob`) sem dependncias externas.

### Referncias a ler ANTES de implementar
- `@RES002` seo F (PluginTemplate)  padres validados
- `@SYNTHESIS` seo F
- `@SSOT` para nomear arquivos corretamente

---

## PROTOCOLO DE ENTREGA

Execute as 3 tarefas **em sequncia** (A  B  C), gerando handoff YAML ao final de cada uma.

### Handoff por tarefa
```yaml
# DIR-DS-002-audit-logs/NC-DS-{029|031|033}-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-029  # ou 031, 033
status: PENDING_REVIEW
lines_added: <N>
files_modified:
  - path/to/file.py
summary: |
  Uma linha descrevendo o que foi entregue.
ajustes_aplicados:
  - Backoff exponencial 102040s implementado
  - Classe PersistentWorker com start/stop/pause
```

### Checklist antes de cada handoff (R20 adaptado)
- [ ] Arquivo criado na write_zone correta
- [ ] Nome segue conveno NC-TIPO-SIGLA-NUM
- [ ] Nenhum import de server.py ou sub_server.py
- [ ] Log via `logging.getLogger(__name__)` (no print)
- [ ] Mnimo 80L de cdigo real (no placeholder)
- [ ] Ajustes da @SYNTHESIS aplicados e confirmados no handoff
