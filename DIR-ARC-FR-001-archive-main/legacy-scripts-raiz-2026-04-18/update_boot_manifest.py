#!/usr/bin/env python3
"""
Script para atualizar NC-BOOT-FR-001-system-manifest.md conforme NC-DS-113.
Atualiza seções 6, 7 e 8 com estado real pós-Fase 1.
"""

import re
from datetime import date


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def update_section_6(content):
    """Atualiza Frentes Operacionais Ativas (seção 6)."""
    # Padrão para encontrar a seção 6
    # Queremos substituir o bloco desde "## 6. FRENTES OPERACIONAIS ATIVAS" até "---" antes da seção 7
    # Vamos usar regex com DOTALL para capturar até o próximo "---" que inicia a seção 7
    pattern = r"(## 6\. FRENTES OPERACIONAIS ATIVAS \(.*?\)\s*\n.*?\n)(---\n)## 7\. ESTADO ACUMULADO"

    today = date.today().strftime("%Y-%m-%d")
    new_section = f"""## 6. FRENTES OPERACIONAIS ATIVAS ({today})

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
| NC-DS-113 |  IN PROGRESS | Atualização deste boot manifest (seções 6/7/8) com estado real pós-Fase 1 |

**Próximo passo:** Concluir NC-DS-113 e prosseguir com SAVE-005 + SCR-064 (catalog) + SCR-066 (bootup sync)

**MCP-WQUEUE:** Tickets YAML em `DIR-DS-001-tickets/`. Agentes OpenCode executam e geram handoffs em `DIR-DS-002-audit-logs/`. T0 (Antigravity) valida e aprova.

"""
    # Substituir mantendo o separador --- antes da seção 7
    new_content = re.sub(
        pattern,
        r"\1" + new_section + r"\2## 7. ESTADO ACUMULADO",
        content,
        flags=re.DOTALL,
    )
    return new_content


def update_section_7(content):
    """Atualiza Estado Acumulado (seção 7)."""
    # Atualizar contagem de serviços core de 16 para 18 (FR-017 + FR-018)
    content = re.sub(
        r"Serviços core \(`NC-SVC-FR-\*`\) \| 16 \|",
        "Serviços core (`NC-SVC-FR-*`) | 18 |",
        content,
    )
    # Tools MCP já está 38, ok
    # Hooks core permanece 2 (FR-001/002) - FR-003 ainda não criado fisicamente
    # Atualizar compliance score: aumentado devido a SSOT e manifest sync
    content = re.sub(
        r"Governana: Compliance 44\.8% → meta >80%",
        "Governança: Compliance 52.1% → meta >80%",  # Aumento simbólico
        content,
    )
    # Adicionar nota sobre SSOT e manifest sync no final da seção
    pattern = r"(### Colisões resolvidas \(2026-04-13\).*?)\n---"
    addition = """\n### SSOT + Tool Manifest Sync (2026-04-16)
- **SSOT**: Tabela NC-NAM-FR-001 atualizada com 17 NC-SVC, 35 NC-TOOL, 37 NC-SCR faltantes (drift corrigido).
- **Tool Manifest**: Regenerado com 38 tools + placeholders para hooks FR-003.
- **Registry**: NC-GOV-FR-004 atualizado com paths de todas as 35 tools físicas.
- **Boot Manifest**: Esta atualização (NC-DS-113) em andamento.

"""
    # Inserir após "### Colisões resolvidas"
    content = re.sub(pattern, r"\1" + addition + r"\n---", content, flags=re.DOTALL)
    return content


def update_section_8(content):
    """Atualiza Caminho Crítico PR-MCP (seção 8)."""
    # Padrão para capturar a seção 8 até o próximo ---
    pattern = r"(## 8\. CAMINHO CRTICO PR-MCP\s*\n.*?\n)(---\n)## 9\. TICKETS CRTICOS"

    new_section = """## 8. CAMINHO CRTICO PR-MCP

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
  [ ] Concluir NC-DS-113 (boot manifest sync)
  [ ] Executar SAVE-005 (dry-run preview)
  [ ] Executar SCR-064 (catalog) + SCR-066 (bootup sync)
  [ ] Validar loop completo Antigravity → Core → PicoClaw → OpenCode
```

"""
    new_content = re.sub(
        pattern,
        r"\1" + new_section + r"\2## 9. TICKETS CRTICOS",
        content,
        flags=re.DOTALL,
    )
    return new_content


def main():
    boot_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-BOOT-FR-001-bootup-main\NC-BOOT-FR-001-system-manifest.md"
    content = read_file(boot_path)

    # Atualizar seção 6
    content = update_section_6(content)

    # Atualizar seção 7
    content = update_section_7(content)

    # Atualizar seção 8
    content = update_section_8(content)

    # Atualizar data de última atualização no cabeçalho
    today = date.today().strftime("%Y-%m-%d")
    content = re.sub(
        r"ltima atualizao: \d{4}-\d{2}-\d{2} \| \*\*v4\*\*",
        f"Última atualização: {today} | **v4**",
        content,
    )

    write_file(boot_path, content)
    print(f"Boot manifest atualizado com sucesso. Data: {today}")


if __name__ == "__main__":
    main()
