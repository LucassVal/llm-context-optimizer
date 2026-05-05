import asyncio
import httpx
import json


async def test_sse_raw():
    """Testa conexão SSE crua com o servidor MCP"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Conectar ao endpoint SSE
            print("Conectando a http://127.0.0.1:8765/sse...")
            async with client.stream("GET", "http://127.0.0.1:8765/sse") as response:
                print(f"Status: {response.status_code}")
                print(f"Headers: {response.headers}")

                # Ler eventos SSE
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: "
                        if data:
                            try:
                                event = json.loads(data)
                                print(
                                    f"Evento recebido: {json.dumps(event, indent=2, ensure_ascii=False)}"
                                )
                            except json.JSONDecodeError:
                                print(f"Dados não-JSON: {data}")
                    elif line:  # Ignorar linhas vazias e comentários
                        print(f"Linha: {line}")

        except Exception as e:
            print(f"Erro: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sse_raw())
