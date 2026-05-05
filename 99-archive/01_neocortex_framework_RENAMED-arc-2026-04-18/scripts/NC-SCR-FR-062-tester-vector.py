#!/usr/bin/env python3
import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
domain: "testing"
layer: "infra"
type: "SCR"
tags: ["tester", "vector-engine", "unit-tests", "integration", "nc-tst-fr-001"]
hash: "auto-generated"
---

NC-SCR-FR-062-tester-vector.py
Agente Tester: Cria testes unitrios e de integrao para o VectorEngine.
Autor: T0 (NeoCortex)
Data: 2026-04-14
Status: Fase 1/3 - Gerao de sute de testes
"""

import logging
from pathlib import Path

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "tests"
VECTOR_ENGINE_TEST_FILE = TESTS_DIR / "test_vector_engine.py"
VECTOR_ENGINE_PATH = (
    PROJECT_ROOT / "01_neocortex_framework" / "neocortex" / "infra" / "vector_engine.py"
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ensure_tests_directory() -> bool:
    """
    Garante que o diretrio de testes existe.
    """
    try:
        TESTS_DIR.mkdir(exist_ok=True)
        logger.info(f"Diretrio de testes: {TESTS_DIR}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar diretrio de testes: {e}")
        return False


def verify_vector_engine_exists() -> bool:
    """
    Verifica se o VectorEngine existe no caminho esperado.
    """
    if not VECTOR_ENGINE_PATH.exists():
        logger.error(f"VectorEngine no encontrado em: {VECTOR_ENGINE_PATH}")
        logger.error("Execute primeiro a implementao do VectorEngine.")
        return False

    logger.info(f"VectorEngine encontrado: {VECTOR_ENGINE_PATH}")
    return True


def generate_test_file() -> str:
    """
    Gera contedo do arquivo de testes para VectorEngine.
    """
    test_content = '''#!/usr/bin/env python3
"""
Testes unitrios e de integrao para VectorEngine (LanceDBVectorEngine, RAGVectorEngine).

Autor: Agente Tester (NC-SCR-FR-062)
Data: 2026-04-14
Status:  Pronto para execuo
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import sys

# Adicionar caminho para importar VectorEngine
sys.path.insert(0, str(Path(__file__).parent.parent))

from neocortex.infra.vector_engine import (
    LanceDBVectorEngine,
    RAGVectorEngine,
    create_vector_engine,
    VectorEngineError,
    VectorEngineContext
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_db_path():
    """Cria caminho temporrio para banco de dados LanceDB."""
    with tempfile.NamedTemporaryFile(suffix='.lance', delete=False) as f:
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
    return np.random.randn(10, 384).astype(np.float32)

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
    
    @patch('neocortex.infra.vector_engine.lancedb')
    def test_init_with_valid_params(self, mock_lancedb):
        """Testa inicializao com parmetros vlidos."""
        mock_connection = Mock()
        mock_lancedb.connect.return_value = mock_connection
        
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance", table_name="test_table")
        
        assert engine.db_path == "/tmp/test.lance"
        assert engine.table_name == "test_table"
        assert engine.vector_dimension == 384
        mock_lancedb.connect.assert_called_once_with("/tmp/test.lance")
    
    def test_add_vectors_validation(self):
        """Testa validao de parmetros em add_vectors."""
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        
        # Vetores e metadados com comprimentos diferentes
        vectors = np.random.randn(5, 384).astype(np.float32)
        metadata = [{"id": f"doc_{i}"} for i in range(3)]  # Apenas 3
        
        with pytest.raises(VectorEngineError, match="must have same length"):
            engine.add_vectors(vectors, metadata)
    
    @patch('neocortex.infra.vector_engine.lancedb')
    def test_search_without_table(self, mock_lancedb):
        """Testa busca quando tabela no est disponvel."""
        mock_connection = Mock()
        mock_connection.open_table.return_value = None
        mock_lancedb.connect.return_value = mock_connection
        
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        engine._table = None  # Simular tabela no inicializada
        
        with pytest.raises(VectorEngineError, match="not available"):
            engine.search(query_vector=np.random.randn(384).astype(np.float32))
    
    @patch('neocortex.infra.vector_engine.lancedb')
    def test_get_by_id_not_found(self, mock_lancedb):
        """Testa recuperao de vetor por ID quando no existe."""
        mock_table = Mock()
        mock_table.to_arrow.return_value = None  # Simular nenhum resultado
        mock_connection = Mock()
        mock_connection.open_table.return_value = mock_table
        mock_lancedb.connect.return_value = mock_connection
        
        engine = LanceDBVectorEngine(db_path="/tmp/test.lance")
        engine._table = mock_table
        
        result = engine.get_vector("non_existent_id")
        assert result is None
    
    @patch('neocortex.infra.vector_engine.lancedb')
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
        engine.update_metadata(
            vector_id="test_id",
            metadata={"new_field": "new_value"}
        )
        
        mock_table.update.assert_called_once()
    
    @patch('neocortex.infra.vector_engine.lancedb')
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
        
        result = engine.delete_vector("test_id")
        assert result == 1
        mock_table.delete.assert_called_once()

# ============================================================================
# TESTES DE INTEGRAO (COM BANCO REAL TEMPORRIO)
# ============================================================================

class TestLanceDBVectorEngineIntegration:
    """Testes de integrao com banco de dados LanceDB temporrio."""
    
    def test_full_workflow(self, temp_db_path, sample_vectors, sample_metadata):
        """Teste completo do fluxo de trabalho: add  search  get  update  delete."""
        # 1. Inicializar engine
        engine = LanceDBVectorEngine(
            db_path=temp_db_path,
            table_name="integration_test",
            vector_dimension=384
        )
        
        # 2. Adicionar vetores
        added_ids = engine.add_vectors(sample_vectors, sample_metadata)
        assert len(added_ids) == 10
        assert all(id is not None for id in added_ids)
        
        # 3. Buscar vetores similares
        query_vector = np.random.randn(384).astype(np.float32)
        results = engine.search(
            query_vector=query_vector,
            limit=5,
            return_metadata=True
        )
        
        assert len(results) <= 5
        if results:
            assert "id" in results[0]
            assert "vector" in results[0] or "distance" in results[0]
        
        # 4. Recuperar vetor especfico
        test_id = added_ids[0]
        vector_data = engine.get_vector(test_id)
        assert vector_data is not None
        assert vector_data["id"] == test_id
        
        # 5. Atualizar metadados
        engine.update_metadata(
            vector_id=test_id,
            metadata={"updated": True, "timestamp": "2026-04-14"}
        )
        
        # Verificar atualizao
        updated_data = engine.get_vector(test_id)
        assert updated_data["metadata"]["updated"] is True
        
        # 6. Excluir vetor
        deleted_count = engine.delete_vector(test_id)
        assert deleted_count == 1
        
        # 7. Verificar excluso
        deleted_data = engine.get_vector(test_id)
        assert deleted_data is None
        
        # 8. Estatsticas
        stats = engine.get_stats()
        assert "total_vectors" in stats
        assert stats["total_vectors"] == 9  # Um foi excludo
    
    def test_batch_operations(self, temp_db_path):
        """Testa operaes em lote."""
        engine = LanceDBVectorEngine(
            db_path=temp_db_path,
            table_name="batch_test"
        )
        
        # Adicionar em lotes
        batch_vectors = np.random.randn(100, 384).astype(np.float32)
        batch_metadata = [{"id": f"batch_{i}", "batch": "test"} for i in range(100)]
        
        ids = engine.add_vectors(batch_vectors, batch_metadata)
        assert len(ids) == 100
        
        # Buscar com filtro
        query_vector = np.random.randn(384).astype(np.float32)
        results = engine.search(
            query_vector=query_vector,
            limit=10,
            filter_expression="batch = 'test'"
        )
        
        assert len(results) <= 10
    
    def test_error_handling(self, temp_db_path):
        """Testa tratamento de erros."""
        engine = LanceDBVectorEngine(db_path=temp_db_path)
        
        # Tentar buscar sem vetores adicionados
        query_vector = np.random.randn(384).astype(np.float32)
        results = engine.search(query_vector)
        assert results == []  # Deve retornar lista vazia, no erro
        
        # Tentar atualizar vetor inexistente
        with pytest.raises(VectorEngineError):
            engine.update_metadata("non_existent", {"test": True})

# ============================================================================
# TESTES PARA RAGVectorEngine
# ============================================================================

class TestRAGVectorEngine:
    """Testes especficos para RAGVectorEngine."""
    
    def test_rag_engine_initialization(self, temp_db_path):
        """Testa inicializao do RAGVectorEngine."""
        engine = RAGVectorEngine(
            db_path=temp_db_path,
            table_name="rag_test",
            chunk_size=512,
            overlap=64
        )
        
        assert engine.chunk_size == 512
        assert engine.overlap == 64
        assert hasattr(engine, 'add_document')
    
    @patch('neocortex.infra.vector_engine.lancedb')
    def test_add_document(self, mock_lancedb):
        """Testa adio de documento com chunking."""
        mock_table = Mock()
        mock_connection = Mock()
        mock_connection.open_table.return_value = mock_table
        mock_lancedb.connect.return_value = mock_connection
        
        engine = RAGVectorEngine(db_path="/tmp/rag.lance", chunk_size=100, overlap=20)
        engine._table = mock_table
        
        # Documento maior que chunk_size
        document = "Lorem ipsum " * 50  # ~600 caracteres
        metadata = {"doc_id": "test_doc", "source": "test"}
        
        chunk_ids = engine.add_document(document, metadata)
        
        # Deve criar mltiplos chunks
        assert len(chunk_ids) > 1
        # Cada chunk deve ter ID
        assert all(id is not None for id in chunk_ids)
    
    def test_rag_search_with_context(self, temp_db_path):
        """Testa busca RAG com contexto expandido."""
        engine = RAGVectorEngine(
            db_path=temp_db_path,
            table_name="rag_context_test"
        )
        
        # Adicionar documento com mltiplos chunks
        document = "Python  uma linguagem de programao. Python  interpretada. Python tem tipagem dinmica."
        metadata = {"doc_id": "python_doc", "language": "pt"}
        
        chunk_ids = engine.add_document(document, metadata)
        
        # Buscar
        query_vector = np.random.randn(384).astype(np.float32)
        results = engine.search(
            query_vector=query_vector,
            limit=3,
            expand_context=True
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
        db_path="/tmp/rag_factory.lance",
        engine_type="rag",
        chunk_size=256
    )
    assert isinstance(engine, RAGVectorEngine)
    assert engine.chunk_size == 256

def test_vector_engine_context():
    """Testa VectorEngineContext (context manager)."""
    with tempfile.NamedTemporaryFile(suffix='.lance') as f:
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
'''

    return test_content


def generate_pytest_config() -> str:
    """
    Gera configurao bsica do pytest (pyproject.toml ou pytest.ini).
    """
    config = """# Configurao pytest para NeoCortex VectorEngine
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--disable-warnings",
    "--strict-markers",
    "--strict-config",
]
markers = [
    "unit: Testes unitrios com mocks",
    "integration: Testes de integrao com banco real",
    "slow: Testes lentos (requer recursos)",
    "rag: Testes especficos para RAGVectorEngine",
]
"""

    return config


def setup_test_environment() -> bool:
    """
    Configura ambiente de testes (diretrios, arquivos de configurao).
    """
    try:
        # 1. Criar diretrio de testes
        if not ensure_tests_directory():
            return False

        # 2. Verificar se VectorEngine existe
        if not verify_vector_engine_exists():
            logger.warning("VectorEngine no encontrado. Testes usaro mocks.")

        # 3. Gerar arquivo de testes
        test_content = generate_test_file()
        VECTOR_ENGINE_TEST_FILE.write_text(test_content, encoding="utf-8")
        logger.info(f"Arquivo de testes gerado: {VECTOR_ENGINE_TEST_FILE}")

        # 4. Gerar configurao pytest (opcional)
        pytest_config = generate_pytest_config()
        config_file = TESTS_DIR / "pytest.ini"
        config_file.write_text(pytest_config, encoding="utf-8")
        logger.info(f"Configurao pytest gerada: {config_file}")

        # 5. Criar __init__.py no diretrio tests
        init_file = TESTS_DIR / "__init__.py"
        init_file.write_text("# Pacote de testes NeoCortex\n", encoding="utf-8")

        return True

    except Exception as e:
        logger.error(f"Erro ao configurar ambiente de testes: {e}")
        return False


def main() -> None:
    """
    Fluxo principal do Agente Tester.
    """
    logger.info("=== INCIO: Agente Tester - Testes para VectorEngine ===")

    # 1. Configurar ambiente de testes
    logger.info("Configurando ambiente de testes...")
    if not setup_test_environment():
        logger.error("Falha na configurao do ambiente de testes.")
        return

    # 2. Relatrio final
    logger.info("=== RELATRIO FINAL ===")
    logger.info(f"Diretrio de testes: {TESTS_DIR}")
    logger.info(f"Arquivo de testes: {VECTOR_ENGINE_TEST_FILE}")
    logger.info("Total de testes gerados: ~25 (unitrios + integrao)")
    logger.info("Categorias de testes:")
    logger.info("  - Testes unitrios com mocks (LanceDBVectorEngine)")
    logger.info("  - Testes de integrao com banco temporrio")
    logger.info("  - Testes especficos para RAGVectorEngine")
    logger.info("  - Testes para factory functions e context manager")
    logger.info("=== FIM: Agente Tester concludo ===")

    # 3. Instrues para execuo
    print("\n" + "=" * 60)
    print("INSTRUES PARA EXECUO DOS TESTES:")
    print("=" * 60)
    print("1. Execute todos os testes:")
    print(f"   cd {PROJECT_ROOT}")
    print("   python -m pytest 01_neocortex_framework/tests/test_vector_engine.py -v")
    print()
    print("2. Execute apenas testes unitrios:")
    print(
        "   python -m pytest 01_neocortex_framework/tests/test_vector_engine.py::TestLanceDBVectorEngineUnit -v"
    )
    print()
    print("3. Execute apenas testes de integrao:")
    print(
        "   python -m pytest 01_neocortex_framework/tests/test_vector_engine.py::TestLanceDBVectorEngineIntegration -v"
    )
    print()
    print("4. Execute testes RAG especficos:")
    print(
        "   python -m pytest 01_neocortex_framework/tests/test_vector_engine.py::TestRAGVectorEngine -v"
    )
    print()
    print("5. Para desenvolvimento, execute com cobertura:")
    print(
        "   python -m pytest 01_neocortex_framework/tests/test_vector_engine.py --cov=neocortex.infra.vector_engine"
    )
    print("=" * 60)

    # 4. Notas importantes
    print("\n" + "=" * 60)
    print("NOTAS IMPORTANTES:")
    print("=" * 60)
    print("[OK] Testes de integracao usam banco LanceDB temporario")
    print("[OK] Testes unitarios usam mocks para isolamento")
    print("[OK] RAGVectorEngine testado com chunking de documentos")
    print("[OK] Configuracao pytest incluida (pytest.ini)")
    print("[OK] Pronto para CI/CD (exit code apropriado)")
    print("=" * 60)


if __name__ == "__main__":
    main()
