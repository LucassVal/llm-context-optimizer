# NC-GOV-FR-002  Ticket Lifecycle Protocol v1.0
<!-- Verso: 1.0 | 20260414 | Criado por opencode (DeepSeekReasoner) -->
<!-- Protocolo de abertura/verificao/fechamento para rotinas YAML, integrado aos 4 ciclos NeoCortex -->

## Propsito

Definir o ciclo completo de rotinas (tickets YAML) para evitar **rotinas inertes**  tickets abertos sem handoff correspondente. Garantir que cada rotina tenha etapas claras de **O que fazer, Como fazer, Por que fazer, Fazer e Validao**, alinhadas com bootup e SSOT.

---

## 1. ESTADO ATUAL (20260414)

| Categoria | Quantidade | Observao |
|-----------|------------|------------|
| Tickets YAML totais | 47 | `DIRDS001tickets/` |
| Handoffs YAML totais | 8 | `DIRDS002auditlogs/` |
| **Tickets rfos** | **39** | Sem handoff correspondente |
| **Tickets ativos rfos** | **37** | Com `integrity_hash`, possivelmente pendentes |
| **Handoffs sem ticket** | **5** | IDs: NCDS062, 064, 065, 066, 067 |

**Problema**: 94.7% dos tickets esto inertes (sem evidncia de concluso).  
**Soluo**: Implementar ciclo de vida obrigatrio com validao em 4 estgios.

---

## 2. CICLO DE VIDA DE UM TICKET

Cada ticket YAML deve passar por **4 estgios**:

```
         [CRIAO]
             
             
       [ABERTURA]  Ticket YAML em DIRDS001tickets/
             
             
    [VERIFICAO]  Validao de prcondies (entry_state)
             
             
     [EXECUO]  Handoff YAML em DIRDS002auditlogs/
             
             
    [FECHAMENTO]  Status final (APPROVED, FAILED, CANCELLED)
```

### 2.1. CRIAO (Ciclo 1  Incio de Sesso)

**O que fazer**: Identificar necessidade de nova rotina com base em roadmaps, bootup ou gaps detectados.  
**Como fazer**:  
1. Consultar `NCTODOFR001projectroadmapconsolidated.md` (Framework) e `NCTODODS001roadmappremcp.md` (Agent)  
2. Verificar se j existe ticket para a mesma tarefa (buscar por keywords no `artifact_catalog.json`)  
3. Criar template usando `NCDSHANDOFFTEMPLATE.yaml` como base  

**Por que fazer**: Evitar duplicao de esforos e garantir alinhamento com prioridades estratgicas.  
**Fazer**: Gerar novo arquivo `NCDSXXXCODE*.yaml` seguindo padro de nomenclatura.  
**Validao**:  
- [ ] Ticket possui `integrity_hash`  
- [ ] Campos obrigatrios preenchidos: `id`, `title`, `task`, `entry_state`, `exit_state`  
- [ ] Referencia roadmaps relevantes (`roadmap_ticket`)  

### 2.2. ABERTURA (Ciclo 2  Durante a Sesso)

**O que fazer**: Colocar ticket em estado "pronto para execuo".  
**Como fazer**:  
1. Adicionar ticket  fila `NCCFGDS004taskqueue.yaml` (se usar workers)  
2. Ou atribuir diretamente a um agente (`assigned_to`)  
3. Atualizar bootup seo 9 (tickets crticos) se for bloqueante  

**Por que fazer**: Tornar ticket visvel para workers e evitar esquecimento.  
**Fazer**:  
- Adicionar `created_at` timestamp  
- Definir `priority` (HIGH, MEDIUM, LOW)  
- Especificar `write_zone` e `active_locks`  

**Validao**:  
- [ ] Ticket aparece na fila (se aplicvel)  
- [ ] Write zone existe e  acessvel  
- [ ] Locks listados esto realmente bloqueados (`NCSECFR001atomiclocks.yaml`)  

### 2.3. VERIFICAO (Prexecuo)

**O que fazer**: Validar prcondies (`entry_state`) antes de comear.  
**Como fazer**:  
1. Executar script `NCSCRFR006ticketvalidator.py` (TOOL001)  
2. Verificar cada item de `entry_state.files_exist` e `files_must_not_exist`  
3. Confirmar que `active_locks` no foram violados  

**Por que fazer**: Prevenir execuo em estado inconsistente (arquivos faltando, locks violados).  
**Fazer**:  
- Rodar validao automatizada  
- Registrar resultado em log temporrio  
- Bloquear execuo se falhas crticas  

**Validao**:  
- [ ] Todos os `files_exist` existem  
- [ ] Nenhum `files_must_not_exist` existe  
- [ ] Atomic locks intactos  
- [ ] Script de validao retorna exit code 0  

### 2.4. EXECUO (Ciclo 2  Durante a Sesso)

**O que fazer**: Realizar trabalho descrito no ticket.  
**Como fazer**:  
1. Seguir `task.description` passo a passo  
2. Respeitar `barriers` (checks de segurana)  
3. Documentar alteraes em tempo real (para handoff futuro)  

**Por que fazer**: Concluir rotina com qualidade e rastreabilidade.  
**Fazer**:  
- Modificar/ criar arquivos conforme `exit_state`  
- Atualizar SSOT (`NCNAMFR001namingconvention.md`) se criar/renomear artefatos  
- Executar verificaes de lint/typecheck  

**Validao**:  
- [ ] `exit_state.files_created` existem  
- [ ] `exit_state.files_modified` foram modificados  
- [ ] SSOT atualizado (se aplicvel)  
- [ ] Lint/typecheck passam  

### 2.5. FECHAMENTO (Ciclo 3  Fim de Sesso)

**O que fazer**: Gerar handoff como evidncia de concluso.  
**Como fazer**:  
1. Criar arquivo `NCDSXXXhandoff<timestamp>.yaml` em `DIRDS002auditlogs/`  
2. Preencher campos obrigatrios: `ticket_id`, `status`, `timestamp`, `summary`  
3. Incluir mtricas: `lines_added`, `files_modified`, `checklist_r20`  

**Por que fazer**: Provar que rotina foi concluda e habilitar auditoria futura.  
**Fazer**:  
- Definir `status`: `APPROVED`, `PARTIALLY_COMPLETED`, `FAILED`, `CANCELLED`  
- Incluir `adjustes_aplicados` e `errors`/`warnings`  
- Referenciar handoff no ticket original (campo `context`)  

**Validao**:  
- [ ] Handoff referencia ticket ID correto  
- [ ] Status reflete realidade  
- [ ] Checklist R20 completo (naming_convention, no_print_statements, etc.)  
- [ ] Handoff adicionado ao catlogo semntico na prxima gerao  

---

## 3. PROTOCOLO PARA ROTINAS INERTES

### 3.1. Classificao de Tickets rfos

| Categoria | Critrio | Ao |
|-----------|----------|------|
| **Template** | Contm "Ticket de Exemplo", "Copie e adapte" | Manter como referncia, no contar como rotina ativa |
| **Placeholder** | `task.description` vazio ou "TODO"/"TBD" | Completar ou arquivar |
| **Ativo** | Possui `integrity_hash` e task definida | **Prioridade**: criar handoff ou marcar como CANCELLED |
| **Incompleto** | Falta campos obrigatrios ou estrutura invlida | Corrigir ou excluir |

### 3.2. Fluxo de Triagem (Ciclo 4  Limpeza Semanal)

1. **Identificar**: Executar `audit_tickets.py` para lista de tickets rfos  
2. **Classificar**: Rodar `classify_tickets.py` para categorizar  
3. **Decidir**:  
   - **Ativos**: Se trabalho foi feito mas handoff faltante  criar handoff retrospectivo  
   - **Placeholders/Incompletos**: Se >30 dias sem atividade  mover para `DIRDS004archivedtickets/`  
   - **Templates**: Manter em `DIRDS001tickets/` com prefixo `TEMPLATE`  
4. **Atualizar**: Bootup seo 6 (frentes ativas) para refletir apenas tickets com handoff recente  

### 3.3. Handoffs Sem Ticket Correspondente

IDs encontrados: **NCDS062, 064, 065, 066, 067**

**Ao**:  
1. Verificar se ticket foi renomeado/excludo  
2. Se trabalho foi realizado sem ticket formal:  
   - Criar ticket retrospectivo com `created_at` anterior  
   - Vincular handoff existente  
3. Se handoff for invlido (sem evidncia real): mover para `DIRDS004archivedhandoffs/`  

---

## 4. INTEGRAO COM BOOTUP E SSOT

### 4.1. Bootup (Seo 6  Frentes Ativas)

**Regra**: Apenas tickets com handoff `APPROVED` nos ltimos 7 dias aparecem como "frentes ativas".  

**Atualizao automtica**: Script `NCSCRFR066bootupsync.py` executa no Ciclo 3:  
1. L `DIRDS002auditlogs/` para handoffs recentes  
2. Extrai `ticket_id` e `status`  
3. Atualiza seo 6 do bootup  
4. Gera backup do manifesto anterior  

### 4.2. SSOT (Mapa de Artefatos)

**Regra**: Todo artefato criado/renomeado durante execuo de ticket deve ser adicionado ao SSOT.  

**Verificao**:  
- `exit_state.ssot_updated: true`  confirma que SSOT foi atualizado  
- Script `NCSCRFR009sanitizeallyamls.py` valida referncias cruzadas  

---

## 5. CHECKLIST DE CONFORMIDADE

### 5.1. Para Novo Ticket
- [ ] Nome segue padro `NCDSXXXCODE*.yaml`  
- [ ] Campos `id`, `title`, `task`, `entry_state`, `exit_state` preenchidos  
- [ ] `integrity_hash` calculado (SHA256[:16] de `id|write_zone|title`)  
- [ ] `roadmap_ticket` referenciado (FRXXX ou DSXXX)  
- [ ] `write_zone` existe e est acessvel  
- [ ] `active_locks` listados e verificados  

### 5.2. Para Handoff
- [ ] Nome segue padro `NCDSXXXhandoff<timestamp>.yaml`  
- [ ] `ticket_id` corresponde ao ticket original  
- [ ] `status` reflete realidade (APPROVED, PARTIALLY_COMPLETED, etc.)  
- [ ] `summary` descreve o que foi feito  
- [ ] `checklist_r20` completo  
- [ ] Referenciado no campo `context` do ticket  

### 5.3. Para Auditoria (Ciclo 4)
- [ ] Tickets rfos identificados e classificados  
- [ ] Handoffs sem ticket resolvidos  
- [ ] Bootup atualizado com frentes reais  
- [ ] Relatrio gerado em `DIRDS002auditlogs/ticket_audit_report.md`  

---

## 6. PRXIMOS PASSOS

1. **Implementar script de triagem** para tickets rfos (`NCSCRFR067tickettriage.py`)  
2. **Criar diretrio de arquivamento** `DIRDS004archivedtickets/`  
3. **Resolver handoffs sem ticket** (5 casos)  
4. **Atualizar bootup** com base em auditoria atual  
5. **Executar ciclo completo** de validao com 1 ticket de exemplo  

---

**Hash do protocolo**: `TICKETLIFECYCLEv1.020260414`  
**Atualizado em**: 20260414  
**Responsvel**: opencode (DeepSeekReasoner)  
**Integridade**: `sha256:$(sha256sum NCGOVFR002ticketlifecycle.md | cut -d' ' -f1)`