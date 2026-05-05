# NC-GOV-FR-001  NWorker Protocol v2.0
<!-- Verso: 2.0 | 20260412T18:37:16 | Criado por deepseekchat via OpenCode -->
<!-- Documentao oficial do sistema de fila Nworkers, claim atmico, autoapprove e limites de escala -->

## Propsito

Coordenar mltiplos workers T1 paralelos (deepseekchat via OpenCode) que executam tickets da fila `NCCFGDS004taskqueue.yaml`. Evitar coliso de write_zone, garantir atomicidade do claim, fornecer autoapprove de handoffs e estabelecer limites escalveis.

---

## Diagrama ASCII do Fluxo NWorkers

```
          [NCCFGDS004taskqueue.yaml]
                     
          
                               
      AVAILABLE             CLAIMED (por worker)
                               
                               
      Worker T1            Worker T1
      l fila              faz claim atmico
                           
                           
  Se no h tasks      Aguarda 5s  rel
                           
                           
  "FILA VAZIA"         Se claim ainda  seu
                           
      
                            
                      L ticket YAML
                            
                            
                      Executa (6 fases)
                            
                            
                      Cria handoff YAML
                            
                            
                      Atualiza fila: DONE
                            
                            
                      Volta para AVAILABLE
```

---

## Claim Protocol (EL1/2/3/4)

O claim  atmicoish via timestamp:

1. **Worker l fila**  encontra primeira task com `status: AVAILABLE`
2. **Worker escreve** na task:
   - `claimed_by: "{seu_timestamp_de_inicio}"`
   - `claimed_at: "{ISO8601_agora}"`
   - `status: CLAIMED`
3. **Worker aguarda 5 segundos**  rel a fila
4. **Se `claimed_by` ainda  seu timestamp**  claim vlido, prossegue
5. **Se outro worker tomou**  pula para a prxima `AVAILABLE` e repete

**Entry Locks (EL) que protegem a ativao de tickets** (ver `NCSECFR002entrylockprotocol.md`):

- **EL1 (ANTIDUPLICATA)**: ticket j `DONE`  bloqueado
- **EL2 (ANTICOLISO)**: ticket j em `ACTIVE`  bloqueado  
- **EL3 (ANTIFANTASMA)**: arquivo YAML do ticket no existe  bloqueado
- **EL4 (ANTISTANDBYSILENCIOSO)**: ticket em `RESERVED`  alerta (no bloqueia)

---

## AutoApprove Conditions (via NCSCRFR005)

O script `NCSCRFR005autoapprove.py` aprova automaticamente um handoff se **TODAS** as condies forem atendidas:

```yaml
approve_if_all_pass:
  - barriers_passed_includes: ["B1", "B2", "B3", "B4"]
  - locks_violated_is_empty: true
  - overall_equals: "SUCCESS"
  - lines_added_gt: 5
```

**Barriers obrigatrios (validao psexecuo):**

- **B1**: naming convention `NC` (prefixo correto)
- **B2**: sem violao de `@LOCKS` (arquivos protegidos)
- **B3**: `py_compile` passa (se for arquivo Python)
- **B4**: SSOT + data (timestamp ISO 8601)
- **B5**: sem hardcode (warning)
- **B6**: sem `print()` (warning)

Se falhar B1B4  worker faz **selfrefine** (mx. 5 rounds). Aps 5 falhas  `ESCALATED` para T0.

---

## Como Adicionar Tasks  Fila

1. Criar arquivo YAML do ticket em `DIRDS001tickets/` com:
   - `ticket_id`: prefixo `NCDSXXX`
   - `write_zone`: diretrio/arquivo onde o worker pode escrever
   - `forbidden_zone`: lista de arquivos que **NUNCA** podem ser modificados
   - `exit_state.files_created`: lista de entregveis obrigatrios
   - `methodology`: passos que o worker deve seguir

2. Inserir entrada no array `tasks:` de `NCCFGDS004taskqueue.yaml`:
   - `status: AVAILABLE`
   - `claimed_by: null`
   - `claimed_at: null`
   - `completed_at: null`

3. Se a task depende de um **progressive lock gate**, definir `progressive_gate: GATEXXX` e aguardar aprovao do ticket prrequisito.

---

## Limites de Escala

### API Keys / Tokens
- **Mximo de tokens por fase**: 4000 (configurvel por ticket)
- **Mximo de rounds de selfrefine**: 4 (configurvel por ticket)
- **Rate limit implcito**: 1 worker por task, fila ordenada por prioridade

### Filesystem
- **Write zone nica por ticket**: garante isolamento
- **Forbidden zones globais** (nunca tocar):
  - `neocortex/mcp/server.py`
  - `neocortex/mcp/sub_server.py`
  - `DIRCFGFR001configmain/neocortex_config.yaml`
  - `DIRDOCFR001docsmain/NCNAMFR001namingconvention.md`
- **Handoffs**: depositados em `DIRDS002auditlogs/` com nome `NCDS{NUM}handoff{YYYYMMDDHHMM}.yaml`

### Workers Paralelos
- **N workers** podem operar simultaneamente desde que suas `write_zones` no colidam
- **Coliso detectada**  status `BLOCKED` + handoff para T0 resolver
- **Claim timeout**: 300 segundos (5 minutos) sem `ACTIVE`  volta para `AVAILABLE`

---

## Handoff Schema (obrigatrio)

Cada worker ao finalizar uma task **deve** gerar um arquivo YAML em `DIRDS002auditlogs/` com o nome:

```
NCDS{NUM}handoff{YYYYMMDDHHMM}.yaml
```

Contedo mnimo:

```yaml
status: PENDING_REVIEW
ticket_id: {id}
submitted_at: "{ISO8601}"
submitted_by: deepseekchat
review_by: autoapprovescript
summary:
  files_created: []
  files_modified: []
  lines_added: 0
  barriers_passed: ["B1","B2","B3","B4","B5","B6"]
  locks_violated: []
  overall: SUCCESS
```

---

## Progressive Lock Gates

Quando um ticket aprovado  prrequisito para modificar um `@LOCK`, ele **no** remove o lock diretamente. Em vez disso, gera um patch `NCPATCH{id}{target}.diff` em `DIRDS004patches/` para **T0 aplicar manualmente**.

Exemplo de cadeia de dependncias:

- `NCDS011` (logging service) APPROVED  unlock `server.py:importlogging`
- `NCDS020` (cache) APPROVED  unlock `server.py:importcache`
- `NCDS022` (metrics) APPROVED  unlock `server.py:importmetrics`

---

## Referncias

- `NCPROMPTDS002workeruniversal.md`  prompt base do worker T1
- `NCCFGDS004taskqueue.yaml`  fila central de tasks
- `NCSECFR002entrylockprotocol.md`  regras EL1/2/3/4
- `NCSCRFR005autoapprove.py`  script de autoaprovao
- `DIRDS001tickets/`  repositrio de tickets YAML