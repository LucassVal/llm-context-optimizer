# NC-PROMPT-DS-019  PIC-002: Config PicoClaw com NeoCortex MCP + DeepSeek
<!-- Agente: B | Porta: 44624 | Ticket: PIC-002 | Data: 2026-04-13 -->

## GOAL
Crie o arquivo de configurao completo do PicoClaw para o ambiente NeoCortex: gateway na porta 18790, DeepSeek como LLM, NeoCortex via MCP stdio, exec habilitado, web search via DuckDuckGo. O arquivo deve ser funcional e pronto para uso.

## STEP-0 (OBRIGATRIO  execute primeiro)
```powershell
python --version
python -m ruff --version
Test-Path "C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\server.py"
```
Reporte exatamente o que retornou. Se falhar, pare.

## LOCKS (@LOCKS  NO TOQUE)
- server.py, sub_server.py, neocortex_config.yaml, NC-NAM-FR-001
- No modifique o neocortex_config.yaml existente

## WRITE ZONE
- `DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json` (arquivo principal)
- Se o arquivo j existir do PIC-001, ATUALIZE-O com o contedo completo

## CONTEXTO
- Lobe de referncia obrigatrio: NC-LBE-INT-001-picoclaw-architecture.mdc (Seo 7  Config Completa)
- Lobe de referncia: NC-LBE-INT-002-opencode-architecture.mdc (Seo 4  MCP)
- PYTHONPATH do NeoCortex: `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42`
- DeepSeek API key: leia de PYTHONPATH\neocortex_config.yaml (campo: deepseek_api_key)
- Portas OpenCode ativas: 59520, 44624, 32763 (NO reinicie)

## TAREFA: Config Final

Crie `DIR-DS-000-agent-config\NC-CFG-PIC-001-picoclaw-config.json` com:

```json
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18790,
    "log_level": "info",
    "public": false
  },
  "model_list": [
    {
      "model_name": "deepseek-v3",
      "model": "deepseek/deepseek-v3",
      "api_key": "<SUBSTITUIR_PELA_KEY_DO_neocortex_config.yaml>"
    }
  ],
  "agents": {
    "defaults": {
      "model_name": "deepseek-v3",
      "temperature": 0.7,
      "max_tokens": 4096
    }
  },
  "tools": {
    "exec": {
      "enabled": true,
      "enable_deny_patterns": true,
      "custom_deny_patterns": []
    },
    "web": {
      "enabled": true,
      "duckduckgo": {
        "enabled": true,
        "max_results": 5
      }
    },
    "cron": {
      "enabled": false
    },
    "mcp": {
      "enabled": true,
      "discovery": {
        "enabled": true,
        "ttl": 5,
        "max_search_results": 5,
        "use_bm25": true
      },
      "servers": {
        "neocortex": {
          "enabled": true,
          "command": "python",
          "args": ["-m", "neocortex.mcp.server"],
          "env": {
            "PYTHONPATH": "C:\\Users\\Lucas Valrio\\Desktop\\TURBOQUANT_V42",
            "PYTHONUTF8": "1"
          }
        }
      }
    }
  },
  "security": {
    "filter_sensitive_data": true,
    "filter_min_length": 8
  }
}
```

**ATENO:** Leia o valor real de `deepseek_api_key` em `neocortex_config.yaml` e substitua no config. No deixe placeholder.

## Validao
```powershell
# Verificar JSON vlido
python -c "import json; json.load(open('DIR-DS-000-agent-config/NC-CFG-PIC-001-picoclaw-config.json'))"
echo "JSON OK: $LASTEXITCODE"
```

## HANDOFF TEMPLATE
```yaml
ticket_id: PIC-002
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 44624
files_modified:
  - DIR-DS-000-agent-config/NC-CFG-PIC-001-picoclaw-config.json
summary: |
  Config PicoClaw criada com gateway :18790, DeepSeek-v3, NeoCortex MCP stdio,
  exec habilitado, DuckDuckGo search. API key substituda (no exposta no handoff).
metrics:
  json_valid: true
  api_key_substituted: true
  mcp_neocortex_configured: true
  write_zone_respected: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  handoff_yaml_complete: true
```

Salve em: `DIR-DS-002-audit-logs/PIC-002-handoff-{YYYYMMDD-HHMMSS}.yaml`
