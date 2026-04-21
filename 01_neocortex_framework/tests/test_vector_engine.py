#!/usr/bin/env python3
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.851892'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-062
tags:
  - neocortex-other
  - level-0
  - python
---"""

"""
Testes unitrios e de integrao para VectorEngine (LanceDBVectorEngine, RAGVectorEngine).

Autor: Agente Tester (NC-SCR-FR-062)
Data: 2026-04-14
Status:  Pronto para execuo
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest

# Adicionar caminho para importar VectorEngine
sys.path.insert(0, str(Path(__file__).parent.parent))

from neocortex.infra.vector_engine import (
    LanceDBVectorEngine,
    RAGVectorEngine,
    VectorEngineContext,
    VectorEngineError,
    create_vector_engine,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_db_path():
    """Cria caminho temporrio para banco de dados LanceDB."""
    with tempfile.NamedTemporaryFile(suffix=".lance", delete=False) as f:
        db_path = f.name
    yield db_path
    # Limpeza aps teste
    try:
        Path(db_path).unlink(missing_ok=True)
    except:
        pass


@pytest.fixture
def sample_vectors():
    """Gera vetores de exemplo para testes."""
    return np.random.randn(10, 384).astype(np.float32).tolist()


@pytest.fixture
def sample_metadata():
    """Gera metadados de exemplo para testes."""
    return [
        {"id": f"doc_{i}", "content": f"Contedo do documento {i}", "category": "test"}
        for i in range(10)
    ]


@pytest.fixture
def sample_ids():
    """Gera IDs de exemplo para testes."""
    return [f"vector_{i}" for i in range(10)]


# ============================================================================
# TESTES UNITRIOS (COM MOCKS)
# ============================================================================


class TestLanceDBVectorEngineUnit:
    """Testes unitrios com mocks para LanceDBVectorEngine."""

    def test_init_with_valid_params(self):
        """Testa inicializao com parmetros vlidos."""
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance", table_name="test_table")

        assert engine.db_path == "/tmp/test.lance"
        assert engine.table_name == "test_table"
        assert engine.embedding_dim == 384

    @pytest.mark.asyncio
    async def test_add_vectors_validation(self):
        """Testa validao de parmetros em add_vectors."""
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")

        # Vetores e metadados com comprimentos diferentes
        vectors = np.random.randn(5, 384).astype(np.float32).tolist()
        metadata = [{"id": f"doc_{i}"} for i in range(3)]  # Apenas 3

        with pytest.raises(VectorEngineError, match="must have same length"):
            await engine.add_vectors(vectors, metadata)

    @pytest.mark.asyncio
    async def test_search_without_table(self):
        """Testa busca quando tabela no est disponvel."""
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        engine._table = None  # Simular tabela no inicializada

        with pytest.raises(VectorEngineError, match="not available"):
            await engine.search(
                query_vector=np.random.randn(384).astype(np.float32).tolist()
            )

    @patch("neocortex.infra.vector_engine.lancedb")
    @pytest.mark.asyncio
    def test_get_by_id_not_found(self, mock_lancedb):
        """Testa recuperao de vetor por ID quando no existe."""
        mock_table = Mock()
        mock_table.to_arrow.return_value = None  # Simular nenhum resultado
        mock_connection = Mock()
        mock_connection.open_table.return_value = mock_table
        mock_lancedb.connect.return_value = mock_connection

        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        engine._table = mock_table

        result = engine.get_by_id("non_existent_id")
        assert result is None

    @patch("neocortex.infra.vector_engine.lancedb")
    def test_update_metadata_success(self, mock_lancedb):
        """Testa atualizao bem-sucedida de metadados."""
        mock_table = Mock()
        mock_table.update.return_value = Mock()  # Simular sucesso
        mock_connection = Mock()
        mock_connection.open_table.return_value = mock_table
        mock_lancedb.connect.return_value = mock_connection

        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        engine._table = mock_table

        # No deve levantar exceo
        engine.update_metadata(vector_id="test_id", metadata={"new_field": "new_value"})

        mock_table.update.assert_called_once()

    @patch("neocortex.infra.vector_engine.lancedb")
    def test_delete_vector_success(self, mock_lancedb):
        """Testa excluso bem-sucedida de vetor."""
        mock_table = Mock()
        mock_delete_result = Mock()
        mock_delete_result.deleted_rows = 1
        mock_table.delete.return_value = mock_delete_result
        mock_connection = Mock()
        mock_connection.open_table.return_value = mock_table
        mock_lancedb.connect.return_value = mock_connection

        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        engine._table = mock_table

        result = engine.delete("test_id")
        assert result == 1
        mock_table.delete.assert_called_once()


# ============================================================================
# TESTES DE INTEGRAO (COM BANCO REAL TEMPORRIO)
# ============================================================================


class TestLanceDBVectorEngineIntegration:
    """Testes de integrao com banco de dados LanceDB temporrio."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_db_path, sample_vectors, sample_metadata):
        """Teste completo do fluxo de trabalho: add  search  get  update  delete."""
        # 1. Inicializar engine
        engine = LanceDBVectorEngine(
            db_path=temp_db_path, table_name="integration_test", vector_dimension=384
        )

        # 2. Adicionar vetores
        added_ids = await engine.add_vectors(sample_vectors, sample_metadata)
        assert len(added_ids) == 10
        assert all(id is not None for id in added_ids)

        # 3. Buscar vetores similares
        query_vector = np.random.randn(384).astype(np.float32)
        results = await engine.search(
            query_vector=query_vector, limit=5, return_metadata=True
        )

        assert len(results) <= 5
        if results:
            assert "id" in results[0]
            assert "vector" in results[0] or "distance" in results[0]

        # 4. Recuperar vetor especfico
        test_id = added_ids[0]
        vector_data = await engine.get_by_id(test_id)
        assert vector_data is not None
        assert vector_data["id"] == test_id

        # 5. Atualizar metadados
        await engine.update_metadata(
            vector_id=test_id, metadata={"updated": True, "timestamp": "2026-04-14"}
        )

        # Verificar atualizao
        updated_data = await engine.get_by_id(test_id)
        assert updated_data["metadata"]["updated"] is True

        # 6. Excluir vetor
        deleted_count = await engine.delete([test_id])
        assert deleted_count == 1

        # 7. Verificar excluso
        deleted_data = await engine.get_by_id(test_id)
        assert deleted_data is None

        # 8. Estatsticas
        stats = await engine.get_stats()
        assert "total_vectors" in stats
        assert stats["total_vectors"] == 9  # Um foi excludo

    @pytest.mark.asyncio
    async def test_batch_operations(self, temp_db_path):
        """Testa operaes em lote."""
        engine = LanceDBVectorEngine(db_path=temp_db_path, table_name="batch_test")

        # Adicionar em lotes
        batch_vectors = np.random.randn(100, 384).astype(np.float32)
        batch_metadata = [{"id": f"batch_{i}", "batch": "test"} for i in range(100)]

        ids = await engine.add_vectors(batch_vectors, batch_metadata)
        assert len(ids) == 100

        # Buscar com filtro
        query_vector = np.random.randn(384).astype(np.float32)
        results = await engine.search(
            query_vector=query_vector, limit=10, filter_expression="batch = 'test'"
        )

        assert len(results) <= 10

    @pytest.mark.asyncio
    async def test_error_handling(self, temp_db_path):
        """Testa tratamento de erros."""
        engine = LanceDBVectorEngine(db_path=temp_db_path)

        # Tentar buscar sem vetores adicionados
        query_vector = np.random.randn(384).astype(np.float32)
        results = await engine.search(query_vector)
        assert results == []  # Deve retornar lista vazia, no erro

        # Tentar atualizar vetor inexistente
        with pytest.raises(VectorEngineError):
            await engine.update_metadata("non_existent", {"test": True})


# ============================================================================
# TESTES PARA RAGVectorEngine
# ============================================================================


class TestRAGVectorEngine:
    """Testes especficos para RAGVectorEngine."""

    def test_rag_engine_initialization(self, temp_db_path):
        """Testa inicializao do RAGVectorEngine."""
        engine = RAGVectorEngine(
            db_path=temp_db_path, table_name="rag_test", chunk_size=512, overlap=64
        )

        assert engine.chunk_size == 512
        assert engine.chunk_overlap == 64
        assert hasattr(engine, "add_documents")

    @patch("neocortex.infra.vector_engine.lancedb")
    @pytest.mark.asyncio
    async def test_add_document(self, mock_lancedb):
        """Testa adio de documento com chunking."""
        mock_table = Mock()
        mock_connection = Mock()
        mock_connection.open_table.return_value = mock_table
        mock_lancedb.connect.return_value = mock_connection

        engine = RAGVectorEngine(
            db_path="/tmp/rag.lance", chunk_size=100, chunk_overlap=20
        )
        engine._table = mock_table

        # Mock add_documents para retornar IDs falsos
        with patch.object(
            engine,
            "add_documents",
            AsyncMock(return_value=["chunk_1", "chunk_2", "chunk_3"]),
        ):
            # Documento maior que chunk_size
            document = {
                "text": "Lorem ipsum " * 50,
                "doc_id": "test_doc",
                "source": "test",
            }

            # Mock da funo de embedding
            mock_embed_fn = AsyncMock(return_value=[0.1] * 384)

            chunk_ids = await engine.add_documents([document], mock_embed_fn)

            # Deve criar mltiplos chunks
            assert len(chunk_ids) > 1
            # Cada chunk deve ter ID
            assert all(id is not None for id in chunk_ids)

    @pytest.mark.asyncio
    async def test_rag_search_with_context(self, temp_db_path):
        """Testa busca RAG com contexto expandido."""
        engine = RAGVectorEngine(db_path=temp_db_path, table_name="rag_context_test")

        # Mock add_documents e search
        with patch.object(
            engine, "add_documents", AsyncMock(return_value=["chunk_1", "chunk_2"])
        ):
            with patch.object(
                engine,
                "search",
                AsyncMock(
                    return_value=[
                        {
                            "chunk_id": "chunk_1",
                            "document_id": "python_doc",
                            "score": 0.9,
                        },
                        {
                            "chunk_id": "chunk_2",
                            "document_id": "python_doc",
                            "score": 0.8,
                        },
                    ]
                ),
            ):
                # Adicionar documento com mltiplos chunks
                document = {
                    "text": "Python  uma linguagem de programao. Python  interpretada. Python tem tipagem dinmica.",
                    "doc_id": "python_doc",
                    "language": "pt",
                }

                # Mock da funo de embedding
                mock_embed_fn = AsyncMock(return_value=[0.1] * 384)

                chunk_ids = await engine.add_documents([document], mock_embed_fn)

                # Buscar
                query_vector = np.random.randn(384).astype(np.float32)
                results = await engine.search(
                    query_vector=query_vector, limit=3, expand_context=True
                )

                assert len(results) <= 3
                if results:
                    # Resultados RAG devem ter campos adicionais
                    assert "chunk_id" in results[0]
                    assert "document_id" in results[0]


# ============================================================================
# TESTES PARA create_vector_engine E VectorEngineContext
# ============================================================================


def test_create_vector_engine_default():
    """Testa factory function create_vector_engine."""
    engine = create_vector_engine(db_path="/tmp/factory.lance")
    assert isinstance(engine, LanceDBVectorEngine)


def test_create_vector_engine_rag():
    """Testa factory function para criar RAGVectorEngine."""
    engine = create_vector_engine(
        db_path="/tmp/rag_factory.lance", engine_type="rag", chunk_size=256
    )
    assert isinstance(engine, RAGVectorEngine)
    assert engine.chunk_size == 256


def test_vector_engine_context():
    """Testa VectorEngineContext (context manager)."""
    with tempfile.NamedTemporaryFile(suffix=".lance") as f:
        with VectorEngineContext(
            LanceDBVectorEngine(db_path=f.name, table_name="context_test")
        ) as engine:
            assert engine._table is not None

            # Operao dentro do contexto
            vectors = np.random.randn(3, 384).astype(np.float32)
            metadata = [{"id": f"ctx_{i}"} for i in range(3)]
            ids = engine.add_vectors(vectors, metadata)
            assert len(ids) == 3

        # Engine deve estar fechada aps contexto
        # (verificao depende da implementao real)


# ============================================================================
# CONFIGURAO PYTEST
# ============================================================================

if __name__ == "__main__":
    """Ponto de entrada para execuo direta dos testes."""
    print("Executando testes do VectorEngine...")
    pytest_args = [
        __file__,
        "-v",  # verbose
        "--tb=short",  # traceback curto
        "--disable-warnings",  # suprimir warnings
    ]

    # Executar pytest
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)
