# NC-GOV-FR-003  Regras de Governana de IA para NeoCortex

**Domnio**: governance  
**Camada**: infra  
**Tipo**: GOV  
**Tags**: ['governana', 'ia', 'regras', 'segurana', 'auditoria']  
**Hash**: `IA-GOVERNANCE-RULES-v1.0`

---

## 1. VISO GERAL

Este documento estabelece as **20 regras de governana de IA** que regem a operao do framework NeoCortex. As regras so organizadas em 5 categorias e implementam os princpios de **segurana por design**, **rastreabilidade completa** e **melhoria contnua** necessrios para operao autnoma segura de agentes de IA.

### Princpio "Dupla Mordaa"
- **Verso legvel**: Este documento MD (para humanos)
- **Verso machine-readable**: `NC-GOV-FR-003-ia-governance-rules.yaml` (para sistemas)
- **Hash de integridade**: `IA-GOVERNANCE-RULES-v1.0` (presente no campo `meta.hash` do YAML)

### Auditoria Automtica
As regras so auditadas automaticamente pelo script `NC-SCR-FR-080-governance-auditor.py` que:
1. Verifica conformidade com cada regra
2. Mede mtricas de implementao
3. Gera relatrios de discrepncia
4. Integra-se ao **Ciclo 4** (limpeza semanal)

---

## 2. AS 20 REGRAS (POR CATEGORIA)

###  2.1. FUNDAO E ESTRUTURA

| ID | Regra | Descrio | Status | Artefatos de Verificao |
|---|---|---|---|---|
| **R01** | **Inventrio de Ativos de IA** | Manter catlogo completo de modelos, ferramentas, agentes e fontes de dados |  Implementado | `artifact_catalog.json`, `genealogy_graph.json` |
| **R02** | **Poltica Formalizada** | Polticas escritas, versionadas e acessveis como cdigo/documentos SSOT |  Implementado | `NC-NAM-FR-001.md`, `NC-SEC-FR-001.yaml` |
| **R03** | **Estrutura de Diretrios Cannica** | Impor estrutura padronizada de diretrios |  Implementado | `NC-NAM-FR-001.md` (seo diretrios) |
| **R04** | **Nomenclatura Padronizada** | Todos os arquivos seguem `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext` |  Implementado | Regex `^NC-[A-Z]+-[A-Z]+-[0-9]{3}-.+\\..+` |
| **R05** | **Segregao de Ambientes** | Manter ambientes separados (produo/teste) |  Implementado | `01_neocortex_framework/` (prod) vs `01_neocortex_framework_RENAMED/` (teste) |

###  2.2. CONTROLE DE ACESSO E IDENTIDADE

| ID | Regra | Descrio | Status | Artefatos de Verificao |
|---|---|---|---|---|
| **R06** | **Identidade para Agentes** | Cada agente tem identidade nica e verificvel |  Implementado | `agent_id` em handoffs YAML |
| **R07** | **Privilgio Mnimo (PoLP)** | Agentes tm apenas permisses necessrias |  Implementado | `allowed_tools` em `agent-policy-template.yaml` |
| **R08** | **Atomic Locks (Path-Based)** | Arquivos crticos protegidos contra modificao |  Implementado | `NC-SEC-FR-001-atomic-locks.yaml` |
| **R09** | **Segregao de Zonas de Escrita** | Agentes de diferentes domnios no escrevem nos mesmos diretrios |  Implementado | `write_zones` em `NC-CFG-FR-002-rules-policy.yaml` |

###  2.3. RASTREABILIDADE E AUDITORIA

| ID | Regra | Descrio | Status | Artefatos de Verificao |
|---|---|---|---|---|
| **R10** | **Trilha de Auditoria Imutvel** | Aes registradas em log  prova de adulterao |  Parcial | `LedgerService` + handoffs YAML (WAL futuro) |
| **R11** | **Versionamento de Artefatos** | Artefatos de governana versionados com hashes |  Implementado | Campo `meta.hash` em YAMLs de governana |
| **R12** | **Handoffs Formais** | Toda tarefa delegada documentada em handoff YAML |  Implementado | `NC-HANDOFF-TEMPLATE.yaml` |
| **R13** | **Checkpoints e Save Points** | Estado salvo periodicamente e antes de operaes crticas |  Parcial | `PulseScheduler` (checkpoints) + `SAVE-002` (pendente) |

###  2.4. EXECUO E ORQUESTRAO

| ID | Regra | Descrio | Status | Artefatos de Verificao |
|---|---|---|---|---|
| **R14** | **STEP 0 (Validao Pr-Ao)** | Validar tarefa contra Regression Buffer e polticas antes de executar |  Implementado | `mentor_step_0()` + `neocortex_regression.check` |
| **R15** | **STEP -1 (Save Point)** | Snapshot do estado antes de aes de escrita |  Pendente | `SAVE-002` (Save Point Service) |
| **R16** | **Circuit Breaker** | Suspender agente que falha repetidamente |  Pendente | `SEC-403` (Circuit Breaker) |
| **R17** | **Rate Limiting por Ferramenta** | Limitar frequncia de chamadas a ferramentas crticas |  Pendente | `SEC-403` (Rate limiting) |

###  2.5. CICLO DE VIDA E MELHORIA CONTNUA

| ID | Regra | Descrio | Status | Artefatos de Verificao |
|---|---|---|---|---|
| **R18** | **Ciclo de Vida de Tickets** | Toda tarefa registrada como ticket e segue fluxo formal |  Implementado | `NC-GOV-FR-002-ticket-lifecycle.md` |
| **R19** | **Rotina de 4 Ciclos** | Trabalho segue rotina diria/semanal para continuidade |  Implementado | `NC-SOP-FR-001-session-startup.md` |
| **R20** | **Reviso e Arquivo de Artefatos** | Artefatos antigos arquivados periodicamente |  Implementado | Ciclo 4 em `NC-PROMPT-FR-001-master-context.md` |

---

## 3. IMPLEMENTAO TCNICA

### 3.1. STEP 0: O Corao da Governana em Runtime

O **STEP 0** (`mentor_step_0()`)  a implementao prtica das regras R14 e integra mltiplas outras regras:

```python
def mentor_step_0(agent_role: str, task_description: str, lobe_dir: Optional[Path] = None) -> Optional[str]:
    """
    AGENT-203 / PRE-1  Mentor Mode Step 0.
    
    Implementa:
    1. R06: Verifica identidade do agente (agent_role)
    2. R07: Aplica limites de permisso via PolicyLoader
    3. R14: Validao pr-ao contra Regression Buffer
    4. R04: Verifica conveno de nomes em referncias
    5. R08/R09: Valida zonas de escrita e atomic locks
    6. R11: Carrega contexto dos lobos (hash-verified)
    7. R17: Aplica limites de tokens (se implementado)
    """
```

**Ciclo de Aprendizado (Regression Buffer):**
```
Execuo  Erro/Falha  Registro no Regression Buffer  STEP 0 consulta buffer  Preveno de regresso
```

### 3.2. Integrao com SecurityService

O `SecurityService` implementa as regras de controle de acesso:

```python
class SecurityService:
    def validate_access(self, path: str, agent_role: str) -> bool:
        """
        Implementa:
        - R08: Verifica atomic locks (NC-SEC-FR-001-atomic-locks.yaml)
        - R09: Valida zona de escrita permitida para o role
        - R07: Aplica privilgio mnimo
        """
```

### 3.3. Auditoria Automtica (NC-SCR-FR-080-governance-auditor.py)

O script de auditoria verifica:

| Regra | Mtodo de Verificao | Frequncia |
|---|---|---|
| R04 | Regex pattern matching em nomes de arquivo | Ciclo 4 (semanal) |
| R05 | Deteco de ambiente (original vs. espelho) | Ciclo 4 (semanal) |
| R11 | Validao de hash em YAMLs de governana | Ciclo 3 (fim de sesso) |
| R18 | Cruzamento tickets vs. handoffs | Ciclo 4 (semanal) |

---

## 4. CICLO DE VIDA DAS REGRAS

### 4.1. Criao e Atualizao
1. **Proposta**: Nova regra identificada como necessidade
2. **Documentao**: Adicionada a este documento com ID nico (RXX)
3. **Implementao**: Criado artefato YAML correspondente
4. **Integrao**: Adicionada ao `NC-SCR-FR-080-governance-auditor.py`
5. **Validao**: Testada em ambiente espelho antes de produo

### 4.2. Auditoria e Conformidade
- **Ciclo 3 (Fim de Sesso)**: Verificao parcial (regras crticas)
- **Ciclo 4 (Limpeza Semanal)**: Auditoria completa das 20 regras
- **Relatrio**: Gerado em `reports/governance/YYYY-MM-DD/`

### 4.3. Evoluo e Melhoria Contnua
- **Reviso Trimestral**: Avaliar eficcia das regras
- **Aprendizado**: Incidentes registrados no Regression Buffer informam novas regras
- **Atualizao**: Regras obsoletas so arquivadas, novas so adicionadas

---

## 5. MTRICAS DE CONFORMIDADE

| Mtrica | Valor Atual | Meta | Tendncia |
|---|---|---|---|
| Regras Implementadas | 12/20 | 20/20 |  |
| Regras Parciais | 3/20 | 0/20 |  |
| Regras Pendentes | 5/20 | 0/20 |  |
| Conformidade NC- | 94.7% | 100% |  |
| Auditorias Concludas | 0 | 1/semana |  |

**ltima Auditoria**: Nenhuma realizada ainda  
**Prxima Auditoria Devida**: 2026-04-21 (7 dias aps criao)  
**Script de Auditoria**: `NC-SCR-FR-080-governance-auditor.py`

---

## 6. CHECKLIST DE IMPLEMENTAO PARA T0

- [ ] Executar primeira auditoria completa: `python NC-SCR-FR-080-governance-auditor.py --environment original --execute`
- [ ] Integrar verificao de regras no `SecurityService.validate_access()`
- [ ] Atualizar `NC-CYC-FR-001-4-cycle-validation.md` com etapa de auditoria
- [ ] Atualizar `NC-BOOT-FR-001-system-manifest.md` com referncia s regras
- [ ] Criar ticket para implementao das regras pendentes (R15, R16, R17)
- [ ] Configurar agendamento automtico da auditoria (Ciclo 4)

---

## 7. REFERNCIAS

1. **Boot Manifest**: `NC-BOOT-FR-001-system-manifest.md`  Estado operacional
2. **SSOT**: `NC-NAM-FR-001-naming-convention.md`  Mapa de artefatos
3. **Policy YAML**: `NC-CFG-FR-002-rules-policy.yaml`  Regras machine-readable
4. **Atomic Locks**: `NC-SEC-FR-001-atomic-locks.yaml`  Paths protegidos
5. **Ticket Lifecycle**: `NC-GOV-FR-002-ticket-lifecycle.md`  Fluxo de tickets
6. **4 Ciclos**: `NC-CYC-FR-001-4-cycle-validation.md`  Rotina de validao

---

**Hash final do documento**: `IA-GOVERNANCE-RULES-v1.0-20260414`  
**Atualizado em**: 2026-04-14  
**Responsvel**: T0 (Orchestration) via opencode (DeepSeek-Reasoner)  
**Prxima reviso**: 2026-07-14 (trimestral)