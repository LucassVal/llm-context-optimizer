══════════════════════════════════════════════════════════════╗
║  REGIME DE GOVERNANÇA ALGORÍTMICA — NÍVEL MÁXIMO           ║
║  Complementar a R01-R133 | Revisão: 2026-05-05 v2.0        ║
║  Violação de >3 regras = rejeição automática                ║
╚══════════════════════════════════════════════════════════════╝

Regra R21 (ZERO SUPOSIÇÕES) está SEMPRE ativa: antes de qualquer
afirmação, CONSULTE os arquivos reais do sistema. Não deduza, não
infira. Dúvida paralisa a ação até verificação.

---

### CLASSIFICAÇÃO DE VIOLAÇÕES (R22-R25)
Toda ação é classificada em 4 níveis (R22):
  L0 — PRIME DIRECTIVE: Sistema FALHA (STEP 0, WAL, Kernel 0 único, Constitution acima de tudo)
  L1 — BINDING: Ação BLOQUEADA (NC- naming, Write Zones, Extend Don't Create, Gateway wire-up)
  L2 — STANDARD: WARNING + Log (Logger, ConfigProvider, Ruff pré-commit, No orphans)
  L3 — GUIDANCE: Log informativo (Templates, Convenções)

R23 (L1): EXTEND, DON'T CREATE — toda tool MCP deve ser estendida, NÃO duplicada.
R24 (L1): SSOT REGISTRATION MANDATORY — artefato criado → registrado no @SSOT no mesmo commit.
R25 (L1): GATEWAY WIRE-UP MANDATORY — toda tool com ação de escrita chama gateway_check().

---

### 4 MORDAÇAS DE GOVERNANÇA (H/C/S/U)
Cada regra é coberta por 4 camadas cumulativas — 133 regras ao todo:

  H — HOOK (instantâneo): Gateway.validate_action() + 15 checks + 30 per-action. Bloqueia ação inválida ANTES de executar.
      Dispara em: toda tool call MCP, todo comando shell, todo path protegido.
      Engines: ConstitutionGateway (FR-129), BashGuard (FR-144), LockGuard (FR-014), CentralWatcher (FR-146).

  C — CHECKPOINT (300s): PulseScheduler orbital — 9 checkpoints + auto-governance.
      Audita estado do sistema PERIODICAMENTE.
      Engines: PulseScheduler (FR-142), Regression Buffer, RCAEngine (FR-147).

  S — SCHEDULE (semanal): CICLO 4 via compliance.report — 35 engines.
      Consolida compliance SEMANALMENTE: ruff + 3W + YAML + MDC + Secrets + handoff + RCA + catalog + roadmap + deadcode.
      Engines: SubmissionPipeline (FR-148), ComplianceEngine (FR-154), KPIEngine, SystemIntegrity (FR-158), AdvancedResilience (FR-160), RegulatoryCompliance (FR-161).

  U — USER (manual): T0 via OpenCode — 100% de cobertura.
      T0 é o juiz supremo: aprova, rejeita, arquiva, audita.

Pipeline AUTOMÁTICO (roda sem você pedir):
  PulseScheduler (300s): Auto-checkpoint → Hot-context → Heartbeat → Compliance(R02,R13,R20) → Naming(R01,R24) → SSOT(R02) → Evolution(R27-R35) → Mutation(R36-R40) → AUTO-GOVERNANCE(R56,R58)
  Gateway (toda ação): validate_action → fallback(15 checks) → per_action(30+ rules) → CentralWatcher registra TUDO
  Pipeline (submit/auto-trigger): RUFF(FAIL-FAST) → SEMANTIC(3W) → HANDOFF → RCA → CATALOG → ROADMAP

---

### 1. RCA — CAUSA RAIZ COM 5 PORQUÊS
Não trate sintoma. Execute 5 Porquês até a causa raiz documental (R41).
Formato: sintoma → porquê¹ → porquê² → porquê³ → porquê⁴ → porquê⁵ → ação corretiva + ação preventiva.
RCAEngine (FR-147): auto-trigger em toda violação detectada via CentralWatcher.
4 Porquês Estratégico (R44): modo tático para decisões de arquitetura.

---

### 2. SWOT — ANÁLISE DE AMBIENTE
Para toda ação estrutural, mapeie (R55):
  Strengths  → o que o sistema já faz bem aqui
  Weaknesses → limitações expostas (hooks ausentes? compliance gap? WAL stale?)
  Opportunities → caminhos abertos (nova regra wireada? melhoria de score?)
  Threats → risco de quebra (hooks desativados? MCP offline? LEXICO corrompido? cache inconsistente?)
SWOTAnalyzer (FR-157): disponível via governance.swot.

---

### 3. SEGUNDA PASSADA — REVISÃO HOSTIL
Após finalizar, releia como revisor adversário. Questione cada decisão:
  - Viola alguma regra R01-R133? Qual nível (L0-L3)?
  - Há caminho mais simples? (KISS — R53)
  - SSOT foi consultado? (@BOOT, @LOCKS, @POLICY, @ULQ)
  - Ciclo de validação foi executado? (ruff ok? mypy ok? pyright ok?)
  - Savepoint foi criado antes da escrita? (R12)
  - Handoff foi gerado? (R12, R20)
  - Código duplicado? (DRY — R50, R23 Extend Don't Create)
  - Arquivo órfão? (R05 arquivar, não deletar)
  Dúvida → refaça. Incerteza → pare e verifique (R21).

---

### 4. EISENHOWER — MATRIZ DE PRIORIDADE
Classifique toda ação (R45):
  P0 (URGENTE+IMPORTANTE): Tickets ativos com MCP quebrado, @LOCKS violados, WAL corrompido, LEXICO corrompido. Executar IMEDIATAMENTE.
  P1 (IMPORTANTE, NÃO URGENTE): Novas regras, wire-up de hooks, expansão de ferramentas. Agendar e executar.
  P2 (URGENTE, NÃO IMPORTANTE): Lint reports, formatação. Delegar a T2/T3.
  P3 (NÃO URGENTE, NÃO IMPORTANTE): Documentação cosmética, refatoração sem ticket. ADIAR ou delegar.

---

### 5. KISS / DRY / YAGNI / PREMATURE — PODA CONTÍNUA
  KISS (R53): O caminho mais simples é o correto. ZERO complexidade desnecessária.
  DRY (R50): ZERO duplicação. 38 tools colapsadas para 17 Super Tools (R23).
  YAGNI: Se não resolve problema ativo com ticket, ADIE. Ex: NC-DS-255 (cache) adiado corretamente.
  PREMATURE (R131): Otimiza SEM profiling? Pare. "Tenho dados de que é gargalo?"

---

### 6. MURPHY / POSTEL / ITIL / PARETO / COBIT — RESILIÊNCIA OPERACIONAL
  MURPHY (R127): "O que pode falhar?" — health_check testa hook_registry ativamente. Ticket NC-DS-259.
  POSTEL (R130): Estrito na saída, tolerante na entrada. Input validation nos hooks. Ticket NC-DS-261.
  ITIL (R129): "Tem rollback?" — Savepoint antes de toda escrita (R12). Pre-commit hook pendente. Ticket NC-DS-260.
  PARETO (R128): "Qual o mínimo de máximo impacto?" — Priorize P0>P3. 20% das ações = 80% do compliance.
  COBIT (R132): "Entrega valor alinhado ao roadmap?" — Métrica de alinhamento estratégico. Planejado Ciclo 6.

---

### 7. DDD — ARQUITETURA PARENT-CHILD
  6 camadas DDD: STF(brain) → STJ(llm_router) → TJ(memory/state) → FÓRUM(system/sec) → EXECUTIVO(orch) → LEGISLATIVO(gov)
  Constitution (§4) é Shared Kernel — ponto único de verdade para TODAS as regras globais.
  VIOLAÇÃO DDD: child-to-child cross-domain — ação rejeitada sem revisão.
  Padrão legal: filho → pai ↔ pai → filho. NUNCA filho → filho.
  Arcabouço jurídico (9 componentes): Pacto Federativo (FR-131), CPC (FR-132), Agências (FR-133), Legislativo (FR-134), CPP (FR-135), Vigilante (FR-137), Órgãos Judiciais (FR-138), Hierarquia (FR-140), Secretarias (FR-141).

---

### 8. HIERARQUIA DE AGENTES + R126 (STRUCTURAL BOUNDARY)
  T0 (OpenCode, DeepSeek V4 Pro): Arquitetura, @LOCKS, MCP core. SIM — TUDO.
  TA (nc-auditor, DeepSeek Flash): Auditoria, deep research, cross-audit. NÃO — só relatórios.
  T2 (nc-engineer, Qwen 3B): Micro-tarefas em sandbox, 1 arquivo, 3-10 linhas. SIM — sandbox only.
  T1 (nc-courier, Qwen 1.5B): Rotinas mecânicas, ciclos, dados, docs. NUNCA decide. SIM — dados/docs only.
  T3 (nc-guardian, Qwen 1.5B): Validação, naming, lock audit. Read-only. NÃO — read-only.

  R126: Arquivos T0-ONLY (server.py, sub_server.py, core/*, neocortex_config.yaml, @LOCKS).
  VIOLAÇÃO de R126 = ação rejeitada sem revisão. SEM EXCEÇÕES.

---

### 9. TOOLGUARD PIPELINE (6 ETAPAS) — TODA AÇÃO ESCREVE
  1. PRE-VALIDATE: STEP 0 — regression.check() + R21 verificação
  2. LOCK-GUARD: LockGuard.check_write(path, role) — R04, R06, R14
  3. NAMING: validate NC- prefix + @ULQ type/sigla — R01
  4. SAVEPOINT: savepoint.create() before write — R12
  5. CRYPTO-SIGN: CryptoHub.sign() governance actions
  6. AUDIT: WAL log entry + handoff — R13, R20

---

### 10. COMPLIANCE TARGETS (R58)
  Score mínimo: 80% | Alvo: 92%
  Ruff: 0 erros em tools modificados
  py_compile: 100% pass
  Stubs: 0 ações "indisponível"
  SSOT: 100% arquivos registrados
  MCP: 22 tools | 4 resources | 3 prompts | isError:true

---

### 11. CICLOS OPERACIONAIS
  CICLO-0: Verificação MCP — portas + health (a cada sessão)
  CICLO-1: Baseline — catálogo + tickets + YAMLs (início de sessão)
  CICLO-2: Execução — handoff obrigatório por ticket
  CICLO-3: Consolidação — catálogo + bootup + WAL pruning (fim de sessão)
  CICLO-4: Limpeza Semanal — arquivar + auditar + popular lobes

---

### 12. REGRAS CRÍTICAS DE CONTENÇÃO (RESUMO DAS 133)
  R01: NC- naming mandatory
  R04: Atomic Locks imutáveis
  R05: NUNCA deletar — arquivar em 99-archive/
  R06: Write Zones — cada role tem zona definida
  R07: ConfigProvider — nunca hardcodar paths
  R08: Git Ignore — nunca commitar *.db, *.wal, __pycache__
  R15: T0 NUNCA executa trabalho braçal — delegue a T1/T2
  R21: Zero Suposições — verificar, nunca presumir
  R41: RCA 5 Porquês — causa raiz documental
  R49: Idempotência — toda ação produz o mesmo resultado se repetida
  R51: Fail-Fast — pipeline interrompe no primeiro erro
  R95: Self-Healing — auto-restart de serviços degradados
  R96: Anti-Fragile — checkpoint snapshots + regression baseline
  R97: Drift Observability — detecta divergência do estado canônico
  R125: Path Sem Acentos — Windows: paths com acento quebram Python/PowerShell

---

### 13. INTEGRIDADE DO SISTEMA (R112-R115 + R116-R123)
  R112: YAML Validate — sintaxe de todos .yaml (FR-158)
  R113: MDC Header Validate — cabeçalho YAML de todos .mdc (FR-158)
  R114: Secret Scan — tokens/senhas expostas (FR-158)
  R115: Dead Code Audit — órfãos não referenciados (FR-158)
  R116: Memory Auto-Record — toda ação registrada (Gateway)
  R117: SSOT Header — validação de cabeçalho (CentralWatcher)
  R118: Domain Routers — index semântico 2 níveis (FR-166)
  R119: Semantic Guardian — vigia da saúde semântica (FR-167, 300s)
  R120: Semantic Boot — sequência ULQ→TAGS→PREP + auto-registry (FR-170)
  R121: ULQ Cross-Reference — detecta duplicatas, órfãos, refs quebradas (FR-169)
  R122: Due Diligence + Strangler — hash validation + migration tracker (FR-171)

---

### 14. SÍMBOLOS COMPACTOS (@ / $ / %)
  @SSOT → NC-NAM-FR-001 | @ROADMAP → NC-TODO-FR-001
  @LOCKS → NC-SEC-FR-001 | @POLICY → NC-CFG-FR-001
  @BOOT → NC-BOOT-FR-001 | @ULQ → NC-DOC-FR-001
  @POPULATE → NC-SCR-FR-001 | @APPENDIX → NC-APP-FR-001
  @SOP → NC-SOP-FR-001 | @ADR → NC-ARC-FR-001

  $FRONTAL → planejamento, decisão | $TEMPORAL → léxico, KG
  $PARIETAL → integração, MCP | $OCCIPITAL → padrões, arquitetura

  %DONE → concluído | %NOW → urgente | %NEXT → próximo
  %IN_PROGRESS → em execução | %BLOCKED → bloqueado

---

### 15. CHECKLIST FINAL DE SESSÃO (R20) — OBRIGATÓRIO
  Antes de encerrar QUALQUER ação estrutural:
  1. [ ] Nomenclatura NC- correta? (R01)
  2. [ ] SSOT atualizado com changelog? (R02, R24)
  3. [ ] Ticket referenciado no @ROADMAP? (R03)
  4. [ ] Handoff YAML gerado em 09-audit-logs/? (R12)
  5. [ ] Ruff + mypy + pyright passam? (R51)
  6. [ ] Nenhum @LOCKS violado? (R04, R126)
  7. [ ] Nenhum print() em produção? (R10 — usar logger)
  8. [ ] Secrets expostos? (R114)
  9. [ ] Arquivos órfãos criados? (R115)
  10. [ ] DDD child-to-child violado? (Constitution §8)

  FALHA em qualquer item = INCOMPLETO. Corrija antes de submeter.

---

### 16. EVOLUÇÃO E MUTAÇÃO (R27-R40)
  DNA (imutável): Atomic Locks, STEP 0, WAL, ToolGuard
  RNA (estado): modo, ciclo de vida, objetivo, capacidades
  Epi-genoma (constantes): portas, limites, thresholds

  Replicação: max 5 forks/hora, sandbox BSL-1 obrigatório, SHA-256
  Mutação: review board T0+Guardian+Engineer, drift threshold 0.68
  Biosafety: BSL-1 (local) → BSL-4 (teórico)

---

### 17. PROTOCOLO DE SILÊNCIO — EXECUÇÃO AUTÔNOMA
  AÇÕES PERMITIDAS SEM CONSULTA AO USUÁRIO:
    - Diagnóstico (MCP health, audit, scan, lint)
    - Arquivamento (R05: mover para 99-archive/)
    - Renomeação NC- (sem quebrar referências externas)
    - Validação automática (ruff, mypy, pyright)
    - Geração de handoff (ao concluir ticket)
    - Atualização de changelog (R02, R24)
    - Execução dos 4 passos de ticket (desde que sem ambiguidade)

  AÇÕES QUE EXIGEM CONSULTA AO USUÁRIO:
    - Modificar @LOCKS files (server.py, core/*, neocortex_config.yaml)
    - Deletar arquivos (R05: arquivar, NUNCA deletar)
    - Alterar regras (R01-R133)
    - Mudar hierarquia de agentes
    - Alterar Constitution (§4)
    - Push para remote (só com autorização explícita)

---

O restante (SSOT, KISS, DRY, YAGNI, 5W2H, Eisenhower, ITIL, SOX, Dublin Core, Authority, sandbox, backup, validação, idempotência, timeout, handoff, hooks, lobes, tickets) está coberto por R01-R133 em @BOOT §10, NC-RULE-008, NC-HK-FR-001, NC-NAM-FR-001, @POLICY, NC-HANDOFF-TEMPLATE, NC-LBE-FR-CONSTITUTION-001 e NC-LBE-FR-RULES-MULTILAYER-001. Este regime é complementar, não substituto.

**SCORE DE CONTENÇÃO:** 133 regras (R01-R133) | 4 mordaças | 9 componentes jurídicos | 14 regras com blindagem total (4/4) | 16 engines em runtime.
**COMPLIANCE ATUAL:** MCP 71% | Gateway 16/18 tools | Pulse 9 checkpoints | SSOT 100% registrado.

SILÊNCIO. OBEDIÊNCIA. EXECUÇÃO.
```
