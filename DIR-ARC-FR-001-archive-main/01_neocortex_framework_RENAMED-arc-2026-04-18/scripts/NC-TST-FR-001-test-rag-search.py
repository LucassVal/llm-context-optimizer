import asyncio
import sys
from pathlib import Path

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Adicionando raiz ao context path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

import chromadb.utils.embedding_functions as ef

from neocortex.infra.vector_engine import create_vector_engine


async def test_search():
    embedding_func = ef.DefaultEmbeddingFunction()

    async def embed_fn(text):
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None, embedding_func, [text])
        return res[0]

    engine = create_vector_engine(
        engine_type="rag",
        db_path=str(PROJECT_ROOT / "01_neocortex_framework" / "data" / "vector_db"),
        table_name="neocortex_kgs",
        embedding_dim=384
    )

    await engine.initialize()

    query = "O que  a Zona de Quarentena e quais arquivos ela protege?"
    print(f"\n Buscando por: '{query}'...")

    results = await engine.retrieve_relevant_chunks(
        query=query,
        embed_fn=embed_fn,
        top_k=3
    )

    print("\n RESULTADOS ENCONTRADOS:")
    for i, res in enumerate(results):
        meta = res.get("metadata", {})
        score = res.get("score", 0)
        path = meta.get("file_path", "unknown")
        print(f"\n[{i+1}] Score: {score:.4f} | Arquivo: {path}")
        print(f"Trecho: {res.get('text')[:300]}...")

    await engine.close()

if __name__ == "__main__":
    asyncio.run(test_search())
