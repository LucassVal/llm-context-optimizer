# NC-ARC-FR-001 — Architecture Decision Records (ADR)

> **Propósito:** Registrar TODAS as decisões arquiteturais do NeoCortex com contexto, alternativas consideradas e justificativa. Essencial para onboarding de novos desenvolvedores e para que a IA entenda o histórico sem precisar re-explorar o código.

---

## ADR-001 — RocksDB via pyspeedb (ao invés de RocksDB puro)

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** Precisávamos de um key-value store ACID para o LedgerStore e ManifestStore com alta performance em Windows.

**Decisão:** Usar `pyspeedb` (fork do RocksDB com patch de latência de compactação).

**Alternativas consideradas:**
- RocksDB puro: latências imprevisíveis durante compactação em Windows.
- LMDB: bom para leitura, ruim para escrita intensa.
- SQLite: overhead relacional desnecessário para KV puro.

**Justificativa:** `pyspeedb` elimina as pausas de compactação do RocksDB mantendo compatibilidade total de API.

---

## ADR-002 — SQLite + FTS5 como Motor de Busca Principal

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** O LobeIndex precisava de busca textual rápida sem dependências externas.

**Decisão:** SQLite com extensão FTS5 nativa.

**Alternativas consideradas:**
- Xapian (`xapian-bindings`): excelente performance mas dependência C++ complexa no Windows.
- Tantivy (Rust): ainda melhor performance, mas bindings Python instáveis.
- Elasticsearch: overkill para uso local, dependência de JVM.

**Justificativa:** FTS5 é built-in no Python, zero dependências extras, performance adequada para até ~100k documentos.

---

## ADR-003 — DuckDB para MetricsStore (ao invés de InfluxDB/TimescaleDB)

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** Precisávamos de analytics de métricas (tokens, custos, performance) com SQL.

**Decisão:** DuckDB como banco embarcado OLAP.

**Alternativas consideradas:**
- InfluxDB: excelente para time-series mas requer servidor separado.
- TimescaleDB: extensão PostgreSQL, overhead desnecessário para uso local.
- SQLite: baixa performance para queries analíticas agregadas.

**Justificativa:** DuckDB é embarcado (zero servidor), performance OLAP superior ao SQLite, suporte nativo a Parquet e Arrow.

---

## ADR-004 — diskcache-rs para HotCache (ao invés de Redis local)

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** PulseScheduler precisava de cache volátil de alta performance para `hot_context`.

**Decisão:** `diskcache-rs` (implementação Rust com bindings Python).

**Alternativas consideradas:**
- Redis (local): mais features mas requer daemon separado.
- `functools.lru_cache`: in-memory puro, não persiste entre reinicializações.
- Shelve/pickle: lento e sem TTL nativo.

**Justificativa:** Performance Rust, TTL nativo, persiste no disco entre sessões, zero daemon externo.

---

## ADR-005 — FastMCP como Framework do Servidor MCP

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** Precisávamos de um framework Python para expor ferramentas via protocolo MCP.

**Decisão:** FastMCP com transporte WebSocket via uvicorn.

**Alternativas consideradas:**
- MCP SDK oficial Python: menos maduro, menos ferramentas de conveniência.
- Implementação manual do protocolo: trabalho excessivo, risco de bugs.
- FastAPI com endpoints REST: não compatível com o protocolo MCP nativo.

**Justificativa:** FastMCP encapsula o protocolo MCP com decorator `@mcp.tool()`, reduzindo boilerplate. WebSocket escolhido sobre STDIO para compatibilidade com múltiplos clientes IDE simultâneos.

---

## ADR-006 — Qwen2.5-Coder 1.5B como Agente Local Principal

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** Precisávamos de um modelo local para execução de tarefas braçais 24/7 sem custo de API.

**Decisão:** Qwen2.5-Coder 1.5B via Ollama para o agente Courier.

**Alternativas consideradas:**
- TinyLlama 1.1B: menor, mas qualidade de código inferior.
- Phi-3 Mini: bom raciocínio, mas menos otimizado para código.
- CodeGemma 2B: bom mas maior consumo de VRAM.

**Justificativa:** Qwen2.5-Coder tem o melhor benchmark de código na faixa de 1-2B parâmetros, roda em 4GB RAM/VRAM, custo zero de API.

---

## ADR-007 — msgspec ao invés de Pydantic para Validação

**Data:** 2026-04  
**Status:** ✅ Implementado

**Contexto:** Precisávamos de serialização/validação de schemas JSON de alta performance.

**Decisão:** `msgspec` para serialização e validação de schemas internos.

**Alternativas consideradas:**
- Pydantic v2: excelente mas overhead maior em validação de alta frequência.
- json (stdlib): sem validação de schema.
- orjson: rápido para serialização mas sem validação.

**Justificativa:** msgspec é 10-50x mais rápido que Pydantic para serialização pura, com zero dependências extras.

---

## ADR-008 — Arquitetura de Lobos como Memória de Longo Prazo

**Data:** 2026-04  
**Status:** ✅ Design implementado, FTS5 indexado

**Contexto:** Como persistir contexto entre sessões sem enviar contexto completo a cada requisição?

**Decisão:** Lobos MDC como unidades atômicas de memória, indexados via FTS5, buscáveis via `neocortex_lobes.search`.

**Justificativa:** Permite que o T0 recupere knowledge específico sem tokens desnecessários, reduzindo custo de API em estimados 60-80% para tarefas recorrentes.
