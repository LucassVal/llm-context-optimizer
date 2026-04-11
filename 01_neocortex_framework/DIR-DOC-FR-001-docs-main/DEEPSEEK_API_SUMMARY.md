# DeepSeek API - Mapeamento Completo

Documentação resumida da API DeepSeek para integração no NeoCortex HUD.

## Modelos Disponíveis

| Modelo | Modo | Contexto | Output Máximo | Preços (por 1M tokens) |
|--------|------|----------|---------------|------------------------|
| `deepseek-chat` | Não-thinking | 128K | 8K (default 4K) | Input Cache Hit: $0.028<br>Input Cache Miss: $0.28<br>Output: $0.42 |
| `deepseek-reasoner` | Thinking | 128K | 64K (default 32K) | Mesmos preços acima |

## Endpoints Principais

- **Base URL**: `https://api.deepseek.com` (ou `https://api.deepseek.com/v1` para compatibilidade OpenAI)
- **Chat Completion**: `POST /chat/completions`
- **Autenticação**: Header `Authorization: Bearer YOUR_API_KEY`

## Cache de Contexto (Context Caching)

Recurso ativado por padrão que reduz custos para requisições com prefixos repetidos.

### Como funciona:
- Cache em disco, unidades de 64 tokens
- Prefixos idênticos entre requisições geram "cache hit"
- Status no response: `prompt_cache_hit_tokens` e `prompt_cache_miss_tokens`

### Exemplo de economia:
```
Primeira requisição: 1000 tokens → $0.28 (cache miss)
Segunda requisição (mesmo prefixo): 
  - 800 tokens cache hit → $0.0224
  - 200 tokens novos → $0.056
  - Total: $0.0784 (72% de economia)
```

## Tool Calls (Integração com MCP)

Suporte nativo a function calling, equivalente ao MCP.

### Modos disponíveis:
1. **Non-thinking mode** (`deepseek-chat`): Tool calls padrão
2. **Thinking mode** (`deepseek-reasoner`): Raciocínio interno antes de tool calls
3. **Strict mode (Beta)**: Validação rigorosa de JSON Schema

### JSON Schema suportado:
- `object`, `string`, `number`, `integer`, `boolean`, `array`, `enum`, `anyOf`
- Validações: `pattern`, `format` (email, hostname, ipv4, ipv6, uuid)
- Restrições: `minimum`, `maximum`, `multipleOf`

## Rate Limits

**Não há limites de taxa impostos**, mas em alta carga:
- Requests podem demorar
- Conexões mantidas por até 10 minutos antes de timeout
- Streaming: envio de comentários `: keep-alive` como keep-alive

## Métricas de Uso (Response Headers)

A API retorna informações de uso no corpo da resposta:

```json
{
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150,
    "prompt_cache_hit_tokens": 80,    // Tokens com cache hit
    "prompt_cache_miss_tokens": 20    // Tokens com cache miss
  }
}
```

## Cálculo de Custos

### Fórmula:
```
Custo = (cache_hit_tokens * 0.028 + cache_miss_tokens * 0.28 + output_tokens * 0.42) / 1_000_000
```

### Eficiência de Cache:
```
Eficiência = (cache_hit_tokens / total_input_tokens) * 100%
```

## Integração com NeoCortex HUD

### Métricas a monitorar:
1. **Economia diária**: Custo real vs. custo sem cache
2. **Taxa de cache hit**: Porcentagem de tokens reutilizados
3. **Tokens por período**: Diário, semanal, mensal
4. **Custo por modelo**: deepseek-chat vs deepseek-reasoner

### Implementação no HUD:
- Consultar `usage` de cada resposta da API
- Acumular métricas no MetricsStore (DuckDB)
- Calcular economia em tempo real
- Alertas para baixa eficiência de cache (< 50%)

## Exemplo de Código para Coleta de Métricas

```python
def calculate_deepseek_cost(usage_data):
    """Calcula custo baseado nos tokens de cache hit/miss."""
    cache_hit = usage_data.get('prompt_cache_hit_tokens', 0)
    cache_miss = usage_data.get('prompt_cache_miss_tokens', 0)
    output_tokens = usage_data.get('completion_tokens', 0)
    
    cost = (cache_hit * 0.028 + cache_miss * 0.28 + output_tokens * 0.42) / 1_000_000
    total_input = cache_hit + cache_miss
    efficiency = (cache_hit / total_input * 100) if total_input > 0 else 0
    
    return {
        'cost_usd': cost,
        'efficiency_percent': efficiency,
        'cache_hit_tokens': cache_hit,
        'cache_miss_tokens': cache_miss,
        'output_tokens': output_tokens
    }
```

## Links Úteis

- [Documentação Oficial](https://api-docs.deepseek.com/)
- [Status da API](https://status.deepseek.com/)
- [Exemplos de Integração](https://github.com/deepseek-ai/awesome-deepseek-integration)
- [Tokenizer](https://cdn.deepseek.com/api-docs/deepseek_v3_tokenizer.zip)

---

**Última atualização**: 2026-04-11  
**Fonte**: https://api-docs.deepseek.com/  
**Integração NeoCortex**: v4.2-cortex