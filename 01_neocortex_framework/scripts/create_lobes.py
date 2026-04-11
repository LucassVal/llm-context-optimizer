#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criação de Lobos para o framework NeoCortex.

Cria Lobos para os módulos: architecture, development, testing, cli, white_label, knowledge,
e sugere novos Lobos com hierarquias.
"""

import json
import sys
import os
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neocortex.core import (
    get_lobe_service,
    get_manifest_service,
    get_kg_service,
    get_checkpoint_service,
)


def create_lobe(lobe_service, lobe_name, content, metadata=None):
    """
    Cria um lobe se não existir.

    Args:
        lobe_service: Instância do LobeService
        lobe_name: Nome do lobe (com .mdc)
        content: Conteúdo do lobe
        metadata: Metadados opcionais

    Returns:
        Resultado da criação
    """
    # Verificar se lobe já existe
    existing_lobe = lobe_service.get_lobe(lobe_name)
    if existing_lobe.get("exists"):
        print(f"   [SKIP] Lobe '{lobe_name}' já existe")
        return {"success": True, "skipped": True}

    # Criar lobe
    lobe_result = lobe_service.create_lobe(
        lobe_name=lobe_name,
        content=content,
        metadata=metadata or {},
    )

    if lobe_result.get("success"):
        print(f"   [OK] Lobe '{lobe_name}' criado")
    else:
        print(
            f"   [WARN] Falha ao criar lobe '{lobe_name}': {lobe_result.get('error', 'Unknown')}"
        )

    return lobe_result


def generate_manifest(manifest_service, lobe_name):
    """
    Gera manifesto para um lobe.

    Args:
        manifest_service: Instância do ManifestService
        lobe_name: Nome do lobe

    Returns:
        Resultado da geração
    """
    manifest_result = manifest_service.generate_manifest(target=lobe_name)

    if manifest_result.get("success"):
        print(f"   [OK] Manifesto gerado para '{lobe_name}'")
    else:
        print(
            f"   [WARN] Falha ao gerar manifesto para '{lobe_name}': {manifest_result.get('error', 'Unknown')}"
        )

    return manifest_result


def main():
    print("=== CRIAÇÃO DE LOBOS PARA NEOcORTEX ===\n")

    # Obter serviços
    lobe_service = get_lobe_service()
    manifest_service = get_manifest_service()

    # Lobos principais solicitados
    main_lobes = [
        {
            "name": "NC-LBE-FR-ARCHITECTURE-001.mdc",
            "module": "architecture",
            "title": "Arquitetura do Framework NeoCortex",
            "description": "Documentação e princípios arquiteturais do framework NeoCortex.",
        },
        {
            "name": "NC-LBE-FR-DEVELOPMENT-001.mdc",
            "module": "development",
            "title": "Desenvolvimento no NeoCortex",
            "description": "Padrões, boas práticas e guias de desenvolvimento.",
        },
        {
            "name": "NC-LBE-FR-TESTING-001.mdc",
            "module": "testing",
            "title": "Testes no NeoCortex",
            "description": "Estratégia de testes, ferramentas e cobertura.",
        },
        {
            "name": "NC-LBE-FR-CLI-001.mdc",
            "module": "cli",
            "title": "Interface de Linha de Comando (CLI)",
            "description": "CLI do NeoCortex: comandos, opções e extensibilidade.",
        },
        {
            "name": "NC-LBE-FR-WHITELABEL-001.mdc",
            "module": "white_label",
            "title": "White Label e Customização",
            "description": "Personalização e white labeling do framework.",
        },
        {
            "name": "NC-LBE-FR-KNOWLEDGE-001.mdc",
            "module": "knowledge",
            "title": "Gestão de Conhecimento",
            "description": "Knowledge Graph, manifestos e gestão de conhecimento.",
        },
    ]

    # Conteúdo base para cada lobe
    for lobe_info in main_lobes:
        print(f"\n1. Criando Lobe: {lobe_info['name']}")

        # Conteúdo específico baseado no módulo
        content = generate_lobe_content(lobe_info)

        # Criar lobe
        create_lobe(
            lobe_service=lobe_service,
            lobe_name=lobe_info["name"],
            content=content,
            metadata={
                "module": lobe_info["module"],
                "category": "core",
                "status": "active",
                "created_by": "opencode",
            },
        )

        # Gerar manifesto
        generate_manifest(manifest_service, lobe_info["name"])

    # Lobos sugeridos (novos)
    suggested_lobes = [
        {
            "name": "NC-LBE-FR-SECURITY-001.mdc",
            "module": "security",
            "title": "Segurança e Autenticação",
            "description": "Segurança, autenticação, autorização e criptografia.",
            "category": "operations",
        },
        {
            "name": "NC-LBE-FR-DEPLOYMENT-001.mdc",
            "module": "deployment",
            "title": "Deploy e Operações",
            "description": "Deploy, containers, orchestration e operações.",
            "category": "operations",
        },
        {
            "name": "NC-LBE-FR-DOCUMENTATION-001.mdc",
            "module": "documentation",
            "title": "Documentação",
            "description": "Padrões de documentação, geradores e templates.",
            "category": "support",
        },
        {
            "name": "NC-LBE-FR-INTEGRATION-001.mdc",
            "module": "integration",
            "title": "Integrações e APIs",
            "description": "Integrações com sistemas externos, APIs e webhooks.",
            "category": "extensions",
        },
        {
            "name": "NC-LBE-FR-MONITORING-001.mdc",
            "module": "monitoring",
            "title": "Monitoramento e Logs",
            "description": "Monitoramento, métricas, logs e alertas.",
            "category": "operations",
        },
        {
            "name": "NC-LBE-FR-PERFORMANCE-001.mdc",
            "module": "performance",
            "title": "Performance e Otimização",
            "description": "Otimização de performance, profiling e benchmarking.",
            "category": "quality",
        },
    ]

    print("\n" + "=" * 60)
    print("SUGESTÃO DE NOVOS LOBES")
    print("=" * 60)

    for lobe_info in suggested_lobes:
        print(f"\n2. Sugerindo Lobe: {lobe_info['name']}")

        # Conteúdo básico
        content = generate_lobe_content(lobe_info)

        # Criar lobe (apenas se não existir)
        create_lobe(
            lobe_service=lobe_service,
            lobe_name=lobe_info["name"],
            content=content,
            metadata={
                "module": lobe_info["module"],
                "category": lobe_info.get("category", "extensions"),
                "status": "suggested",  # Marcar como sugerido
                "suggested_by": "opencode",
            },
        )

    # Propor hierarquias
    print("\n" + "=" * 60)
    print("HIERARQUIA PROPOSTA PARA LOBOS")
    print("=" * 60)

    hierarchies = {
        "Core Framework": [
            "NC-LBE-FR-ARCHITECTURE-001.mdc",
            "NC-LBE-FR-DEVELOPMENT-001.mdc",
            "NC-LBE-FR-TESTING-001.mdc",
            "NC-LBE-FR-KNOWLEDGE-001.mdc",
            "NC-LBE-FR-CORE-001.mdc",  # Existente
        ],
        "Modules & Extensions": [
            "NC-LBE-FR-CLI-001.mdc",
            "NC-LBE-FR-MCP-001.mdc",  # Existente
            "NC-LBE-FR-PULSE-001.mdc",  # Existente
            "NC-LBE-FR-BENCHMARKS-001.mdc",  # Existente
            "NC-LBE-FR-PROFILES-001.mdc",  # Existente
            "NC-LBE-FR-WHITELABEL-001.mdc",
            "NC-LBE-FR-INTEGRATION-001.mdc",
        ],
        "Operations & Quality": [
            "NC-LBE-FR-SECURITY-001.mdc",
            "NC-LBE-FR-DEPLOYMENT-001.mdc",
            "NC-LBE-FR-MONITORING-001.mdc",
            "NC-LBE-FR-PERFORMANCE-001.mdc",
        ],
        "Support & Documentation": [
            "NC-LBE-FR-DOCUMENTATION-001.mdc",
        ],
    }

    for category, lobes in hierarchies.items():
        print(f"\n{category}:")
        for lobe in lobes:
            print(f"  - {lobe}")

    # Adicionar entidades ao KG para os novos Lobos
    print("\n" + "=" * 60)
    print("ATUALIZANDO KNOWLEDGE GRAPH")
    print("=" * 60)

    kg_service = get_kg_service()

    # Adicionar entidades para cada Lobo criado/sugerido
    all_lobes = main_lobes + suggested_lobes

    for lobe_info in all_lobes:
        entity_id = lobe_info["module"].lower().replace("_", "-")
        entity_name = lobe_info["title"]

        kg_result = kg_service.add_entity(
            entity=entity_id,
            entity_type="lobe_category",
        )

        if kg_result.get("success"):
            print(f"   [OK] Entidade KG '{entity_name}' adicionada")
        else:
            print(f"   [WARN] Falha ao adicionar entidade KG: {entity_name}")

    # Criar checkpoint
    print("\n" + "=" * 60)
    print("CRIANDO CHECKPOINT")
    print("=" * 60)

    checkpoint_service = get_checkpoint_service()
    checkpoint_id = f"CP-LOBES-CREATED-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

    checkpoint_result = checkpoint_service.set_current_checkpoint(
        checkpoint_id=checkpoint_id,
        description=f"Criação de Lobos principais e sugestão de novos Lobos. Total: {len(all_lobes)}",
        lobe_id="NC-LBE-FR-002-claude-assistant",
    )

    if checkpoint_result.get("success"):
        print(f"   [OK] Checkpoint criado: {checkpoint_id}")
    else:
        print(
            f"   [WARN] Falha ao criar checkpoint: {checkpoint_result.get('error', 'Unknown')}"
        )

    print("\n" + "=" * 60)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 60)
    print(f"- Lobos principais criados/verificados: {len(main_lobes)}")
    print(f"- Lobos sugeridos criados/verificados: {len(suggested_lobes)}")
    print(f"- Total de Lobos processados: {len(all_lobes)}")
    print(f"- Hierarquias propostas: {len(hierarchies)} categorias")
    print(f"- Checkpoint: {checkpoint_id}")
    print("\nPróximos passos:")
    print("1. Revisar conteúdo dos Lobos criados")
    print("2. Ativar Lobos relevantes no memory_cortex")
    print("3. Popular Lobos com conteúdo específico do projeto")
    print("4. Estabelecer relações entre Lobos no KG")


def generate_lobe_content(lobe_info):
    """
    Gera conteúdo inicial para um lobe baseado no módulo.

    Args:
        lobe_info: Dicionário com informações do lobe

    Returns:
        Conteúdo do lobe em formato markdown
    """
    module = lobe_info["module"]
    title = lobe_info["title"]
    description = lobe_info["description"]

    # Conteúdo base
    content = f"""# {title}

{description}

## Propósito
Gerenciar conhecimento específico do módulo {module}.

## Status
{"Ativo" if lobe_info.get("status", "suggested") == "active" else "Sugerido"}

## Tags
#{module}, #framework, #neocortex

## Checkpoints
- CP-{module.upper()}-001: Criação inicial

## Conteúdo Inicial
*Este lobe está em construção. Adicione aqui:*

### 1. Visão Geral
- Objetivos principais
- Escopo do módulo
- Integrações com outros módulos

### 2. Componentes Principais
- Lista de componentes/classes
- Responsabilidades
- Dependências

### 3. Padrões e Convenções
- Padrões de código
- Convenções de nomenclatura
- Boas práticas

### 4. Exemplos de Uso
- Exemplos básicos
- Casos de uso comuns
- Configurações típicas

### 5. Referências
- Links para documentação
- Arquivos relevantes no projeto
- Exemplos externos

## Notas
- Criado automaticamente por OpenCode
- Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Revisão necessária para conteúdo específico do projeto
"""

    # Adicionar conteúdo específico por módulo
    if module == "architecture":
        content += """
## Princípios Arquiteturais do NeoCortex

### Arquitetura Hexagonal
- Separação clara entre lógica de negócio e infraestrutura
- Repositórios como portas de entrada/saída
- Serviços encapsulam regras de negócio

### Camadas do Framework
1. **Camada de Repositórios**: FileSystemRepository, HubRepository, DatabaseRepository
2. **Camada de Serviços**: CortexService, LobeService, LedgerService
3. **Camada de Protocolos**: MCP Server, A2A Protocol
4. **Camada de Aplicação**: CLI, Interfaces de usuário

### Contratos JSON Schema
- LEDGER_SCHEMA: Estrutura do ledger principal
- A2A_MESSAGE_SCHEMA: Protocolo agent-to-agent
- TOOL_MANIFEST_SCHEMA: Metadados de ferramentas MCP

### Padrões de Design
- Repository Pattern
- Service Layer
- Singleton Pattern (para serviços)
- Factory Pattern (para repositórios)
"""

    elif module == "development":
        content += """
## Guia de Desenvolvimento NeoCortex

### Estrutura de Diretórios
- `neocortex/core/`: Serviços de negócio
- `neocortex/repositories/`: Implementações de repositório
- `neocortex/mcp/`: Servidor e ferramentas MCP
- `neocortex/cli/`: Interface de linha de comando
- `neocortex/schemas/`: Esquemas JSON

### Convenções de Código
- Nomes de classes: PascalCase
- Nomes de funções: snake_case
- Nomes de variáveis: snake_case
- Constantes: UPPER_SNAKE_CASE

### Padrões de Importação
```python
# Importação absoluta dentro do projeto
from neocortex.core import get_cortex_service
from neocortex.repositories import FileSystemRepositoryFactory

# Importação relativa dentro do mesmo módulo
from .file_utils import read_cortex
```

### Documentação
- Docstrings no formato Google Style
- Type hints obrigatórios para funções públicas
- Exemplos de uso em docstrings complexas

### Testes
- Testes unitários para serviços
- Testes de integração para repositórios
- Testes end-to-end para ferramentas MCP
"""

    elif module == "testing":
        content += """
## Estratégia de Testes NeoCortex

### Tipos de Testes
1. **Testes Unitários**: Serviços individuais
2. **Testes de Integração**: Repositórios + Serviços
3. **Testes End-to-End**: Fluxos completos MCP
4. **Testes de Performance**: Benchmarks

### Ferramentas
- `pytest`: Framework principal
- `unittest`: Para compatibilidade
- `coverage.py`: Cobertura de código
- `pytest-asyncio`: Testes assíncronos

### Estrutura de Testes
```
tests/
├── unit/
│   ├── core/
│   │   ├── test_cortex_service.py
│   │   └── test_lobe_service.py
│   └── repositories/
│       ├── test_filesystem_repository.py
│       └── test_ledger_repository.py
├── integration/
│   ├── test_service_integration.py
│   └── test_mcp_integration.py
└── e2e/
    ├── test_cli_commands.py
    └── test_mcp_tools.py
```

### Cobertura Alvo
- Serviços Core: >80%
- Repositórios: >70%
- Ferramentas MCP: >60%
- CLI: >50%

### Mocking
- Mock de repositórios para testes de serviço
- Mock de serviços para testes de integração
- Mock de MCP server para testes de ferramentas
"""

    elif module == "cli":
        content += """
## Interface de Linha de Comando (CLI)

### Comandos Disponíveis
1. `neocortex server`: Inicia servidor MCP
2. `neocortex info`: Mostra informações do framework
3. `neocortex tools`: Lista ferramentas MCP disponíveis
4. `neocortex version`: Mostra versão do framework

### Modos de Operação
- **Modo stdio**: Para integração com IDEs (VS Code, Cursor)
- **Modo socket**: Para integração via rede (em desenvolvimento)

### Extensão de Comandos
```python
# Exemplo de adição de novo comando
# Em neocortex/cli/main.py, adicionar:
new_parser = subparsers.add_parser("novo", help="Novo comando")
new_parser.add_argument("--opcao", help="Opção do comando")
```

### Integração com Serviços
- CLI usa os mesmos serviços que o MCP server
- Acesso ao cortex, ledger, lobes via services
- Configuração via environment variables

### Exemplos de Uso
```bash
# Iniciar servidor MCP para IDE
neocortex server --stdio

# Ver informações detalhadas
neocortex info --verbose

# Listar todas as ferramentas MCP
neocortex tools
```
"""

    elif module == "white_label":
        content += """
## White Label e Customização

### Personalização Disponível
1. **Branding**: Nome, logo, cores
2. **Configurações**: Valores padrão, comportamentos
3. **Extensões**: Módulos customizados
4. **Templates**: Templates de documentos, relatórios

### Diretórios de Customização
- `white_label/branding/`: Logos, cores, temas
- `white_label/config/`: Configurações customizadas
- `white_label/templates/`: Templates personalizados
- `white_label/extensions/`: Extensões customizadas

### Processo de White Label
1. Copiar diretório `white_label/` do template
2. Modificar arquivos de branding
3. Ajustar configurações
4. Adicionar extensões customizadas
5. Rebuild do framework

### Configuração via Environment
```bash
# Definir branding customizado
export NEOCORTEX_BRAND_NAME="MeuFramework"
export NEOCORTEX_PRIMARY_COLOR="#3b82f6"
export NEOCORTEX_LOGO_PATH="white_label/branding/logo.png"
```

### Templates Customizáveis
- Cortex template
- Lobe templates
- Documentação templates
- Relatórios templates
"""

    elif module == "knowledge":
        content += """
## Gestão de Conhecimento NeoCortex

### Componentes Principais
1. **Knowledge Graph (KG)**: Entidades e relações
2. **Manifestos**: Metadados de cortex e lobes
3. **Regression Buffer**: Aprendizados e erros
4. **Memory Cortex**: Estado ativo da memória

### Knowledge Graph Service
- `KGService`: Gerencia entidades e relações
- Entidades: framework, component, lobe, concept
- Relações: part_of, required_by, integrated_with

### Manifest Service
- `ManifestService`: Gera e gerencia manifestos
- Manifestos para cortex e lobes
- Metadados: tamanho, tags, entidades, dependências

### Fluxo de Conhecimento
1. **Aquisição**: Ferramentas MCP, análise de código
2. **Processamento**: Extração de entidades, geração de manifestos
3. **Armazenamento**: Ledger JSON, arquivos .mdc
4. **Recuperação**: Query no KG, busca em manifestos

### Exemplos de Uso
```python
# Adicionar entidade ao KG
kg_service.add_entity(entity="neocortex", entity_type="framework")

# Adicionar relação
kg_service.add_relation(
    source="pulse_scheduler",
    relation="part_of",
    target="neocortex"
)

# Gerar manifesto para lobe
manifest_service.generate_manifest("NC-LBE-FR-CORE-001.mdc")
```
"""

    # Conteúdo para módulos sugeridos
    elif module == "security":
        content += """
## Segurança e Autenticação

### Componentes de Segurança
- `SecurityService`: Validação de acesso, criptografia
- `ProfileManager`: Gestão de perfis e permissões
- `AgentSession`: Sessões de agentes, autenticação

### Autenticação
- Tokens JWT para agentes
- API keys para integrações externas
- Session-based authentication para CLI

### Autorização
- RBAC (Role-Based Access Control)
- Perfis: admin, developer, viewer, guest
- Permissões granulares por recurso

### Criptografia
- Sensitive data encryption at rest
- TLS/SSL para comunicações
- Hash de senhas e tokens

### Auditoria
- Log de todas as operações sensíveis
- Trail de alterações no ledger
- Monitoramento de acesso
"""

    elif module == "deployment":
        content += """
## Deploy e Operações

### Opções de Deploy
1. **Local**: Python package, desenvolvimento
2. **Docker**: Containerização
3. **Kubernetes**: Orchestration
4. **Serverless**: AWS Lambda, Azure Functions

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["neocortex", "server", "--stdio"]
```

### Kubernetes
- Deployment para MCP server
- ConfigMap para configurações
- Secret para tokens e chaves
- Service para exposição

### CI/CD
- GitHub Actions para build e testes
- Docker image auto-build
- Automated deployment to staging/prod

### Monitoramento
- Health checks: /health endpoint
- Metrics: Prometheus metrics
- Logs: Structured logging (JSON)
- Alerts: AlertManager integration
"""

    elif module == "documentation":
        content += """
## Documentação

### Tipos de Documentação
1. **Documentação de Usuário**: Guias, tutoriais
2. **Documentação de Desenvolvedor**: API, arquitetura
3. **Documentação de Operações**: Deploy, monitoramento
4. **Documentação de Referência**: Schemas, contratos

### Ferramentas
- MkDocs para documentação estática
- Sphinx para documentação de código
- Swagger/OpenAPI para API documentation
- PlantUML para diagramas

### Estrutura de Diretórios
```
docs/
├── user/
│   ├── getting-started.md
│   └── tutorials/
├── developer/
│   ├── architecture.md
│   └── api-reference.md
├── operations/
│   ├── deployment.md
│   └── monitoring.md
└── reference/
    ├── schemas.md
    └── contracts.md
```

### Geração Automática
- Auto-doc from docstrings
- Schema documentation from JSON schemas
- Tool documentation from MCP tool manifests
"""

    elif module == "integration":
        content += """
## Integrações e APIs

### Protocolos Suportados
1. **MCP (Model Context Protocol)**: Integração com IDEs
2. **A2A (Agent-to-Agent)**: Comunicação entre agentes
3. **REST API**: Para integrações externas
4. **WebSocket**: Comunicação em tempo real

### MCP Server
- 17 ferramentas multi-ação
- Suporte a stdio e socket modes
- Tool discovery and documentation

### A2A Protocol
- Message schemas definidos
- Agentes: cortex, security, consolidation, etc.
- Comunicação assíncrona via event bus

### REST API
- CRUD para lobes, cortex, ledger
- GraphQL para queries complexas
- Webhooks para notificações

### WebSocket
- Real-time updates
- Bi-directional communication
- Subscription to events
"""

    elif module == "monitoring":
        content += """
## Monitoramento e Logs

### Métricas
- Request latency
- Error rates
- Memory usage
- Active sessions
- Tool usage statistics

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log rotation and retention
- Centralized log aggregation

### Alertas
- Threshold-based alerts
- Anomaly detection
- Notification channels: email, Slack, PagerDuty
- Escalation policies

### Dashboard
- Grafana dashboards
- Real-time metrics
- Historical trends
- Custom visualizations

### Tracing
- Distributed tracing
- Request correlation
- Performance profiling
- Dependency mapping
"""

    elif module == "performance":
        content += """
## Performance e Otimização

### Benchmarks
- `BenchmarkService`: Medição de performance
- Metrics: latency, throughput, memory, CPU
- Comparative analysis

### Otimizações
- Caching strategies
- Database/index optimization
- Query optimization
- Memory management

### Profiling
- CPU profiling
- Memory profiling
- I/O profiling
- Network profiling

### Load Testing
- Simulated user loads
- Stress testing
- Soak testing
- Spike testing

### Tuning
- Configuration tuning
- Resource allocation
- Concurrency tuning
- Batch processing optimization
"""

    return content


if __name__ == "__main__":
    main()
