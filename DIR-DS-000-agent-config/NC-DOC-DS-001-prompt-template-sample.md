# NC-DOC-DS-001  Sample Prompt Cannico (Template Agente T1)
<!-- SSOT: Modelo oficial de prompt para agentes NeoCortex T1 (DeepSeek via OpenCode) -->
<!-- Verso: 1.0 | Data: 2026-04-13 | Governa: todos NC-PROMPT-DS-* -->

> **Use este arquivo como base ao criar qualquer novo NC-PROMPT-DS-XXX.**
> Cada seo  OBRIGATRIA. Adapte o contedo, nunca remova as sees.

---

```markdown
# NC-PROMPT-DS-XXX  Agent Prompt: NC-DS-NNN + NC-DS-MMM
# Verso: 1.0 | Data: YYYY-MM-DD | Template: Brockman v1
# Despachar para: 1 agente opencode livre

---

##  GOAL

[O QUE implementar  seja especfico e sem ambiguidade]
- **NC-DS-NNN:** `NC-TIPO-SIGLA-NUM-nome.py`  [descrio 1 linha]
- **NC-DS-MMM:** `NC-TIPO-SIGLA-NUM-nome.py`  [descrio 1 linha]

Zona de escrita: `01_neocortex_framework/neocortex/[subpasta]/`
Restrio ABSOLUTA: NO modificar `server.py`, `sub_server.py` (@LOCKS).

[Adicionar: Test-Path para confirmar que os arquivos NO existem ainda:]
Test-Path "caminho\do\arquivo.py"   # deve retornar False

---

##  RETURN FORMAT

Ao concluir, produzir **N handoff YAMLs** em `DIR-DS-002-audit-logs/`:

NC-DS-NNN-handoff-{YYYYMMDD-HHMMSS}.yaml

Cada YAML DEVE conter exatamente:

ticket_id: NC-DS-NNN
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: {porta desta sesso}
lines_added: <N real  conte as linhas}
files_modified:
  - caminho/relativo/ao/arquivo.py
summary: |
  <1-3 linhas descrevendo o que foi implementado>
metrics:
  lines_real: <N>
  files_created: <N>
  ruff_check: PASS
  py_compile: PASS
  dependencies_used: []   # apenas stdlib ou lista de deps validadas
  write_zone_respected: true
  locks_respected: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  min_80_lines: true
  no_locked_files_modified: true
  handoff_yaml_complete: true

---

##  WARNINGS  STEP-0 OBRIGATRIO (execute ANTES de qualquer cdigo)

# 1. Python disponvel?
python --version   # esperado: 3.12.x

# 2. Ferramentas de qualidade?
python -m ruff --version
python -m pytest --version

# 3. Dependncias instaladas? (ground truth 2026-04-13)
python -c "
deps = ['mcp','fastmcp','ruamel','rich','cachetools','platformdirs',
        'notifypy','diskcache','duckdb','msgspec','psutil','yaml']
import importlib
for d in deps:
    try: importlib.import_module(d); print(f'OK  {d}')
    except ImportError as e: print(f'ERR {d}: {e}')
"

# 4. Aps criar/modificar cada arquivo:
python -m py_compile ARQUIVO.py                  # sintaxe OK?
python -m ruff check --fix ARQUIVO.py            # lint + auto-fix
python -m ruff check ARQUIVO.py                  # confirmar 0 erros

REGRA R21: Se py_compile falhar  PARE. Se dep faltar  instale antes de avanar.
Consulte: .agents/rules/NC-RULE-006-no-assumptions.mdc

Evitar SEMPRE:
- print() em qualquer lugar  logger = logging.getLogger(__name__)
- Import de mdulo com hfen  importlib.util.spec_from_file_location (R09)
- Hardcode de paths  get_config()
- Deps externas fora das 12 validadas (stdlib  sempre OK)
- Arquivos abaixo de 80 linhas de cdigo real

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP Framework em C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\
SSOT: 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md
Roadmap sprint: 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-DS-001-roadmap-pre-mcp.md
Regras: .agents/rules/neocortexrules.md (R21  a regra mais crtica)
Lobe desta frente: [NC-LBE-DS-XXX  caminho do lobe se existir]

[Adicionar contexto especfico da tarefa:]
- Arquivos de referncia que o agente deve ler antes de codificar
- Dependncias entre servios (ex: EventBus existente, Session-Buddy)
- Interface mnima esperada (se outro servio j depende deste)
- Sprint context: [o que este ticket desbloqueia no roadmap]

---

## TAREFA A  NC-DS-NNN: [Nome do Servio/Util]

Ticket: NC-DS-NNN
Arquivo: caminho/NC-TIPO-FR-NUM-nome.py
Esforo: ~NL linhas

### Interface mnima obrigatria:

[Cole aqui a assinatura completa da classe/funes esperadas  no deixe vago]

class NomeDoServico:
    """Docstring obrigatria."""
    
    def metodo_principal(self, param: Tipo) -> TipoRetorno:
        """Docstring."""
        ...
    
    def get_X(self) -> Dict:
        """Retorna [o qu]."""
        ...

def get_nome_do_servico() -> NomeDoServico:
    """Singleton."""
    ...

### Restries especficas:
- [Thread-safe se necessrio: threading.Lock/RLock]
- [Singleton obrigatrio: padro __new__ ou _instance]
- [Import de mdulos com hfen via importlib (R09)]
- [Deps externas: apenas as 12 validadas ou stdlib]

---

## TAREFA B  NC-DS-MMM: [Nome]

[Repetir estrutura da Tarefa A]

---

## PROTOCOLO DE ENTREGA

1. Implemente Tarefa A  py_compile + ruff (0 erros)  confirme
2. Implemente Tarefa B  py_compile + ruff (0 erros)  confirme
3. Gere N handoff YAMLs em DIR-DS-002-audit-logs/
4. NO modifique nada alm dos N arquivos + N YAMLs

Se dep ausente  registre em warnings do YAML, no trave.
Se arquivo j existir  leia antes de sobrescrever, reporte no summary.
```

---

## Checklist de Reviso (T0 usa ao auditar handoffs)

Ao receber um handoff YAML do agente, T0 verifica:

- [ ] `status: PENDING_REVIEW` presente?
- [ ] `ruff_check: PASS` e `py_compile: PASS`?
- [ ] `lines_real`  80?
- [ ] `no_print_statements: true`?
- [ ] `naming_convention: true`?
- [ ] Arquivo realmente existe em disco?
- [ ] Nenhum @LOCK foi modificado?
- [ ] Handoff YAML segue `NC-DS-NNN-handoff-YYYYMMDD-HHMMSS.yaml`?

Se tudo OK  muda `status` para `APPROVED` e registra no @SSOT.
Se falha  devolve ao agente com feedback no YAML.

---

## Changelog

- [2026-04-13] Criado  T0 Antigravity. Template cannico v1 com Brockman (GOAL/RETURN FORMAT/WARNINGS/CONTEXT DUMP) + STEP-0 v2 + protocolo de entrega + checklist de reviso T0.
