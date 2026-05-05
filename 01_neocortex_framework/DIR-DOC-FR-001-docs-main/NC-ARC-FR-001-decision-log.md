# NC-ARC-FR-001 — Architecture Decision Log
# @ADR — Registro de decisões arquiteturais do NeoCortex
# Hash: ADR-v1.0-20260427

## ADR-001: MCP via SSE remoto, não stdio local
- **Data:** 2026-04-27
- **Decisão:** OpenCode conecta ao MCP via SSE remoto (http://localhost:8766/sse)
- **Alternativa rejeitada:** stdio local (uv_spawn incompatível com paths com espaço no Windows)
- **Consequência:** Servidor MCP precisa estar rodando antes do OpenCode iniciar

## ADR-002: PYTHONPATH via Junction C:\TQ
- **Data:** 2026-04-27
- **Decisão:** Usar C:\TQ como junction para C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42
- **Motivo:** Acento em "Valério" corrompia em múltiplas ferramentas
- **Consequência:** Todos os paths internos referenciam C:\TQ

### ⚠️ R125 — Path sem acento (derivado de ADR-002)
**REGRA:** Scripts Python/ferramentas externas NÃO processam paths com acento corretamente no Windows.
- Use `C:\TQ` (junction) em vez de `C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42`
- Em Python: `pathlib.Path(r"C:\TQ")` sempre
- Em PowerShell: use `Get-Item` para resolver paths com acento, NUNCA strings literais
- No LEXICO e SSOT: documente paths com acento, mas em runtime use C:\TQ
- **Violação:** scripts falham silenciosamente (file not found)

## ADR-003: PulseScheduler desabilitado no SSE
- **Data:** 2026-04-27
- **Decisão:** Desabilitar PulseScheduler.start() e SessionManager no modo SSE
- **Motivo:** Background threads causavam crash do servidor após ~30s
- **Consequência:** Auto-checkpoints, pruning, TTL parados. Operações manuais via MCP.

## ADR-004: ToolGuard como middleware central
- **Data:** 2026-04-27
- **Decisão:** Criar NC-CORE-FR-125-tool-guard.py como middleware único de governança
- **Pipeline:** STEP 0 → LockGuard → Naming (@ULQ) → SavePoint → CryptoSign → Audit
- **Alternativa rejeitada:** Middleware em cada tool separadamente (código duplicado)

## ADR-005: Super Tools consolidam 38 tools em 17
- **Data:** 2026-04-20
- **Decisão:** Consolidar 38 NC-TOOL-FR-* em 17 NC-SUPER-* (uma por domínio DDD)
- **Motivo:** Reduzir chamadas MCP e unificar ações relacionadas
- **Consequência:** Tools antigas arquivadas em v1/, Super Tools respondem por múltiplas ações

## ADR-006: DDD com 6 camadas (STF, STJ, TJ, FÓRUM, EXECUTIVO, LEGISLATIVO)
- **Data:** 2026-04-18
- **Decisão:** Arquitetura em 6 camadas inspirada na divisão dos poderes
- **Blueprint:** NC-ARC-FR-002-architecture-blueprint.yaml
- **Consequência:** Cada camada tem responsabilidades bem definidas e isoladas

## ADR-007: Junction @SSOT em DIR-DOC-FR-001-docs-main/
- **Data:** 2026-04-13
- **Decisão:** Centralizar documentação SSOT em DIR-DOC-FR-001-docs-main/
- **Arquivos:** NC-NAM-FR-001, NC-TODO-FR-001, NC-SEC-FR-001, NC-ARC-FR-002
- **Consequência:** Único ponto de verdade para documentação do sistema
