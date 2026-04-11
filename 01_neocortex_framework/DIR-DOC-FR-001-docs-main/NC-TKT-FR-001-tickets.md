# NC-TKT-FR-001 - NeoCortex Development Tickets

> **Sistema de tickets para rastreamento de desenvolvimento do framework NeoCortex v4.2-cortex**

---

## **TICKETS T0 - ESSENCIAL (PHASE 1: Fundação)**

### **T0-001: Refatoração Modular do Servidor MCP**
- **ID:** `T0-001`
- **Título:** Refatorar `NC-MCP-FR-001-mcp-server.py` para arquitetura modular
- **Descrição:** Separar as 16 ferramentas MCP em módulos individuais no diretório `tools/`. Criar estrutura `neocortex/mcp/tools/` com imports organizados. Implementar Repository Pattern, JSON Schemas e separação hexagonal (business logic vs adapters).
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `completed`
- **Estimativa:** 4-6 horas
- **Dependências:** Nenhuma
- **Entregáveis:**
  1. Estrutura de diretórios `tools/` com módulos separados
  2. Arquivo `__init__.py` para exports
  3. Servidor principal refatorado para importar ferramentas dinamicamente
  4. Testes de importação funcionais
  5. Repository Pattern implementado (interfaces + FileSystemRepository)
  6. JSON Schemas definidos (ledger, A2A messages)
  7. Serviços de negócio (CortexService, LedgerService, LobeService, ProfileService)
  8. Separação hexagonal: core/ (business logic) vs mcp/tools/ (adapters)

### **T0-002: Configuração de Packaging (pip install)**
- **ID:** `T0-002`
- **Título:** Criar `requirements.txt` e `pyproject.toml` para instalação via pip
- **Descrição:** Configurar estrutura de packaging Python para permitir `pip install -e .` e distribuição via PyPI no futuro.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T0-001 (estrutura modular)
- **Entregáveis:**
  1. Arquivo `requirements.txt` com dependências mínimas
  2. Arquivo `pyproject.toml` configurado
  3. `setup.py` ou `setup.cfg` (se necessário)
  4. Instalação local funcionando (`pip install -e .`)

### **T0-003: Documentação Raiz (README.md)**
- **ID:** `T0-003`
- **Título:** Escrever `README.md` completo para o repositório raiz
- **Descrição:** Criar documentação de instalação, uso rápido, arquitetura e exemplos para desenvolvedores.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T0-002 (packaging)
- **Entregáveis:**
  1. `README.md` na raiz do projeto
  2. Seções: Introdução, Instalação, Uso Rápido, Arquitetura, Contribuição
  3. Exemplos de código funcionais
  4. Links para documentação detalhada

### **T0-004: White-Label Documentation**
- **ID:** `T0-004`
- **Título:** Completar `white_label/NC-DOC-WL-001-readme.md` com guia de 5 minutos
- **Descrição:** Criar template white-label completo com exemplos práticos de como usar o NeoCortex em novos projetos.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T0-003 (README)
- **Entregáveis:**
  1. `NC-DOC-WL-001-readme.md` completo
  2. Exemplos práticos passo-a-passo
  3. Template de cortex para clientes
  4. Guia de migração de projetos existentes

### **T0-005: Testes Unitários Básicos**
- **ID:** `T0-005`
- **Título:** Adicionar testes unitários para funções auxiliares
- **Descrição:** Criar testes para `read_cortex`, `write_ledger`, `find_lobes` e outras funções utilitárias.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependências:** T0-001 (estrutura modular)
- **Entregáveis:**
  1. Arquivo `test_utils.py` com testes básicos
  2. Cobertura >70% das funções auxiliares
  3. Configuração `pytest` funcionando
  4. Testes de integração simples

### **T0-006: CI/CD Pipeline (GitHub Actions)**
- **ID:** `T0-006`
- **Título:** Configurar GitHub Actions para CI (lint, testes, build)
- **Descrição:** Implementar pipeline automatizada que roda lint, testes e build em cada push.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T0-005 (testes)
- **Entregáveis:**
  1. Arquivo `.github/workflows/ci.yml`
  2. Pipeline verde no push
  3. Lint com `black`/`ruff` configurado
  4. Build automático do pacote

### **T0-007: Benchmarks Oficiais**
- **ID:** `T0-007`
- **Título:** Executar benchmark completo e publicar em `BENCHMARKS.md`
- **Descrição:** Rodar testes `Titanomachy`, `Drift` e publicar métricas oficiais de economia (-38% tokens, -80% drift).
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crítica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T0-001 (estrutura estável)
- **Entregáveis:**
  1. `BENCHMARKS.md` atualizado com resultados
  2. Métricas validadas: token reduction, context drift
  3. Scripts de benchmark reproduzíveis
  4. Gráficos/visualizações (opcional)

---

## **TICKETS T1 - PRIORITÁRIO (PHASE 2: MCP)**

### **T1-001: Autenticação e Validação MCP**
- **ID:** `T1-001`
- **Título:** Adicionar autenticação e validação às ferramentas MCP
- **Descrição:** Integrar sistema de permissões hierárquicas nas ferramentas `neocortex_security` e `neocortex_peers`.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependências:** T0-001 (MCP modular)
- **Entregáveis:**
  1. Integração do `profile_manager` com MCP server
  2. Ação `validate_access` em `neocortex_security`
  3. Controle de acesso baseado em hierarquia
  4. Testes de permissões

### **T1-002: Cliente CLI**
- **ID:** `T1-002`
- **Título:** Criar cliente CLI (`NC-CLI-FR-001-cli-tool.py`)
- **Descrição:** Desenvolver interface de linha de comando para interagir com o framework NeoCortex.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependências:** T0-001 (MCP modular)
- **Entregáveis:**
  1. `NC-CLI-FR-001-cli-tool.py` funcional
  2. Comandos: `init`, `checkpoint`, `ledger`, `tools`, `profile`
  3. Integração com MCP server via stdio
  4. Documentação de uso

### **T1-003: Testes de Integração com IDEs**
- **ID:** `T1-003`
- **Título:** Testar integração MCP com VS Code/Cursor/Antigravity
- **Descrição:** Validar que as 16 ferramentas funcionam corretamente em IDEs reais.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T1-001 (autenticação), T1-002 (CLI)
- **Entregáveis:**
  1. Guia de integração para cada IDE
  2. Configurações de exemplo (`mcp.json`)
  3. Validação de ferramentas visíveis
  4. Relatório de compatibilidade

### **T1-004: Documentação de Ferramentas MCP**
- **ID:** `T1-004`
- **Título:** Documentar todas as 16 ferramentas MCP com exemplos de uso
- **Descrição:** Criar referência de API completa para desenvolvedores.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependências:** T0-003 (README)
- **Entregáveis:**
  1. Arquivo `MCP-API-REFERENCE.md`
  2. Exemplos para cada ação (54 total)
  3. Padrões de uso recomendados
  4. Guia de troubleshooting

---

## **TICKETS T2 - IMPORTANTE (PHASE 3: Aprendizado)**

### **T2-001: Perfil Pessoal (Lucas.json) Integrado**
- **ID:** `T2-001`
- **Título:** Integrar perfil `Lucas.json` como perfil de desenvolvedor base
- **Descrição:** Converter o perfil pessoal existente para schema NeoCortex e integrar ao sistema.
- **Fase:** PHASE 3
- **Prioridade:** T2 (Média)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T1-001 (sistema de perfis)
- **Entregáveis:**
  1. Perfil convertido em `NC-PRF-USR-001-profile.json`
  2. Integração com `profile_manager`
  3. Testes de carregamento e validação
  4. Mapeamento completo de campos

### **T2-002: Sistema de Predições**
- **ID:** `T2-002`
- **Título:** Implementar engine de predições baseada em padrões
- **Descrição:** Desenvolver modelo simples de predição baseado em histórico de tarefas e preferências.
- **Fase:** PHASE 3
- **Prioridade:** T2 (Média)
- **Status:** `pending`
- **Estimativa:** 4-5 horas
- **Dependências:** T2-001 (perfil integrado)
- **Entregáveis:**
  1. Módulo `prediction_engine.py`
  2. Modelo de aprendizado supervisionado básico
  3. API para sugerir próximas ações
  4. Testes com dados simulados

### **T2-003: Assistente que Aprende (Learning Loop)**
- **ID:** `T2-003`
- **Título:** Criar loop de aprendizado contínuo para o assistente
- **Descrição:** Implementar feedback loop onde o sistema aprende com correções e preferências do usuário.
- **Fase:** PHASE 3
- **Prioridade:** T2 (Média)
- **Status:** `pending`
- **Estimativa:** 4-5 horas
- **Dependências:** T2-002 (predições)
- **Entregáveis:**
  1. Sistema de feedback e correção
  2. Atualização automática de perfis
  3. Log de aprendizado no ledger
  4. Interface para revisão de erros

---

## **TICKETS T3 - COMPLEMENTAR (PHASE 4: Colaboração)**

### **T3-001: Hub Multi-Usuário**
- **ID:** `T3-001`
- **Título:** Evoluir framework para hub MCP multi-usuário com perfis hierárquicos
- **Descrição:** Permitir colaboração controlada em empresas, escolas, governos com controle de acesso baseado em níveis.
- **Fase:** PHASE 4
- **Prioridade:** T3 (Baixa)
- **Status:** `pending`
- **Estimativa:** 6-8 horas
- **Dependências:** T1-001 (autenticação), T2-001 (perfis)
- **Entregáveis:**
  1. Schemas para dev/team profiles
  2. Controle de acesso baseado em níveis
  3. Regras: ler inferiores/laterais, não superiores
  4. Testes de cenários colaborativos

### **T3-002: Compartilhamento de Conhecimento**
- **ID:** `T3-002`
- **Título:** Implementar sistema de compartilhamento de conhecimento entre usuários
- **Descrição:** Permitir que padrões, templates e workflows sejam compartilhados dentro da hierarquia.
- **Fase:** PHASE 4
- **Prioridade:** T3 (Baixa)
- **Status:** `pending`
- **Estimativa:** 4-5 horas
- **Dependências:** T3-001 (hub multi-usuário)
- **Entregáveis:**
  1. Sistema de templates compartilhados
  2. Repositório de padrões aprovados
  3. Controle de versão para conhecimento
  4. Interface de busca e reutilização

### **T3-003: Governança e Auditoria**
- **ID:** `T3-003`
- **Título:** Adicionar sistema de governança e auditoria avançada
- **Descrição:** Implementar logging detalhado, aprovações de mudanças e relatórios de conformidade.
- **Fase:** PHASE 4
- **Prioridade:** T3 (Baixa)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependências:** T1-001 (segurança)
- **Entregáveis:**
  1. Sistema de auditoria completo
  2. Relatórios de conformidade
  3. Workflows de aprovação
  4. Exportação de logs para análise

---

## **TICKETS T4 - ECOSSISTEMA (PHASE 5: Distribuição)**

### **T4-001: Distribuição PyPI**
- **ID:** `T4-001`
- **Título:** Publicar pacote no PyPI como `neocortex-framework`
- **Descrição:** Configurar publicação automatizada no PyPI com versionamento semântico.
- **Fase:** PHASE 5
- **Prioridade:** T4 (Muito Baixa)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependências:** T0-002 (packaging), T0-006 (CI/CD)
- **Entregáveis:**
  1. Conta PyPI configurada
  2. Workflow de publicação automatizada
  3. Versionamento semântico (`0.1.0`)
  4. Testes de instalação remota

### **T4-002: Comunidade e Documentação**
- **ID:** `T4-002`
- **Título:** Criar comunidade e documentação abrangente
- **Descrição:** Desenvolver site/documentação, exemplos avançados, guias de contribuição.
- **Fase:** PHASE 5
- **Prioridade:** T4 (Muito Baixa)
- **Status:** `pending`
- **Estimativa:** 5-6 horas
- **Dependências:** T0-003 (README), T1-004 (API docs)
- **Entregáveis:**
  1. Site/documentação estática
  2. Tutoriais passo-a-passo
  3. Guia de contribuição
  4. Exemplos de projetos reais

### **T4-003: Artigo Técnico**
- **ID:** `T4-003`
- **Título:** Escrever artigo técnico sobre NeoCortex Framework
- **Descrição:** Documentar arquitetura, inovações, benchmarks e casos de uso para publicação técnica.
- **Fase:** PHASE 5
- **Prioridade:** T4 (Muito Baixa)
- **Status:** `pending`
- **Estimativa:** 6-8 horas
- **Dependências:** T0-007 (benchmarks), T3-001 (hub)
- **Entregáveis:**
  1. Artigo técnico completo
  2. Dados de benchmark validados
  3. Diagramas de arquitetura
  4. Estudo de caso real

---

## **Prioridade de Implementação**

1. **T0 Tickets (Essencial):** T0-001 → T0-007 (sequencial)
2. **T1 Tickets (Prioritário):** T1-001 → T1-004 (após T0)
3. **T2 Tickets (Importante):** T2-001 → T2-003 (após T1)
4. **T3 Tickets (Complementar):** T3-001 → T3-003 (após T2)
5. **T4 Tickets (Ecossistema):** T4-001 → T4-003 (após T3)

---

## **TICKETS T5 - ORQUESTRAÇÃO MULTI-AGENTE (PHASE 6: Capacidade Avançada)**

### **ORCH-001: Script de Inicialização do Sub-MCP Server**
- **ID:** `ORCH-001`
- **Título:** Criar script de inicialização do sub-MCP server (`neocortex/mcp/sub_server.py`)
- **Descrição:** Script que aceita argumentos --port, --lobe-dir, --tools para iniciar um servidor MCP isolado.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avançada)
- **Status:** `completed`
- **Estimativa:** 2-3 horas

### **ORCH-002: Ferramenta MCP `neocortex_subserver`**
- **ID:** `ORCH-002`
- **Título:** Criar ferramenta MCP `neocortex_subserver` (orquestrador)
- **Descrição:** Ferramenta com ações spawn, stop, list_active, send_task para gerenciar sub-servidores.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avançada)
- **Status:** `completed`
- **Estimativa:** 2-3 horas

### **ORCH-003: Ferramenta MCP `neocortex_task`**
- **ID:** `ORCH-003`
- **Título:** Criar ferramenta MCP `neocortex_task` (receptor de tarefas)
- **Descrição:** Ferramenta com ações execute, list_queued, get_result, cancel para execução de tarefas em sub-servidores.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avançada)
- **Status:** `completed`
- **Estimativa:** 2-3 horas

### **ORCH-004: Lobos Isolados para Fire Test**
- **ID:** `ORCH-004`
- **Título:** Criar lobos isolados para fire test (guardian, backend_dev, indexer)
- **Descrição:** Três diretórios de lobos com arquivos .agents/rules dedicados para validação multi-agente.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avançada)
- **Status:** `completed`
- **Estimativa:** 3-4 horas

### **ORCH-005: Orquestração do Fire Test**
- **ID:** `ORCH-005`
- **Título:** Orquestrar execução do fire test (spawn 3 sub-servers, enviar tarefas paralelas)
- **Descrição:** Validação de coordenação e isolamento multi-agente.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avançada)
- **Status:** `completed`
- **Estimativa:** 4-5 horas

### **ORCH-006: Validação de Resiliência**
- **ID:** `ORCH-006`
- **Título:** Validar resiliência (detecção de falhas, isolamento, tratamento de concorrência)
- **Descrição:** Relatório de teste com verificação de recuperação de falhas e isolamento.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avançada)
- **Status:** `completed`
- **Estimativa:** 3-4 horas

## **TICKETS T6 - ARQUITETURA EMPRESARIAL (PHASE 7: Futuro)**

> **Nota:** Tickets T6 detalhados serão adicionados conforme a Phase 7 for iniciada. Seguem os grupos principais:

- **HIER-001 a HIER-005:** Arquitetura hierárquica de lobos (auditoria, design, implementação, ferramenta MCP, audit trail)
- **CONN-001 a CONN-004:** Conectividade de rede (mDNS, gRPC, Tailscale, MCP Gateway)
- **TEST-001 a TEST-003:** Validação (hierarquia, conectividade, segurança)
- **DOC-001 a DOC-005:** Documentação (relatórios, guias, manuais)
- **VAL-001:** Validação final

**Total de Tickets:** 20 (T0-T4) + 6 (T5) + 18 (T6) = 44 tickets  
**Estimativa Total:** ~60-80 horas (T0-T4) + ~15-20 horas (T5) + ~45-60 horas (T6) = ~120-160 horas  
**Timeline Estimada:** 6-8 semanas (considerando desenvolvimento incremental)

---

**Versão:** 2.0 (Expanded)  
**Última Atualização:** 2026-04-10  
**Próxima Revisão:** 2026-04-11  
**Responsável:** OpenCode (T0 cortex executor)