# NCTOOLFRTEMPLATE  Template de Plugin para NeoCortex

Este diretrio contm a estrutura padro para criar um novo plugin (tool) para o NeoCortex.
Use o script `NCSCRFR012newtool.py` para gerar uma cpia personalizada deste template.

## Estrutura de Arquivos

```
NCTOOLFRTEMPLATE/
 NCCFGFR001plugin.json          # Metadados do plugin
 commands/
    NCCMDEXAMPLE.md              # Template de documentao de comando
 hooks/
    NCHKEXAMPLE.py               # Template de hook (PreToolUse, PostToolUse, ToolError)
 tests/
    test_example.py                # Template de teste unitrio
 README.md                          (este arquivo)
```

## Passo a Passo para Criar um Novo Plugin

1. **Execute o scaffolding script:**
   ```bash
   python scripts/NCSCRFR012newtool.py NCTOOLFR031meuplugin
   ```
   Isso criar uma cpia do template com o nome fornecido.

2. **Ajuste os metadados** em `NCCFGFR001plugin.json`:
   - `name`: nome completo do plugin (deve coincidir com o nome do diretrio)
   - `version`: verso semntica inicial (ex.: `0.1.0`)
   - `neocortex_min_version`: verso mnima do NeoCortex requerida
   - `hooks`: lista de eventos que o plugin responde (PreToolUse, PostToolUse, ToolError)
   - `commands`: lista de comandos CLI que o plugin adiciona
   - `write_zones`: diretrios onde o plugin tem permisso de escrita

3. **Implemente a funcionalidade principal** em um arquivo Python no diretrio apropriado
   (normalmente `neocortex/mcp/tools/`). O nome do arquivo deve seguir o padro `NCTOOLFRXXX*`.

4. **Documente cada comando** em `commands/NCCMD*.md`.

5. **Escreva hooks** em `hooks/NCHK*.py` (opcional).

6. **Adicione testes** em `tests/`.

7. **Registre o plugin** no sistema:
   - Plugins locais: coloque o diretrio do plugin em `.nc/plugins/` (autodiscovery via scanner).
   - Plugins externos: use entry points do setuptools (`neocortex.plugins`).

## Campos Obrigatrios no plugin.json

| Campo | Tipo | Descrio |
|---|---|---|
| `name` | string | Nome do plugin (ex.: `NCTOOLFR031meuplugin`) |
| `version` | string | Verso semntica (`MAJOR.MINOR.PATCH`) |
| `neocortex_min_version` | string | **Obrigatrio**  verso mnima do NeoCortex compatvel |
| `hooks` | array | Lista de eventos suportados (`PreToolUse`, `PostToolUse`, `ToolError`) |
| `commands` | array | Lista de comandos CLI que o plugin adiciona |
| `write_zones` | array | Diretrios onde o plugin pode escrever (ex.: `["DIREXAMPLE/"]`) |

## Exemplo de Uso do HookRegistry

Se o plugin define hooks, eles podem ser registrados manualmente ou via YAML:

```python
from neocortex.core.hooks import hook_registry
from .hooks import meu_hook

hook_registry.register("PreToolUse", meu_hook, timeout=2.0)
```

Ou via arquivo YAML `.nc/hooks/meuplugin.yaml`:

```yaml
hooks:
  - event: PreToolUse
    module: meu_plugin.hooks
    function: meu_hook
    timeout: 2.0
```

## Testes

O template inclui um esqueleto de teste unitrio. Execute com:

```bash
pytest tests/ -v
```

## Licena

Este template  parte do projeto NeoCortex e segue a mesma licena do projeto principal.
Substitua esta seo pela licena do seu plugin, se diferente.