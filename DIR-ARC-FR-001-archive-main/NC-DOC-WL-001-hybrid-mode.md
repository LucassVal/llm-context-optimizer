# NC-DOC-WL-001 - NeoCortex Hybrid LLM Mode Guide

## Overview

NeoCortex supports a hybrid LLM mode that allows simultaneous use of multiple LLM providers (local and cloud) with automatic fallback and role-based routing. This enables cost optimization, resilience, and specialized task execution.

## Key Features

- **Multiple Backends**: Support for Ollama (local), DeepSeek (cloud), OpenAI (cloud), and more
- **Fallback Chains**: Automatic failover between backends when one is unavailable
- **Role-Based Routing**: Different agents can use different backends based on their role
- **Runtime Configuration**: Backend configuration can be changed at runtime via MCP tools
- **Health Monitoring**: Backend availability and performance tracking

## Configuration

### Global LLM Configuration

Configure LLM settings in `neocortex_config.yaml`:

```yaml
llm:
  provider: "ollama"  # Default provider
  model: "llama2"     # Default model
  base_url: "http://localhost:11434"
  api_key: ""         # For cloud providers
  temperature: 0.7
  max_tokens: 4096
  fallback_chain:
    - provider: "ollama"
      model: "llama2"
      base_url: "http://localhost:11434"
    - provider: "deepseek"
      model: "deepseek-chat"
      api_key: "${DEEPSEEK_API_KEY}"
```

### Agent-Specific Backend Configuration

Set backends for specific agent roles:

```yaml
llm:
  agent_backends:
    guardian:
      provider: "ollama"
      model: "llama2:7b"
    backend_dev:
      provider: "deepseek"
      model: "deepseek-coder"
    indexer:
      provider: "ollama"
      model: "nomic-embed-text"
```

## MCP Tools

### `neocortex_config`

Use the `set_agent_backend` action to configure backends at runtime:

```bash
# Set Ollama backend for 'guardian' role
neocortex_config set_agent_backend guardian '{"provider": "ollama", "model": "llama2"}'

# Set DeepSeek backend for 'backend_dev' role
neocortex_config set_agent_backend backend_dev deepseek
```

### `neocortex_agent`

Specify backend override when spawning agents:

```bash
# Spawn guardian agent with Ollama backend
neocortex_agent spawn guardian --backend ollama

# Spawn backend developer with DeepSeek backend
neocortex_agent spawn backend_dev --backend deepseek
```

## AgentExecutor Integration

The `AgentExecutor` class provides programmatic access to hybrid LLM capabilities:

```python
from neocortex.agent.executor import get_agent_executor, AgentTask

# Get executor
executor = get_agent_executor()

# Create task
task = AgentTask(
    task_id="task-001",
    role="guardian",
    prompt="Analyze this code for security vulnerabilities...",
    system_prompt="You are a security expert..."
)

# Execute with optional backend override
response = executor.execute(task, backend_override="ollama")
print(response.content)
```

## Fallback Chains

Fallback chains provide resilience when primary backends fail:

```python
# Configuration for fallback chain
fallback_config = [
    {"provider": "ollama", "model": "llama2"},
    {"provider": "deepseek", "model": "deepseek-chat"},
    {"provider": "openai", "model": "gpt-4"}
]

# Use in agent configuration
llm:
  agent_backends:
    critical:
      - provider: "ollama"
        model: "llama2"
      - provider: "deepseek"
        model: "deepseek-chat"
```

## Testing Hybrid Scenarios

### Local + Cloud Testing

1. **Start Ollama locally**:
   ```bash
   ollama run llama2
   ```

2. **Configure DeepSeek API key**:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key"
   ```

3. **Test hybrid execution**:
   ```python
   # Test will use Ollama first, fallback to DeepSeek if unavailable
   executor.execute(task, role="guardian")
   ```

### Performance Benchmarking

Generate benchmark reports with `BENCHMARKS_HYBRID.md`:

- Compare token usage across providers
- Measure latency differences
- Calculate cost savings

## Troubleshooting

### Backend Unavailable

If a backend is unavailable:
1. Check service status (Ollama running, API keys valid)
2. Review logs for connection errors
3. Verify network connectivity

### Configuration Issues

Common configuration problems:
- Missing API keys (set via environment variables)
- Incorrect base URLs for local backends
- Model names not available on provider

### Performance Optimization

- Use local backends for high-frequency tasks
- Reserve cloud backends for complex reasoning
- Monitor token usage with `AgentExecutor.get_stats()`

## Best Practices

1. **Default to Local**: Use Ollama for most tasks to minimize costs
2. **Cloud for Complexity**: Use cloud providers for complex reasoning tasks
3. **Role Specialization**: Match backend capabilities to agent roles
4. **Monitor Usage**: Regularly review backend usage statistics
5. **Plan Fallbacks**: Always configure fallback chains for critical agents

## Example Use Cases

### Development Workflow
- **Guardian Agent**: Ollama for code review
- **Backend Developer**: DeepSeek for complex coding tasks
- **Indexer Agent**: Ollama for embedding generation

### Production Deployment
- **Primary**: Ollama cluster for 80% of requests
- **Fallback**: DeepSeek for remaining 20%
- **Emergency**: OpenAI as last-resort fallback

## Next Steps

1. **Benchmarking**: Run hybrid benchmarks to measure performance
2. **Optimization**: Fine-tune backend selection based on task type
3. **Monitoring**: Implement detailed metrics collection
4. **Expansion**: Add support for additional providers (Anthropic, Groq, etc.)

---

**Version**: 1.0  
**Last Updated**: 2026-04-10  
**Author**: NeoCortex Framework Team