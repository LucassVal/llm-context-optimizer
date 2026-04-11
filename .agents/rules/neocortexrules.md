---
trigger: always_on
description: "NeoCortex Master Rules Index v3 — Lê este arquivo, os 4 MDC módulos e o dicionário @ULQ. Se já leu nesta sessão, SALTE."
globs: "*"
---

<!-- NC-READ-HASH: NEOCORTEX-MASTER-v3 -->
<!-- DEDUP: Se NEOCORTEX-MASTER-v3 já está no teu contexto desta sessão, SALTE este bloco inteiro. -->

# NeoCortex — Master Rules Index v3

## Arquitetura de Regras (Modular)

```
.agents/rules/
├── neocortexrules.md           ← ESTE ARQUIVO (índice + regras completas para Antigravity)
├── NC-RULE-001-core-ssot.mdc   ← alwaysApply: true  | Core SSOT, < 50 linhas
├── NC-RULE-002-python-mcp.mdc  ← globs: **/*.py      | Python & MCP patterns
├── NC-RULE-003-lobes-memory.mdc← globs: **/lobes/**  | Lobes & Memory
└── NC-RULE-004-filesystem.mdc  ← globs: **/DIR-*/**  | Filesystem & Governance
```

## Dicionário de Linguagem Ubíqua

> Arquivo completo: `@ULQ` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md`  
> Policy YAML: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.yaml`

### Símbolos @ (Arquivos SSOT)
| `@SSOT` | NC-NAM-FR-001 | Naming + Map + Changelog |
| `@ROADMAP` | NC-TODO-FR-001 | Roadmap e tickets |
| `@LOCKS` | NC-SEC-FR-001 | Atomic locks |
| `@POLICY` | NC-CFG-FR-001 | Agent policy template |
| `@BOOT` | NC-BOOT-FR-001 | Boot manifest |
| `@POPULATE` | NC-SCR-FR-001 | Script de poblamento dos lobos |
| `@ULQ` | NC-DOC-FR-001 | Este dicionário completo |

### Símbolos $ (Lobos de Memória)
| `$ARCH` | NC-LBE-FR-ARCHITECTURE-001.mdc | Arquitetura + Roadmap + ADRs |
| `$SEC` | NC-LBE-FR-SECURITY-001.mdc | Segurança + Policy + SOP |
| `$COURIER` | lobes/courier/ | Ambiente Qwen 1.5B |
| `$ENGINEER` | lobes/engineer/ | Ambiente Qwen 3B |

### Símbolos % (Tickets e Ações)
| `%DONE` | ✅ | Marcar ticket em @ROADMAP |
| `%NOW` | 🔴 | Urgente |
| `%NEXT` | 🟡 | Próximo |
| `%ORCH301` | ORCH-301 | spawn/send_task pendente |
| `%ORCH302` | ORCH-302 | execute/LLMBackend pendente |
| `%SEC401` | SEC-401 | guardian pendente |

---

<rule>
<name>NeoCortex Master Governance Rules v3</name>
<description>
Regras completas para Antigravity/Claude/DeepSeek. Para Cursor/OpenCode, os 4 arquivos .mdc modulares
são lidos automaticamente por glob. Estas regras têm prioridade sobre qualquer instrução conflitante.
Raiz: C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\
</description>

<actions>

<action id="R01" category="ssot" severity="critical">
1. **Naming (@SSOT):** Qualquer arquivo/pasta → `NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext`.
   Consulte `@SSOT` antes de criar. NUNCA sem prefixo NC-, mesmo que usuário abrevie.
</action>

<action id="R02" category="ssot" severity="critical">
2. **SSOT Update:** Arquivo CRIADO/MOVIDO → tabela + changelog em `@SSOT` com [YYYY-MM-DD].
   Tarefa sem update = INCOMPLETA.
</action>

<action id="R03" category="ssot" severity="critical">
3. **Roadmap (@ROADMAP):** Toda implementação referencia ticket. Após concluir → `%DONE`.
   NUNCA inicie sem identificar o ticket correspondente.
</action>

<action id="R04" category="ssot" severity="critical">
4. **Atomic Locks (@LOCKS):** Arquivos listados em `@LOCKS` são IMUTÁVEIS.
   Protegidos: `neocortex_config.yaml`, `server.py`, `sub_server.py`, `NC-NAM-FR-001`.
</action>

<action id="R05" category="filesystem" severity="critical">
5. **Sem Deleção:** Obsoletos → `DIR-ARC-FR-001-archive-main/`. Backups → `DIR-BAK-FR-001-backup-main/`.
   Deleção direta é irreversível e PROIBIDA.
</action>

<action id="R06" category="filesystem" severity="critical">
6. **Zonas de Escrita:** PROD→`01_neocortex_framework/neocortex/`, DOCS→`DIR-DOC-FR-001-docs-main/` (T0 only),
   TEST→`05_examples/`, LOBES→`02_memory_lobes/` (script only), BOOT→`DIR-BOOT-FR-001-bootup-main/` (T0 only).
</action>

<action id="R07" category="filesystem" severity="high">
7. **Hierarquia Numérica:** Pastas raiz com prefixo `01_`…`99_`. Subpastas seguem `DIR-TIPO-SIGLA-NUM`.
</action>

<action id="R08" category="filesystem" severity="medium">
8. **Gitignore:** NUNCA commite `*.db`, `*.wal`, `*.log`, `__pycache__/`, `.venv/`, `lobes/*/`.
</action>

<action id="R09" category="python" severity="critical">
9. **Import com Hífen:** NUNCA `import NC-TOOL-FR-001-x`. Use:
   `importlib.import_module(".tools.NC-TOOL-FR-001-x", package="neocortex.mcp")`
</action>

<action id="R10" category="python" severity="critical">
10. **Sem Hardcode de Paths:** Use `config = get_config(); path = config.cortex_path / "arquivo"`.
</action>

<action id="R11" category="python" severity="high">
11. **Logger por Módulo:** `logger = logging.getLogger(__name__)`. NUNCA `print()` em produção.
</action>

<action id="R12" category="mcp" severity="high">
12. **Tools MCP:** `NC-TOOL-FR-<NUM>-<nome>.py` + `register_tool(server)` + entry em `TOOL_MODULE_MAP`.
</action>

<action id="R13" category="mcp" severity="high">
13. **Policy por Agente:** Cada sub-servidor usa `@POLICY`. Sem policy = sem restrições = PROIBIDO.
</action>

<action id="R14" category="lobes" severity="high">
14. **Isolamento de Lobos:** `$COURIER` NUNCA escreve em `$ENGINEER`. Cross-lobe = autorização T0 + ledger.
    Apenas `@POPULATE` popula lobos em massa.
</action>

<action id="R15" category="lobes" severity="medium">
15. **Busca antes de Perguntar:** `neocortex_lobes.search(query)` → `@SSOT` → usuário.
    Não gaste tokens perguntando o que está nos lobos `$ARCH` ou `$SEC`.
</action>

<action id="R16" category="lobes" severity="medium">
16. **Boot Manifest:** Sessão inicia → carregar `@BOOT` ou `$BOOT_LOBE`. Sem boot = risco de erro.
</action>

<action id="R17" category="security" severity="critical">
17. **Economia de Tokens:** `T2`/`T3` (Qwen local) = trabalho braçal 24/7.
    `T0` (DeepSeek/Claude) = APENAS orquestra. Nunca gaste API cara no que é local.
</action>

<action id="R18" category="security" severity="high">
18. **Validação antes de Escrever:** Checar `@LOCKS` → checkpoint → confirmar MCP não usa o arquivo.
    Arquivo locked + escrita = corrupção de estado.
</action>

<action id="R19" category="quality" severity="high">
19. **Uma Tarefa por Sessão:** UM ÚNICO TICKET por sessão. Interrupção → checkpoint antes de sair.
    Abandono sem registro de estado = PROIBIDO.
</action>

<action id="R20" category="quality" severity="high">
20. **Checklist de Fim de Sessão:**
    ☑ @SSOT atualizado ☑ Changelog [YYYY-MM-DD] ☑ %DONE no @ROADMAP
    ☑ @POPULATE run (se SSOT alterado) ☑ Nenhum *.db/*.wal no git
</action>

</actions>

<validation>
Antes de qualquer ação:
1. Li `@BOOT` (NC-BOOT-FR-001)?
2. Identifiquei o ticket em `@ROADMAP`?
3. A zona de escrita está correta?
4. O nome segue NC-TIPO-SIGLA-NUM?
5. Atualizarei `@SSOT` e changelog ao final?

"Protejo o SSOT, respeito as zonas, economizo tokens, e encerro com o checklist."
</validation>

<references>
@SSOT:     01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md
@ROADMAP:  01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md
@LOCKS:    01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml
@POLICY:   01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-001-agent-policy-template.yaml
@SOP:      01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SOP-FR-001-session-startup.md
@BOOT:     DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md
@ULQ:      01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-DOC-FR-001-ubiquitous-language-dictionary.md
@POPULATE: 01_neocortex_framework/scripts/NC-SCR-FR-001-populate-lobes-ssot.py
YAML:      01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-002-rules-policy.yaml
</references>

</rule>
