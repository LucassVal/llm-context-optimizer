# NC-STEP-0  Padro OBRIGATRIO de Verificao de Ambiente
# Verso: 2.0 | Data: 2026-04-13
# INSERIR no incio de TODOS os prompts enviados para agentes opencode/DeepSeek

---

## STEP-0  EXECUTE ANTES DE QUALQUER COISA (OBRIGATRIO)

```powershell
# === 1. VERIFICAR PYTHON ===
python --version
# Esperado: Python 3.12.x

# === 2. VERIFICAR FERRAMENTAS DE QUALIDADE ===
python -m ruff --version 2>&1
python -m pytest --version 2>&1
python -m bandit --version 2>&1

# === 3. VERIFICAR DEPENDNCIAS CRTICAS DO PROJETO ===
python -c "
deps = ['mcp', 'fastmcp', 'ruamel', 'rich', 'cachetools', 'platformdirs',
        'notifypy', 'diskcache', 'duckdb', 'tantivy', 'msgspec',
        'psutil', 'pystray', 'yaml', 'jsonschema', 'aiohttp']
import importlib
for d in deps:
    try:
        importlib.import_module(d)
        print(f'  OK  {d}')
    except ImportError as e:
        print(f'  ERR {d}: {e}')
" 2>&1

# === 4. VALIDAO POR ARQUIVO (aps criar/modificar) ===
# Passo 4a: Sintaxe Python
python -m py_compile ARQUIVO.py

# Passo 4b: Lint + auto-fix Python
python -m ruff check --fix ARQUIVO.py
python -m ruff check ARQUIVO.py   # confirmar 0 erros

# Passo 4c: Import smoke test Python
python -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('mod', 'ARQUIVO.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['mod'] = mod
try:
    spec.loader.exec_module(mod)
    print('Import OK')
except Exception as e:
    print(f'Import ERR: {e}')
" 2>&1

# Passo 4d: Sintaxe PowerShell (.ps1)  OBRIGATORIO antes de qualquer entrega
$erros = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile(
    'ARQUIVO.ps1', [ref]$null, [ref]$erros)
if ($erros) { $erros | ForEach-Object { "ERR: $_" } } else { 'Syntax OK' }
# ARMADILHAS PS1 (QUAL-005 a QUAL-008):
# - @NOME: em double-quoted  drive var   usar single-quote '...'
# - [ ] em double-quoted     array idx   usar single-quote '...'
# - "@ de here-string        coluna 0    sem espao antes
# - cd 'path com espaco'    usar Set-Location "path"
```

## RESULTADO ESPERADO (ground truth 2026-04-13)

| Dependncia | Status | Verso Instalada |
|---|---|---|
| Python | OK | 3.12.10 |
| ruff | OK | 0.15.10 |
| pytest | OK | 9.0.3 |
| bandit | OK | 1.9.4 |
| mcp | OK | 1.27.0 |
| fastmcp | OK | 3.2.3 |
| ruamel.yaml | OK | 0.19.1 |
| rich | OK | 14.2.0 |
| cachetools | OK | 6.2.4 |
| platformdirs | OK | 4.5.0 |
| notifypy | OK | 0.3.42 |
| diskcache | OK | 5.6.3 |
| duckdb | OK | 1.5.1 |
| msgspec | OK | 0.21.0 |
| psutil | OK | 7.2.0 |
| PyYAML | OK | 6.0.3 |
| jsonschema | OK | 4.26.0 |
| aiohttp | OK | 3.13.3 |

## SE ALGUMA DEPENDNCIA FALHAR

```powershell
# Instalar o que faltar:
pip install notify-py ruamel.yaml rich cachetools platformdirs diskcache duckdb msgspec
```

## REGRAS R09 (imports com hfen  CRTICO)

NUNCA:
```python
import NC-SVC-FR-005-event-bus  # ERRO  hfens impedem import normal
from NC_HK_FR_001_hook_registry import ...  # ERRO  R09 violation
```

SEMPRE:
```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "event_bus",
    Path(__file__).parent / "NC-SVC-FR-005-event-bus.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules["event_bus"] = mod
spec.loader.exec_module(mod)
```
