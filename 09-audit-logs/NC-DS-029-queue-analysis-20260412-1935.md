# Anlise da Fila N-Workers - Dificuldades Identificadas
**Worker:** worker-44949-2196eb  
**Ticket:** NC-DS-029 (GOV-014)  
**Data:** 2026-04-12T19:35:00  
**Status:** ACTIVE (mas com violao EL-6)

## Situao Atual da Fila

### Estatsticas (NC-CFG-DS-004-task-queue.yaml):
- **Total de tasks:** 20
- **AVAILABLE:** 6 (NC-DS-019, 021, 022, 023, 024, 025)
- **CLAIMED:** 2 (NC-DS-017, 026)
- **ACTIVE:** 4 (NC-DS-016, 018, 027, 029)
- **DONE:** 8 (NC-DS-015, 020, 028 + outros)
- **Concorrncia estimada:** 6-9 workers simultneos

### Problemas Identificados:

#### 1. **Inconsistncias de Estado**
- **NC-DS-016:** Status `ACTIVE` mas `completed_at: "2026-04-12T18:34:46"` (deveria ser DONE)
- **NC-DS-019:** Status `AVAILABLE` mas `claimed_by` preenchido com timestamp antigo
- **NC-DS-021/022/023/024/025:** Status `AVAILABLE` mas `claimed_by` e `claimed_at` preenchidos (claims fantasmas)

#### 2. **Race Conditions no Protocolo de Claim**
- Protocolo "atomic-ish" via timestamp + wait 5s pode no escalar para 9+ workers
- Workers podem ler estado desatualizado entre leitura e escrita
- Sem mecanismo de lock verdadeiramente atmico (ex: arquivo .lock ou SQLite)

#### 3. **Problemas de Cleanup**
- Claims expirados (mais de 300s) no so automaticamente revertidos para AVAILABLE
- Entradas `claimed_by` antigas persistem mesmo aps completion
- Status inconsistente entre `completed_at` e `status`

#### 4. **Violao EL-6 para NC-DS-029**
- Arquivo de sada `NC-GOV-FR-001-nworker-protocol.md` j existe (criado 2026-04-12T18:37:16)
- SHA-256: `fe64588d40c3364540ce369791968f5654bdcab100f62f69b0bccd64290a89f6`
- Isso indica que o ticket pode j ter sido executado (mas sem handoff encontrado)
- Executar novamente seria trabalho duplicado/sobrescrita

## Verificao Entry Locks (NC-DS-029):

### EL-1: @LOCKS no tocados 
- `neocortex/mcp/server.py` - no tocado
- `neocortex/mcp/sub_server.py` - no tocado  
- `neocortex_config.yaml` - no tocado
- `NC-NAM-FR-001-naming-convention.md` - no tocado

### EL-2: Ticket j em tickets_done de outra frente 
- Verificar NC-CFG-DS-003: precisa inspeo manual T0

### EL-3: Ticket YAML existe 
- `DIR-DS-001-tickets/NC-DS-029-gov014-nworker-protocol.yaml` existe

### EL-4: Ticket em tickets_reservados 
- Verificar NC-CFG-DS-003: precisa inspeo manual T0

### EL-5: Handoff j aprovado 
- Nenhum handoff encontrado em `DIR-DS-002-audit-logs/` para NC-DS-029

### EL-6: Idempotncia de sada  **VIOLAO**
- Arquivo `NC-GOV-FR-001-nworker-protocol.md` j existe
- SHA-256 calculado: `fe64588d40c3364540ce369791968f5654bdcab100f62f69b0bccd64290a89f6`
- **BLOCKED:** "EL-6: arquivo de sada j existe. T0 deve revisar."

## Recomendaes para Melhoria da Queue:

### Curto Prazo:
1. **Script de cleanup:** Remover automaticamente claims >300s sem ACTIVE
2. **Validao de estado:** Verificar consistncia `completed_at` vs `status`
3. **Reset de claims fantasmas:** Limpar `claimed_by` em tasks AVAILABLE

### Mdio Prazo:
4. **Lock atmico real:** Usar SQLite com transaes ou arquivo .lock
5. **Monitoramento em tempo real:** Dashboard/watchdog da fila
6. **Timeout configurvel:** Diferentes timeouts por tipo de task

### Longo Prazo:
7. **Queue distribuda:** Redis/RabbitMQ para alta concorrncia
8. **Prioridade dinmica:** Baseada em dependncias e recursos
9. **Balanceamento de carga:** Distribuir tasks por tipo de recurso

## Ao Imediata:

1. **NC-DS-029:** BLOCKED devido a EL-6 (arquivo j existe)
2. **Worker hibernando:** Aguardando deciso T0
3. **Log criado:** Este arquivo para anlise T0

## Local para Logs Futuros:
- `DIR-DS-002-audit-logs/` (padro atual) - OK
- Sugesto: subdiretrio `queue-analysis/` para relatrios de sistema

---

**Worker:** worker-44949-2196eb  
**Ao:** Hibernando aps deteco EL-6  
**Prximo passo:** T0 deve revisar violao EL-6 e decidir:  
   a) Aprovar handoff existente (se houver) e marcar NC-DS-029 como DONE  
   b) Renomear arquivo existente e permitir reexecuo  
   c) Ignorar EL-6 e permitir sobrescrita (no recomendado)