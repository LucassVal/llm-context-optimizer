# NC-ALN-FR-001 - Alinhamento Arquitetural NeoCortex

> **Documento de alinhamento entre o estado atual do framework e o plano arquitetural de 6 fases para atingir maturidade 98/100**

---

## 📊 Estado Atual do Framework (2026-04-10)

### **Progresso Real**
- **Ferramentas MCP:** 17/16 (ultrapassou meta original)
- **Ações implementadas:** 65/81 (80% concluído)
- **Pulse Scheduler:** Implementado e operacional
- **Arquitetura Modular:** Concluída (core/, mcp/tools/, repositories/)
- **JSON Schemas:** Definidos (ledger, A2A messages)
- **Repository Pattern:** Implementado (FileSystemRepository)
- **Serviços de Negócio:** 17 serviços implementados

### **Pontos Críticos Identificados**
1. **ConfigProvider ausente** - Paths hardcoded em `file_utils.py` e repositórios
2. **Singleton/globals** - Serviços usam variáveis globais, dificultando testes
3. **Interfaces genéricas** - `LedgerRepository` usado para tudo, violando ISP
4. **Falta de testes unitários** - Cobertura 0%
5. **Ausência de EventBus/IoC** - Acoplamento direto entre serviços

---

## 🏗️ Plano Arquitetural de 6 Fases (100% Cobertura da Auditoria)

| Fase | Nome | Duração Estimada | Objetivo | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Fase 1** | Fundação para Testabilidade | 2-3 horas | Remover bloqueios críticos (ConfigProvider, Factory Pattern) | **Pendente** |
| **Fase 2** | Refinamento do Domínio | 4-6 horas | Interfaces específicas, KnowledgeUnit, DomainException | **Pendente** |
| **Fase 3** | Desacoplamento Avançado | 3-4 horas | EventBus, IoC Container, JSON Schemas | **Parcial** |
| **Fase 4** | Pulso Cognitivo Completo | 2-3 horas | PulseScheduler + ferramentas MCP | **80%** |
| **Fase 5** | Testes Unitários (T0-005) | 6-8 horas | Cobertura de testes para Services, Repositories e Tools | **Pendente** |
| **Fase 6** | Refatorações Leves e Polimento | 2-3 horas | Type hints, constantes, documentação | **Pendente** |

**Total Estimado:** **19-27 horas** (≈ 3-4 dias de trabalho focado)

---

## 🔬 FASE 1: Fundação para Testabilidade (2-3 horas)

**Objetivo:** Eliminar os bloqueios críticos que impedem a escrita de testes unitários limpos.

| Task ID | Descrição | Prioridade | Status | Entregável |
| :--- | :--- | :---: | :---: | :--- |
| **F1.1** | Criar `neocortex/config.py` com classe `Config` | **Crítica** | Pendente | `Config` centralizado |
| **F1.2** | Atualizar `file_utils.py` e repositórios para usar `Config` | **Crítica** | Pendente | Paths não hardcoded |
| **F1.3** | Remover singletons, implementar funções fábrica | **Crítica** | Pendente | Serviços instanciáveis com DI |
| **F1.4** | Atualizar `mcp/server.py` para usar fábricas | **Alta** | Pendente | Servidor funcional com nova estrutura |
| **F1.5** | Teste de sanidade: executar `neocortex server` e `neocortex tools` | **Crítica** | Pendente | Confirmação de estabilidade |

**Dependências:** Nenhuma

---

## 🧠 FASE 2: Refinamento do Domínio (4-6 horas)

**Objetivo:** Implementar as melhorias arquiteturais de médio prazo.

| Task ID | Descrição | Prioridade | Status | Entregável |
| :--- | :--- | :---: | :---: | :--- |
| **F2.1** | Criar interfaces de repositório específicas | **Alta** | Pendente | Interfaces segregadas (ISP) |
| **F2.2** | Atualizar serviços para dependências específicas | **Alta** | Pendente | Serviços com dependências corretas |
| **F2.3** | Atualizar `FileSystemRepository` para implementar todas interfaces | **Alta** | Pendente | Implementação concreta atualizada |
| **F2.4** | Criar `KnowledgeUnit` (Protocol) e implementações | **Média** | Pendente | Abstração de unidade de conhecimento |
| **F2.5** | Atualizar `AKLService` e `ConsolidationService` para usar `KnowledgeUnit` | **Média** | Pendente | AKL e Consolidação desacoplados |
| **F2.6** | Criar hierarquia de exceções de domínio | **Média** | Pendente | Exceções de domínio |
| **F2.7** | Substituir `raise Exception` genéricos | **Média** | Pendente | Código mais semântico |

**Dependências:** Fase 1 concluída

---

## 🔗 FASE 3: Desacoplamento Avançado (3-4 horas)

**Objetivo:** Implementar EventBus, IoC Container e validação com JSON Schemas.

| Task ID | Descrição | Prioridade | Status | Entregável |
| :--- | :--- | :---: | :---: | :--- |
| **F3.1** | Criar `EventBus` (Publish-Subscribe simples) | **Média** | Pendente | EventBus funcional |
| **F3.2** | Integrar `EventBus` nos serviços | **Média** | Pendente | Serviços desacoplados via eventos |
| **F3.3** | Criar `IoCContainer` simples | **Média** | Pendente | Container de Inversão de Controle |
| **F3.4** | Atualizar `mcp/server.py` para usar `IoCContainer` | **Média** | Pendente | Servidor usa IoC |
| **F3.5** | Criar JSON Schemas adicionais | **Média** | **50%** | Schemas formais (parcial) |
| **F3.6** | Criar `validators.py` com `jsonschema` | **Média** | Pendente | Validação de dados |
| **F3.7** | Integrar validação nos repositórios | **Média** | Pendente | Integridade de dados garantida |

**Progresso Parcial:** JSON Schemas já existem (ledger_schema.json, a2a_message_schema.json)

---

## 🫀 FASE 4: Pulso Cognitivo Completo (2-3 horas)

**Objetivo:** Implementar o `PulseScheduler` completo e as ferramentas MCP associadas.

| Task ID | Descrição | Prioridade | Status | Entregável |
| :--- | :--- | :---: | :---: | :--- |
| **F4.1** | Criar `neocortex/core/pulse_scheduler.py` | **Crítica** | **✅** | Agendador funcional |
| **F4.2** | Integrar `PulseScheduler` ao `mcp/server.py` | **Crítica** | **✅** | Pulso ativo no servidor |
| **F4.3** | Criar `neocortex/mcp/tools/pulse.py` | **Alta** | **✅** | Ferramenta MCP de controle |
| **F4.4** | Criar `neocortex/mcp/tools/session.py` | **Média** | Pendente | Ferramenta MCP de sessão |
| **F4.5** | Registrar novas ferramentas no `server.py` | **Alta** | **✅** | Ferramentas expostas |
| **F4.6** | Testar: `neocortex server` e `neocortex call neocortex_pulse status` | **Crítica** | Pendente | Validação |

**Progresso:** 80% - Pulse Scheduler implementado, falta ferramenta `session` e testes

---

## 🧪 FASE 5: Testes Unitários (T0-005) (6-8 horas)

**Objetivo:** Alcançar cobertura de testes >70% para Services, Repositories e Tools.

| Task ID | Descrição | Prioridade | Status | Entregável |
| :--- | :--- | :---: | :---: | :--- |
| **F5.1** | Configurar `pytest` e `pytest-mock` | **Alta** | Pendente | Ambiente de testes |
| **F5.2** | Testes para `neocortex/config.py` | **Média** | Pendente | Cobertura de Config |
| **F5.3** | Testes para `neocortex/core/*_service.py` (17 serviços) | **Alta** | Pendente | Cobertura de lógica de negócio |
| **F5.4** | Testes para `neocortex/repositories/*.py` | **Média** | Pendente | Cobertura de persistência |
| **F5.5** | Testes para `neocortex/mcp/tools/*.py` (17 ferramentas) | **Média** | Pendente | Cobertura de adaptadores MCP |
| **F5.6** | Configurar `pytest-cov` e gerar relatório | **Alta** | Pendente | Relatório de cobertura |

**Dependências:** Fases 1-3 concluídas (testabilidade garantida)

---

## ✨ FASE 6: Refatorações Leves e Polimento (2-3 horas)

**Objetivo:** Completar os itens de baixa prioridade e polir o código.

| Task ID | Descrição | Prioridade | Status | Entregável |
| :--- | :--- | :---: | :---: | :--- |
| **F6.1** | Extrair constantes mágicas para `neocortex/constants.py` | **Baixa** | Pendente | Constantes centralizadas |
| **F6.2** | Revisar e completar **type hints** em todos os arquivos | **Média** | Pendente | Código totalmente tipado |
| **F6.3** | Melhorar docstrings de todos os serviços e ferramentas | **Média** | Pendente | Documentação inline completa |
| **F6.4** | Atualizar `README.md` com nova estrutura | **Média** | Pendente | Documentação principal atualizada |

---

## 🗺️ Mapeamento com Roadmap Existente

| Plano Arquitetural | Roadmap NeoCortex | Correspondência |
| :--- | :--- | :--- |
| **Fase 1** | T0-001 (modularização) + T0-005 (testes) | Refinamento da arquitetura para testabilidade |
| **Fase 2** | T0-001 (repository pattern) + T1-001 (validação) | Evolução do domínio e interfaces |
| **Fase 3** | T0-001 (JSON Schemas) + T3-001 (hub) | Desacoplamento avançado e contratos |
| **Fase 4** | Nova fase (Pulse Scheduler) | Manutenção autônoma e monitoramento |
| **Fase 5** | T0-005 (testes unitários) | Cobertura de testes abrangente |
| **Fase 6** | T0-003 (documentação) + T0-004 (white-label) | Polimento e documentação |

---

## 🚀 Próximos Passos Imediatos (Prioridade)

1. **Implementar Fase 1** (ConfigProvider + Factory Pattern) - **2-3 horas**
   - Criar `neocortex/config.py`
   - Atualizar repositórios e serviços
   - Testar estabilidade

2. **Executar povoamento inicial do banco de memória** - **1 hora**
   - Usar `neocortex_init.scan_project`
   - Populare Córtex, Lobos, Regression Buffer
   - Criar Checkpoint Tree para Fase 1

3. **Atualizar tickets** com progresso real - **30 min**
   - Marcar T0-001 como `completed`
   - Atualizar estimativas com base no plano arquitetural

4. **Iniciar Fase 2** (Refinamento do Domínio) - **4-6 horas**
   - Criar interfaces específicas
   - Implementar `KnowledgeUnit`

---

## 📈 Métricas de Sucesso Arquitetural

| Métrica | Atual | Meta Fase 1 | Meta Final |
| :--- | :---: | :---: | :---: |
| **Cobertura de testes** | 0% | 0% | >70% |
| **Paths configuráveis** | 0% | 100% | 100% |
| **Singletons eliminados** | 0% | 100% | 100% |
| **Interfaces segregadas** | 0% | 0% | 100% |
| **EventBus implementado** | 0% | 0% | 100% |
| **IoC Container** | 0% | 0% | 100% |
| **Pulse Scheduler** | 80% | 100% | 100% |

---

## 📅 Cronograma Realista

| Dia | Foco | Horas Estimadas |
| :--- | :--- | :---: |
| **Dia 1 (hoje)** | Fase 1 + Povoamento inicial | 3-4h |
| **Dia 2** | Fase 2 (Refinamento do Domínio) | 4-6h |
| **Dia 3** | Fase 3 (Desacoplamento Avançado) | 3-4h |
| **Dia 4** | Fase 5 (Testes Unitários) parcial | 3-4h |
| **Dia 5** | Fase 5 concluir + Fase 6 | 3-4h |

**Total:** 16-22 horas (≈ 2-3 dias de trabalho focado)

---

## 🏁 Conclusão

Este plano arquitetural cobre **100% dos pontos levantados na auditoria**, transformando o NeoCortex em uma arquitetura **impecável, testável e preparada para escalar indefinidamente**.

Ao final da execução, o NeoCortex será um sistema:

- **100% testável** (sem singletons, com injeção de dependência)
- **100% configurável** (paths e constantes externalizados)
- **100% validado** (JSON Schemas garantem integridade)
- **100% desacoplado** (EventBus e IoC Container)
- **100% autônomo** (PulseScheduler mantém o contexto saudável)
- **100% documentado** (type hints, docstrings, README)

A maturidade arquitetural saltará de **87/100** para **98/100**. O NeoCortex estará pronto para escalar, ser testado, distribuído e, mais importante, **vendido** como uma infraestrutura de conhecimento de nível empresarial.

---

**Versão:** 1.0  
**Última Atualização:** 2026-04-10  
**Próxima Revisão:** 2026-04-11  
**Responsável:** OpenCode (T0 cortex executor)