<!-- NC-READ-HASH: NC-LBE-FR-DEEPSEEK-001-v2 -->
<!-- DEDUP: Se NC-LBE-FR-DEEPSEEK-001-v2 j est no teu contexto desta sesso, SALTE este bloco inteiro. -->

# $DEEPSEEK  Lobe de Referncia Completa da API DeepSeek

**Arquivo:** NC-LBE-FR-DEEPSEEK-001.md | **Verso:** 2.0.0 | 2026-04-11  
**Fonte:** https://api-docs.deepseek.com (completo)

---

## 1. Fundamentos

- API **100% compatvel com OpenAI SDK** (`base_url=https://api.deepseek.com`)
- **Autenticao:** `Authorization: Bearer sk-...`
- **Stateless:** Servidor no guarda contexto  sempre enviar histrico completo

---

## 2. Modelos Disponveis

```
GET https://api.deepseek.com/models
Authorization: Bearer {api_key}

Response: {"object":"list","data":[
  {"id":"deepseek-chat","object":"model","owned_by":"deepseek"},
  {"id":"deepseek-reasoner","object":"model","owned_by":"deepseek"}
]}
```

| Model | Verso | Context | Melhor para |
|---|---|---|---|
| `deepseek-chat` | DeepSeek-V3.2 | 128K | Chat, cdigo, JSON, Tool Calls |
| `deepseek-reasoner` | DeepSeek-R1 | 128K | Matemtica, lgica, planejamento profundo, CoT |

---

## 3. Parmetros Principais (`/chat/completions`)

| Parmetro | Tipo | Padro | Notas |
|---|---|---|---|
| `model` | string |  | Obrigatrio |
| `messages` | array |  | Obrigatrio  sempre concatenar histrico |
| `temperature` | float | **1.0** | 0.02.0. Ignorado em Thinking Mode |
| `max_tokens` | int |  | Inclui CoT no Thinking Mode (32K default, 64K max) |
| `stream` | bool | false | SSE streaming |
| `top_p` | float | 1.0 | Ignorado em Thinking Mode |
| `response_format` | object |  | `{"type":"json_object"}` |
| `tools` | array |  | Tool calling (ver seo 7) |
| `stop` | string/array |  | Stop sequences |
| `tool_choice` | string/object | `auto` | `auto`, `none`, `required`, ou `{"type":"function","function":{"name":"..."}}` |

### Temperature por Caso de Uso
| Caso | temperature |
|---|---|
| Cdigo / Matemtica | `0.0` |
| Data / JSON | `1.0` |
| Chat geral | `1.3` |
| Criativo / Escrita | `1.5` |

---

## 4. Thinking Mode (`deepseek-reasoner`)

O modelo retorna **dois campos** na resposta:
- `reasoning_content`  o processo de raciocnio (CoT interno)
- `content`  a resposta final

### Parmetros suportados

|  Suportado |  NO suportado |
|---|---|
| JSON Output, Tool Calls, Chat Prefix | FIM Completion |
| `max_tokens` (at 64K, inclui CoT) | `temperature`, `top_p` |
| Chat Completion, stream | `frequency_penalty`, `logprobs` |

> Definir temperature/top_p no gera erro mas  ignorado. Definir logprobs/top_logprobs gera erro.

### Exemplo Multi-turn com Reasoner

```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com")

# Turno 1
messages = [{"role": "user", "content": "9.11 e 9.8, qual  maior?"}]
response = client.chat.completions.create(model="deepseek-reasoner", messages=messages)
reasoning = response.choices[0].message.reasoning_content  # CoT  NO passar no prximo turno
answer = response.choices[0].message.content

# Turno 2  passar APENAS content, no reasoning_content
messages.append({"role": "assistant", "content": answer})
messages.append({"role": "user", "content": "Explique melhor."})
response = client.chat.completions.create(model="deepseek-reasoner", messages=messages)
```

> **Regra crtica:** Em multi-turn com reasoner, NO concatenar `reasoning_content` no histrico  apenas `content`.

---

## 5. Multi-Round Conversation (stateless)

A API NO guarda estado. Sempre concatenar o histrico completo:

```python
# Turno 1
messages = [{"role": "user", "content": "Qual a montanha mais alta?"}]
resp = client.chat.completions.create(model="deepseek-chat", messages=messages)
messages.append(resp.choices[0].message)  # adicionar resposta do model

# Turno 2
messages.append({"role": "user", "content": "E a segunda?"})
resp2 = client.chat.completions.create(model="deepseek-chat", messages=messages)
```

**Padro NeoCortex:** LedgerService armazena o histrico  no precisamos gerenciar isso manualmente; o `mentor_step_0` injeta o contexto relevante dos lobos.

---

## 6. Context Caching (KV Cache  Automtico)

> **ATIVO POR PADRO  Zero configurao necessria.**

Como funciona:
1. Cada request cria cache em disco da prefix
2. Requests subsequentes com **mesma prefix** = cache hit (10x mais barato)

### Preos (cache)
| Tipo | Custo |
|---|---|
| Cache **HIT** | 0.1 yuan / M tokens |
| Cache **MISS** | 1 yuan / M tokens |

### Verificar cache hit na resposta
```python
usage = response.usage
hit_tokens = usage.prompt_cache_hit_tokens    # tokens que vieram do cache
miss_tokens = usage.prompt_cache_miss_tokens  # tokens que custaram full price
```

### Regras do Cache
- Unidade mnima: **64 tokens** (abaixo disso: no cached)
- Cache expira automaticamente: horas a alguns dias sem uso
- Cache hit rate: **best-effort**, no garantido 100%
- Output  sempre gerado (aleatrio por temperature)  s o input  cached

### Estratgia NeoCortex com KV Cache
```
System Prompt (estvel)  SEMPRE no incio  max cache hit
Contexto de Lobe (semi-estvel)  depois do system
Mensagem do usurio (dinmica)  sempre no fim  no cached
```

---

## 7. Tool Calls (Function Calling)

### Modo Normal (`deepseek-chat`)

```python
tools = [{
    "type": "function",
    "function": {
        "name": "neocortex_search",
        "description": "Busca nos lobos de memria do NeoCortex",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto a buscar"},
                "lobe": {"type": "string", "enum": ["architecture", "security", "dev"]}
            },
            "required": ["query"]
        }
    }
}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Busque sobre ORCH-301"}],
    tools=tools,
    tool_choice="auto"
)

# Se model quer chamar uma tool:
tool_call = response.choices[0].message.tool_calls[0]
func_name = tool_call.function.name       # "neocortex_search"
func_args = json.loads(tool_call.function.arguments)  # {"query": "ORCH-301"}

# Executar a tool e devolver resultado:
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(search_result)
})
```

### Strict Mode (Beta)
```python
"function": {
    "name": "my_func",
    "strict": True,  # garante que model s use campos definidos no schema
    "parameters": {...}
}
```

### Tool Calls em Thinking Mode (`deepseek-reasoner`)
-  Suportado  model raciocina internamente antes de decidir qual tool usar
- O CoT aparece em `reasoning_content` mas tool_calls  separado

---

## 8. Chat Prefix Completion (Beta)

Fora o incio da resposta do modelo  til para sada estruturada:

```python
messages = [
    {"role": "system", "content": "Retorne sempre JSON vlido."},
    {"role": "user", "content": "Gere config do agente courier"},
    {"role": "assistant", "content": "{", "prefix": True}  # fora incio com {
]
response = client.chat.completions.create(model="deepseek-chat", messages=messages)
# Resposta ser sempre JSON comeando com {
```

> **Aplicao NeoCortex:** Usar para garantir que agentes retornem JSON quando chamados via `neocortex_task.execute`

---

## 9. FIM Completion  Fill In the Middle (Beta)

**Endpoint:** `https://api.deepseek.com/beta` (diferente do padro!)  
**Limite:** 4K tokens max  
**Uso:** Completar cdigo no meio de um arquivo

```python
from openai import OpenAI
client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com/beta"  #  /beta obrigatrio
)

response = client.completions.create(
    model="deepseek-chat",
    prompt="def fibonacci(n):",           # prefixo
    suffix="    return fib(n-1) + fib(n-2)",  # sufixo
    max_tokens=128
)
print(response.choices[0].text)  # corpo do meio gerado
```

> **Integrao Editor:** Compatvel com plugin Continue (VSCode/Cursor)

---

## 10. APIs Utilitrias

### Listar Modelos
```python
GET https://api.deepseek.com/models
Authorization: Bearer {api_key}
```

### Consultar Saldo
```python
GET https://api.deepseek.com/user/balance
Authorization: Bearer {api_key}

Response: {
  "is_available": true,
  "balance_infos": [{
    "currency": "CNY",          # ou "USD"
    "total_balance": "110.00",
    "granted_balance": "10.00", # saldo cortesia
    "topped_up_balance": "100.00" # saldo comprado
  }]
}
```

> Consumo: usa `granted_balance` primeiro, depois `topped_up_balance`

### Python helper para saldo (adicionar ao NC-TOOL-FR-016 ou observability)
```python
import httpx

def check_deepseek_balance(api_key: str) -> dict:
    resp = httpx.get(
        "https://api.deepseek.com/user/balance",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return resp.json()
```

---

## 11. Cdigos de Erro

| HTTP | Causa | Soluo |
|---|---|---|
| 400 | Parmetro invlido | Verificar body do request |
| 401 | API key invlida | Verificar config key |
| 402 | Saldo zerado | Top-up em platform.deepseek.com |
| 422 | Campo obrigatrio ausente | Adicionar model + messages |
| 429 | Rate limit | Backoff exponencial |
| 500 | Erro interno | Retry aps 1-2s |
| 503 | Sobrecarga | Fallback para Ollama |

---

## 12. Integrao NeoCortex

| Componente | Path | Status |
|---|---|---|
| Backend | `neocortex/infra/llm/deepseek_backend.py` |  Funcional |
| Config | `DIR-CFG-FR-001-config-main/neocortex_config.yaml` |  Configurado |
| Lobe | `lobes/backend_dev/NC-LBE-FR-DEEPSEEK-001.md` |  Este arquivo |

### To-Do no Backend (ps-ORCH-301)
- [ ] Adicionar suporte a `tool_calls` no `DeepSeekBackend.generate()`
- [ ] Adicionar `response_format=json_object` como option
- [ ] Adicionar `chat_prefix` support
- [ ] Expor `check_balance()` como MCP tool via `NC-TOOL-FR-026-observability`
- [ ] Rastrear `prompt_cache_hit_tokens` no MetricsStore

---

## 13. Links
| Doc | URL |
|---|---|
| First Call | https://api-docs.deepseek.com |
| Models & Pricing | https://api-docs.deepseek.com/quick_start/pricing |
| Thinking Mode | https://api-docs.deepseek.com/guides/thinking_mode |
| Tool Calls | https://api-docs.deepseek.com/guides/tool_calls |
| KV Cache | https://api-docs.deepseek.com/guides/kv_cache |
| FIM | https://api-docs.deepseek.com/guides/fim_completion |
| Chat Prefix | https://api-docs.deepseek.com/guides/chat_prefix_completion |
| Multi-round | https://api-docs.deepseek.com/guides/multi_round_chat |
| List Models | https://api-docs.deepseek.com/api/list-models |
| User Balance | https://api-docs.deepseek.com/api/get-user-balance |
| Integrations | https://github.com/deepseek-ai/awesome-deepseek-integration |
