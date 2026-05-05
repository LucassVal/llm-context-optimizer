# NC-ARC-FR-001  Architecture Decision Records (ADR)

> **Propsito:** Registrar TODAS as decises arquiteturais do NeoCortex com contexto, alternativas consideradas e justificativa. Essencial para onboarding de novos desenvolvedores e para que a IA entenda o histrico sem precisar re-explorar o cdigo.

---

## ADR-001  RocksDB via pyspeedb (ao invs de RocksDB puro)

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** Precisvamos de um key-value store ACID para o LedgerStore e ManifestStore com alta performance em Windows.

**Deciso:** Usar `pyspeedb` (fork do RocksDB com patch de latncia de compactao).

**Alternativas consideradas:**
- RocksDB puro: latncias imprevisveis durante compactao em Windows.
- LMDB: bom para leitura, ruim para escrita intensa.
- SQLite: overhead relacional desnecessrio para KV puro.

**Justificativa:** `pyspeedb` elimina as pausas de compactao do RocksDB mantendo compatibilidade total de API.

---

## ADR-002  SQLite + FTS5 como Motor de Busca Principal

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** O LobeIndex precisava de busca textual rpida sem dependncias externas.

**Deciso:** SQLite com extenso FTS5 nativa.

**Alternativas consideradas:**
- Xapian (`xapian-bindings`): excelente performance mas dependncia C++ complexa no Windows.
- Tantivy (Rust): ainda melhor performance, mas bindings Python instveis.
- Elasticsearch: overkill para uso local, dependncia de JVM.

**Justificativa:** FTS5  built-in no Python, zero dependncias extras, performance adequada para at ~100k documentos.

---

## ADR-003  DuckDB para MetricsStore (ao invs de InfluxDB/TimescaleDB)

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** Precisvamos de analytics de mtricas (tokens, custos, performance) com SQL.

**Deciso:** DuckDB como banco embarcado OLAP.

**Alternativas consideradas:**
- InfluxDB: excelente para time-series mas requer servidor separado.
- TimescaleDB: extenso PostgreSQL, overhead desnecessrio para uso local.
- SQLite: baixa performance para queries analticas agregadas.

**Justificativa:** DuckDB  embarcado (zero servidor), performance OLAP superior ao SQLite, suporte nativo a Parquet e Arrow.

---

## ADR-004  diskcache-rs para HotCache (ao invs de Redis local)

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** PulseScheduler precisava de cache voltil de alta performance para `hot_context`.

**Deciso:** `diskcache-rs` (implementao Rust com bindings Python).

**Alternativas consideradas:**
- Redis (local): mais features mas requer daemon separado.
- `functools.lru_cache`: in-memory puro, no persiste entre reinicializaes.
- Shelve/pickle: lento e sem TTL nativo.

**Justificativa:** Performance Rust, TTL nativo, persiste no disco entre sesses, zero daemon externo.

---

## ADR-005  FastMCP como Framework do Servidor MCP

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** Precisvamos de um framework Python para expor ferramentas via protocolo MCP.

**Deciso:** FastMCP com transporte WebSocket via uvicorn.

**Alternativas consideradas:**
- MCP SDK oficial Python: menos maduro, menos ferramentas de convenincia.
- Implementao manual do protocolo: trabalho excessivo, risco de bugs.
- FastAPI com endpoints REST: no compatvel com o protocolo MCP nativo.

**Justificativa:** FastMCP encapsula o protocolo MCP com decorator `@mcp.tool()`, reduzindo boilerplate. WebSocket escolhido sobre STDIO para compatibilidade com mltiplos clientes IDE simultneos.

---

## ADR-006  Qwen2.5-Coder 1.5B como Agente Local Principal

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** Precisvamos de um modelo local para execuo de tarefas braais 24/7 sem custo de API.

**Deciso:** Qwen2.5-Coder 1.5B via Ollama para o agente Courier.

**Alternativas consideradas:**
- TinyLlama 1.1B: menor, mas qualidade de cdigo inferior.
- Phi-3 Mini: bom raciocnio, mas menos otimizado para cdigo.
- CodeGemma 2B: bom mas maior consumo de VRAM.

**Justificativa:** Qwen2.5-Coder tem o melhor benchmark de cdigo na faixa de 1-2B parmetros, roda em 4GB RAM/VRAM, custo zero de API.

---

## ADR-007  msgspec ao invs de Pydantic para Validao

**Data:** 2026-04  
**Status:**  Implementado

**Contexto:** Precisvamos de serializao/validao de schemas JSON de alta performance.

**Deciso:** `msgspec` para serializao e validao de schemas internos.

**Alternativas consideradas:**
- Pydantic v2: excelente mas overhead maior em validao de alta frequncia.
- json (stdlib): sem validao de schema.
- orjson: rpido para serializao mas sem validao.

**Justificativa:** msgspec  10-50x mais rpido que Pydantic para serializao pura, com zero dependncias extras.

---

## ADR-008  Arquitetura de Lobos como Memria de Longo Prazo

**Data:** 2026-04  
**Status:**  Design implementado, FTS5 indexado

**Contexto:** Como persistir contexto entre sesses sem enviar contexto completo a cada requisio?

**Deciso:** Lobos MDC como unidades atmicas de memria, indexados via FTS5, buscveis via `neocortex_lobes.search`.

**Justificativa:** Permite que o T0 recupere knowledge especfico sem tokens desnecessrios, reduzindo custo de API em estimados 60-80% para tarefas recorrentes.
