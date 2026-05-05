# Monitoramento de Segurança YAML/JSON - NeoCortex

## Configuração Instalada

✅ **Hooks de pre-commit** configurados para validação automática de:
- Segurança YAML (padrões perigosos, tags Python)
- Validação JSON (XSS, scripts maliciosos)  
- Convenção de nomenclatura NC-
- Campos obrigatórios em tickets

✅ **Scripts de validação** disponíveis:
- `validate_yaml.py` - Validação completa de YAMLs
- `pre_commit_hook.py` - Hook para validação pré-commit
- `fix_tickets_yaml.py` - Correção automática de tickets

✅ **Monitoramento periódico** configurado para execução diária

## Uso

### Validação Manual
```bash
# Validar todos os YAMLs
python validate_yaml.py

# Executar hook de pre-commit
python pre_commit_hook.py
```

### Correção Automática
```bash
# Corrigir tickets YAML
python fix_tickets_yaml.py
```

### Git Hooks
Os hooks são executados automaticamente antes de cada commit.
Para executar manualmente em todos os arquivos:
```bash
pre-commit run --all-files
```

## Estrutura de Validação

1. **Segurança**: Bloqueia tags Python perigosas, scripts maliciosos
2. **Estrutura**: Valida campos obrigatórios, valores permitidos
3. **Convenção**: Verifica padrão NC- para tickets e configs
4. **Sanitização**: Remove automaticamente conteúdo perigoso

## Logs e Relatórios

- `yaml_validation_report.json` - Relatório de validação YAML
- `ticket_fix_report.json` - Relatório de correção de tickets  
- `metadata_audit_report.json` - Auditoria de metadados JSON
- `validation.log` - Log de execuções periódicas (cron)

## Manutenção

Para atualizar configuração:
```bash
pre-commit autoupdate
```

Para desinstalar hooks:
```bash
pre-commit uninstall
```

---

*Sistema configurado em: 2026-04-22*
*NeoCortex Framework - Compliance NC-CONST-FR-001-v0.2*
