# NC-CYC-FR-001  Validao de 4 Ciclos NeoCortex

**Domnio**: orchestration  
**Camada**: infra  
**Tipo**: CYC  
**Tags**: ['ciclos', 'validao', 'governana', 'automation']  
**Hash**: `4CYC-VAL-v1.0`

---

## 1. VISO GERAL

O NeoCortex opera em **4 ciclos** para manter conscincia situacional completa e evitar perda de contexto entre sesses. Cada ciclo possui etapas explcitas de **validao** e segue o padro **O que fazer  Como fazer  Por que fazer  Fazer  Validar**.

### Referncias Crticas
- **Boot Manifest**: `NC-BOOT-FR-001-system-manifest.md`  estado operacional, frentes, tickets
- **SSOT**: `NC-NAM-FR-001-naming-convention.md`  mapa de 460 artefatos (253 PY, 207 YAML)
- **Catlogo Semntico**: `artifact_catalog.json`  anlise semntica (imports, funes, propsito)
- **Roadmaps**:  
  - `NC-TODO-FR-001-project-roadmap-consolidated.md` (FR  Framework)  
  - `NC-TODO-DS-001-roadmap-pre-mcp.md` (DS  Agent)

### Princpios de Validao (Dupla Mordaa)
1. **Documentao + Dados**: Cada artefato crtico possui verso `.md` (documentao) e `.yaml` (dados machinereadable)
2. **Hash de Integridade**: Arquivos YAML incluem campo `hash` na seo `meta` para verificao de alteraes
3. **Crossreference**: Catlogo semntico cruza SSOT, bootup e roadmaps para detectar discrepncias
4. **Validao Automtica**: Scripts `NCSCRFR009sanitizeallyamls.py` e `NCSCRFR014endofcycle.ps1` garantem conformidade

---

## 2. CICLO 1  INCIO DE SESSO

**Objetivo**: Carregar contexto do catlogo semntico e estabelecer baseline para a sesso.

| O que fazer | Como fazer | Por que fazer | Fazer | Validao |
|-------------|------------|---------------|-------|-----------|
| **Verificar idade do catlogo** | `artifact_catalog.json` (`metadata.generated`) | Evitar usar dados desatualizados (>24h) | Ler timestamp do catlogo | Se >24h, gerar novo catlogo |
| **Carregar trechos relevantes** | Buscar por path/nome no `artifact_catalog.md` | Saber funo de cada arquivo antes de editar | Extrair propsito, imports, referncias | Crossreference com SSOT |
| **Atualizar bootup (se necessrio)** | `NCBOOTFR001systemmanifest.md`  verificar frentes ativas | Manter estado operacional atualizado | Comparar com tickets YAML e handoffs | Verificar se h tickets crticos bloqueantes |
| **Validar YAMLs de governana** | `NCSECFR001atomiclocks.yaml`, `NCCFGFR002rulespolicy.yaml` | Garantir que regras estejam ntegras | Checar campo `hash` e estrutura YAML | Script `NCSCRFR009sanitizeallyamls.py` |

**Checklist de Validao (Ciclo 1)**:
- [ ] Catlogo gerado nas ltimas 24h
- [ ] Bootup reflete frentes ativas (seo 6)
- [ ] Atomic locks e rulespolicy possuem `hash` vlido
- [ ] Nenhum ticket YAML rfo (sem handoff correspondente)
- [ ] Roadmaps FR e DS alinhados com bootup

---

## 3. CICLO 2  DURANTE A SESSO

**Objetivo**: Referenciar artefatos durante tarefas e garantir conformidade com regras.

| O que fazer | Como fazer | Por que fazer | Fazer | Validao |
|-------------|------------|---------------|-------|-----------|
| **Consultar catlogo antes de editar** | `artifact_catalog.json`  buscar por path | Evitar modificaes cegas em artefatos desconhecidos | Extrair propsito, imports, dependncias | Verificar impacto de renomeao (se aplicvel) |
| **Respeitar zonas de escrita** | `NCCFGFR002rulespolicy.yaml`  `write_zones` | Prevenir modificaes no autorizadas em reas protegidas | Validar path contra `allowed_roles` | SecurityService (`validate_access`) |
| **Atualizar SSOT aps criao/renomeao** | `NCNAMFR001namingconvention.md`  adicionar entrada | Manter mapa de artefatos atualizado | Executar `@POPULATE` se necessrio | Verificar changelog no SSOT |
| **Registrar handoff para tickets concludos** | `DIRDS002auditlogs/NCDS*handoff*.yaml` | Provar concluso e gerar evidncia auditvel | Gerar YAML com `status: APPROVED` | Crossreference com ticket YAML |

**Checklist de Validao (Ciclo 2)**:
- [ ] Artefato consultado no catlogo antes da edio
- [ ] Zona de escrita permitida para o role atual
- [ ] SSOT atualizado com nova entrada (se criado/renomeado)
- [ ] Handoff gerado para ticket concludo
- [ ] Nenhuma violao de atomic locks

---

## 4. CICLO 3  FIM DE DIA/SESSO

**Objetivo**: Atualizar catlogo semntico e consolidar ganhos de contexto.

| O que fazer | Como fazer | Por que fazer | Fazer | Validao |
|-------------|------------|---------------|-------|-----------|
| **Atualizar catlogo de artefatos** | `NCSCRFR064artifactcatalog.py`  execuo automtica | Manter conscincia situacional atualizada | Executar se catlogo >24h ou mudanas significativas | Verificar `total_py` e `total_yaml` no metadata |
| **Sincronizar bootup com estado real** | `NCBOOTFR001systemmanifest.md`  atualizar frentes, tickets, status | Garantir que bootup reflita realidade operacional | Atualizar sees 6 (frentes) e 9 (tickets crticos) | Comparar com tickets YAML e handoffs |
| **Validar integridade de YAMLs de rotina** | `NCSCRFR009sanitizeallyamls.py`  sanitizao global | Corrigir claimed_by sujo, completed_at inconsistente | Executar script e aplicar correes | Relatrio de issues/fixes gerado |
| **Executar rotina de fim de ciclo** | `NCSCRFR014endofcycle.ps1 -UpdateCatalog` | Limpeza de caches, verificao de lint/typecheck | Rodar script com parmetros apropriados | Exit code 0, logs limpos |

**Checklist de Validao (Ciclo 3)**:
- [ ] Catlogo atualizado (timestamp atual)
- [ ] Bootup sincronizado com frentes ativas
- [ ] YAMLs de rotina sanitizados (0 issues crticas)
- [ ] Rotina de fim de ciclo executada com sucesso
- [ ] Nenhum `.db`/`.wal`/`__pycache__` commitado

---

## 5. CICLO 4  LIMPEZA SEMANAL

**Objetivo**: Manter baseline limpa e preparar ambiente para prxima semana.

| O que fazer | Como fazer | Por que fazer | Fazer | Validao |
|-------------|------------|---------------|-------|-----------|
| **Auditar tickets YAML rfos** | `DIRDS001tickets/` vs `DIRDS002auditlogs/` | Identificar rotinas inertes que precisam ser abertas/verificadas/fechadas | Cruzar IDs de tickets com handoffs | Listar tickets sem handoff (>30 dias) |
| **Verificar padro dupla mordaa** | Para cada YAML de governana, verificar hash e documento MD correspondente | Garantir validao em duas camadas (dados + documentao) | Checar `meta.hash` e existncia de arquivo `.md` | Hash coincide com contedo |
| **Otimizar catlogo para RAG** | `artifact_catalog.json`  extrair trechos mais relevantes | Melhorar recuperao de contexto em sesses futuras | Filtrar por frequncia de uso, criticidade | Testar queries RAG com 10 scriptschave |
| **Validar conformidade de nomenclatura** | `NCNAMFR001namingconvention.md` vs catlogo | Garantir que todos os artefatos sigam padro NC | Comparar nomes de arquivos com regex `^NC` | Relatrio de noconformidades |
| **Auditar governana de IA (20 regras)** | `NCSCRFR080governanceauditor.py --environment original --execute` | Validar conformidade com 20 regras de governana de IA | Executar auditoria completa e gerar relatrios | Verificar compliance >80% e implementar correes |

**Checklist de Validao (Ciclo 4)**:
- [ ] Tickets rfos identificados e triados
- [ ] Hash de YAMLs de governana vlidos
- [ ] Catlogo otimizado para RAG (trechos relevantes extrados)
- [ ] 100% dos artefatos seguem padro NC
- [ ] Auditoria de governana de IA executada (20 regras) e compliance >80%
- [ ] Relatrio de limpeza gerado em `DIRDS002auditlogs/`

---

## 6. COORDENAO DE YAMLS DE ROTINA

### 6.1. Tipos de YAMLs
| Tipo | Path | Finalidade | Validao |
|------|------|------------|-----------|
| **Tickets** | `DIRDS001tickets/NCDS*.yaml` | Rotinas de trabalho para agentes | Handoff correspondente em `DIRDS002auditlogs/` |
| **Handoffs** | `DIRDS002auditlogs/NCDS*handoff*.yaml` | Evidncia de concluso | `status: APPROVED`, referncia a ticket ID |
| **Governana** | `DIRDOCFR001docsmain/NC{SEC,CFG}FR*.yaml` | Regras machinereadable | Campo `meta.hash`, estrutura vlida |
| **Configurao** | `DIRDS000agentconfig/NCCFGDS*.yaml` | Configurao de agentes, filas | Sanitizao automtica via `NCSCRFR009` |
| **Zonas Ativas** | `DIRDS003entrylocks/activezones.yaml` | Controle de concorrncia | Entradas no rfs, timestamp recente |

### 6.2. Protocolo Dupla Mordaa
Cada YAML de governana **deve**:
1. **Ter um hash na meta**: `meta.hash: "RULESYAMLv2"`
2. **Referenciar documento MD correspondente**: Ex: `NCCFGFR002rulespolicy.yaml`  `NCCFGFR002rulespolicy.md` (se existir)
3. **Ser validado pelo SecurityService**: `validate_access()` verifica atomic locks
4. **Ser sanitizado periodicamente**: Script `NCSCRFR009sanitizeallyamls.py`

### 6.3. Estado Atual dos YAMLs (20260415)
- **Tickets YAML**: 47 arquivos
- **Handoffs**: 8 arquivos  **39 tickets rfos (inerte)**
- **Governana**: 3 arquivos (`atomiclocks`, `rulespolicy`, `agentpolicytemplate`)
- **Configurao**: 4 arquivos (`taskqueue`, `coordination`, `sessioncontract`, `agentpolicy`)

**Ao Requerida**: Executar auditoria de tickets rfos e definir protocolo de abertura/verificao/fechamento.

---

## 7. INTEGRAO COM BOOTUP E SSOT

### 7.1. Atualizao Automtica do Bootup
O bootup manifesto **deve** ser atualizado no **Ciclo 3** com:
1. **Frentes ativas** (seo 6)  extradas de tickets YAML com handoff recente
2. **Tickets crticos** (seo 9)  bloqueantes prMCP (SAVE005, ORCH301, ORCH302)
3. **Estado acumulado** (seo 7)  servios core, tools MCP, hooks
4. **Checklist fim de sesso** (seo 11)  verificao de SSOT, roadmap, populate

**Script de atualizao**: `NCSCRFR066bootupsync.py` (a ser criado)

### 7.2. Sincronizao SSOT  Catlogo
- **SSOT**: `NCNAMFR001namingconvention.md`  lista de artefatos + caminhos
- **Catlogo**: `artifact_catalog.json`  anlise semntica (imports, funes, propsito)
- **Integrao**: Catlogo complementa SSOT com dados semnticos; SSOT  autoridade para nomes e paths.

**Validao cruzada**: Verificar se todos os artefatos do SSOT esto no catlogo e viceversa.

---

## 8. CHECKLIST CONSOLIDADO  4 CICLOS

### Ciclo 1 (Incio)
- [ ] Catlogo semntico carregado (<24h)
- [ ] Bootup lido  frentes ativas identificadas
- [ ] YAMLs de governana validados (hash)
- [ ] Roadmaps FR/DS alinhados

### Ciclo 2 (Durante)
- [ ] Artefato consultado no catlogo antes de editar
- [ ] Zona de escrita permitida verificada
- [ ] SSOT atualizado aps criao/renomeao
- [ ] Handoff gerado para ticket concludo

### Ciclo 3 (Fim)
- [ ] Catlogo atualizado (se necessrio)
- [ ] Bootup sincronizado com estado real
- [ ] YAMLs de rotina sanitizados
- [ ] Rotina de fim de ciclo executada
- [ ] Lint/typecheck/testes passando

### Ciclo 4 (Limpeza)
- [ ] Tickets rfos auditados
- [ ] Hash de YAMLs de governana verificados
- [ ] Catlogo otimizado para RAG
- [ ] Conformidade de nomenclatura 100%
- [ ] Auditoria de governana de IA executada (20 regras) e compliance >80%
- [ ] Relatrio de limpeza gerado

---

## 9. PRXIMOS PASSOS

1. **Criar script de sincronizao do bootup** (`NCSCRFR066bootupsync.py`)
2. **Executar auditoria de tickets rfos** (39 tickets sem handoff)
3. **Implementar validao dupla mordaa** para todos os YAMLs de governana
4. **Integrar checklist de 4 ciclos** na rotina `NCSCRFR014endofcycle.ps1`
5. **Testar RAG com catlogo** usando 10 scriptschave como gabarito

---

**Hash final do documento**: `4CYC-VAL-v1.2-20260415`  
**Atualizado em**: 2026-04-15  
**Responsvel**: T0 (Orchestration)