#!/usr/bin/env python3
# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
NC-SCR-FR-051-knowledge-graph-builder.py
Knowledge Graph Builder - Pipeline de Vetorizao Geomtrico (LanceDB/ChromaDB)

Adaptado a partir da base do manifest-factory, itera a rvore do projeto (KGS),
extrai o frontmatter YAML topolgico e converte os arquivos em chunks semnticos
no LanceDBVectorEngine, construindo relacionamentos RAG robustos.

Autor: T0 (NeoCortex Antigravity)
Data: 2026-04-14
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Adicionando raiz ao context path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

# Engine importado do pacote do framework
from typing import Union

from neocortex.infra.vector_engine import (
    LanceDBVectorEngine,
    RAGVectorEngine,
    create_vector_engine,
)

try:
    import ruamel.yaml

    yaml = ruamel.yaml.YAML(typ="safe")
except ImportError:
    yaml = None
    logging.warning(
        "ruamel.yaml not found. Falling back to simple YAML extraction if possible."
    )

from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("GraphBuilder")

DB_PATH = PROJECT_ROOT / "data" / "vector_db"

# Diretrios/arquivos ignorados
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "lobes",
    "DIR-BAK-FR-001-backup-main",
    "DIR-ARC-FR-001-archive-main",
    "data",
}


def extract_frontmatter(content: str) -> dict:
    if not yaml:
        return {}
    if "---" in content[:500]:
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_str = parts[1]
                result = yaml.load(fm_str)
                if isinstance(result, dict):
                    return result
                elif result is None:
                    return {}
                else:
                    # If result is a string or other type, return empty dict
                    logger.debug(f"Frontmatter parsed as non-dict: {type(result)}")
                    return {}
        except Exception as e:
            logger.debug(f"Failed to parse frontmatter: {e}")
    return {}


async def build_knowledge_graph():
    logger.info("Iniciando Knowledge Graph Builder (NC-DS-051)...")

    # 1. Carregar funo de embedding padro do Chroma (usa tokenizador leve ONNX/minilm)
    # Isso gera vetores de dimenso 384 perfeitos para o LanceDB local
    try:
        ef = embedding_functions.DefaultEmbeddingFunction()
        logger.info(
            "ChromaDB Embedding Function (all-MiniLM-L6-v2) inicializada com sucesso."
        )
    except Exception as e:
        logger.error(f"Erro ao inicializar ChomraDB Embedding Function: {e}")
        return

    # 2. Inicializar RAG Vector Engine local (LanceDB backend)
    engine: Union[LanceDBVectorEngine, RAGVectorEngine] = create_vector_engine(
        engine_type="rag",
        db_path=str(DB_PATH),
        table_name="neocortex_kgs",
        embedding_dim=384,
        distance_metric="cosine",
        chunk_size=1000,
        chunk_overlap=200,
    )

    await engine.initialize()
    logger.info("LanceDB RAG Vector Engine pronta.")

    documents = []

    # 3. Scanning assncrono lgico da rvore
    logger.info(
        "Escaneando arquivos para indexao (Respeitando Quarentena de Legados)..."
    )
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        dirnames[:] = [
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        for name in filenames:
            if name.endswith(
                (".py", ".md", ".json", ".yaml", ".yml")
            ) and not name.startswith("."):
                path = Path(dirpath) / name

                # Prevenir scan do vetor db
                if "vector_db" in str(path):
                    continue

                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    fm = extract_frontmatter(content)

                    # Garantir que fm  um dicionrio
                    if not isinstance(fm, dict):
                        fm = {}
                        logger.debug(
                            f"Frontmatter no  dict para {name}, usando vazio"
                        )

                    # Convert arrays to strings to fit metadata constraints in lancedb
                    tags_v = fm.get("tags", [])
                    if isinstance(tags_v, list):
                        tags_v = ", ".join(str(t) for t in tags_v)
                    else:
                        tags_v = str(tags_v)

                    doc = {
                        "text": content,
                        "file_name": name,
                        "file_path": str(path.relative_to(PROJECT_ROOT)).replace(
                            "\\", "/"
                        ),
                        "file_ext": path.suffix,
                        "domain": str(fm.get("domain", "undocumented")),
                        "layer": str(fm.get("layer", "undocumented")),
                        "type": str(fm.get("type", "undocumented")),
                        "tags": tags_v,
                    }
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"Erro na leitura do arquivo {name}: {e}")

    logger.info(f"Concludo. Processando {len(documents)} arquivos aptos...")

    # 4. Wrapper assncrono para o provider de embeddings Sync do chromadb
    async def embed_fn(text) -> list:
        loop = asyncio.get_running_loop()
        if isinstance(text, list):
            result = await loop.run_in_executor(None, ef, text)
            # Converter lista de ndarrays para lista de listas
            converted = []
            for emb in result:
                if hasattr(emb, "tolist"):
                    converted.append(emb.tolist())
                else:
                    converted.append(emb)
            return converted
        # Executa em theadpool para no travar a Roda de Eventos (ACL Constraint)
        result = await loop.run_in_executor(None, ef, [text])
        # result  uma lista de embeddings (ndarray), pegar o primeiro e converter
        if result:
            emb = result[0]
            if hasattr(emb, "tolist"):
                return emb.tolist()  # retorna list[float]
            # Se no for ndarray, assumir que j  lista
            if isinstance(emb, list):
                return emb
            # Caso inesperado, converter para lista
            return list(emb)
        return []

    logger.info("Executando pipeline de chunking em lote + integrao vetorial...")

    # Garantir que o engine  RAGVectorEngine para ter mtodo add_documents
    if not isinstance(engine, RAGVectorEngine):
        logger.error("Engine no  RAGVectorEngine. No pode usar add_documents.")
        return

    # Processar em lotes para melhor progresso e resilincia
    batch_size = 20
    total_docs = len(documents)
    total_chunks = 0

    logger.info(f"Processando {total_docs} documentos em lotes de {batch_size}...")

    for i in range(0, total_docs, batch_size):
        batch = documents[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_docs + batch_size - 1) // batch_size

        logger.info(
            f"Lote {batch_num}/{total_batches}: processando {len(batch)} documentos..."
        )

        try:
            chunk_ids = await engine.add_documents(
                documents=batch,
                embed_fn=embed_fn,
                metadata_fields=[
                    "file_name",
                    "file_path",
                    "file_ext",
                    "domain",
                    "layer",
                    "type",
                    "tags",
                ],
            )
            total_chunks += len(chunk_ids)
            logger.info(
                f"Lote {batch_num} concludo: {len(chunk_ids)} chunks adicionados (total acumulado: {total_chunks})"
            )

            # Pequena pausa para evitar sobrecarga
            await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Erro no lote {batch_num}: {e}")
            # Continuar com prximos lotes
            continue

    logger.info(f"Processamento em lotes concludo. Total de chunks: {total_chunks}")

    stats = await engine.get_stats()
    logger.info("---------------------------------------------------------")
    logger.info(" VETORIZAO KNOWLEDGE GRAPH CONCLUDA")
    logger.info(f" Tabela: {stats.get('table_name')}")
    logger.info(f" Total de Vetores Injetados (Chunks): {stats.get('vector_count')}")
    logger.info(
        f" Dimenso: {stats.get('embedding_dim')} / Distncia: {stats.get('distance_metric')}"
    )
    logger.info("---------------------------------------------------------")

    await engine.close()


if __name__ == "__main__":
    asyncio.run(build_knowledge_graph())
