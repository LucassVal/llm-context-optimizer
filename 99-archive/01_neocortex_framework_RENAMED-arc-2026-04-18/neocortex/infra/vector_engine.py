"""---
domain: "infrastructure"
layer: "infra"
type: "engine"
tags: ["vector", "database", "lancedb", "rag", "async", "007"]
hash: "auto-generated"
---"""

#!/usr/bin/env python3
"""
Vector Engine - Real LanceDB-based vector database engine with async CRUD operations.

Provides high-performance vector storage, similarity search, and RAG preparation
with LanceDB backend. Designed for async/await patterns and configurability via kwargs.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class VectorEngineError(Exception):
    """Base exception for vector engine errors."""

    pass


class EmbeddingProvider(str, Enum):
    """Supported embedding providers for vector generation."""

    OPENAI = "openai"
    OLLAMA = "ollama"
    SELF_HOSTED = "self_hosted"
    CUSTOM = "custom"


@dataclass
class VectorRecord:
    """Represents a vector record with metadata."""

    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    embedding_model: Optional[str] = None
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())


@dataclass
class SearchResult:
    """Represents a similarity search result."""

    id: str
    score: float
    vector: List[float]
    metadata: Dict[str, Any]
    embedding_model: Optional[str] = None


class LanceDBVectorEngine:
    """
    Async vector engine using LanceDB for storage and similarity search.

    Features:
    - Async CRUD operations (create, read, update, delete)
    - Batch vector insertion with metadata
    - Approximate nearest neighbor search (ANN)
    - RAG-ready document indexing
    - Configurable embedding dimensions and distance metrics
    - Automatic table creation and schema management
    """

    def __init__(
        self,
        db_path: Union[str, Path] = "lancedb_data",
        table_name: str = "vectors",
        embedding_dim: int = 1536,  # OpenAI ada-002 default
        distance_metric: str = "cosine",
        **kwargs,
    ):
        """
        Initialize LanceDB vector engine.

        Args:
            db_path: Path to LanceDB database directory
            table_name: Name of the table/collection
            embedding_dim: Dimensionality of vectors
            distance_metric: Distance metric for similarity ('cosine', 'l2', 'ip')
            **kwargs: Additional LanceDB connection options
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.embedding_dim = embedding_dim
        self.distance_metric = distance_metric
        self._connection = None
        self._table = None
        self._initialized = False
        self._kwargs = kwargs

        logger.info(
            f"LanceDBVectorEngine initialized (db_path={db_path}, "
            f"table={table_name}, dim={embedding_dim}, metric={distance_metric})"
        )

    async def initialize(self) -> None:
        """Initialize connection and create table if not exists."""
        if self._initialized:
            return

        try:
            # Import lancedb inside method to allow optional dependency
            import lancedb

            # Create database directory if not exists
            self.db_path.mkdir(parents=True, exist_ok=True)

            # Connect to LanceDB
            self._connection = lancedb.connect(self.db_path)

            # Define schema for vector table using LanceDB schema format
            import pyarrow as pa

            schema = pa.schema(
                [
                    pa.field("id", pa.string()),
                    pa.field("vector", lancedb.vector(self.embedding_dim)),
                    pa.field("metadata", pa.string()),  # JSON stored as string
                    pa.field("embedding_model", pa.string()),
                    pa.field("created_at", pa.float64()),
                ]
            )

            # Create or open table
            if self.table_name in self._connection.table_names():
                self._table = self._connection.open_table(self.table_name)
                logger.debug(f"Opened existing table: {self.table_name}")
            else:
                self._table = self._connection.create_table(
                    name=self.table_name,
                    schema=schema,
                    mode="create",
                )
                logger.info(f"Created new table: {self.table_name}")

            # Create vector index if not exists
            if not self._table.list_indices():
                try:
                    await asyncio.to_thread(
                        self._table.create_index,
                        vector_column_name="vector",
                        metric=self.distance_metric,
                        num_partitions=256,
                        num_sub_vectors=16,
                    )
                    logger.debug(
                        f"Created vector index with metric: {self.distance_metric}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Ignorando erro de indexao (a tabela pode ser pequena demais para IVF_PQ): {e}"
                    )

            self._initialized = True
            logger.info("LanceDBVectorEngine fully initialized")

        except ImportError as e:
            logger.error("Lancedb not installed. Install with: pip install lancedb")
            raise VectorEngineError(
                "LanceDB dependency missing. Install with 'pip install lancedb' "
                "or use the 'vectors' extra: pip install neocortex-framework[vectors]"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize LanceDBVectorEngine: {e}")
            raise VectorEngineError(f"Initialization failed: {e}") from e

    async def _ensure_table(self) -> None:
        """Ensure table exists and is ready for operations."""
        if self._table is not None:
            return

        # If not initialized, try to initialize
        if not self._initialized:
            await self.initialize()
            return

        # If initialized but table is still None, something went wrong
        # Try to reconnect and create table
        try:
            import lancedb
            import pyarrow as pa

            # Create database directory if not exists
            self.db_path.mkdir(parents=True, exist_ok=True)

            # Connect to LanceDB
            self._connection = lancedb.connect(self.db_path)

            # Define schema for vector table using LanceDB schema format
            schema = pa.schema(
                [
                    pa.field("id", pa.string()),
                    pa.field("vector", lancedb.vector(self.embedding_dim)),
                    pa.field("metadata", pa.string()),  # JSON stored as string
                    pa.field("embedding_model", pa.string()),
                    pa.field("created_at", pa.float64()),
                ]
            )

            # Try to open existing table
            if self.table_name in self._connection.table_names():
                self._table = self._connection.open_table(self.table_name)
                logger.debug(f"Reopened table: {self.table_name}")
            else:
                # Create new table
                self._table = self._connection.create_table(
                    name=self.table_name,
                    schema=schema,
                    mode="create",
                )
                logger.info(f"Created new table: {self.table_name}")

            logger.debug("Table ensured successfully")

        except Exception as e:
            logger.error(f"Failed to ensure table existence: {e}")
            raise VectorEngineError(f"Table initialization failed: {e}") from e

    async def add_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        embedding_model: Optional[str] = None,
    ) -> List[str]:
        """
        Add vectors with metadata to the store.

        Args:
            vectors: List of vector embeddings
            metadata: List of metadata dictionaries
            embedding_model: Optional embedding model identifier

        Returns:
            List of generated vector IDs
        """
        await self._ensure_table()
        if self._table is None:
            raise VectorEngineError("Table not available after initialization")
        assert self._table is not None  # Type guard for LSP

        if len(vectors) != len(metadata):
            raise VectorEngineError("Vectors and metadata must have same length")

        # Generate unique IDs
        import json
        import uuid

        vector_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

        # Prepare records for insertion
        records = []
        for vec_id, vector, meta in zip(vector_ids, vectors, metadata):
            records.append(
                {
                    "id": vec_id,
                    "vector": vector,
                    "metadata": json.dumps(meta),
                    "embedding_model": embedding_model or "unknown",
                    "created_at": asyncio.get_event_loop().time(),
                }
            )

        # Insert records asynchronously
        try:
            await asyncio.to_thread(self._table.add, records)
            logger.debug(f"Added {len(vectors)} vectors to table {self.table_name}")
            return vector_ids
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            raise VectorEngineError(f"Vector addition failed: {e}") from e

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[SearchResult]:
        """
        Search for similar vectors using approximate nearest neighbor search.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter (e.g., {"category": "document"})
            **kwargs: Additional search parameters

        Returns:
            List of SearchResult objects ordered by similarity
        """
        await self._ensure_table()
        if self._table is None:
            raise VectorEngineError("Table not available after initialization")
        assert self._table is not None  # Type guard for LSP

        try:
            # Build search query
            query = self._table.search(query_vector).limit(top_k)

            # Apply metadata filter if provided
            if filter:
                # Since metadata is stored as JSON string, use json_extract with CAST to BLOB
                filter_parts = []
                for k, v in filter.items():
                    # Escape single quotes in value
                    safe_v = str(v).replace("'", "''")
                    # CAST metadata to BLOB for json_extract function
                    filter_parts.append(
                        f"json_extract(CAST(metadata AS BLOB), '$.{k}') = '{safe_v}'"
                    )
                filter_expr = " AND ".join(filter_parts)
                query = query.where(filter_expr)

            # Execute search asynchronously
            results = await asyncio.to_thread(query.to_list)

            # Convert to SearchResult objects
            search_results = []
            for result in results:
                # Deserialize metadata from JSON string
                metadata_str = result["metadata"]
                try:
                    metadata_dict = json.loads(metadata_str) if metadata_str else {}
                except json.JSONDecodeError:
                    logger.warning(
                        f"Failed to decode metadata JSON: {metadata_str[:100]}"
                    )
                    metadata_dict = {}
                search_results.append(
                    SearchResult(
                        id=result["id"],
                        score=result["_distance"],
                        vector=result["vector"],
                        metadata=metadata_dict,
                        embedding_model=result.get("embedding_model"),
                    )
                )

            logger.debug(f"Search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorEngineError(f"Search failed: {e}") from e

    async def get_by_id(self, vector_id: str) -> Optional[VectorRecord]:
        """
        Retrieve a vector record by ID.

        Args:
            vector_id: Vector identifier

        Returns:
            VectorRecord if found, None otherwise
        """
        await self.initialize()

        try:
            result = await asyncio.to_thread(
                self._table.search([0.0] * self.embedding_dim)
                .where(f"id = '{vector_id}'")
                .limit(1)
                .to_list
            )

            if not result:
                return None

            data = result[0]
            # Deserialize metadata from JSON string
            metadata_str = data["metadata"]
            try:
                metadata_dict = json.loads(metadata_str) if metadata_str else {}
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode metadata JSON: {metadata_str[:100]}")
                metadata_dict = {}
            return VectorRecord(
                id=data["id"],
                vector=data["vector"],
                metadata=metadata_dict,
                embedding_model=data.get("embedding_model"),
                created_at=data.get("created_at", 0.0),
            )
        except Exception as e:
            logger.error(f"Failed to get vector {vector_id}: {e}")
            raise VectorEngineError(f"Get by ID failed: {e}") from e

    async def update_metadata(
        self,
        vector_id: str,
        metadata: Dict[str, Any],
        merge: bool = True,
    ) -> bool:
        """
        Update metadata for an existing vector.

        Args:
            vector_id: Vector identifier
            metadata: New metadata dictionary
            merge: If True, merge with existing metadata; otherwise replace

        Returns:
            True if successful
        """
        await self.initialize()

        try:
            # Get existing record
            record = await self.get_by_id(vector_id)
            if not record:
                return False

            # Merge or replace metadata
            if merge:
                new_metadata = {**record.metadata, **metadata}
            else:
                new_metadata = metadata

            # Update using LanceDB's update operation
            await asyncio.to_thread(
                self._table.update,
                where=f"id = '{vector_id}'",
                values={"metadata": json.dumps(new_metadata)},
            )

            logger.debug(f"Updated metadata for vector {vector_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update metadata for {vector_id}: {e}")
            raise VectorEngineError(f"Metadata update failed: {e}") from e

    async def delete(self, vector_ids: List[str]) -> int:
        """
        Delete vectors by IDs.

        Args:
            vector_ids: List of vector identifiers

        Returns:
            Number of vectors deleted
        """
        await self.initialize()

        if not vector_ids:
            return 0

        try:
            # Build delete condition
            ids_str = ", ".join([f"'{vid}'" for vid in vector_ids])
            condition = f"id IN ({ids_str})"

            # Execute delete and get deleted rows count
            delete_result = await asyncio.to_thread(
                self._table.delete,
                where=condition,
            )
            deleted_count = delete_result.deleted_rows

            logger.debug(f"Deleted {deleted_count} vectors")
            return deleted_count

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise VectorEngineError(f"Delete failed: {e}") from e

    async def clear(self) -> bool:
        """Clear all vectors from the table."""
        await self.initialize()

        try:
            delete_result = await asyncio.to_thread(self._table.delete, "1 = 1")
            logger.info(
                f"Cleared all vectors from table {self.table_name}, deleted rows: {delete_result.deleted_rows}"
            )
            return True
        except Exception as e:
            logger.error(f"Clear failed: {e}")
            raise VectorEngineError(f"Clear failed: {e}") from e

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Dictionary with statistics
        """
        await self.initialize()

        try:
            count = await asyncio.to_thread(self._table.count_rows)
            indices = await asyncio.to_thread(self._table.list_indices)

            return {
                "table_name": self.table_name,
                "vector_count": count,
                "embedding_dim": self.embedding_dim,
                "distance_metric": self.distance_metric,
                "indices": indices,
                "initialized": self._initialized,
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise VectorEngineError(f"Stats retrieval failed: {e}") from e

    async def close(self) -> None:
        """Close engine and release resources."""
        if self._connection:
            # LanceDB connection doesn't need explicit close, but we can clean up
            self._connection = None
            self._table = None
            self._initialized = False
            logger.debug("LanceDBVectorEngine closed")


# RAG-specific extensions
class RAGVectorEngine(LanceDBVectorEngine):
    """
    Extended vector engine optimized for RAG workflows.

    Adds document chunking, text embedding, and retrieval-augmented generation
    preparation methods.
    """

    def __init__(
        self,
        db_path: Union[str, Path] = "lancedb_data",
        table_name: str = "documents",
        embedding_dim: int = 1536,
        distance_metric: str = "cosine",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs,
    ):
        """
        Initialize RAG-optimized vector engine.

        Args:
            chunk_size: Character count per document chunk
            chunk_overlap: Overlap between chunks
            **kwargs: Passed to parent LanceDBVectorEngine
        """
        super().__init__(
            db_path=db_path,
            table_name=table_name,
            embedding_dim=embedding_dim,
            distance_metric=distance_metric,
            **kwargs,
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embed_fn: callable,
        metadata_fields: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents with automatic chunking and embedding.

        Args:
            documents: List of documents with 'text' and optional metadata
            embed_fn: Async function that takes text and returns embedding vector
            metadata_fields: List of metadata fields to preserve in chunks

        Returns:
            List of vector IDs for all chunks
        """

        all_chunk_ids = []

        for doc in documents:
            # Extract text and metadata
            text = doc.get("text", "")
            if not text:
                logger.warning("Document missing 'text' field, skipping")
                continue

            metadata = {k: v for k, v in doc.items() if k != "text"}
            if metadata_fields:
                metadata = {k: v for k, v in metadata.items() if k in metadata_fields}

            # Chunk text
            chunks = self._chunk_text(text)

            # Generate embeddings for each chunk
            vectors = []
            chunk_metadatas = []

            for i, chunk in enumerate(chunks):
                # Create chunk-specific metadata
                chunk_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "chunk_total": len(chunks),
                    "chunk_text_preview": chunk[:100] + "..."
                    if len(chunk) > 100
                    else chunk,
                }
                chunk_metadatas.append(chunk_metadata)

            # Generate embedding in one batch
            try:
                vectors = await embed_fn(chunks)
            except Exception as e:
                logger.error(f"Failed to batch embed chunks: {e}")
                continue

            # Add vectors to store
            if vectors:
                chunk_ids = await self.add_vectors(
                    vectors=vectors,
                    metadata=chunk_metadatas,
                    embedding_model=getattr(embed_fn, "__name__", "custom"),
                )
                all_chunk_ids.extend(chunk_ids)
                logger.debug(f"Added {len(vectors)} chunks for document")

        logger.info(
            f"Added {len(all_chunk_ids)} total chunks from {len(documents)} documents"
        )
        return all_chunk_ids

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.chunk_overlap

        return chunks

    async def retrieve_relevant_chunks(
        self,
        query: str,
        embed_fn: callable,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: Search query text
            embed_fn: Async function to embed query text
            top_k: Number of chunks to retrieve
            filter: Optional metadata filter

        Returns:
            List of relevant chunks with metadata and scores
        """
        # Embed query
        query_vector = await embed_fn(query)

        # Search for similar vectors
        results = await self.search(
            query_vector=query_vector,
            top_k=top_k,
            filter=filter,
        )

        # Format results
        chunks = []
        for result in results:
            chunks.append(
                {
                    "id": result.id,
                    "score": result.score,
                    "text": result.metadata.get("chunk_text_preview", ""),
                    "metadata": result.metadata,
                    "embedding_model": result.embedding_model,
                }
            )

        return chunks


# Factory function for creating vector engines
def create_vector_engine(
    engine_type: str = "lancedb",
    **kwargs,
) -> Union[LanceDBVectorEngine, RAGVectorEngine]:
    """
    Create vector engine instance.

    Args:
        engine_type: "lancedb" or "rag"
        **kwargs: Engine-specific arguments

    Returns:
        Vector engine instance
    """
    if engine_type == "rag":
        return RAGVectorEngine(**kwargs)
    else:
        return LanceDBVectorEngine(**kwargs)


# Async context manager support
class VectorEngineContext:
    """Context manager for vector engine."""

    def __init__(self, engine: LanceDBVectorEngine):
        self.engine = engine

    async def __aenter__(self):
        await self.engine.initialize()
        return self.engine

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.engine.close()


# Quick test function
async def test_vector_engine():
    """Test vector engine functionality."""
    import numpy as np

    # Create engine with test configuration
    engine = LanceDBVectorEngine(
        db_path="test_lancedb",
        table_name="test_vectors",
        embedding_dim=128,  # Smaller for testing
    )

    try:
        await engine.initialize()

        # Generate test vectors
        vectors = [np.random.randn(128).tolist() for _ in range(10)]
        metadata = [{"test": f"data_{i}", "index": i} for i in range(10)]

        # Add vectors
        ids = await engine.add_vectors(vectors, metadata)
        print(f" Added {len(ids)} vectors")

        # Search
        query = vectors[0]
        results = await engine.search(query, top_k=3)
        print(f" Search returned {len(results)} results")

        # Get stats
        stats = await engine.get_stats()
        print(f" Stats: {stats['vector_count']} vectors")

        # Cleanup
        await engine.clear()
        print(" Test completed successfully")

    finally:
        await engine.close()
        # Clean up test directory
        import shutil

        test_path = Path("test_lancedb")
        if test_path.exists():
            shutil.rmtree(test_path)


if __name__ == "__main__":
    # Run test if module executed directly
    asyncio.run(test_vector_engine())
