# NC-SEC-FR-002  Entry Lock Protocol
<!-- Verso: 1.0 | 2026-04-12T17:33:00 | Criado por Antigravity T0 -->
<!-- Protege NC-CFG-DS-003 contra ativao duplicada, coliso e ticket ausente -->

## Propsito

Antes de qualquer T0 ativar/mover um ticket em NC-CFG-DS-003, o protocolo
Entry Lock executa 3 verificaes. Se QUALQUER falhar  fluxo bloqueado.

---

## 3 Regras do Entry Lock (verificar todas antes de editar NC-CFG-DS-003)

```
EL-1 [ANTI-DUPLICATA]
  Para cada frente em frentes.*:
    SE ticket_id  tickets_done  BLOQUEADO
  Motivo: ticket j foi executado e aprovado. Reexecutar = desperdcio / corrupo.

EL-2 [ANTI-COLISO]
  Para cada frente em frentes.*:
    SE ticket_id  tickets_ativos  BLOQUEADO
  Motivo: ticket j est rodando em outra frente. Duplicar = conflito de write_zone.

EL-3 [ANTI-FANTASMA]
  SE arquivo DIR-DS-001-tickets/{ticket_id}*.yaml NO existe  BLOQUEADO
  Motivo: ativar ticket sem YAML = agente sem instrues  para silenciosamente.
```

---

## Fluxo T0 (checklist mental obrigatrio)

```
[ ] Li NC-CFG-DS-003 atual?
[ ] O ticket_id est em tickets_done de alguma frente? (EL-1)
[ ] O ticket_id est em tickets_ativos de alguma frente? (EL-2)
[ ] O arquivo DIR-DS-001-tickets/{ticket_id}*.yaml existe? (EL-3)
[ ] TODOS passaram  posso editar tickets_ativos agora.
[ ] ALGUM falhou  criar entry lock e parar.
```

---

## Quando o Lock Dispara: criar NC-SEC-EL-{ticket_id}-{YYYYMMDD-HHMM}.yaml

```yaml
# Arquivo de bloqueio  depositado em DIR-DS-003-entry-locks/
entry_lock_id: NC-SEC-EL-{ticket_id}-{YYYYMMDD-HHMM}
timestamp: "YYYY-MM-DDTHH:MM:SS"
triggered_by: antigravity-t0
ticket_id: {ticket_id}
rule_violated: EL-1 | EL-2 | EL-3
rule_description: "{motivo do bloqueio}"
status: BLOCKED
resolution: |
  Corrigir manualmente antes de prosseguir.
  EL-1: ticket j done  criar novo ticket com next_ticket.
  EL-2: ticket em andamento  aguardar handoff da frente ativa.
  EL-3: criar arquivo YAML do ticket em DIR-DS-001-tickets/ antes de ativar.
```

---

## Bug Report desta sesso (exemplo de uso retroativo)

```yaml
# O que o Entry Lock teria capturado em 2026-04-12:
incident: NC-DS-008 ativado como reservado em vez de ativo
rule_EL-3: PASS (arquivo existia)
rule_EL-1: PASS (no estava em done)
rule_EL-2: PASS (no estava em ativos)
root_cause: "tickets_reservados  tickets_ativos  erro de campo, no capturado pelo EL"
improvement: "Adicionar EL-4: ticket em reservados no conta como ativo  alerta T0"
```

---

## EL-4 (extenso futura)

```
EL-4 [ANTI-STANDBY-SILENCIOSO]
  SE ticket_id  tickets_reservados  ALERTA (no bloquear, mas avisar)
  Motivo: reservado  ativo. Agente vai ler [] e parar silenciosamente.
  Ao: T0 confirmar se quer ativar (mover de reservados para ativos).
```

---

## Integrao com NC-CFG-DS-003

A seo `entry_lock` no coordination YAML documenta a poltica ativa:

```yaml
entry_lock:
  protocol: NC-SEC-FR-002
  enabled: true
  rules: [EL-1, EL-2, EL-3, EL-4]
  lock_dir: "DIR-DS-003-entry-locks/"
  last_incident: "2026-04-12T16:48:00  NC-DS-008 in reservados instead of ativos"
```
