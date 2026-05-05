# NC-CFG-FR-002  Rules Policy: Governana MachineReadable
<!-- Verso: 2.0 | 20260414 | Criado por opencode (DeepSeekReasoner) -->
<!-- Documentao das regras de governana em formato machinereadable -->

## Propsito

Fornecer uma verso **machinereadable** das regras de governana do NeoCortex, consumida pelo SecurityService e `mentor_step_0()` para enforcement automtico em runtime. Complementa os arquivos MDC de regras (.mdc) com estrutura YAML processvel por scripts.

**Companion YAML**: `NCCFGFR002rulespolicy.yaml`

---

## 1. VISO GERAL

O Rules Policy YAML contm:

1. **Regras crticas** (R01R20)  enforcement automtico pelo SecurityService
2. **Zonas de escrita**  controle de acesso por role
3. **Deduplicao de leitura**  economia de tokens
4. **Linguagem ubqua**  dicionrio de referncias rpidas (@SSOT, @LOCKS, etc.)
5. **Tiers de LLM**  modelos, custos e papis

---

## 2. REGRAS CRTICAS (Enforcement Automtico)

| ID | Nome | Severidade | Aplicase a | Violao | Mensagem |
|----|------|------------|-------------|----------|----------|
| **R01** | naming_convention | critical | file_creation | block_and_alert | Arquivo criado sem prefixo NC. Consulte @SSOT antes de criar. |
| **R02** | ssot_update | critical | file_creation, file_move, file_rename | block_session_close | SSOT no atualizado. Tarefa est INCOMPLETA. |
| **R03** | roadmap_ticket | critical | implementation_start | warn_and_log |  |
| **R05** | no_deletion | critical | delete, rm, unlink, os.remove, shutil.rmtree | block_and_alert |  |

### 2.1. R01  Naming Convention
- **Padro**: `^NC[AZ]+[AZ]+[09]{3}.+\..+`
- **Ao**: Bloqueia criao de arquivos que no sigam o padro NC
- **Justificativa**: Manter consistncia no SSOT e facilitar rastreamento

### 2.2. R02  SSOT Update
- **Requer aps**: criao, movimentao ou renomeao de arquivo
- **Arquivo alvo**: `NCNAMFR001namingconvention.md`
- **Ao**: Bloqueia fechamento de sesso se SSOT no foi atualizado
- **Justificativa**: Garantir que o mapa de artefatos esteja sempre atualizado

### 2.3. R03  Roadmap Ticket
- **Requer antes**: incio de implementao
- **Arquivo alvo**: `NCTODOFR001projectroadmapconsolidated.md`
- **Ao**: Apenas alerta (no bloqueia)
- **Justificativa**: Manter rastreabilidade entre trabalho e roadmap

### 2.4. R05  No Deletion
- **Operaes bloqueadas**: delete, rm, unlink, os.remove, shutil.rmtree
- **Redirecionar para**: `DIRARCFR001archivemain/`
- **Ao**: Bloqueia e alerta
- **Justificativa**: Nunca deletar artefatos; arquivar se necessrio

---

## 3. ZONAS DE ESCRITA

| Zona | Path | Roles Permitidos | Descrio |
|------|------|------------------|------------|
| **ZONE_PROD** | `01_neocortex_framework/neocortex/` | T0, engineer, courier | Cdigo de produo |
| **ZONE_DOCS** | `01_neocortex_framework/DIRDOCFR001docsmain/` | T0 | Documentao SSOT  apenas T0 |
| **ZONE_TEST** | `05_examples/`, `01_neocortex_framework/DIRTESTFR001testsmain/` | T0, engineer, courier | Testes e exemplos |
| **ZONE_LOBES** | `02_memory_lobes/` | (nenhum) | Lobos  somente via script de poblamento |
| **ZONE_BOOT** | `DIRBOOTFR001bootupmain/` | T0 | Boot manifest  apenas T0 |

**Uso pelo SecurityService**:
```python
# Verifica se role tem acesso  zona
if not security_service.check_write_zone(role="engineer", path="some/path"):
    raise AccessDeniedError("Zona de escrita no permitida")
```

---

## 4. DEDUPLICAO DE LEITURA

**Objetivo**: Evitar releitura de arquivos j processados na mesma sesso (economia de tokens).

**Hashes conhecidos** (exemplos):
- `RULE001COREv2`  `NCRULE001coressot.mdc`  ao: `skip_reread`
- `RULE002PYv2`  `NCRULE002pythonmcp.mdc`  ao: `skip_reread`
- `RULE003LOBESv2`  `NCRULE003lobesmemory.mdc`  ao: `skip_reread`
- `RULE004FSv2`  `NCRULE004filesystem.mdc`  ao: `skip_reread`
- `ULQv1.0`  `NCDOCFR001ubiquitouslanguagedictionary.md`  ao: `skip_reread`
- `RULESYAMLv2`  `NCCFGFR002rulespolicy.yaml`  ao: `skip_reread`

**Fluxo**:
1. Agente l arquivo pela primeira vez
2. Calcula hash de contedo
3. Registra hash em `read_checkpoints`
4. Se mesmo hash aparece novamente  pula releitura

---

## 5. LINGUAGEM UBQUA (Abreviada)

### 5.1. Referncias SSOT (@)
| Smbolo | Path | Descrio |
|---------|------|-----------|
| `@SSOT` | `NCNAMFR001namingconvention.md` | Mapa de artefatos |
| `@ROADMAP` | `NCTODOFR001projectroadmapconsolidated.md` | Roadmap Framework |
| `@LOCKS` | `NCSECFR001atomiclocks.yaml` | Atomic locks |
| `@POLICY` | `NCCFGFR001agentpolicytemplate.yaml` | Template de poltica |
| `@BOOT` | `NCBOOTFR001systemmanifest.md` | Boot manifesto |
| `@POPULATE` | `NCSCRFR001populatelobesssot.py` | Script de poblamento |
| `@APPENDIX` | `NCAPPFR001technicalappendix.md` | Apndice tcnico |
| `@SOP` | `NCSOPFR001sessionstartup.md` | SOP de incio de sesso |
| `@ULQ` | `NCDOCFR001ubiquitouslanguagedictionary.md` | Dicionrio de linguagem |

### 5.2. Lobos ($)
| Smbolo | Path | Descrio |
|---------|------|-----------|
| `$ARCH` | `NCLBEFRARCHITECTURE001.mdc` | Lobe de arquitetura |
| `$SEC` | `NCLBEFRSECURITY001.mdc` | Lobe de segurana |
| `$DEV` | `NCLBEFRDEVELOPMENT001.mdc` | Lobe de desenvolvimento |
| `$COURIER` | `lobes/courier/` | Diretrio do Courier |
| `$ENGINEER` | `lobes/engineer/` | Diretrio do Engineer |
| `$GUARDIAN` | `lobes/guardian/` | Diretrio do Guardian |

### 5.3. Tickets e Aes (%)
| Smbolo | Significado |
|---------|-------------|
| `%DONE` | Marcar ticket como  DONE no @ROADMAP |
| `%NOW` | Ao imediata obrigatria () |
| `%NEXT` | Prximo na fila () |
| `%AGENT203` | Ticket AGENT203  mentor_step_0()   DONE |
| `%ORCH301` | Ticket ORCH301  spawn/send_task   Pendente |
| `%ORCH302` | Ticket ORCH302  execute/LLMBackend   Pendente |
| `%SEC401` | Ticket SEC401  neocortex_guardian   Pendente |
| `%SEC403` | Ticket SEC403  limits enforcement   Parcial |

---

## 6. TIERS DE LLM

| Tier | Nome | Modelos | Custo | Papel |
|------|------|---------|-------|-------|
| **T0** | Orquestrador | deepseekreasoner, claude35sonnet | expensive | Orquestra e decide APENAS. Nunca faz trabalho braal. |
| **T2** | Courier | qwen2.5coder:1.5b | free_local | Indexao, busca, formatao, boilerplate 24/7 |
| **T3** | Engineer | qwen2.5coder:3b | free_local | Gerao de cdigo, testes, refatorao |
| **TG** | Guardian | qwen2.5coder:1.5b | free_local | Validao, auditoria, segurana |

**Uso**: O T0 atribui tarefas aos tiers inferiores com base no tipo de trabalho e custo.

---

## 7. INTEGRAO COM SECURITYSERVICE

O YAML  carregado pelo SecurityService durante inicializao:

```python
# Carrega regras crticas
critical_rules = security_service.load_rules("NCCFGFR002rulespolicy.yaml")

# Aplica enforcement
if not security_service.validate_rule("R01", path="new_file.py"):
    raise RuleViolationError("R01: naming_convention")
```

**Checkpoints**:
- `mentor_step_0()` verifica regras antes de iniciar trabalho
- SecurityService intercepta operaes de filesystem
- Scripts de sanitizao validam conformidade peridica

---

## 8. ATUALIZAO DA POLTICA

1. **Modificar YAML**: Adicionar/atualizar regras, zonas, hashes
2. **Atualizar MD**: Este documento deve refletir mudanas
3. **Validar hash**: Campo `meta.hash` deve ser atualizado se contedo mudar
4. **Testar enforcement**: Executar `NCSCRFR009sanitizeallyamls.py`
5. **Comunicar mudanas**: Notificar agentes sobre novas regras

**Importante**: Alteraes em `write_zones` podem afetar acesso de agentes existentes.

---

## 9. CHECKLIST DE VALIDAO

- [ ] YAML possui `meta.hash` vlido
- [ ] MD correspondente atualizado
- [ ] Regras crticas so aplicveis e testadas
- [ ] Zonas de escrita no conflitam com atomic locks
- [ ] Hashes de deduplicao correspondem a arquivos reais
- [ ] Linguagem ubqua est atualizada
- [ ] SecurityService carrega YAML sem erros

---

## 10. PRXIMOS PASSOS

1. **Implementar enforcement automtico** para todas as regras crticas
2. **Criar dashboard de conformidade** com relatrios de violaes
3. **Integrar com mentor_step_0()** para validao prexecuo
4. **Estender para novos agentes** (ex: Tester, Auditor)

---

**Hash do documento**: `RULESPOLICYv2.020260414`  
**Atualizado em**: 20260414  
**Responsvel**: opencode (DeepSeekReasoner)  
**Integridade**: `sha256:$(sha256sum NCCFGFR002rulespolicy.md | cut -d' ' -f1)`