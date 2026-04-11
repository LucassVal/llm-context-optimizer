# NC-DOC-FR-001-ubiquitous-language-dictionary.md
# Dicionário de Linguagem Ubíqua — NeoCortex Framework
# Símbolos: @ = arquivo/documento, $ = lobo/memória, % = ticket/ação

<!-- NC-READ-HASH: ULQ-v1.0 -->
<!-- Se você já leu este arquivo nesta sessão (hash ULQ-v1.0 presente no contexto), PARE. Não releia. -->

---

## @ — Referência de Arquivos SSOT

| Símbolo | Expande para | Caminho Real |
| :--- | :--- | :--- |
| `@SSOT` | NC-NAM-FR-001 (Naming + Map + Changelog) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md` |
| `@ROADMAP` | NC-TODO-FR-001 (Roadmap consolidado) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` |
| `@APPENDIX` | NC-APP-FR-001 (Apêndice técnico) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-APP-FR-001-technical-appendix.md` |
| `@LOCKS` | NC-SEC-FR-001 (Atomic locks) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml` |
| `@POLICY` | NC-CFG-FR-001 (Agent policy template) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-001-agent-policy-template.yaml` |
| `@SOP` | NC-SOP-FR-001 (Session startup SOP) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md` |
| `@ADR` | NC-ARC-FR-001 (Architecture decision log) | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-ARC-FR-001-decision-log.md` |
| `@BOOT` | NC-BOOT-FR-001 (Boot manifest) | `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md` |
| `@PROMPT` | NC-PROMPT-FR-001 (Master context prompt) | `NC-PROMPT-FR-001-master-context.md` |
| `@RULES` | NC-RULE-001 / neocortexrules.md | `.agents/rules/NC-RULE-001-workspace-standards.mdc` |
| `@POPULATE` | Script de poblamento dos lobos | `01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py` |
| `@CONFIG` | neocortex_config.yaml | `01_neocortex_framework/DIR-CFG-FR-001-config-main/neocortex_config.yaml` |

---

## $ — Referência de Lobos (Memória Persistente)

| Símbolo | Lobo MDC | Conteúdo |
| :--- | :--- | :--- |
| `$ARCH` | NC-LBE-FR-ARCHITECTURE-001.mdc | Roadmap + Naming + ADRs + Apêndice Técnico |
| `$SEC` | NC-LBE-FR-SECURITY-001.mdc | Atomic Locks + Agent Policy + SOP + Checklist |
| `$DEV` | NC-LBE-FR-DEVELOPMENT-001.mdc | Auditorias + Alinhamentos de Arquitetura |
| `$PROF` | NC-LBE-FR-PROFILES-001.mdc | Schemas de developer/team |
| `$WL` | NC-LBE-FR-WHITELABEL-001.mdc | Templates white-label |
| `$BENCH` | NC-LBE-FR-BENCHMARKS-001.mdc | Resultados de benchmark |
| `$BOOT_LOBE` | NC-BOOT-FR-001-system-manifest.mdc | Boot manifest indexado |
| `$COURIER` | lobes/courier/ | Ambiente isolado Courier (Qwen 1.5B) |
| `$ENGINEER` | lobes/engineer/ | Ambiente isolado Engineer (Qwen 3B) |
| `$GUARDIAN` | lobes/guardian/ | Ambiente isolado Guardian (validação) |

---

## % — Referência de Tickets e Ações

| Símbolo | Ticket | Descrição |
| :--- | :--- | :--- |
| `%AGENT203` | AGENT-203 | mentor_step_0() — ✅ DONE |
| `%ORCH301` | ORCH-301 | spawn/stop/send_task robustos — 🔴 Pendente |
| `%ORCH302` | ORCH-302 | execute integrado com LLMBackend — 🔴 Pendente |
| `%SEC401` | SEC-401 | neocortex_guardian ativo — 🔴 Pendente |
| `%SEC403` | SEC-403 | limits.* enforcement por agente — 🟡 Parcial |
| `%DONE` | ✅ | Marcar ticket como concluído em @ROADMAP |
| `%NOW` | 🔴 | Ação imediata obrigatória |
| `%NEXT` | 🟡 | Próximo na fila |

---

## Agentes e Tiers LLM

| Símbolo | Agente | Modelo | Custo |
| :--- | :--- | :--- | :--- |
| `T0` | Orquestrador (você/AI principal) | DeepSeek / Claude | 💰 Caro |
| `T2` | Courier | qwen2.5-coder:1.5b | 🟢 Grátis local |
| `T3` | Engineer | qwen2.5-coder:3b | 🟢 Grátis local |
| `TG` | Guardian | qwen2.5-coder:1.5b | 🟢 Grátis local |

---

## Zonas de Escrita Permitidas

| Zona | Caminho | Quem pode escrever |
| :--- | :--- | :--- |
| `ZONE:PROD` | `01_neocortex_framework/` | T0 + agentes autorizados |
| `ZONE:TEST` | `05_examples/` + `DIR-TEST-FR` | T2, T3 |
| `ZONE:DOCS` | `01_neocortex_framework/DIR-DOC-FR-001-docs-main/` | T0 apenas |
| `ZONE:LOBES` | `02_memory_lobes/` | Script @POPULATE apenas |
| `ZONE:ARCH` | `DIR-ARC-FR-001-archive-main/` | Qualquer (só movimentos) |
| `ZONE:BOOT` | `DIR-BOOT-FR-001-bootup-main/` | T0 apenas |

---

## Padrão de Nomenclatura Resumido

```
NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext
DIR-<TIPO>-<SIGLA>-<NUM>-<desc>/
```

| TIPO | Uso |
| `DOC` | Documentação geral |
| `TODO` | Roadmap e tickets |
| `APP` | Apêndice técnico |
| `TOOL` | Ferramenta MCP |
| `SCR` | Script Python |
| `LBE` | Lobo de memória .mdc |
| `CFG` | Configuração YAML |
| `SEC` | Segurança e locks |
| `SOP` | Standard Operating Procedure |
| `ARC` | ADR e decisões |
| `BAK` | Backup |
| `BOOT` | Arquivos de inicialização |
| `ALN` | Alinhamento arquitetural |
| `AUD` | Auditoria |
| `TST` | Testes |
| `DPL` | Deployment |
| `API` | Referência de API |
| `LIB` | Dependências externas |
| `PRF` | Profile de usuário/agente |
| `NAM` | Naming convention (este arquivo) |
