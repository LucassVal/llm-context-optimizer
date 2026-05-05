#!/usr/bin/env python3
"""
Script para atualizar NC-BOOT-FR-001-system-manifest.md conforme NC-DS-113.
Atualiza seções 6, 7 e 8 com estado real pós-Fase 1.
Abordagem: split por seções.
"""

import re
from datetime import date


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def update_content(content):
    today = date.today().strftime("%Y-%m-%d")

    # 1. Atualizar data no cabeçalho
    content = re.sub(
        r"ltima atualizao: \d{4}-\d{2}-\d{2} \| \*\*v4\*\*",
        f"Última atualização: {today} | **v4**",
        content,
    )

    # 2. Substituir SEÇÃO 6 inteira
    # Encontrar desde "## 6. FRENTES OPERACIONAIS ATIVAS" até "---" antes da seção 7
    # Usar lookahead para capturar até o próximo "## 7."
    pattern_section6 = r"(## 6\. FRENTES OPERACIONAIS ATIVAS \(.*?\)\s*\n.*?)(?=\n## 7\. ESTADO ACUMULADO)"

    new_section6 = f"""## 6. FRENTES OPERACIONAIS ATIVAS ({today})

**CICLO 3 — CONCLUÍDO em 2026-04-16**

| Ticket | Status | Resumo |
|---|---|---|
| NC-DS-085 |  DONE | SCR-002 + SCR-022 validados (Marco 2 Rastreabilidade) |
| NC-DS-088 |  DONE | Roadmaps v5/v6/v7 arquivados — estrutura limpa |
| NC-DS-089 |  DONE | WAL integrado nos 3 scripts do Ciclo 3 |
| NC-DS-090 |  DONE | NC-SVC-FR-018 TagNormalizerService criado |
| NC-DS-091 |  DONE | NC-SVC-FR-017 CryptoHub Fernet real criado |
| NC-DS-092 |  DONE | TagNormalizer wired → SCR-009, SCR-066 |
| NC-DS-093 |  DONE | CryptoHub wired → security_service.py |
| NC-DS-094 |  DONE | SSOT @LOCK→@LOCKS, símbolos $ adicionados, sys.modules fix |
| NC-DS-095 |  DONE | NC-DS-089 fechado, boot manifest seção 7 atualizado |
| NC-DS-096 |  DONE | ORCH-301 + ORCH-302: send_task() HTTP real + SSE status |
| NC-DS-097 |  DONE | Marco 2 + arquivo roadmaps fechados formalmente |

**CICLO 4 — EM ANDAMENTO (SSOT + Tool Manifest Sync)**

| Ticket | Status | Resumo |
|---|---|---|
| NC-DS-111 |  DONE | Cross-audit SSOT vs arquivos físicos; drift report gerado; SSOT atualizado |
| NC-DS-112 |  DONE | Tool manifest regenerado (38 tools + hooks FR-003); registry atualizado |
| NC-DS-113 |  DONE | Atualização deste boot manifest (seções 6/7/8) com estado real pós-Fase 1 |

**Próximo passo:** Prosseguir com SAVE-005 + SCR-064 (catalog) + SCR-066 (bootup sync)

**MCP-WQUEUE:** Tickets YAML em `DIR-DS-001-tickets/`. Agentes OpenCode executam e geram handoffs em `DIR-DS-002-audit-logs/`. T0 (Antigravity) valida e aprova.

"""
    content = re.sub(pattern_section6, new_section6, content, flags=re.DOTALL)

    # 3. Substituir SEÇÃO 7 inteira (desde "## 7. ESTADO ACUMULADO" até "---" antes da seção 8)
    pattern_section7 = r"(## 7\. ESTADO ACUMULADO  O QUE FOI CONSTRUDO\s*\n.*?)(?=\n## 8\. CAMINHO CRTICO PR-MCP)"

    new_section7 = """## 7. ESTADO ACUMULADO  O QUE FOI CONSTRUDO

| Grupo | Quantidade | Status |
|---|---|---|
| Serviços core (`NC-SVC-FR-*`) | 18 |  DONE |
| Utils (`NC-UTL-FR-*`) | 4 |  DONE |
| Tools MCP (`NC-TOOL-FR-000037`) | 38 |  DONE |
| Hooks core (`NC-HK-FR-001/002`) | 2 |  DONE |
| Config core (`NC-CFG-FR-004`) | 1 |  DONE |
| Lobes de integração (`NC-LBE-INT-004/005`) | 2 |  Em documentação |
| HUD Tkinter (5 abas) | 1 |  FUNCIONAL |
| PicoClaw gateway | 1 |  :18790 ativo |

**Serviços adicionados em 2026-04-16 (Ciclo 3):**

| Serviço | ID | Status | Descrição |
|---|---|---|---|
| CryptoHub | `NC-SVC-FR-017` |  ACTIVE | Fernet AES-128 + HMAC-SHA256. Key via PBKDF2(MASTER_KEY). Fallback hash-only. |
| TagNormalizer | `NC-SVC-FR-018` |  ACTIVE | Valida @/$/%  contra NC-DOC-FR-001 SSOT. scan(), normalize(), validate_lobe(). |

**Governança:** Compliance 52.1% → meta >80%

### Colisões resolvidas (2026-04-13)
FR-032, FR-033, FR-020-categories, FR-028-export  arquivados em `DIR-ARC-FR-001-archive-main/tools-duplicates-20260413/`

### SSOT + Tool Manifest Sync (2026-04-16)
- **SSOT**: Tabela NC-NAM-FR-001 atualizada com 17 NC-SVC, 35 NC-TOOL, 37 NC-SCR faltantes (drift corrigido).
- **Tool Manifest**: Regenerado com 38 tools + placeholders para hooks FR-003.
- **Registry**: NC-GOV-FR-004 atualizado com paths de todas as 35 tools físicas.
- **Boot Manifest**: Esta atualização (NC-DS-113) concluída.

"""
    content = re.sub(pattern_section7, new_section7, content, flags=re.DOTALL)

    # 4. Substituir SEÇÃO 8 inteira (desde "## 8. CAMINHO CRTICO PR-MCP" até "---" antes da seção 9)
    pattern_section8 = (
        r"(## 8\. CAMINHO CRTICO PR-MCP\s*\n.*?)(?=\n## 9\. TICKETS CRTICOS)"
    )

    new_section8 = """## 8. CAMINHO CRTICO PR-MCP

```
FASE PR-MCP [ATUAL]:
   Antigravity ↔ MCP stdio ↔ NeoCortex Core — configurado
   PicoClaw ↔ OpenCode ↔ DeepSeek — operacional
   38 tools MCP físicos — criados e manifestados
   ORCH-301 — DONE (NC-DS-096, send_task() HTTP POST :18790)
   ORCH-302 — DONE (NC-DS-096, neocortex_task SSE polling)
   SAVE-005 — WIRED (dry-run preview middleware)

CRITÉRIO DE ENCERRAMENTO DA FASE PR-MCP:
  Antigravity chama tool MCP → Core recebe → PicoClaw despacha → OpenCode executa → resultado retorna
  = Loop completo Antigravity ↔ Core ↔ PicoClaw ↔ OpenCode via MCP

PRÓXIMOS PASSOS:
  [ ] Executar SAVE-005 (dry-run preview)
  [ ] Executar SCR-064 (catalog) + SCR-066 (bootup sync)
  [ ] Validar loop completo Antigravity → Core → PicoClaw → OpenCode
```

"""
    content = re.sub(pattern_section8, new_section8, content, flags=re.DOTALL)

    return content


def main():
    boot_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-BOOT-FR-001-bootup-main\NC-BOOT-FR-001-system-manifest.md"
    content = read_file(boot_path)
    new_content = update_content(content)
    write_file(boot_path, new_content)
    print(
        f"Boot manifest atualizado com sucesso. Data: {date.today().strftime('%Y-%m-%d')}"
    )


if __name__ == "__main__":
    main()
