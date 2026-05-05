"""---
domain: "infrastructure"
layer: "infra"
type: "example"
tags: ["vector", "example", "lancedb", "async"]
hash: "auto-generated"
---"""

#!/usr/bin/env python3
"""
Example usage of LanceDBVectorEngine with NeoCortex configuration.

This example demonstrates:
1. Creating a vector engine using framework configuration
2. Adding vectors with metadata
3. Performing similarity searches
4. Using the RAG engine for document chunking
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neocortex.NC-CORE-FR-001-config import get_config
from neocortex.infra.vector_engine import (
    LanceDBVectorEngine,
    RAGVectorEngine,
    create_vector_engine,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_operations():
    """Demonstrate basic vector engine operations."""
    print("=== Basic Vector Engine Operations ===\n")

    # Get framework configuration
    config = get_config()

    # Create engine using framework configuration
    engine = LanceDBVectorEngine(
        db_path=config.vector_db_path,
        table_name=f"{config.vector_store_collection_prefix}test_vectors",
        embedding_dim=config.vector_store_embedding_dimension,
        distance_metric=config.vector_store_metric,
    )

    try:
        # Initialize engine (creates database and table)
        await engine.initialize()
        print(f" Engine initialized at: {config.vector_db_path}")

        # Generate some test vectors (random embeddings)
        import numpy as np

        np.random.seed(42)

        vectors = [
            np.random.randn(config.vector_store_embedding_dimension).tolist()
            for _ in range(5)
        ]
        metadata = [
            {"type": "document", "title": f"Document {i}", "category": "test"}
            for i in range(5)
        ]

        # Add vectors
        vector_ids = await engine.add_vectors(
            vectors, metadata, embedding_model="test_model"
        )
        print(f" Added {len(vector_ids)} vectors with IDs: {vector_ids[:3]}...")

        # Search for similar vectors
        query_vector = vectors[0]  # Use first vector as query
        results = await engine.search(query_vector, top_k=3)
        print(f" Search returned {len(results)} results:")
        for i, result in enumerate(results):
            print(
                f"  {i + 1}. ID: {result.id}, Score: {result.score:.4f}, Title: {result.metadata.get('title')}"
            )

        # Get vector by ID
        if vector_ids:
            vector_record = await engine.get_by_id(vector_ids[0])
            if vector_record:
                print(f" Retrieved vector {vector_ids[0]}: {vector_record.metadata}")

        # Get engine statistics
        stats = await engine.get_stats()
        print(
            f" Engine stats: {stats['vector_count']} vectors, {stats['embedding_dim']} dimensions"
        )

        # Clean up (optional)
        await engine.clear()
        print(" Cleared test vectors")

    finally:
        await engine.close()
        print(" Engine closed")


async def example_rag_workflow():
    """Demonstrate RAG-specific vector operations."""
    print("\n=== RAG Workflow Example ===\n")

    config = get_config()

    # Create RAG-optimized engine
    rag_engine = RAGVectorEngine(
        db_path=config.vector_db_path,
        table_name=f"{config.vector_store_collection_prefix}documents",
        embedding_dim=config.vector_store_embedding_dimension,
        distance_metric=config.vector_store_metric,
        chunk_size=500,
        chunk_overlap=100,
    )

    try:
        await rag_engine.initialize()
        print(" RAG engine initialized")

        # Mock embedding function (in real usage, use OpenAI, Ollama, etc.)
        async def mock_embed_fn(text: str):
            """Mock embedding function for demonstration."""
            import numpy as np

            # Generate deterministic random vector based on text hash
            hash_val = hash(text) % 10000
            np.random.seed(hash_val)
            return np.random.randn(config.vector_store_embedding_dimension).tolist()

        # Sample documents
        documents = [
            {
                "text": "The NeoCortex framework provides structured AI-assisted development with MCP integration.",
                "source": "framework_docs",
                "author": "NeoCortex Team",
            },
            {
                "text": "Vector databases enable efficient similarity search and retrieval-augmented generation.",
                "source": "tech_article",
                "author": "AI Research",
            },
            {
                "text": "LanceDB is an open-source vector database designed for machine learning workloads.",
                "source": "database_docs",
                "author": "LanceDB Team",
            },
        ]

        # Add documents with automatic chunking and embedding
        chunk_ids = await rag_engine.add_documents(
            documents=documents,
            embed_fn=mock_embed_fn,
            metadata_fields=["source", "author"],
        )
        print(f" Added {len(chunk_ids)} document chunks")

        # Search for relevant chunks
        query = "What is NeoCortex framework?"
        chunks = await rag_engine.retrieve_relevant_chunks(
            query=query,
            embed_fn=mock_embed_fn,
            top_k=2,
        )

        print(f" Retrieved {len(chunks)} relevant chunks for query: '{query}'")
        for i, chunk in enumerate(chunks):
            print(f"  {i + 1}. Score: {chunk['score']:.4f}")
            print(f"     Text: {chunk['text']}")
            print(f"     Source: {chunk['metadata'].get('source')}")

        # Clean up
        await rag_engine.clear()
        print(" Cleared RAG documents")

    finally:
        await rag_engine.close()
        print(" RAG engine closed")


async def example_factory_pattern():
    """Demonstrate using the factory function to create engines."""
    print("\n=== Factory Pattern Example ===\n")

    config = get_config()

    # Create standard vector engine using factory
    standard_engine = create_vector_engine(
        engine_type="lancedb",
        db_path=config.vector_db_path,
        table_name=f"{config.vector_store_collection_prefix}factory_test",
        embedding_dim=config.vector_store_embedding_dimension,
        distance_metric=config.vector_store_metric,
    )

    # Create RAG engine using factory
    rag_engine = create_vector_engine(
        engine_type="rag",
        db_path=config.vector_db_path,
        table_name=f"{config.vector_store_collection_prefix}factory_rag",
        embedding_dim=config.vector_store_embedding_dimension,
        distance_metric=config.vector_store_metric,
        chunk_size=1000,
        chunk_overlap=200,
    )

    print(f" Created standard engine: {type(standard_engine).__name__}")
    print(f" Created RAG engine: {type(rag_engine).__name__}")

    # Cleanup
    await standard_engine.close()
    await rag_engine.close()
    print(" Engines closed")


async def main():
    """Run all examples."""
    print("NeoCortex Vector Engine Examples")
    print("=" * 50)

    try:
        await example_basic_operations()
        await example_rag_workflow()
        await example_factory_pattern()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
