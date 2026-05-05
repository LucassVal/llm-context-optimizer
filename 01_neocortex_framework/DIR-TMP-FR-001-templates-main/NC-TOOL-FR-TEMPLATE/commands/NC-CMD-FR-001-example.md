# NC-CMD-EXAMPLE  Comando de Exemplo

> Template de documentao para comandos de plugins do NeoCortex.

## Nome do Comando

`examplecommand`

## Descrio

Breve descrio do que o comando faz, qual problema resolve e em qual contexto deve ser usado.

## Sintaxe

```bash
neocortex examplecommand [--option value] <argument>
```

## Parmetros

| Parmetro | Obrigatrio? | Descrio | Exemplo |
|---|---|---|---|
| `--option` | Opcional | Explicao da opo. | `--option foo` |
| `argument` | Obrigatrio | Explicao do argumento posicional. | `input.txt` |

## Exemplos de Uso

```bash
# Exemplo bsico
neocortex examplecommand --option value meu_arquivo.yaml

# Exemplo sem opes
neocortex examplecommand input.json
```

## Integrao com Hooks

Este comando pode disparar os seguintes hooks:

- **PreToolUse**: antes de executar o comando.
- **PostToolUse**: aps execuo bemsucedida.
- **ToolError**: se ocorrer um erro durante a execuo.

## Permisses

- **Write zones**: `DIREXAMPLE/` (conforme plugin.json)
- **Forbidden zones**: `server.py`, `sub_server.py`, `NCNAMFR001*` (@LOCKS)

## Cdigofonte

O cdigo do comando deve residir em um arquivo Python com o nome do tool, seguindo o padro `NCTOOLFRXXX*.py`.

---

**Nota:** Este arquivo  um template. Substitua o contedo conforme o comando real.