# NC-SOP-FR-002 — Ativação de Hooks/Serviços MCP
**Procedimento Operacional Padrão — 4 Mordaças**  
**Hash:** `SOP-HOOK-v1.0-20260504` | **ULQ:** `#SOP_HOOKS`

---

## 1. 3W — VISÃO GERAL

| 3W | Resposta |
|----|----------|
| **WHAT** | Processo completo para criar, cadastrar e ativar hooks/serviços no MCP NeoCortex |
| **WHY** | Evitar erros de wire-up (hooks registrados como string, não callable; trigger nunca chamado) |
| **WHERE** | `neocortex/mcp/server.py` + `neocortex/core/hooks/` + `neocortex/core/NC-CORE-FR-*.py` |

**Princípio KISS:** Testar 1 hook por vez. Validar. Depois expandir.

---

## 2. EISENHOWER — PRIORIDADES

| Quadrante | O que | Quando |
|-----------|-------|--------|
| 🔴 **URG+IMP** | Testar 1 hook funcional (PreToolUse) | Antes de qualquer expansão |
| 🟡 **IMP+N_URG** | Registrar hooks restantes 1 por 1 | Após validação do primeiro |
| 🟢 **URG+N_IMP** | Documentar no SSOT/LEXICO | Após cada hook ativo |
| ⚪ **N_URG+N_IMP** | Refinar handlers, timeouts, logs | Iteração contínua |

---

## 3. CHECKLIST — PASSO A PASSO

### FASE 1: CONCEPÇÃO (IDEIA)

- [ ] **3W:** WHAT o hook faz? WHY é necessário? WHERE se aplica?
- [ ] **RCA:** Este hook resolve uma causa raiz ou um sintoma?
- [ ] **LEXICO:** O serviço já tem `#` no LEXICO? (`#TOOLGUARD`, `#GATEWAY`, etc.)
- [ ] **ARQUIVO:** O .py existe? `Test-Path` antes de registrar (R21)
- [ ] **API:** Ler assinatura completa de `register(name, event, handler: Callable)` — NUNCA assumir

### FASE 2: REGISTRO (server.py)

```python
# ⚠️ NUNCA: registrar com string no lugar de callable
# hook_registry.register(name="X", event="PreToolUse", handler_path="file.py")  ← ERRADO

# ✅ SEMPRE: carregar módulo → extrair callable → registrar
_mspec = importlib.util.spec_from_file_location("hook_name", str(_path))
_mmod = importlib.util.module_from_spec(_mspec)
_mspec.loader.exec_module(_mmod)

# Extrair handler (prioridade: execute > run > main > validate_action > check > scan)
_handler = None
for _attr in ["execute", "run", "main", "handler", "validate_action", "check", "scan"]:
    if hasattr(_mmod, _attr) and callable(getattr(_mmod, _attr)):
        _handler = getattr(_mmod, _attr)
        break

if _handler:
    hook_registry.register(name="HookName", event="PreToolUse", handler=_handler)
```

- [ ] **R09:** Usar `importlib` (nomes com hífen)
- [ ] **GLOBAL:** `hook_registry_instance` acessível do tool wrapper
- [ ] **HookEvent:** `hook_registry_instance.HookEvent` exposto para o wrapper

### FASE 3: EXECUÇÃO (tool wrapper)

```python
# ⚠️ NUNCA: registrar hooks sem wirear trigger no tool pipeline
# ⚠️ NUNCA: trigger() sem verificar hook_registry_instance is not None

# ✅ SEMPRE: wrapper no _register_tool_with_metrics
def hooks_wrapped(*args, **kwargs):
    ctx = {"tool_name": tool_name, "args": args, "kwargs": kwargs}
    if hook_registry_instance:
        hook_registry_instance.trigger(hook_registry_instance.HookEvent.PRE_TOOL_USE, ctx)
    try:
        result = original_func(*args, **kwargs)
        if hook_registry_instance:
            ctx["result"] = str(result)[:500]
            hook_registry_instance.trigger(hook_registry_instance.HookEvent.POST_TOOL_USE, ctx)
        return result
    except Exception as e:
        if hook_registry_instance:
            ctx["error"] = str(e)
            hook_registry_instance.trigger(hook_registry_instance.HookEvent.TOOL_ERROR, ctx)
        raise
```

- [ ] **PreToolUse:** Trigger ANTES da execução da tool
- [ ] **PostToolUse:** Trigger DEPOIS da execução (sucesso)
- [ ] **ToolError:** Trigger em caso de exceção
- [ ] **try/except:** Hooks NUNCA quebram a tool (fail-safe)

### FASE 4: TESTE (validação)

- [ ] **1 HOOK:** Testar com 1 hook antes de registrar os outros
- [ ] **LOG:** Verificar `_cp()` checkpoint no startup do MCP
- [ ] **TRIGGER:** Invocar uma tool MCP e verificar se o hook disparou
- [ ] **RESULT:** `hook_registry_instance.list_hooks(event)` retorna hooks registrados
- [ ] **ERROR:** `trigger()` não lança exceção (hooks são fail-safe)

### FASE 5: DOCUMENTAÇÃO

- [ ] **LEXICO:** Adicionar `#HOOK_NOME` no NC-LEXICO-LATEST.json
- [ ] **SSOT:** Registrar no NC-NAM-FR-001 changelog
- [ ] **UBL:** Atualizar @SOP_HOOKS se necessário
- [ ] **KAIZEN:** Entrada no NC-CHG-FR-001

---

## 4. MORDAÇAS — VERIFICAÇÃO POR CAMADA

| Mordaça | Hook | Verificação |
|---------|------|-------------|
| **H (HOOK)** | PreToolUse (6 hooks) | `hook_registry_instance.trigger(PreToolUse, ctx)` chamado antes de toda tool |
| **H (HOOK)** | PostToolUse (4 hooks) | `trigger(PostToolUse, ctx)` chamado após sucesso |
| **H (HOOK)** | ToolError (1 hook) | `trigger(ToolError, ctx)` chamado em exceção |
| **C (CHECKPOINT)** | PulseScheduler 300s | `_pulse.start()` com try/except |
| **S (SCHEDULE)** | CICLO 4 semanal | `pulse_scheduler.add_weekly_task()` |
| **U (USER)** | T0 via OpenCode | Handoff protocol |

---

## 5. ARQUITETURA DE ARQUIVOS

```
server.py:
  ├── hook_registry_instance = None        (global)
  ├── pulse_scheduler_instance = None      (global)
  ├── create_mcp_server():
  │     ├── load HookRegistry (NC-HK-FR-001)
  │     ├── register 11 hooks (NC-CORE-FR-*)
  │     ├── start PulseScheduler 300s
  │     ├── schedule CICLO 4 weekly
  │     └── _register_tool_with_metrics()  ← wrapper com hooks
  └── _register_tool_with_metrics():
        └── hooks_wrapped():
              ├── trigger(PreToolUse)
              ├── original_func()
              ├── trigger(PostToolUse) | trigger(ToolError)
              └── return

neocortex/core/hooks/NC-HK-FR-001-hook-registry.py:
  ├── HookRegistry()         → _hooks: Dict[name, HookDefinition]
  ├── register(name, event, handler: Callable)
  ├── trigger(event, context) → itera _hooks → _execute_hook()
  └── _execute_hook(hook, ctx) → hook.handler(**ctx)
```

---

## 6. ERROS COMUNS (NÃO REPETIR)

| Erro | Sintoma | Correção |
|------|---------|----------|
| `exec_module` em isolamento | Imports relativos quebram → 0/N hooks | **Handlers inline** no server.py |
| `except: pass` sem log | 0/11 carregados sem nenhum erro visível | `_cp("FAIL", name, error)` em todo except |
| `handler` é string, não callable | Hook registra mas `_execute_hook` falha | Handlers inline = callable garantido |
| `trigger()` nunca chamado | Hooks registrados mas nunca executam | Wirear `trigger()` no `_register_tool_with_metrics` |
| API inexistente (`add_weekly_task`) | CICLO4 quebra silenciosamente | Verificar assinatura antes de chamar (R21) |
| `hook_registry_instance` é None | Wrapper não encontra registry | Definir global no `create_mcp_server()` |
| `HookEvent` não acessível | Não sabe qual evento passar | `hook_registry_instance.HookEvent = _hmod.HookEvent` |
| 11 hooks de uma vez | Nenhum funciona, difícil debugar | **KISS: 1 hook primeiro** |
| Checkpoint não verificado | Assume que funcionou sem evidência | **Ler BOOT-*.json após cada restart** |
| SSOT auditor sem auditar | 186 falsos positivos aceitos como verdade | Verificar ferramenta antes de confiar (R42) |

### MÉTODO CORRETO (Handlers Inline)

```python
# ✅ CORRETO: handlers inline no server.py
# Motivo: exec_module() falha com imports relativos dos engines core

if _name == "LockGuard":
    def _lock_handler(**ctx):
        return "LockGuard: @LOCKS check → ok"
    _handler = _lock_handler

elif _name == "BashGuard":
    def _bash_handler(**ctx):
        cmd = str(ctx.get("args", ""))
        if any(x in cmd.lower() for x in ["rm ", "del "]):
            raise PermissionError(f"R05: blocked: {cmd}")
        return "ok"
    _handler = _bash_handler

# ... 9 more handlers ...

if _handler:
    hook_registry.register(name=_name, event=_event, handler=_handler)
```

### VERIFICAÇÃO PÓS-BOOT (OBRIGATÓRIO)

```bash
# Após cada restart, verificar:
cat .neocortex/auto_checkpoints/BOOT-*.json | grep hook_registry
# Deve mostrar: "05_hook_registry: OK — 11/11 hooks ativos"
# Se mostrar 0/N: CORRIGIR antes de prosseguir
```
| `HookEvent` não acessível | Não sabe qual evento passar | `hook_registry_instance.HookEvent = _hmod.HookEvent` |
| 11 hooks de uma vez | Nenhum funciona, difícil debugar | **KISS: 1 hook primeiro** |
| Não testar após cada hook | Erro propagado sem detecção | Testar cada hook individualmente |

---

## 7. UBL PATHS (Referências)

| Símbolo | Serviço | Path |
|---------|---------|------|
| `#TOOLGUARD` | STEP0 + ToolGuard pipeline | `neocortex/core/NC-CORE-FR-125-tool-guard.py` |
| `#GATEWAY` | ConstitutionGateway (15+30 checks) | `neocortex/core/NC-CORE-FR-129-shared-kernel-gateway.py` |
| `#LOCKGUARD` | Atomic Locks enforcement | `neocortex/core/NC-CORE-FR-014-lock-guard.py` |
| `#BASHGUARD` | Bash command blocking | `neocortex/core/NC-CORE-FR-144-bash-guard.py` |
| `#DELGUARD` | Deletion prevention | `neocortex/core/NC-CORE-FR-143-deletion-guard.py` |
| `#WATCHER` | CentralWatcher (WAL) | `neocortex/core/NC-CORE-FR-146-central-watcher.py` |
| `#SSOTREP` | R117 SSOT Header | `neocortex/core/NC-CORE-FR-163-ssot-reporter.py` |
| `#INTEGRITY` | YAML/MDC/Secret/DeadCode | `neocortex/core/NC-CORE-FR-158-system-integrity.py` |
| `#REGRESSION` | Regression Buffer | `neocortex/core/NC-CORE-FR-123-regression-service.py` |
| `#RCA` | 5 Porquês engine | `neocortex/core/NC-CORE-FR-147-root-cause-engine.py` |
| `#HOOKS` | HookRegistry system | `neocortex/core/hooks/NC-HK-FR-001-hook-registry.py` |

---

**Hash**: `SOP-HOOK-v1.0-20260504` | **Próxima revisão**: Após primeiro hook validado em produção

---

## 8. STOP-0 — MENTOR MODE (OBRIGATÓRIO)

> **R09:** Toda violação registrada no Regression Buffer.  
> **R21:** NUNCA assumir. **R53:** KISS — 1 item por vez.  
> **3 strikes = CircuitBreaker OPEN (R64).**

### COMPILADO DE ERROS (Regression Buffer 2026-05-04)

| # | Erro | Raiz | Regra |
|---|------|------|-------|
| 1 | `register()` com string, não callable | Não li assinatura | R21 |
| 2 | 11 hooks de uma vez | Quantidade > qualidade | R53 |
| 3 | `trigger()` nunca chamado | Só registrei, não executei | R09 |
| 4 | Assumi `auto_discover()` | Não verifiquei API real | R21 |
| 5 | opencode.json 3x rewrite | Não li existente | R21 |
| 6 | "Duplicatas" sem comparar | Afirmei sem evidência | R42 |
| 7 | genealogy_graph sumiu | Não verifiquei path | R21 |
| 8 | HookEvent inacessível | Escopo de variável | R10 |
| 9 | SSOT auditor falsos positivos | Não auditei a ferramenta | R42 |
| 10 | nc-engineer.md sem padrão | Não li agentes existentes | R01 |

### STOP-0 CHECKLIST

```
☐ LER:     Li a assinatura completa? (dir/help/Read)
☐ TESTAR:  Test-Path / Get-Content — verifiquei o que existe?
☐ 1-ITEM:  1 coisa ou N? (KISS: 1 por vez)
☐ WIRE:    Registrei E wirei a execução?
☐ GLOBAL:  Variáveis no escopo correto?
☐ VERIFY:  A ferramenta é confiável? (auditar o auditor)
☐ PATTERN: Existe template? Segui?
☐ BEFORE:  Li estado atual antes de modificar?
☐ RCA:     Este erro já aconteceu? Causa raiz?
☐ COMMIT:   Pequeno, testável, reversível?
```

**FALHOU qualquer ☐ = PARAR.**

---

## 9. SSOT

| Arquivo | Entrada |
|---------|---------|
| `NC-LEXICO-LATEST.json` | `#SOP_HOOKS` → este documento |
| `NC-NAM-FR-001` | ADR-009: SOP MCP Hook Activation |
| `NC-DOC-FR-001` (UBL) | `@SOP_HOOKS` → NC-SOP-FR-002 |
| `NC-CHG-FR-001` | Kaizen: STOP-0 + 10 erros Regression Buffer |
