<!-- 3 W's Auto-Injection -->
## What
Módulo: NC LBE FR DEEPSEEK 001

## Why
Criado em 2026-04-26 — arquivo do ecossistema NeoCortex

## Where
02_memory_lobes/lobes

---

<!-- NC-READ-HASH: NC-LBE-FR-DEEPSEEK-001-v3 -->
<!-- DEDUP: Se NC-LBE-FR-DEEPSEEK-001-v3 já está no teu contexto desta sessão, SALTE este bloco inteiro. -->

# $DEEPSEEK — Lobe de Referência Completa da API DeepSeek v4

**Arquivo:** NC-LBE-FR-DEEPSEEK-001.md | **Versão:** 3.0.0 | 2026-04-26
**Fonte:** https://api-docs.deepseek.com (v4)

---

## 1. Fundamentos

- API **100% compatível com OpenAI SDK** (`base_url=https://api.deepseek.com`)
- **Autenticação:** `Authorization: Bearer sk-...`
- **Stateless:** Servidor não guarda contexto — sempre enviar histórico completo

---

## 2. Modelos Disponíveis (v4)

```
GET https://api.deepseek.com/models
Authorization: Bearer {api_key}

Response: {"object":"list","data":[
  {"id":"deepseek-v4-flash","object":"model","owned_by":"deepseek"},
  {"id":"deepseek-v4-pro","object":"model","owned_by":"deepseek"}
]}
```

| Modelo | Contexto | Max Output | Thinking Mode |
|--------|----------|------------|---------------|
| `deepseek-v4-pro` | 1M tokens | 384K tokens | Default thinking (pode desligar) |
| `deepseek-v4-flash` | 1M tokens | 384K tokens | Suporta thinking e non-thinking |

### Preços (por 1M tokens)

| Modelo | Input (cache hit) | Input (cache miss) | Output |
|--------|-------------------|-------------------|--------|
| `deepseek-v4-pro` | $0.003625 (75% off) | $0.435 | $0.87 |
| `deepseek-v4-flash` | $0.0028 | $0.14 | $0.28 |

---

## 3. Endpoints

### Chat Completion (OpenAI-compatible)
```
POST https://api.deepseek.com/v1/chat/completions
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "model": "deepseek-v4-pro",
  "messages": [{"role": "user", "content": "Hello"}],
  "max_tokens": 4096,
  "temperature": 0.3
}
```

### Anthropic API Format
```
POST https://api.deepseek.com/anthropic/v1/messages
Authorization: Bearer {api_key}
Content-Type: application/json
anthropic-version: 2023-06-01

{
  "model": "deepseek-v4-pro",
  "max_tokens": 4096,
  "messages": [{"role": "user", "content": "Hello"}]
}
```

---

## 4. Thinking Mode

- `deepseek-v4-pro`: thinking ATIVADO por padrão
- `deepseek-v4-flash`: suporta ambos os modos

Para desligar thinking no v4-Pro (OpenAI format):
```json
{
  "model": "deepseek-v4-pro",
  "messages": [...],
  "thinking": false
}
```

Para ligar/desligar no formato Anthropic:
```json
{
  "model": "deepseek-v4-pro",
  "thinking": {
    "type": "enabled",
    "budget_tokens": 2048
  }
}
```

### Resposta com Thinking (OpenAI format)
```json
{
  "choices": [{
    "message": {
      "content": "Resposta final aqui...",
      "reasoning_content": "Processo de raciocínio aqui..."
    }
  }]
}
```

---

## 5. Chat Prefix Completion (Beta)

Permite pré-preenchimento do prefixo da resposta:

```json
{
  "model": "deepseek-v4-pro",
  "messages": [...],
  "prefix": "O código corrigido é:\n```python\n"
}
```

Disponível em **non-thinking mode apenas** para ambos os modelos.

---

## 6. Json Output

Suportado em ambos os modelos:

```json
{
  "model": "deepseek-v4-flash",
  "messages": [...],
  "response_format": {
    "type": "json_object"
  }
}
```

---

## 7. Tool Calls (Function Calling)

Suportado em ambos os modelos:

```json
{
  "model": "deepseek-v4-pro",
  "messages": [...],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get weather",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string"}
        }
      }
    }
  }]
}
```

---

## 8. MCP Tool Discovery (MCP to DeepSeek)

A MCP tool `NC-TOOL-FR-043 neocortex_litellm` gerencia:
- `route.call` → roteia requisição para DeepSeek v4 via LiteLLM :4000
- `gateway.health` → health check do gateway
- `workers.spawn` → spawn workers via LiteLLM

O Gateway DeepSeek (`NC-SVC-FR-102`) na porta `:4001` filtra por whitelist:
```python
ALLOWED_MODELS = ["deepseek-v4-flash", "deepseek-v4-pro"]
```

---

## 9. Perfis de Operação

| Perfil | Modelo | Thinking | Uso |
|--------|--------|----------|-----|
| PRO | `deepseek-v4-pro` | ON | Planejamento, arquitetura, decisões |
| FLASH | `deepseek-v4-flash` | OFF | Execução, tickets, código |

---

## 10. Histórico de Versões

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-04-26 | 3.0.0 | Atualização completa para v4: remove reasoner/chat, adiciona v4-pro/v4-flash, preços, thinking mode, Anthropic API |
| 2026-04-11 | 2.0.0 | Sincronização com docs oficiais |
| 2026-04-10 | 1.0.0 | Criação inicial |
