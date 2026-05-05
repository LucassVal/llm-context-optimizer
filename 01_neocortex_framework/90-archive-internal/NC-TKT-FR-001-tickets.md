# NC-TKT-FR-001 - NeoCortex Development Tickets

> **Sistema de tickets para rastreamento de desenvolvimento do framework NeoCortex v4.2-cortex**

---

## **TICKETS T0 - ESSENCIAL (PHASE 1: Fundao)**

### **T0-001: Refatorao Modular do Servidor MCP**
- **ID:** `T0-001`
- **Ttulo:** Refatorar `NC-MCP-FR-001-mcp-server.py` para arquitetura modular
- **Descrio:** Separar as 16 ferramentas MCP em mdulos individuais no diretrio `tools/`. Criar estrutura `neocortex/mcp/tools/` com imports organizados. Implementar Repository Pattern, JSON Schemas e separao hexagonal (business logic vs adapters).
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `completed`
- **Estimativa:** 4-6 horas
- **Dependncias:** Nenhuma
- **Entregveis:**
  1. Estrutura de diretrios `tools/` com mdulos separados
  2. Arquivo `__init__.py` para exports
  3. Servidor principal refatorado para importar ferramentas dinamicamente
  4. Testes de importao funcionais
  5. Repository Pattern implementado (interfaces + FileSystemRepository)
  6. JSON Schemas definidos (ledger, A2A messages)
  7. Servios de negcio (CortexService, LedgerService, LobeService, ProfileService)
  8. Separao hexagonal: core/ (business logic) vs mcp/tools/ (adapters)

### **T0-002: Configurao de Packaging (pip install)**
- **ID:** `T0-002`
- **Ttulo:** Criar `requirements.txt` e `pyproject.toml` para instalao via pip
- **Descrio:** Configurar estrutura de packaging Python para permitir `pip install -e .` e distribuio via PyPI no futuro.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T0-001 (estrutura modular)
- **Entregveis:**
  1. Arquivo `requirements.txt` com dependncias mnimas
  2. Arquivo `pyproject.toml` configurado
  3. `setup.py` ou `setup.cfg` (se necessrio)
  4. Instalao local funcionando (`pip install -e .`)

### **T0-003: Documentao Raiz (README.md)**
- **ID:** `T0-003`
- **Ttulo:** Escrever `README.md` completo para o repositrio raiz
- **Descrio:** Criar documentao de instalao, uso rpido, arquitetura e exemplos para desenvolvedores.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T0-002 (packaging)
- **Entregveis:**
  1. `README.md` na raiz do projeto
  2. Sees: Introduo, Instalao, Uso Rpido, Arquitetura, Contribuio
  3. Exemplos de cdigo funcionais
  4. Links para documentao detalhada

### **T0-004: White-Label Documentation**
- **ID:** `T0-004`
- **Ttulo:** Completar `white_label/NC-DOC-WL-001-readme.md` com guia de 5 minutos
- **Descrio:** Criar template white-label completo com exemplos prticos de como usar o NeoCortex em novos projetos.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T0-003 (README)
- **Entregveis:**
  1. `NC-DOC-WL-001-readme.md` completo
  2. Exemplos prticos passo-a-passo
  3. Template de cortex para clientes
  4. Guia de migrao de projetos existentes

### **T0-005: Testes Unitrios Bsicos**
- **ID:** `T0-005`
- **Ttulo:** Adicionar testes unitrios para funes auxiliares
- **Descrio:** Criar testes para `read_cortex`, `write_ledger`, `find_lobes` e outras funes utilitrias.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependncias:** T0-001 (estrutura modular)
- **Entregveis:**
  1. Arquivo `test_utils.py` com testes bsicos
  2. Cobertura >70% das funes auxiliares
  3. Configurao `pytest` funcionando
  4. Testes de integrao simples

### **T0-006: CI/CD Pipeline (GitHub Actions)**
- **ID:** `T0-006`
- **Ttulo:** Configurar GitHub Actions para CI (lint, testes, build)
- **Descrio:** Implementar pipeline automatizada que roda lint, testes e build em cada push.
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T0-005 (testes)
- **Entregveis:**
  1. Arquivo `.github/workflows/ci.yml`
  2. Pipeline verde no push
  3. Lint com `black`/`ruff` configurado
  4. Build automtico do pacote

### **T0-007: Benchmarks Oficiais**
- **ID:** `T0-007`
- **Ttulo:** Executar benchmark completo e publicar em `BENCHMARKS.md`
- **Descrio:** Rodar testes `Titanomachy`, `Drift` e publicar mtricas oficiais de economia (-38% tokens, -80% drift).
- **Fase:** PHASE 1
- **Prioridade:** T0 (Crtica)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T0-001 (estrutura estvel)
- **Entregveis:**
  1. `BENCHMARKS.md` atualizado com resultados
  2. Mtricas validadas: token reduction, context drift
  3. Scripts de benchmark reproduzveis
  4. Grficos/visualizaes (opcional)

---

## **TICKETS T1 - PRIORITRIO (PHASE 2: MCP)**

### **T1-001: Autenticao e Validao MCP**
- **ID:** `T1-001`
- **Ttulo:** Adicionar autenticao e validao s ferramentas MCP
- **Descrio:** Integrar sistema de permisses hierrquicas nas ferramentas `neocortex_security` e `neocortex_peers`.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependncias:** T0-001 (MCP modular)
- **Entregveis:**
  1. Integrao do `profile_manager` com MCP server
  2. Ao `validate_access` em `neocortex_security`
  3. Controle de acesso baseado em hierarquia
  4. Testes de permisses

### **T1-002: Cliente CLI**
- **ID:** `T1-002`
- **Ttulo:** Criar cliente CLI (`NC-CLI-FR-001-cli-tool.py`)
- **Descrio:** Desenvolver interface de linha de comando para interagir com o framework NeoCortex.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependncias:** T0-001 (MCP modular)
- **Entregveis:**
  1. `NC-CLI-FR-001-cli-tool.py` funcional
  2. Comandos: `init`, `checkpoint`, `ledger`, `tools`, `profile`
  3. Integrao com MCP server via stdio
  4. Documentao de uso

### **T1-003: Testes de Integrao com IDEs**
- **ID:** `T1-003`
- **Ttulo:** Testar integrao MCP com VS Code/Cursor/Antigravity
- **Descrio:** Validar que as 16 ferramentas funcionam corretamente em IDEs reais.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T1-001 (autenticao), T1-002 (CLI)
- **Entregveis:**
  1. Guia de integrao para cada IDE
  2. Configuraes de exemplo (`mcp.json`)
  3. Validao de ferramentas visveis
  4. Relatrio de compatibilidade

### **T1-004: Documentao de Ferramentas MCP**
- **ID:** `T1-004`
- **Ttulo:** Documentar todas as 16 ferramentas MCP com exemplos de uso
- **Descrio:** Criar referncia de API completa para desenvolvedores.
- **Fase:** PHASE 2
- **Prioridade:** T1 (Alta)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependncias:** T0-003 (README)
- **Entregveis:**
  1. Arquivo `MCP-API-REFERENCE.md`
  2. Exemplos para cada ao (54 total)
  3. Padres de uso recomendados
  4. Guia de troubleshooting

---

## **TICKETS T2 - IMPORTANTE (PHASE 3: Aprendizado)**

### **T2-001: Perfil Pessoal (Lucas.json) Integrado**
- **ID:** `T2-001`
- **Ttulo:** Integrar perfil `Lucas.json` como perfil de desenvolvedor base
- **Descrio:** Converter o perfil pessoal existente para schema NeoCortex e integrar ao sistema.
- **Fase:** PHASE 3
- **Prioridade:** T2 (Mdia)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T1-001 (sistema de perfis)
- **Entregveis:**
  1. Perfil convertido em `NC-PRF-USR-001-profile.json`
  2. Integrao com `profile_manager`
  3. Testes de carregamento e validao
  4. Mapeamento completo de campos

### **T2-002: Sistema de Predies**
- **ID:** `T2-002`
- **Ttulo:** Implementar engine de predies baseada em padres
- **Descrio:** Desenvolver modelo simples de predio baseado em histrico de tarefas e preferncias.
- **Fase:** PHASE 3
- **Prioridade:** T2 (Mdia)
- **Status:** `pending`
- **Estimativa:** 4-5 horas
- **Dependncias:** T2-001 (perfil integrado)
- **Entregveis:**
  1. Mdulo `prediction_engine.py`
  2. Modelo de aprendizado supervisionado bsico
  3. API para sugerir prximas aes
  4. Testes com dados simulados

### **T2-003: Assistente que Aprende (Learning Loop)**
- **ID:** `T2-003`
- **Ttulo:** Criar loop de aprendizado contnuo para o assistente
- **Descrio:** Implementar feedback loop onde o sistema aprende com correes e preferncias do usurio.
- **Fase:** PHASE 3
- **Prioridade:** T2 (Mdia)
- **Status:** `pending`
- **Estimativa:** 4-5 horas
- **Dependncias:** T2-002 (predies)
- **Entregveis:**
  1. Sistema de feedback e correo
  2. Atualizao automtica de perfis
  3. Log de aprendizado no ledger
  4. Interface para reviso de erros

---

## **TICKETS T3 - COMPLEMENTAR (PHASE 4: Colaborao)**

### **T3-001: Hub Multi-Usurio**
- **ID:** `T3-001`
- **Ttulo:** Evoluir framework para hub MCP multi-usurio com perfis hierrquicos
- **Descrio:** Permitir colaborao controlada em empresas, escolas, governos com controle de acesso baseado em nveis.
- **Fase:** PHASE 4
- **Prioridade:** T3 (Baixa)
- **Status:** `pending`
- **Estimativa:** 6-8 horas
- **Dependncias:** T1-001 (autenticao), T2-001 (perfis)
- **Entregveis:**
  1. Schemas para dev/team profiles
  2. Controle de acesso baseado em nveis
  3. Regras: ler inferiores/laterais, no superiores
  4. Testes de cenrios colaborativos

### **T3-002: Compartilhamento de Conhecimento**
- **ID:** `T3-002`
- **Ttulo:** Implementar sistema de compartilhamento de conhecimento entre usurios
- **Descrio:** Permitir que padres, templates e workflows sejam compartilhados dentro da hierarquia.
- **Fase:** PHASE 4
- **Prioridade:** T3 (Baixa)
- **Status:** `pending`
- **Estimativa:** 4-5 horas
- **Dependncias:** T3-001 (hub multi-usurio)
- **Entregveis:**
  1. Sistema de templates compartilhados
  2. Repositrio de padres aprovados
  3. Controle de verso para conhecimento
  4. Interface de busca e reutilizao

### **T3-003: Governana e Auditoria**
- **ID:** `T3-003`
- **Ttulo:** Adicionar sistema de governana e auditoria avanada
- **Descrio:** Implementar logging detalhado, aprovaes de mudanas e relatrios de conformidade.
- **Fase:** PHASE 4
- **Prioridade:** T3 (Baixa)
- **Status:** `pending`
- **Estimativa:** 3-4 horas
- **Dependncias:** T1-001 (segurana)
- **Entregveis:**
  1. Sistema de auditoria completo
  2. Relatrios de conformidade
  3. Workflows de aprovao
  4. Exportao de logs para anlise

---

## **TICKETS T4 - ECOSSISTEMA (PHASE 5: Distribuio)**

### **T4-001: Distribuio PyPI**
- **ID:** `T4-001`
- **Ttulo:** Publicar pacote no PyPI como `neocortex-framework`
- **Descrio:** Configurar publicao automatizada no PyPI com versionamento semntico.
- **Fase:** PHASE 5
- **Prioridade:** T4 (Muito Baixa)
- **Status:** `pending`
- **Estimativa:** 2-3 horas
- **Dependncias:** T0-002 (packaging), T0-006 (CI/CD)
- **Entregveis:**
  1. Conta PyPI configurada
  2. Workflow de publicao automatizada
  3. Versionamento semntico (`0.1.0`)
  4. Testes de instalao remota

### **T4-002: Comunidade e Documentao**
- **ID:** `T4-002`
- **Ttulo:** Criar comunidade e documentao abrangente
- **Descrio:** Desenvolver site/documentao, exemplos avanados, guias de contribuio.
- **Fase:** PHASE 5
- **Prioridade:** T4 (Muito Baixa)
- **Status:** `pending`
- **Estimativa:** 5-6 horas
- **Dependncias:** T0-003 (README), T1-004 (API docs)
- **Entregveis:**
  1. Site/documentao esttica
  2. Tutoriais passo-a-passo
  3. Guia de contribuio
  4. Exemplos de projetos reais

### **T4-003: Artigo Tcnico**
- **ID:** `T4-003`
- **Ttulo:** Escrever artigo tcnico sobre NeoCortex Framework
- **Descrio:** Documentar arquitetura, inovaes, benchmarks e casos de uso para publicao tcnica.
- **Fase:** PHASE 5
- **Prioridade:** T4 (Muito Baixa)
- **Status:** `pending`
- **Estimativa:** 6-8 horas
- **Dependncias:** T0-007 (benchmarks), T3-001 (hub)
- **Entregveis:**
  1. Artigo tcnico completo
  2. Dados de benchmark validados
  3. Diagramas de arquitetura
  4. Estudo de caso real

---

## **Prioridade de Implementao**

1. **T0 Tickets (Essencial):** T0-001  T0-007 (sequencial)
2. **T1 Tickets (Prioritrio):** T1-001  T1-004 (aps T0)
3. **T2 Tickets (Importante):** T2-001  T2-003 (aps T1)
4. **T3 Tickets (Complementar):** T3-001  T3-003 (aps T2)
5. **T4 Tickets (Ecossistema):** T4-001  T4-003 (aps T3)

---

## **TICKETS T5 - ORQUESTRAO MULTI-AGENTE (PHASE 6: Capacidade Avanada)**

### **ORCH-001: Script de Inicializao do Sub-MCP Server**
- **ID:** `ORCH-001`
- **Ttulo:** Criar script de inicializao do sub-MCP server (`neocortex/mcp/sub_server.py`)
- **Descrio:** Script que aceita argumentos --port, --lobe-dir, --tools para iniciar um servidor MCP isolado.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avanada)
- **Status:** `completed`
- **Estimativa:** 2-3 horas

### **ORCH-002: Ferramenta MCP `neocortex_subserver`**
- **ID:** `ORCH-002`
- **Ttulo:** Criar ferramenta MCP `neocortex_subserver` (orquestrador)
- **Descrio:** Ferramenta com aes spawn, stop, list_active, send_task para gerenciar sub-servidores.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avanada)
- **Status:** `completed`
- **Estimativa:** 2-3 horas

### **ORCH-003: Ferramenta MCP `neocortex_task`**
- **ID:** `ORCH-003`
- **Ttulo:** Criar ferramenta MCP `neocortex_task` (receptor de tarefas)
- **Descrio:** Ferramenta com aes execute, list_queued, get_result, cancel para execuo de tarefas em sub-servidores.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avanada)
- **Status:** `completed`
- **Estimativa:** 2-3 horas

### **ORCH-004: Lobos Isolados para Fire Test**
- **ID:** `ORCH-004`
- **Ttulo:** Criar lobos isolados para fire test (guardian, backend_dev, indexer)
- **Descrio:** Trs diretrios de lobos com arquivos .agents/rules dedicados para validao multi-agente.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avanada)
- **Status:** `completed`
- **Estimativa:** 3-4 horas

### **ORCH-005: Orquestrao do Fire Test**
- **ID:** `ORCH-005`
- **Ttulo:** Orquestrar execuo do fire test (spawn 3 sub-servers, enviar tarefas paralelas)
- **Descrio:** Validao de coordenao e isolamento multi-agente.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avanada)
- **Status:** `completed`
- **Estimativa:** 4-5 horas

### **ORCH-006: Validao de Resilincia**
- **ID:** `ORCH-006`
- **Ttulo:** Validar resilincia (deteco de falhas, isolamento, tratamento de concorrncia)
- **Descrio:** Relatrio de teste com verificao de recuperao de falhas e isolamento.
- **Fase:** PHASE 6
- **Prioridade:** T5 (Capacidade Avanada)
- **Status:** `completed`
- **Estimativa:** 3-4 horas

## **TICKETS T6 - ARQUITETURA EMPRESARIAL (PHASE 7: Futuro)**

> **Nota:** Tickets T6 detalhados sero adicionados conforme a Phase 7 for iniciada. Seguem os grupos principais:

- **HIER-001 a HIER-005:** Arquitetura hierrquica de lobos (auditoria, design, implementao, ferramenta MCP, audit trail)
- **CONN-001 a CONN-004:** Conectividade de rede (mDNS, gRPC, Tailscale, MCP Gateway)
- **TEST-001 a TEST-003:** Validao (hierarquia, conectividade, segurana)
- **DOC-001 a DOC-005:** Documentao (relatrios, guias, manuais)
- **VAL-001:** Validao final

**Total de Tickets:** 20 (T0-T4) + 6 (T5) + 18 (T6) = 44 tickets  
**Estimativa Total:** ~60-80 horas (T0-T4) + ~15-20 horas (T5) + ~45-60 horas (T6) = ~120-160 horas  
**Timeline Estimada:** 6-8 semanas (considerando desenvolvimento incremental)

---

**Verso:** 2.0 (Expanded)  
**ltima Atualizao:** 2026-04-10  
**Prxima Reviso:** 2026-04-11  
**Responsvel:** OpenCode (T0 cortex executor)