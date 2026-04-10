# NC-AUD-FR-001 - Resultados da Auditoria Arquitetural Preventiva

**Data da Auditoria:** 10 de abril de 2026  
**Contexto:** Avaliação completa antes de prosseguir com otimizações OPT-009 a OPT-012  
**Risco Geral:** ALTO (3 vulnerabilidades críticas identificadas)

---

## 🚨 **Vulnerabilidades Críticas (ALTO RISCO)**

### **1. Persistência Híbrida**
**Descrição:** Stores otimizados (LedgerStore, ManifestStore, LobeIndex) existem mas NÃO são utilizados pelos serviços. Sistema opera em modo híbrido (stores vs filesystem).
**Impacto:** Perda de performance, inconsistência de dados, complexidade de manutenção.
**Localização:** Sistema inteiro - falta de integração entre serviços core e stores.
**Correção Necessária:** Atualizar `get_*_service()` para usar stores otimizados.

### **2. Violação Arquitetural (MCP → Infra)**
**Descrição:** `neocortex/mcp/tools/ledger.py:87-90` acessa `FileSystemLedgerRepository` diretamente, violando a arquitetura hexagonal.
**Impacto:** Alto acoplamento, impossibilidade de trocar implementações, violação de camadas.
**Localização Exata:** `neocortex_framework/neocortex/mcp/tools/ledger.py:87-90`
```python
# CÓDIGO ATUAL (INCORRETO):
from ...repositories import FileSystemLedgerRepository
repo = FileSystemLedgerRepository()
repo.write_ledger(ledger)
```
**Correção Necessária:** Substituir por uso do `LedgerService` via `get_ledger_service()`.

### **3. Factories Não Configuráveis (Hardcoding)**
**Descrição:** `get_*_service()` hardcoded com implementações concretas (ex: `FileSystemLedgerRepository`), sem uso de `ConfigProvider`.
**Impacto:** Impossibilidade de Module Sandbox (troca dinâmica de implementações).
**Localização Exata:** `neocortex/core/ledger_service.py:27-30` e outras factories.
```python
# CÓDIGO ATUAL (INCORRETO):
from ..repositories import FileSystemLedgerRepository
self.repository = FileSystemLedgerRepository()
```
**Correção Necessária:** Implementar `RepositoryFactory` que decide implementação baseada em configuração.

---

## ⚠️ **Vulnerabilidades de MÉDIO RISCO**

### **4. PulseScheduler Assumindo Métodos Não Existentes**
**Descrição:** `self.ledger.prune_context()` pode falhar silenciosamente se o método não existir.
**Localização:** `neocortex/core/pulse_scheduler.py:90`
**Correção:** Adicionar verificação de método ou interface contratual.

### **5. Recuperação de Falhas Limitada**
**Descrição:** Sem auto-repair para cache corrompido; fallback para JSON funciona mas requer intervenção manual.
**Localização:** Stores otimizados (LedgerStore, ManifestStore).
**Correção:** Implementar auto-repair com validação de checksum.

### **6. Timeout Operations**
**Descrição:** Operações de I/O sem timeout configurável, podendo causar bloqueios.
**Localização:** Operações de leitura/escrita em stores.
**Correção:** Adicionar timeout configurável via `ConfigProvider`.

---

## 📋 **Plano de Correção Priorizado**

### **Fase 1: Consistência de Persistência** (2-3 horas)
1. **Corrigir `ledger.py`** - Substituir acesso direto por `LedgerService`
2. **Atualizar `get_ledger_service()`** - Retornar `LedgerStore` como default
3. **Executar migração completa** - Validar integridade dados

### **Fase 2: Factory Pattern Configurável** (3-4 horas)
1. **Implementar `RepositoryFactory`** - Decide implementação baseada em `Config`
2. **Atualizar todas as `get_*_service()`** - Usar `RepositoryFactory`
3. **Configurar `ConfigProvider`** - Adicionar seção `repository_implementation`

### **Fase 3: Resiliência e Error Handling** (2 horas)
1. **Adicionar auto-repair** para cache corrompido
2. **Implementar timeout** para operações de I/O
3. **Unificar logging** para inglês

### **Fase 4: Testes de Integração** (2 horas)
1. Executar suíte de testes sugerida
2. Validar performance pós-migração
3. Documentar procedimentos de recuperação

---

## 🔗 **Dependências de Implementação**

### **Pré-requisitos para OPT-009 a OPT-012:**
- [ ] Vulnerabilidades de ALTO RISCO corrigidas
- [ ] Migração completa validada
- [ ] Factory pattern configurável implementado
- [ ] Testes de integração passando

### **Impacto no Roadmap:**
- **OPT-006** (Integrar LobeIndex): Requer Fase 1 completa
- **OPT-007** (MCP tool search.py): Requer Fase 1 completa  
- **OPT-009** (Integrar HotCache): Requer Fase 2 completa
- **OPT-011/012** (Stubs): Podem ser feitos paralelamente

---

## 📊 **Métricas de Sucesso Pós-Correção**

1. **100% uso dos stores otimizados** - Nenhum acesso direto a filesystem
2. **Arquitetura hexagonal intacta** - Core → Interfaces ← Implementações
3. **Factories configuráveis** - Troca de implementações via `Config`
4. **Recuperação automática** - Auto-repair para cache corrompido
5. **Timeout configurável** - I/O com limites definidos

---

## 🗂️ **Arquivos para Correção**

### **Alto Risco:**
1. `neocortex/mcp/tools/ledger.py:87-90`
2. `neocortex/core/ledger_service.py:27-30`
3. `neocortex/core/__init__.py` (funções `get_*_service()`)

### **Médio Risco:**
4. `neocortex/core/pulse_scheduler.py:90`
5. `neocortex/infra/ledger_store.py` (adicionar auto-repair)
6. `neocortex/infra/manifest_store.py` (adicionar timeout)

---

**Status da Auditoria:** ✅ Concluída - Aguardando implementação de correções  
**Próxima Ação:** Implementar Fase 1 do plano de correção

---
*Documento gerado automaticamente em 10 de abril de 2026 - NeoCortex Framework*