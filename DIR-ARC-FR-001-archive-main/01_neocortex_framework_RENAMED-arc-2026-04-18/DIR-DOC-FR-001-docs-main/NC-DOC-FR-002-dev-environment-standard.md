# NC-DOC-FR-002  Padro de Ambiente de Desenvolvimento NeoCortex
# Criado: 2026-04-13 | Verso: 1.0

## 1. Estado Real do Ambiente (2026-04-13)

| Ferramenta | Status | Verso |
|---|---|---|
| Python |  INSTALADO | 3.12.10 |
| ruff |  INSTALADO | 0.15.10 |
| fastmcp / mcp |  INSTALADO | presente |
| cachetools |  INSTALADO | presente |
| ruamel.yaml |  INSTALADO | presente |
| platformdirs |  INSTALADO | presente |
| rich |  INSTALADO | presente |
| notifypy |  NO VERIFICADO |  |
| pytest |  NO VERIFICADO |  |
| bandit |  NO INSTALADO |  |
| pyright |  NO INSTALADO |  |
| pre-commit |  NO INSTALADO |  |
| uv |  NO INSTALADO |  |

---

## 2. Toolchain Recomendado 2025 (Pesquisa)

### Camada 1  Qualidade de Cdigo (CRTICA)
| Ferramenta | Papel | Instalao |
|---|---|---|
| **ruff** | Lint + Formatao + isort (substitui flake8+black+isort) | `pip install ruff` |
| **pyright** | type checking esttico (substitui mypy) | `pip install pyright` |
| **bandit** | segurana (detecta senhas hardcoded, shell injection, etc.) | `pip install bandit` |

### Camada 2  Testes (CRTICA)
| Ferramenta | Papel | Instalao |
|---|---|---|
| **pytest** | testes unitrios e integrao | `pip install pytest pytest-cov` |
| **pytest-cov** | cobertura de cdigo | includo acima |

### Camada 3  Automao (ALTA)
| Ferramenta | Papel | Instalao |
|---|---|---|
| **pre-commit** | roda lint/testes a cada `git commit` automaticamente | `pip install pre-commit` |

### Camada 4  Gesto de Deps (MDIA  Fase 2)
| Ferramenta | Papel | Instalao |
|---|---|---|
| **uv** | substitui pip, gerencia venv, muito mais rpido | `pip install uv` |

---

## 3. Ciclo de Vida Obrigatrio de um Arquivo

Cada agente opencode/DeepSeek DEVE executar este ciclo completo:

```
CRIAO  STEP-0  LINT  TYPE CHECK  COMPILE  TESTE  HANDOFF
```

### STEP-0: Verificar Ambiente
```powershell
python --version                    # deve ser 3.8+
python -m ruff --version 2>&1       # verificar se ruff disponvel
python -m pytest --version 2>&1     # verificar se pytest disponvel
```

### STEP-1: Aps Criar/Modificar Arquivo
```powershell
# Compile check (SEMPRE  stdlib, sem deps externas)
python -m py_compile ARQUIVO.py

# Lint + auto-fix (se ruff disponvel)
python -m ruff check --fix ARQUIVO.py
python -m ruff format ARQUIVO.py

# Type check (se pyright disponvel)
python -m pyright ARQUIVO.py 2>&1
```

### STEP-2: Testes
```powershell
# Teste unitrio do arquivo (se existir)
python -m pytest tests/test_NOME.py -v 2>&1

# Teste de import (sempre  verifica que o mdulo carrega)
python -c "import importlib.util, sys
spec = importlib.util.spec_from_file_location('mod', 'ARQUIVO.py')
mod = importlib.util.module_from_spec(spec)
print('Import OK:', 'mod')"
```

### STEP-3: Segurana (se bandit disponvel)
```powershell
python -m bandit -r ARQUIVO.py --severity-level medium 2>&1
```

### STEP-4: Handoff
S gerar handoff YAML com `status: PENDING_REVIEW` aps todos os steps acima passarem.
Registrar resultado de cada step no campo `checklist_r20`.

---

## 4. Problemas Identificados no Sprint Atual

| Problema | Impacto | Correo |
|---|---|---|
| Nenhum agente rodou py_compile | Erros de sintaxe poderiam passar despercebidos | Ciclo obrigatrio nos prompts |
| Nenhum agente rodou ruff | 16 erros de import encontrados depois | ruff --fix aps entrega |
| ruff assumido como instalado | Falha silenciosa no ambiente | STEP-0 de verificao |
| Sem testes unitrios | Cdigo funciona em teoria, no comprovado | Prxima fase: pytest |
| Sem pre-commit hooks | Commits sujos sem validao | Instalar pre-commit |

---

## 5. Instalao Imediata Recomendada

```powershell
# No diretrio do projeto:
pip install pytest pytest-cov bandit pyright pre-commit

# Setup pre-commit (aps instalar):
pre-commit install
```

### `.pre-commit-config.yaml` (criar na raiz do projeto):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.10
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.9
    hooks:
      - id: bandit
        args: ["-r", ".", "--severity-level", "MEDIUM"]
        exclude: "^05_examples/|^DIR-ARC-FR-001-archive-main/"
```

---

## 6. Template STEP-0 para Prompts de Agente (OBRIGATRIO)

Inserir no incio de TODOS os prompts enviados para opencode/DeepSeek:

```markdown
## STEP-0  VERIFICAR AMBIENTE ANTES DE QUALQUER CDIGO

Execute e cole o resultado no handoff campo `errors:` se falhar:

1. python --version
2. python -m ruff --version 2>&1
3. python -m pytest --version 2>&1

Ao criar/modificar CADA arquivo:
4. python -m py_compile ARQUIVO.py
5. python -m ruff check --fix ARQUIVO.py (se ruff disponvel)
6. python -c "import importlib.util; spec=importlib.util.spec_from_file_location('x','ARQUIVO.py'); m=importlib.util.module_from_spec(spec); print('OK')"

SE py_compile FALHAR  PARE. No gere handoff. Corrija e repita.
SE ruff falhar sem --fix  reporte em warnings: do handoff.
```

---

## 7. Prximos Passos

- [ ] Instalar pytest, bandit, pyright no ambiente global
- [ ] Criar `.pre-commit-config.yaml` na raiz do projeto
- [ ] Criar testes unitrios mnimos (1 por arquivo core) em `05_examples/tests/`
- [ ] Adicionar STEP-0 a TODOS os prompts futuros (DS-004, DS-005, DS-006 atualizados )
- [ ] Criar NC-SCR-FR-013-validate-file.py: script que roda o ciclo completo em 1 comando
