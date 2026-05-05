# NC-DOC-LEG-001: DOCUMENTAÇÃO DE ARQUIVOS LEGADOS

## 📜 STATUS: DOCUMENTAÇÃO OFICIAL - VIGENTE

## 🎯 OBJETIVO

Documentar arquivos legados que NÃO seguem convenção NC-, garantindo:
1. **Rastreabilidade** de origem e propósito
2. **SSOT (Single Source of Truth)** para auditoria
3. **Justificativa técnica** para manutenção do nome original
4. **Plano de migração** quando aplicável

## 📋 CATEGORIAS DE ARQUIVOS LEGADOS

### 1. ARQUIVOS CRÍTICOS (Não renomeáveis)
Arquivos essenciais para funcionamento do sistema. **NUNCA** devem ser renomeados.

| Arquivo | Categoria | Justificativa | Exemption Code |
|---------|-----------|---------------|----------------|
| **`.pre-commit-config.yaml`** | Configuração | Configuração global de hooks de pre-commit | `CRIT-001` |
| **`opencode.json`** | Configuração | Configuração principal do OpenCode | `CRIT-002` |
| **`validate_yaml.py`** | Validação | Validador YAML essencial para sistema | `CRIT-003` |
| **`pre_commit_hook.py`** | Validação | Hook de pre-commit principal | `CRIT-004` |
| **`test_sanitization.py`** | Teste | Testes de sanitização críticos | `CRIT-005` |
| **`fix_tickets_yaml.py`** | Correção | Corretor de tickets YAML | `CRIT-006` |

### 2. ARQUIVOS DE TRANSIÇÃO (Temporários)
Arquivos criados durante migração NC-. Podem ser removidos após estabilização.

| Arquivo | Categoria | Justificativa | Data de Expiração |
|---------|-----------|---------------|-------------------|
| **`safe_naming_fix.py`** | Migração | Script inicial de análise NC- | 2026-05-22 |
| **`safe_naming_fix_v2.py`** | Migração | Script v2 de análise NC- | 2026-05-22 |
| **`safe_naming_fix_v3.py`** | Migração | Script v3 de análise NC- | 2026-05-22 |
| **`analyze_naming_simple.py`** | Migração | Análise simplificada | 2026-05-22 |
| **`apply_naming_fix_safe.py`** | Migração | Aplicação segura de NC- | 2026-05-22 |
| **`apply_naming_fix_auto.py`** | Migração | Aplicação automática | 2026-05-22 |
| **`apply_naming_yaml_json.py`** | Migração | Aplicação YAML/JSON | 2026-05-22 |
| **`fix_json_conflicts.py`** | Migração | Correção de conflitos JSON | 2026-05-22 |
| **`apply_naming_md.py`** | Migração | Aplicação Markdown | 2026-05-22 |
| **`apply_naming_final.py`** | Migração | Aplicação final | 2026-05-22 |
| **`check_naming_hook.py`** | Validação | Hook de validação NC- | PERMANENTE |
| **`final_validation.py`** | Validação | Validação final | 2026-05-22 |
| **`test_system_after_rename.py`** | Teste | Testes pós-renomeação | 2026-05-22 |
| **`safe_rename_markdown.py`** | Migração | Renomeação segura de MD | 2026-05-22 |

### 3. ARQUIVOS TEMPORÁRIOS (Debug/Desenvolvimento)
Arquivos criados automaticamente ou para debug.

| Arquivo | Categoria | Justificativa | Data de Expiração |
|---------|-----------|---------------|-------------------|
| **`C_Temp_chk121.py`** | Debug | Checkpoint temporário | 24h após criação |
| **`C_Temp_imp121.py`** | Debug | Import temporário | 24h após criação |
| **`C_Temp_run121.py`** | Debug | Execução temporária | 24h após criação |
| **`test_f841_metrics_store.py`** | Teste | Teste específico de métricas | 2026-05-22 |

### 4. ARQUIVOS DE SISTEMA (Gerados automaticamente)
Arquivos criados/atualizados automaticamente pelo sistema.

| Arquivo | Categoria | Justificativa | Frequência de Atualização |
|---------|-----------|---------------|---------------------------|
| **`checkpoints_log.json`** | Log | Log de checkpoints do sistema | Contínua |
| **`handoffs_log.json`** | Log | Log de handoffs do sistema | Contínua |
| **`monitoring_log.json`** | Log | Log de monitoramento | Contínua |
| **`ticket_fix_report.json`** | Relatório | Relatório de correção de tickets | Após cada correção |
| **`master_decision.json`** | Decisão | Decisões mestras do sistema | Quando necessário |
| **`*.metadata.json`** | Metadados | Metadados de arquivos Markdown | Automático |

### 5. ARQUIVOS DE RELATÓRIO (Gerados por auditoria)
Relatórios gerados automaticamente por scripts de auditoria.

| Padrão | Categoria | Justificativa | Retenção |
|--------|-----------|---------------|----------|
| **`compliance_check_*.json`** | Auditoria | Relatórios de compliance | 30 dias |
| **`CP_*.json`** | Checkpoint | Checkpoints do sistema | 90 dias |
| **`HANDOFF_*.json`** | Handoff | Handoffs do sistema | 90 dias |
| **`naming_*.json`** | Migração | Relatórios de naming | 60 dias |
| **`naming_*.py`** | Migração | Scripts de naming | 60 dias |

## 📋 JUSTIFICATIVAS TÉCNICAS DETALHADAS

### 1. Por que `.pre-commit-config.yaml` não pode ser renomeado?
- **Dependência do Git**: Git hooks procuram especificamente por este nome
- **Configuração global**: Referenciado por múltiplos sistemas
- **Convenção padrão**: Nome padrão da indústria para hooks de pre-commit
- **Risco**: Renomear quebraria todo o sistema de validação

### 2. Por que `opencode.json` não pode ser renomeado?
- **Ponto de entrada**: Arquivo principal do OpenCode
- **Hardcoded em ferramentas**: Múltiplas ferramentas referenciam este nome
- **Configuração crítica**: Contém credenciais e configurações sensíveis
- **Risco**: Renomear quebraria inicialização do OpenCode

### 3. Por que arquivos temporários são permitidos?
- **Necessidade de debug**: Desenvolvimento requer arquivos temporários
- **Ciclo de vida curto**: São automaticamente limpos após 24h
- **Padrão reconhecido**: Prefixo `C_Temp_` é padrão no sistema
- **Monitoramento**: Sistema SSOT rastreia e alerta sobre expiração

### 4. Por que metadados (.metadata.json) são isentos?
- **Geração automática**: Criados por ferramentas externas
- **Vinculação dinâmica**: Nome deve corresponder ao arquivo principal
- **Uso transitório**: São recriados frequentemente
- **Convenção**: Padrão de metadados em muitos sistemas

## 📋 PLANO DE MIGRAÇÃO (QUANDO APLICÁVEL)

### 1. Arquivos de Transição
```
FASE 1 (Até 22/05/2026): Manter como estão
FASE 2 (22/05-22/06): Avaliar necessidade
FASE 3 (Após 22/06/2026): Remover ou arquivar
```

### 2. Processo de Remoção Segura
```bash
# 1. Backup
python NC-HLP-BKP-001-safe-backup.py --target safe_naming_fix.py

# 2. Validação de dependências
python NC-AUD-DEP-001-dependency-check.py --file safe_naming_fix.py

# 3. Remoção (se seguro)
rm safe_naming_fix.py

# 4. Atualização SSOT
python NC-AUD-SSO-001-ssot-audit-system.py --update
```

### 3. Critérios para Manutenção Permanente
1. **Uso ativo**: Arquivo referenciado por outros sistemas
2. **Valor histórico**: Documentação importante do processo de migração
3. **Referência futura**: Pode ser útil para migrações similares
4. **Aprovação**: Decisão por comitê de 2 mantenedores

## 📋 SSOT (SINGLE SOURCE OF TRUTH)

### 1. Registro Oficial
Todos os arquivos legados estão registrados em:
- **`NC-RPT-LEG-001-legacy-files.json`** - Registro completo
- **`nc_ssot.db`** - Banco de dados SQLite com histórico

### 2. Campos do Registro SSOT
```json
{
  "filename": "validate_yaml.py",
  "category": "CRITICAL",
  "exemption_code": "CRIT-003",
  "justification": "Validador YAML essencial para sistema",
  "created_date": "2024-01-15",
  "last_audit": "2026-04-22",
  "compliance_status": "EXEMPT",
  "migration_plan": "NONE",
  "dependencies": ["pre_commit_hook.py", ".pre-commit-config.yaml"],
  "risk_assessment": "HIGH - Não renomear"
}
```

### 3. Auditoria Periódica
```bash
# Mensalmente
python NC-AUD-SSO-001-ssot-audit-system.py --audit

# Verificação de integridade
python NC-AUD-SSO-001-ssot-audit-system.py --integrity

# Relatório de conformidade
python NC-HLP-VAL-001-naming-validator.py --audit
```

## 📋 PROCESSO PARA NOVAS EXCEÇÕES

### 1. Critérios para Nova Exceção
1. **Necessidade técnica comprovada**
2. **Impacto negativo da renomeação**
3. **Alternativas consideradas e rejeitadas**
4. **Prazo definido (temporário ou permanente)**

### 2. Solicitação Formal
```yaml
# NC-TKT-EXC-001-exception-request.yaml
exception_request:
  filename: "novo_arquivo_critico.py"
  requested_by: "@username"
  date: "2026-04-22"
  
  justification: |
    Arquivo crítico que integra com sistema externo
    que espera nome específico. Renomear quebraria
    integração com API terceira.
  
  technical_details:
    external_system: "Sistema Externo XYZ"
    integration_type: "API REST"
    expected_filename: "novo_arquivo_critico.py"
  
  alternatives_considered:
    - "Wrapper com nome NC-": "Rejeitado - overhead de performance"
    - "Symlink": "Rejeitado - não suportado no Windows"
  
  requested_duration: "PERMANENT"
  supporting_docs: ["api_docs.pdf", "integration_spec.md"]
```

### 3. Aprovação
- **Requer**: 2 mantenedores
- **Processo**: Revisão técnica + votação
- **Registro**: No SSOT com justificativa detalhada
- **Revisão**: Anual para exceções permanentes

## 📋 RESPONSABILIDADES

### 1. Proprietário do Sistema
- **@lucasvalerio**: Aprovação final de exceções
- **Responsabilidade**: Garantir que exceções são tecnicamente justificadas

### 2. Mantenedores
- **Revisão técnica**: Avaliar mérito das exceções
- **Auditoria**: Verificar conformidade periódica
- **Documentação**: Manter esta documentação atualizada

### 3. Sistema Automático
- **Validação**: Hook de pre-commit NC-HLP-VAL-001
- **Auditoria**: NC-AUD-SSO-001-ssot-audit-system.py
- **Relatórios**: Geração automática de compliance reports

## 📋 PENALIDADES POR VIOLAÇÃO

### 1. Arquivos Novos sem NC-
- **1ª violação**: PR rejeitado + aviso
- **2ª violação**: Bloqueio temporário (24h)
- **3ª violação**: Revisão obrigatória com mantenedor

### 2. Modificação de Arquivos Críticos
- **Alerta imediato**: Sistema notifica mantenedores
- **Reversão automática**: Se detectado em PR
- **Análise de segurança**: Verificação de motivação

### 3. Uso Indevido de Exceções
- **Revogação**: Exceção cancelada se mal utilizada
- **Revisão**: Todas as exceções do usuário revisadas
- **Treinamento**: Obrigatório sobre convenção NC-

## 📋 REVISÃO E ATUALIZAÇÃO

### 1. Frequência de Revisão
- **Mensal**: Estatísticas de conformidade
- **Trimestral**: Revisão de exceções temporárias
- **Anual**: Revisão completa desta política

### 2. Processo de Atualização
1. Coletar métricas dos últimos períodos
2. Identificar padrões de não conformidade
3. Propostas de melhoria via `NC-POL-REV-001-policy-review.md`
4. Discussão com mantenedores
5. Aprovação por maioria
6. Publicação da nova versão

### 3. Histórico de Versões
| Versão | Data | Mudanças Principais | Aprovado Por |
|--------|------|-------------------|--------------|
| 1.0 | 22/04/2026 | Versão inicial | @lucasvalerio |
| 1.1 | 22/05/2026 | (Planejado) Revisão pós-migração | - |

---

## 🏛️ ASSINATURAS

| Nome | Cargo | Data | Assinatura |
|------|-------|------|------------|
| **Sistema NeoCortex** | Autoridade de Governança | 22/04/2026 | `NC-SYS-GOV-001` |
| **Lucas Valério** | Proprietário do Sistema | 22/04/2026 | `@lucasvalerio` |

---

## 📎 ANEXOS

1. **`NC-RPT-LEG-001-legacy-files.json`** - Registro completo de arquivos legados
2. **`NC-HLP-VAL-001-naming-validator.py`** - Validador de nomenclatura
3. **`NC-AUD-SSO-001-ssot-audit-system.py`** - Sistema de auditoria SSOT
4. **`NC-TKT-EXC-001-exception-request.yaml`** - Template de solicitação de exceção

---

**"Documentar o legado é tão importante quanto construir o novo."**