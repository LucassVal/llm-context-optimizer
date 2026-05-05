# RESOLUÇÃO NC-POL-NAM-001: CONVENÇÃO DE NOMENCLATURA NC-

## 📜 STATUS: OFICIAL - VIGENTE A PARTIR DE 22/04/2026

## 🎯 OBJETIVO

Estabelecer padrão obrigatório para nomenclatura de arquivos no sistema NeoCortex, garantindo:
1. **Consistência** em toda a base de código
2. **Rastreabilidade** de origem e propósito
3. **SSOT (Single Source of Truth)** para auditoria
4. **Manutenibilidade** a longo prazo

## 📋 ARTIGO 1: PADRÃO OBRIGATÓRIO

### 1.1 Formato Geral
```
NC-<TIPO>-<SIGLA>-<NUM>-<descrição>.<extensão>
```

### 1.2 Componentes Obrigatórios

| Componente | Descrição | Exemplo |
|------------|-----------|---------|
| **NC-** | Prefixo obrigatório | NC- |
| **TIPO** | Categoria do arquivo (3 letras) | SCR, SVC, CFG, DOC |
| **SIGLA** | Sigla específica (3-4 letras) | ANL, AUD, TST, MCP |
| **NUM** | Identificador único (6+ dígitos) | 001, 22160444 |
| **descrição** | Descrição em kebab-case | naming-convention-fix |
| **extensão** | Extensão padrão | .py, .md, .yaml |

## 📋 ARTIGO 2: CATEGORIAS OFICIAIS (TIPO)

### 2.1 Categorias Principais

| TIPO | Nome Completo | Uso | Exemplo |
|------|---------------|-----|---------|
| **SCR** | Script | Scripts Python executáveis | NC-SCR-ANL-001-data-analysis.py |
| **SVC** | Service | Serviços/sistemas principais | NC-SVC-MCP-001-http-proxy.py |
| **CFG** | Configuration | Arquivos de configuração | NC-CFG-AUT-001-autoloader.yaml |
| **DOC** | Documentation | Documentação Markdown | NC-DOC-NAM-001-naming-policy.md |
| **RPT** | Report | Relatórios JSON/outros | NC-RPT-AUD-001-compliance.json |
| **POL** | Policy | Políticas/resoluções | NC-POL-NAM-001-naming-resolution.md |
| **AUD** | Audit | Auditorias/verificações | NC-AUD-SYS-001-system-check.py |
| **TST** | Test | Testes automatizados | NC-TST-INT-001-integration-test.py |
| **PLN** | Plan | Planos/roadmaps | NC-PLN-DEV-001-roadmap.yaml |
| **HLP** | Helper | Utilitários/helpers | NC-HLP-VAL-001-validation.py |

### 2.2 Siglas Específicas (SIGLA)

| SIGLA | Descrição | Exemplo |
|-------|-----------|---------|
| **ANL** | Análise | NC-SCR-ANL-001-data-analysis.py |
| **AUD** | Auditoria | NC-SCR-AUD-001-compliance-check.py |
| **MCP** | MCP Integration | NC-SVC-MCP-001-http-server.py |
| **TST** | Teste | NC-SCR-TST-001-unit-test.py |
| **VAL** | Validação | NC-SCR-VAL-001-yaml-validate.py |
| **NAM** | Naming | NC-DOC-NAM-001-convention-guide.md |
| **SYS** | Sistema | NC-RPT-SYS-001-system-report.json |
| **CMP** | Compliance | NC-SVC-CMP-001-monitor.py |
| **CHK** | Checkpoint | NC-SVC-CHK-001-backup.py |
| **HOF** | Handoff | NC-SVC-HOF-001-transfer.py |

## 📋 ARTIGO 3: REGRAS DE TRANSIÇÃO

### 3.1 Arquivos Novos (A partir de 22/04/2026)
- **OBRIGATÓRIO**: Seguir padrão NC- desde a criação
- **VALIDAÇÃO**: Hook de pre-commit rejeita arquivos sem NC-
- **NUMERAÇÃO**: Usar timestamp (YYYYMMDDHHMM) ou sequencial

### 3.2 Arquivos Existentes (Legado)
- **PERMITIDO**: Manter nomes originais
- **REQUISITO**: Registro no SSOT (NC-RPT-LEG-001-legacy-files.json)
- **AUDITORIA**: Verificação periódica de conformidade
- **MIGRAÇÃO**: Opcional, apenas se necessário para funcionalidade

### 3.3 Arquivos Críticos (Não renomeáveis)
```
# LISTA OFICIAL DE ARQUIVOS CRÍTICOS
1. .pre-commit-config.yaml
2. opencode.json
3. validate_yaml.py
4. pre_commit_hook.py
5. test_sanitization.py
6. fix_tickets_yaml.py
```

## 📋 ARTIGO 4: SISTEMA DE VALIDAÇÃO

### 4.1 Pre-commit Hook Automático
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-nc-naming
        name: Validate NC- naming convention
        entry: python NC-HLP-VAL-001-naming-validator.py
        language: system
        stages: [commit]
        pass_filenames: true
```

### 4.2 Validador Python
```python
# NC-HLP-VAL-001-naming-validator.py
def validate_nc_naming(filename):
    """Valida se arquivo segue padrão NC-"""
    if filename in CRITICAL_FILES:
        return True  # Arquivos críticos são isentos
    
    if not filename.startswith("NC-"):
        print(f"ERRO: {filename} não segue padrão NC-")
        return False
    
    # Valida formato: NC-TIPO-SIGLA-NUM-desc.ext
    pattern = r'^NC-[A-Z]{3}-[A-Z]{3,4}-\d{3,}-[a-z0-9-]+\.[a-z]+$'
    return bool(re.match(pattern, filename))
```

### 4.3 Auditoria Periódica
```bash
# Executar mensalmente
python NC-AUD-SYS-001-compliance-audit.py --report --fix
```

## 📋 ARTIGO 5: SSOT (SINGLE SOURCE OF TRUTH)

### 5.1 Registro de Arquivos Legados
```json
{
  "legacy_files": [
    {
      "filename": "validate_yaml.py",
      "category": "CRITICAL",
      "reason": "Validador YAML essencial",
      "exemption_code": "CRIT-001",
      "last_audit": "2026-04-22",
      "compliance_status": "EXEMPT"
    }
  ]
}
```

### 5.2 Auditoria de Conformidade
- **Frequência**: Mensal
- **Escopo**: Todos os arquivos no sistema
- **Métrica**: % de conformidade com NC-
- **Meta**: >90% de conformidade

### 5.3 Relatório SSOT
```json
{
  "audit_date": "2026-04-22",
  "total_files": 150,
  "nc_compliant": 112,
  "legacy_exempt": 25,
  "non_compliant": 13,
  "compliance_rate": "74.7%",
  "recommendations": ["Renomear 13 arquivos não críticos"]
}
```

## 📋 ARTIGO 6: PROCESSO DE EXCEÇÃO

### 6.1 Solicitação de Exceção
1. Criar ticket no formato: `NC-TKT-EXC-001-exception-request.yaml`
2. Justificar necessidade técnica
3. Especificar duração da exceção
4. Aprovação requerida por 2 mantenedores

### 6.2 Exceções Automáticas
```yaml
# NC-CFG-EXC-001-auto-exceptions.yaml
auto_exceptions:
  - pattern: "C_Temp_*.py"
    reason: "Arquivos temporários de debug"
    duration: "24h"
  
  - pattern: "scratchpad_*.md"
    reason: "Rascunhos/notas temporárias"
    duration: "7d"
  
  - pattern: "*.metadata.json"
    reason: "Metadados gerados automaticamente"
    duration: "PERMANENT"
```

## 📋 ARTIGO 7: MIGRAÇÃO CONTROLADA

### 7.1 Critérios para Migração
1. **Necessidade funcional** (ex: import/export quebrado)
2. **Consolidação** (ex: arquivos duplicados)
3. **Refatoração major** (ex: reestruturação de módulos)
4. **Aprovação** via PR com revisão de 2 pessoas

### 7.2 Processo de Migração
```bash
# Passo 1: Backup
python NC-HLP-BKP-001-safe-backup.py --target arquivo_antigo.py

# Passo 2: Renomeação
python NC-HLP-RNM-001-safe-rename.py \
  --old arquivo_antigo.py \
  --new NC-SCR-NEW-001-novo-nome.py

# Passo 3: Validação
python NC-TST-INT-001-post-rename-test.py

# Passo 4: Atualização SSOT
python NC-AUD-SYS-001-update-ssot.py --migrated arquivo_antigo.py
```

## 📋 ARTIGO 8: RESPONSABILIDADES

### 8.1 Mantenedores
- **@lucasvalerio**: Proprietário da política
- **@sistema**: Validação automática via hooks
- **@equipe**: Cumprimento em novos arquivos

### 8.2 Penalidades por Não Conformidade
1. **Aviso**: PR rejeitado pelo hook
2. **Correção**: Requerida dentro de 24h
3. **Escalação**: Após 3 violações, revisão obrigatória

## 📋 ARTIGO 9: VIGÊNCIA E REVISÃO

### 9.1 Vigência
- **Data de início**: 22 de Abril de 2026
- **Revisão programada**: 22 de Outubro de 2026
- **Validade**: Indeterminada, sujeita a revisão

### 9.2 Processo de Revisão
1. Coletar métricas de 6 meses
2. Analisar eficácia do sistema
3. Propostas de melhoria via `NC-POL-REV-001-policy-review.md`
4. Votação entre mantenedores

## 📋 ARTIGO 10: DISPOSIÇÕES FINAIS

### 10.1 Eficácia Imediata
Esta resolução entra em vigor imediatamente após sua publicação no repositório principal.

### 10.2 Hierarquia
Esta política tem precedência sobre qualquer convenção de nomenclatura anterior.

### 10.3 Publicação
Publicado em: `brain/NC-POL-NAM-001-naming-convention-resolution.md`

---

## 🏛️ ASSINATURAS

| Nome | Cargo | Data | Assinatura |
|------|-------|------|------------|
| **Sistema NeoCortex** | Autoridade de Governança | 22/04/2026 | `NC-SYS-GOV-001` |
| **Lucas Valério** | Proprietário do Sistema | 22/04/2026 | `@lucasvalerio` |

---

## 📎 ANEXOS

1. **NC-RPT-LEG-001-legacy-files.json** - Registro de arquivos legados
2. **NC-CFG-EXC-001-auto-exceptions.yaml** - Exceções automáticas
3. **NC-HLP-VAL-001-naming-validator.py** - Validador de nomenclatura
4. **NC-AUD-SYS-001-compliance-audit.py** - Auditoria de conformidade

---

**"A consistência na nomenclatura é a base da manutenibilidade a longo prazo."**