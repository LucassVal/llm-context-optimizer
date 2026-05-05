#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ['script', 'automation']
hash: "auto-generated"
---"""

# -*- coding: utf-8 -*-
"""
Criao de Lobos para o framework NeoCortex.

Cria Lobos para os mdulos: architecture, development, testing, cli, white_label, knowledge,
e sugere novos Lobos com hierarquias.
"""

import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neocortex.core import (
    get_checkpoint_service,
    get_kg_service,
    get_lobe_service,
    get_manifest_service,
)


def create_lobe(lobe_service, lobe_name, content, metadata=None):
    """
    Cria um lobe se no existir.

    Args:
        lobe_service: Instncia do LobeService
        lobe_name: Nome do lobe (com .mdc)
        content: Contedo do lobe
        metadata: Metadados opcionais

    Returns:
        Resultado da criao
    """
    # Verificar se lobe j existe
    existing_lobe = lobe_service.get_lobe(lobe_name)
    if existing_lobe.get("exists"):
        print(f"   [SKIP] Lobe '{lobe_name}' j existe")
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
        manifest_service: Instncia do ManifestService
        lobe_name: Nome do lobe

    Returns:
        Resultado da gerao
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
    print("=== CRIAO DE LOBOS PARA NEOcORTEX ===\n")

    # Obter servios
    lobe_service = get_lobe_service()
    manifest_service = get_manifest_service()

    # Lobos principais solicitados
    main_lobes = [
        {
            "name": "NC-LBE-FR-ARCHITECTURE-001.mdc",
            "module": "architecture",
            "title": "Arquitetura do Framework NeoCortex",
            "description": "Documentao e princpios arquiteturais do framework NeoCortex.",
        },
        {
            "name": "NC-LBE-FR-DEVELOPMENT-001.mdc",
            "module": "development",
            "title": "Desenvolvimento no NeoCortex",
            "description": "Padres, boas prticas e guias de desenvolvimento.",
        },
        {
            "name": "NC-LBE-FR-TESTING-001.mdc",
            "module": "testing",
            "title": "Testes no NeoCortex",
            "description": "Estratgia de testes, ferramentas e cobertura.",
        },
        {
            "name": "NC-LBE-FR-CLI-001.mdc",
            "module": "cli",
            "title": "Interface de Linha de Comando (CLI)",
            "description": "CLI do NeoCortex: comandos, opes e extensibilidade.",
        },
        {
            "name": "NC-LBE-FR-WHITELABEL-001.mdc",
            "module": "white_label",
            "title": "White Label e Customizao",
            "description": "Personalizao e white labeling do framework.",
        },
        {
            "name": "NC-LBE-FR-KNOWLEDGE-001.mdc",
            "module": "knowledge",
            "title": "Gesto de Conhecimento",
            "description": "Knowledge Graph, manifestos e gesto de conhecimento.",
        },
    ]

    # Contedo base para cada lobe
    for lobe_info in main_lobes:
        print(f"\n1. Criando Lobe: {lobe_info['name']}")

        # Contedo especfico baseado no mdulo
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
            "title": "Segurana e Autenticao",
            "description": "Segurana, autenticao, autorizao e criptografia.",
            "category": "operations",
        },
        {
            "name": "NC-LBE-FR-DEPLOYMENT-001.mdc",
            "module": "deployment",
            "title": "Deploy e Operaes",
            "description": "Deploy, containers, orchestration e operaes.",
            "category": "operations",
        },
        {
            "name": "NC-LBE-FR-DOCUMENTATION-001.mdc",
            "module": "documentation",
            "title": "Documentao",
            "description": "Padres de documentao, geradores e templates.",
            "category": "support",
        },
        {
            "name": "NC-LBE-FR-INTEGRATION-001.mdc",
            "module": "integration",
            "title": "Integraes e APIs",
            "description": "Integraes com sistemas externos, APIs e webhooks.",
            "category": "extensions",
        },
        {
            "name": "NC-LBE-FR-MONITORING-001.mdc",
            "module": "monitoring",
            "title": "Monitoramento e Logs",
            "description": "Monitoramento, mtricas, logs e alertas.",
            "category": "operations",
        },
        {
            "name": "NC-LBE-FR-PERFORMANCE-001.mdc",
            "module": "performance",
            "title": "Performance e Otimizao",
            "description": "Otimizao de performance, profiling e benchmarking.",
            "category": "quality",
        },
    ]

    print("\n" + "=" * 60)
    print("SUGESTO DE NOVOS LOBES")
    print("=" * 60)

    for lobe_info in suggested_lobes:
        print(f"\n2. Sugerindo Lobe: {lobe_info['name']}")

        # Contedo bsico
        content = generate_lobe_content(lobe_info)

        # Criar lobe (apenas se no existir)
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
        description=f"Criao de Lobos principais e sugesto de novos Lobos. Total: {len(all_lobes)}",
        lobe_id="NC-LBE-FR-002-claude-assistant",
    )

    if checkpoint_result.get("success"):
        print(f"   [OK] Checkpoint criado: {checkpoint_id}")
    else:
        print(
            f"   [WARN] Falha ao criar checkpoint: {checkpoint_result.get('error', 'Unknown')}"
        )

    print("\n" + "=" * 60)
    print("RESUMO DA EXECUO")
    print("=" * 60)
    print(f"- Lobos principais criados/verificados: {len(main_lobes)}")
    print(f"- Lobos sugeridos criados/verificados: {len(suggested_lobes)}")
    print(f"- Total de Lobos processados: {len(all_lobes)}")
    print(f"- Hierarquias propostas: {len(hierarchies)} categorias")
    print(f"- Checkpoint: {checkpoint_id}")
    print("\nPrximos passos:")
    print("1. Revisar contedo dos Lobos criados")
    print("2. Ativar Lobos relevantes no memory_cortex")
    print("3. Popular Lobos com contedo especfico do projeto")
    print("4. Estabelecer relaes entre Lobos no KG")


def generate_lobe_content(lobe_info):
    """
    Gera contedo inicial para um lobe baseado no mdulo.

    Args:
        lobe_info: Dicionrio com informaes do lobe

    Returns:
        Contedo do lobe em formato markdown
    """
    module = lobe_info["module"]
    title = lobe_info["title"]
    description = lobe_info["description"]

    # Contedo base
    content = f"""# {title}

{description}

## Propsito
Gerenciar conhecimento especfico do mdulo {module}.

## Status
{"Ativo" if lobe_info.get("status", "suggested") == "active" else "Sugerido"}

## Tags
#{module}, #framework, #neocortex

## Checkpoints
- CP-{module.upper()}-001: Criao inicial

## Contedo Inicial
*Este lobe est em construo. Adicione aqui:*

### 1. Viso Geral
- Objetivos principais
- Escopo do mdulo
- Integraes com outros mdulos

### 2. Componentes Principais
- Lista de componentes/classes
- Responsabilidades
- Dependncias

### 3. Padres e Convenes
- Padres de cdigo
- Convenes de nomenclatura
- Boas prticas

### 4. Exemplos de Uso
- Exemplos bsicos
- Casos de uso comuns
- Configuraes tpicas

### 5. Referncias
- Links para documentao
- Arquivos relevantes no projeto
- Exemplos externos

## Notas
- Criado automaticamente por OpenCode
- Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Reviso necessria para contedo especfico do projeto
"""

    # Adicionar contedo especfico por mdulo
    if module == "architecture":
        content += """
## Princpios Arquiteturais do NeoCortex

### Arquitetura Hexagonal
- Separao clara entre lgica de negcio e infraestrutura
- Repositrios como portas de entrada/sada
- Servios encapsulam regras de negcio

### Camadas do Framework
1. **Camada de Repositrios**: FileSystemRepository, HubRepository, DatabaseRepository
2. **Camada de Servios**: CortexService, LobeService, LedgerService
3. **Camada de Protocolos**: MCP Server, A2A Protocol
4. **Camada de Aplicao**: CLI, Interfaces de usurio

### Contratos JSON Schema
- LEDGER_SCHEMA: Estrutura do ledger principal
- A2A_MESSAGE_SCHEMA: Protocolo agent-to-agent
- TOOL_MANIFEST_SCHEMA: Metadados de ferramentas MCP

### Padres de Design
- Repository Pattern
- Service Layer
- Singleton Pattern (para servios)
- Factory Pattern (para repositrios)
"""

    elif module == "development":
        content += """
## Guia de Desenvolvimento NeoCortex

### Estrutura de Diretrios
- `neocortex/core/`: Servios de negcio
- `neocortex/repositories/`: Implementaes de repositrio
- `neocortex/mcp/`: Servidor e ferramentas MCP
- `neocortex/cli/`: Interface de linha de comando
- `neocortex/schemas/`: Esquemas JSON

### Convenes de Cdigo
- Nomes de classes: PascalCase
- Nomes de funes: snake_case
- Nomes de variveis: snake_case
- Constantes: UPPER_SNAKE_CASE

### Padres de Importao
```python
# Importao absoluta dentro do projeto
from neocortex.core import get_cortex_service
from neocortex.repositories import FileSystemRepositoryFactory

# Importao relativa dentro do mesmo mdulo
from .file_utils import read_cortex
```

### Documentao
- Docstrings no formato Google Style
- Type hints obrigatrios para funes pblicas
- Exemplos de uso em docstrings complexas

### Testes
- Testes unitrios para servios
- Testes de integrao para repositrios
- Testes end-to-end para ferramentas MCP
"""

    elif module == "testing":
        content += """
## Estratgia de Testes NeoCortex

### Tipos de Testes
1. **Testes Unitrios**: Servios individuais
2. **Testes de Integrao**: Repositrios + Servios
3. **Testes End-to-End**: Fluxos completos MCP
4. **Testes de Performance**: Benchmarks

### Ferramentas
- `pytest`: Framework principal
- `unittest`: Para compatibilidade
- `coverage.py`: Cobertura de cdigo
- `pytest-asyncio`: Testes assncronos

### Estrutura de Testes
```
tests/
 unit/
    core/
       test_cortex_service.py
       test_lobe_service.py
    repositories/
        test_filesystem_repository.py
        test_ledger_repository.py
 integration/
    test_service_integration.py
    test_mcp_integration.py
 e2e/
     test_cli_commands.py
     test_mcp_tools.py
```

### Cobertura Alvo
- Servios Core: >80%
- Repositrios: >70%
- Ferramentas MCP: >60%
- CLI: >50%

### Mocking
- Mock de repositrios para testes de servio
- Mock de servios para testes de integrao
- Mock de MCP server para testes de ferramentas
"""

    elif module == "cli":
        content += """
## Interface de Linha de Comando (CLI)

### Comandos Disponveis
1. `neocortex server`: Inicia servidor MCP
2. `neocortex info`: Mostra informaes do framework
3. `neocortex tools`: Lista ferramentas MCP disponveis
4. `neocortex version`: Mostra verso do framework

### Modos de Operao
- **Modo stdio**: Para integrao com IDEs (VS Code, Cursor)
- **Modo socket**: Para integrao via rede (em desenvolvimento)

### Extenso de Comandos
```python
# Exemplo de adio de novo comando
# Em neocortex/cli/main.py, adicionar:
new_parser = subparsers.add_parser("novo", help="Novo comando")
new_parser.add_argument("--opcao", help="Opo do comando")
```

### Integrao com Servios
- CLI usa os mesmos servios que o MCP server
- Acesso ao cortex, ledger, lobes via services
- Configurao via environment variables

### Exemplos de Uso
```bash
# Iniciar servidor MCP para IDE
neocortex server --stdio

# Ver informaes detalhadas
neocortex info --verbose

# Listar todas as ferramentas MCP
neocortex tools
```
"""

    elif module == "white_label":
        content += """
## White Label e Customizao

### Personalizao Disponvel
1. **Branding**: Nome, logo, cores
2. **Configuraes**: Valores padro, comportamentos
3. **Extenses**: Mdulos customizados
4. **Templates**: Templates de documentos, relatrios

### Diretrios de Customizao
- `white_label/branding/`: Logos, cores, temas
- `white_label/config/`: Configuraes customizadas
- `white_label/templates/`: Templates personalizados
- `white_label/extensions/`: Extenses customizadas

### Processo de White Label
1. Copiar diretrio `white_label/` do template
2. Modificar arquivos de branding
3. Ajustar configuraes
4. Adicionar extenses customizadas
5. Rebuild do framework

### Configurao via Environment
```bash
# Definir branding customizado
export NEOCORTEX_BRAND_NAME="MeuFramework"
export NEOCORTEX_PRIMARY_COLOR="#3b82f6"
export NEOCORTEX_LOGO_PATH="white_label/branding/logo.png"
```

### Templates Customizveis
- Cortex template
- Lobe templates
- Documentao templates
- Relatrios templates
"""

    elif module == "knowledge":
        content += """
## Gesto de Conhecimento NeoCortex

### Componentes Principais
1. **Knowledge Graph (KG)**: Entidades e relaes
2. **Manifestos**: Metadados de cortex e lobes
3. **Regression Buffer**: Aprendizados e erros
4. **Memory Cortex**: Estado ativo da memria

### Knowledge Graph Service
- `KGService`: Gerencia entidades e relaes
- Entidades: framework, component, lobe, concept
- Relaes: part_of, required_by, integrated_with

### Manifest Service
- `ManifestService`: Gera e gerencia manifestos
- Manifestos para cortex e lobes
- Metadados: tamanho, tags, entidades, dependncias

### Fluxo de Conhecimento
1. **Aquisio**: Ferramentas MCP, anlise de cdigo
2. **Processamento**: Extrao de entidades, gerao de manifestos
3. **Armazenamento**: Ledger JSON, arquivos .mdc
4. **Recuperao**: Query no KG, busca em manifestos

### Exemplos de Uso
```python
# Adicionar entidade ao KG
kg_service.add_entity(entity="neocortex", entity_type="framework")

# Adicionar relao
kg_service.add_relation(
    source="pulse_scheduler",
    relation="part_of",
    target="neocortex"
)

# Gerar manifesto para lobe
manifest_service.generate_manifest("NC-LBE-FR-CORE-001.mdc")
```
"""

    # Contedo para mdulos sugeridos
    elif module == "security":
        content += """
## Segurana e Autenticao

### Componentes de Segurana
- `SecurityService`: Validao de acesso, criptografia
- `ProfileManager`: Gesto de perfis e permisses
- `AgentSession`: Sesses de agentes, autenticao

### Autenticao
- Tokens JWT para agentes
- API keys para integraes externas
- Session-based authentication para CLI

### Autorizao
- RBAC (Role-Based Access Control)
- Perfis: admin, developer, viewer, guest
- Permisses granulares por recurso

### Criptografia
- Sensitive data encryption at rest
- TLS/SSL para comunicaes
- Hash de senhas e tokens

### Auditoria
- Log de todas as operaes sensveis
- Trail de alteraes no ledger
- Monitoramento de acesso
"""

    elif module == "deployment":
        content += """
## Deploy e Operaes

### Opes de Deploy
1. **Local**: Python package, desenvolvimento
2. **Docker**: Containerizao
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
- ConfigMap para configuraes
- Secret para tokens e chaves
- Service para exposio

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
## Documentao

### Tipos de Documentao
1. **Documentao de Usurio**: Guias, tutoriais
2. **Documentao de Desenvolvedor**: API, arquitetura
3. **Documentao de Operaes**: Deploy, monitoramento
4. **Documentao de Referncia**: Schemas, contratos

### Ferramentas
- MkDocs para documentao esttica
- Sphinx para documentao de cdigo
- Swagger/OpenAPI para API documentation
- PlantUML para diagramas

### Estrutura de Diretrios
```
docs/
 user/
    getting-started.md
    tutorials/
 developer/
    architecture.md
    api-reference.md
 operations/
    deployment.md
    monitoring.md
 reference/
     schemas.md
     contracts.md
```

### Gerao Automtica
- Auto-doc from docstrings
- Schema documentation from JSON schemas
- Tool documentation from MCP tool manifests
"""

    elif module == "integration":
        content += """
## Integraes e APIs

### Protocolos Suportados
1. **MCP (Model Context Protocol)**: Integrao com IDEs
2. **A2A (Agent-to-Agent)**: Comunicao entre agentes
3. **REST API**: Para integraes externas
4. **WebSocket**: Comunicao em tempo real

### MCP Server
- 17 ferramentas multi-ao
- Suporte a stdio e socket modes
- Tool discovery and documentation

### A2A Protocol
- Message schemas definidos
- Agentes: cortex, security, consolidation, etc.
- Comunicao assncrona via event bus

### REST API
- CRUD para lobes, cortex, ledger
- GraphQL para queries complexas
- Webhooks para notificaes

### WebSocket
- Real-time updates
- Bi-directional communication
- Subscription to events
"""

    elif module == "monitoring":
        content += """
## Monitoramento e Logs

### Mtricas
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
## Performance e Otimizao

### Benchmarks
- `BenchmarkService`: Medio de performance
- Metrics: latency, throughput, memory, CPU
- Comparative analysis

### Otimizaes
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
