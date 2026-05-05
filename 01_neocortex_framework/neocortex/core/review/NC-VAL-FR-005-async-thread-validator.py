"""---
@Module  mcp _genealogy:   injected_at: '2026-04-16T00:23:58.39
---
"""



"""---
domain: "core"
layer: "core"
type: "file"
tags: ["val", "005", "async", "validator"]
hash: "auto-generated"
---
NC-VAL-FR-005-async-thread-validator.py
FR-VAL-005  AsyncThreadValidator: Envelopamento Async da Anti-Corruption Layer para VectorDB.

Protege a thread principal de modelos vetoriais que afogam a thread, criando workers persistentes isolados.
"""

import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List, Optional

from . import ValidationResult

logger = logging.getLogger(__name__)


class AsyncVectorStore:
    """
    Wrapper assncrono para VectorStore que executa operaes pesadas em workers isolados.

    Interface pblica (async):
      - async_add_vectors(vectors, metadata) -> List[str]
      - async_search(query_vector, top_k) -> List[Dict]
      - async_delete(vector_ids) -> bool
      - async_get_stats() -> Dict
      - async_clear() -> bool
      - close() -> None

    Uso:
        store = AsyncVectorStore(store_type="infinity", max_workers=2)
        await store.async_add_vectors(...)
    """

    def __init__(
        self,
        store_type: str = "infinity",
        max_workers: int = 1,
        **kwargs,
    ):
        """
        Inicializa AsyncVectorStore.

        Args:
            store_type: "infinity" ou "lancedb"
            max_workers: Nmero mximo de workers do ProcessPoolExecutor
            **kwargs: Argumentos passados para o VectorStore subjacente
        """
        self.store_type = store_type
        self.store_kwargs = kwargs
        self.max_workers = max_workers
        self._executor: Optional[ProcessPoolExecutor] = None
        self._vector_store = None

        # Inicializar executor e carregar store em processo separado
        self._init_executor()

    def _init_executor(self):
        """Inicializa ProcessPoolExecutor."""
        if self._executor is None:
            self._executor = ProcessPoolExecutor(
                max_workers=self.max_workers,
                initializer=self._worker_initializer,
                initargs=(self.store_type, self.store_kwargs),
            )
            logger.info(
                f"AsyncVectorStore iniciado com {self.max_workers} workers (tipo: {self.store_type})"
            )

    @staticmethod
    def _worker_initializer(store_type: str, kwargs: Dict[str, Any]):
        """Inicializa o VectorStore no processo worker."""
        # Importar dentro do worker para evitar pickling de mdulos
        # Atribuir ao namespace global do worker
        import threading

        from neocortex.infra.vector_store import create_vector_store

        threading.current_thread().worker_store = create_vector_store(
            store_type, **kwargs
        )

    @staticmethod
    def _get_worker_store():
        """Retorna a store do worker atual."""
        import threading

        return getattr(threading.current_thread(), "worker_store", None)

    async def async_add_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
    ) -> List[str]:
        """Adiciona vetores com metadata (assncrono)."""
        loop = asyncio.get_event_loop()
        try:
            # Executa em worker separado
            result = await loop.run_in_executor(
                self._executor,
                self._sync_add_vectors,
                vectors,
                metadata,
            )
            return result
        except Exception as e:
            logger.error(f"Erro em async_add_vectors: {e}")
            raise

    def _sync_add_vectors(self, vectors, metadata):
        """Funo sncrona executada no worker."""
        store = self._get_worker_store()
        if store is None:
            raise RuntimeError("VectorStore no inicializado no worker")
        return store.add_vectors(vectors, metadata)

    async def async_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Busca vetores similares (assncrono)."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                self._sync_search,
                query_vector,
                top_k,
            )
            return result
        except Exception as e:
            logger.error(f"Erro em async_search: {e}")
            raise

    def _sync_search(self, query_vector, top_k):
        store = self._get_worker_store()
        if store is None:
            raise RuntimeError("VectorStore no inicializado no worker")
        return store.search(query_vector, top_k)

    async def async_delete(self, vector_ids: List[str]) -> bool:
        """Deleta vetores por IDs (assncrono)."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                self._sync_delete,
                vector_ids,
            )
            return result
        except Exception as e:
            logger.error(f"Erro em async_delete: {e}")
            raise

    def _sync_delete(self, vector_ids):
        store = self._get_worker_store()
        if store is None:
            raise RuntimeError("VectorStore no inicializado no worker")
        return store.delete(vector_ids)

    async def async_get_stats(self) -> Dict[str, Any]:
        """Obtm estatsticas da store (assncrono)."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                self._sync_get_stats,
            )
            return result
        except Exception as e:
            logger.error(f"Erro em async_get_stats: {e}")
            raise

    def _sync_get_stats(self):
        store = self._get_worker_store()
        if store is None:
            raise RuntimeError("VectorStore no inicializado no worker")
        return store.get_stats()

    async def async_clear(self) -> bool:
        """Limpa todos os vetores (assncrono)."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                self._sync_clear,
            )
            return result
        except Exception as e:
            logger.error(f"Erro em async_clear: {e}")
            raise

    def _sync_clear(self):
        store = self._get_worker_store()
        if store is None:
            raise RuntimeError("VectorStore no inicializado no worker")
        return store.clear()

    def close(self):
        """Libera recursos do executor."""
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("AsyncVectorStore fechado")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncThreadValidator:
    """
    Validador que verifica se operaes de VectorDB esto sendo realizadas de forma assncrona.

    Score 100 se todas as operaes de VectorDB estiverem usando AsyncVectorStore.
    Penaliza operaes sncronas que podem afogar a thread.
    """

    def __init__(self, max_sync_operations: int = 0):
        """
        Args:
            max_sync_operations: Nmero mximo permitido de operaes sncronas
        """
        self.max_sync_operations = max_sync_operations

    def validate(self, data: Dict) -> ValidationResult:
        """
        Valida se o handoff contm indicaes de uso de async para VectorDB.

        Procura por:
          - Uso de AsyncVectorStore
          - Nmero de operaes sncronas de embedding
          - Tempos de resposta longos que indicam bloqueio
        """
        # Por enquanto, este validador  um stub que sempre aprova.
        # Futuramente, integrar com mtricas reais de thread blocking.
        score = 100
        passed = True
        message = "Validao async de VectorDB passou (stub)"

        # Simulao: se houver muitas operaes sncronas, penalizar
        sync_ops = data.get("sync_vector_ops", 0)
        if sync_ops > self.max_sync_operations:
            penalty = min(20 * (sync_ops - self.max_sync_operations), 80)
            score = max(20, 100 - penalty)
            passed = score >= 80
            message = f"Encontradas {sync_ops} operaes sncronas de VectorDB (limite: {self.max_sync_operations})"

        return ValidationResult(
            validator_name="async_vector_db",
            passed=passed,
            score=score,
            message=message,
            details={
                "sync_vector_ops": sync_ops,
                "max_allowed": self.max_sync_operations,
                "async_recommended": True,
            },
        )


# Funo de fbrica para validador (compatibilidade com ConfidenceReviewService)
def create_async_vector_validator(max_sync_operations: int = 0):
    """Cria instncia do validador async."""
    return AsyncThreadValidator(max_sync_operations).validate


# Exemplo de uso do AsyncVectorStore
async def example_usage():
    """Exemplo de uso do AsyncVectorStore."""
    async with AsyncVectorStore(store_type="infinity", max_workers=2) as store:
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadata = [{"text": "hello"}, {"text": "world"}]
        ids = await store.async_add_vectors(vectors, metadata)
        print(f"Vetores adicionados: {ids}")

        results = await store.async_search([0.1, 0.2, 0.3], top_k=1)
        print(f"Resultados da busca: {results}")


if __name__ == "__main__":
    # Teste bsico (sncrono)
    import asyncio

    asyncio.run(example_usage())
    print(" AsyncVectorStore testado com sucesso")
