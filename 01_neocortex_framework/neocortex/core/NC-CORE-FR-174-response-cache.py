"""---
@Module NC-CORE-FR-174-response-cache mcp NC-CORE-FR-174-response-cache.py
---
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ResponseCache:
    """Semantic response cache with embedding similarity via LanceDB.

    KISS: <300 lines. Uses existing infra (LanceDB + sentence-transformers).
    RCA: Hash-exact cache can't reuse semantically similar prompts. Embedding
    similarity >threshold (default 0.92) returns cached response without
    hitting the API. 15-25% reuse eliminates that % of API cost.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.92,
        ttl_seconds: int | None = 86400,
        max_entries: int = 10000,
        table_name: str = "response_cache",
    ):
        self._threshold = similarity_threshold
        self._ttl = ttl_seconds
        self._max = max_entries
        self._table_name = table_name
        self._model = None
        self._model_name = model_name
        self._db = None
        self._table = None
        self._dims = None
        self._stats = {"hits": 0, "misses": 0, "stores": 0}

        if db_path is None:
            db_path = (
                Path(__file__).parent.parent.parent
                / ".neocortex"
                / "data"
                / "lancedb_cache"
            )
        self._db_path = Path(db_path)
        self._db_path.mkdir(parents=True, exist_ok=True)
        self._init_storage()

    def _get_model(self):
        if self._model is None:
            import sentence_transformers as _st
            self._model = _st.SentenceTransformer(self._model_name)
            self._dims = self._model.get_sentence_embedding_dimension()
        return self._model

    def _encode(self, text: str) -> list[float]:
        return self._get_model().encode([text])[0].tolist()

    def _init_storage(self):
        try:
            import lancedb
            self._db = lancedb.connect(str(self._db_path))
            available = self._db.table_names()
            if self._table_name in available:
                self._table = self._db.open_table(self._table_name)
            else:
                self._table = None
        except Exception as e:
            logger.warning(f"ResponseCache: LanceDB init failed — {e}")

    def _ensure_table(self, dims: int):
        if self._table is not None:
            return
        if self._db is None:
            return
        import pyarrow as pa
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("prompt_hash", pa.string()),
            pa.field("prompt", pa.string()),
            pa.field("response_json", pa.string()),
            pa.field("tool_name", pa.string()),
            pa.field("created_at", pa.float64()),
            pa.field("vector", pa.list_(pa.float32(), dims)),
        ])
        self._table = self._db.create_table(self._table_name, schema=schema, mode="overwrite")

    def _prune_expired(self):
        if self._table is None or self._ttl is None:
            return
        try:
            cutoff = time.time() - self._ttl
            self._table.delete(f"created_at < {cutoff}")
        except Exception:
            pass

    def query(
        self, prompt: str, tool_name: str = "default"
    ) -> dict[str, Any] | None:
        """Query cache for semantically similar prompt.

        Returns cached response dict if similarity > threshold, None otherwise.
        """
        if self._table is None or self._db is None:
            self._stats["misses"] += 1
            return None

        try:
            self._prune_expired()
            vector = self._encode(prompt)
            self._ensure_table(len(vector))

            results = (
                self._table.search(vector)
                .limit(1)
                .select(["prompt", "response_json", "tool_name", "created_at", "id"])
                .to_list()
            )

            if not results:
                self._stats["misses"] += 1
                return None

            top = results[0]
            cached_prompt = top.get("prompt", "")
            sim = self._cosine_similarity(vector, self._encode(cached_prompt))

            if sim >= self._threshold:
                self._stats["hits"] += 1
                cached_response = json.loads(top.get("response_json", "{}"))
                cached_response["_cache_hit"] = True
                cached_response["_cache_similarity"] = round(sim, 4)
                cached_response["_cache_matched_prompt"] = cached_prompt[:100]
                return cached_response

            self._stats["misses"] += 1
            return None
        except Exception as e:
            logger.debug(f"ResponseCache query error: {e}")
            self._stats["misses"] += 1
            return None

    def store(
        self,
        prompt: str,
        response: dict[str, Any],
        tool_name: str = "default",
        ttl_seconds: int | None = None,
    ):
        """Store a prompt-response pair in the cache."""
        if self._table is None and self._db is not None:
            dims = self._get_model().get_sentence_embedding_dimension()
            self._ensure_table(dims)

        if self._table is None:
            return

        try:
            vector = self._encode(prompt)
            self._stats["stores"] += 1
            now = time.time()
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
            row = [{
                "id": f"{tool_name}:{prompt_hash}:{int(now)}",
                "prompt_hash": prompt_hash,
                "prompt": prompt,
                "response_json": json.dumps(response, ensure_ascii=False),
                "tool_name": tool_name,
                "created_at": now,
                "vector": vector,
            }]
            self._table.add(row)
        except Exception as e:
            logger.warning(f"ResponseCache store error: {e}")

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def stats(self) -> dict:
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "stores": self._stats["stores"],
            "hit_rate": round(hit_rate, 4),
            "table": self._table_name,
            "threshold": self._threshold,
            "entries": self._table.count_rows() if self._table else 0,
        }

    def flush(self):
        if self._table is not None:
            self._table.delete("id IS NOT NULL")


_cache_instance: ResponseCache | None = None


def get_response_cache() -> ResponseCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ResponseCache()
    return _cache_instance
