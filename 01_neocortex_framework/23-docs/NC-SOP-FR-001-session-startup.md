# NC-SOP-FR-001 — Session Startup SOP
# @SOP — Standard Operating Procedure para início de sessão
# Hash: SOP-v1.0-20260427

> **Regra R16:** Toda sessão inicia carregando @BOOT e executando este SOP.

## 1. CICLO 0 — Verificação MCP (obrigatório)

```bash
# Verificar se o MCP server está rodando
netstat -ano | findstr ":8766" | findstr "LISTENING"

# Se não estiver, iniciar:
start "NeoCortex-MCP" /min python -m neocortex.mcp.server --transport sse --port 8766

# Ou usar o launcher:
C:\TQ\NC-SCR-FR-104-neocortex-launcher.bat
```

## 2. OpenCode MCP Config

Arquivo: `~\.config\opencode\opencode.jsonc`
```json
{
  "mcp": {
    "neocortex": {
      "type": "remote",
      "url": "http://localhost:8766/sse",
      "enabled": true,
      "timeout": 60000
    }
  }
}
```

## 3. Verificações pós-conexão

1. No TUI do OpenCode, confirmar que MCP está verde (20 tools)
2. Rodar `bootup.sync` para carregar estado atual
3. Rodar `regression.check` para ver STEP 0 buffer
4. Rodar `compliance.report` para ver score

## 4. Carregar contexto da sessão anterior

1. `checkpoint.list` — ver último checkpoint
2. `@ROADMAP` — ver tickets pendentes
3. `@BOOT` — ver frentes ativas e estado do sistema

## 5. Iniciar trabalho

1. Criar handoff: `handoff.create(title="retomada", description="...")`
2. Executar tarefas seguindo @ROADMAP
3. A cada arquivo modificado: ruff check + py_compile + checkpoint
4. Ao fim: `bootup.sync` + `compliance.report` + `checkpoint.set`

## Portas de referência

| Serviço | Porta | Status típico |
|---------|-------|---------------|
| MCP SSE | 8766 | Deve estar LISTENING |
| LiteLLM | 4000 | Scheduled task |
| PicoClaw | 18790 | Scheduled task |
| Ollama | 11434 | Windows service |
| Mission Control | 3000 | Não disponível |
