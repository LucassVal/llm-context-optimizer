#!/usr/bin/env python3
"""---
NC-SVC-FR-102 - DeepSeek Gateway
---
"""

"""---
NC-SVC-FR-102 - DeepSeek Gateway
---
"""

"""
NC-SVC-FR-102 - DeepSeek Gateway
Proxy para DeepSeek API com whitelist de modelos.
Porta 4001, API OpenAI-compatible.
"""

import http.server
import json
import os
import sys
import time
import urllib.request
import urllib.error
import ssl

PORT = 4001
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
# Whitelist de modelos permitidos
ALLOWED_MODELS = ["deepseek-v4-flash", "deepseek-v4-pro"]
DEFAULT_MODEL = "deepseek-v4-pro"

# Ler API key do ambiente, com fallback hardcoded (seguro pois é ambiente controlado)
API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""


class DeepSeekGatewayHandler(http.server.BaseHTTPRequestHandler):
    """Handler HTTP que filtra modelos por whitelist e força DEFAULT_MODEL."""

    def log_message(self, format, *args):
        """Log estruturado com timestamp."""
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}\n")

    def _send_json(self, status, data):
        """Helper para responder JSON."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.wfile.write(body)

    def _send_error_json(self, status, message):
        self._send_json(status, {"error": {"message": message, "type": "gateway_blocked"}})

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {
                "status": "healthy",
                "gateway": "deepseek-gateway",
                "port": PORT,
                "default_model": DEFAULT_MODEL,
                "allowed_models": ALLOWED_MODELS
            })
        elif self.path == "/v1/models":
            self._send_json(200, {
                "object": "list",
                "data": [
                    {
                        "id": model_id,
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "deepseek"
                    }
                    for model_id in ALLOWED_MODELS
                ]
            })
        else:
            self._send_error_json(404, f"Not found: {self.path}")

    def do_OPTIONS(self):
        """CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._send_error_json(404, f"Not found: {self.path}")
            return

        # Ler body
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_error_json(400, "Empty request body")
            return

        try:
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self._send_error_json(400, f"Invalid JSON: {e}")
            return

        # Validar modelo contra whitelist
        requested_model = request_data.get("model", "")
        original_model = requested_model

        if requested_model and requested_model not in ALLOWED_MODELS:
            self._send_error_json(403, (
                f"MODEL BLOCKED: '{requested_model}' não está na whitelist. "
                f"Modelos permitidos: {', '.join(ALLOWED_MODELS)}. "
                f"Isso previne consumo acidental de tokens em modelos não-autorizados."
            ))
            return

        # Forçar modelo padrão se não especificado, senão respeita o request
        if not requested_model:
            request_data["model"] = DEFAULT_MODEL
        else:
            request_data["model"] = requested_model

        # Encaminhar para DeepSeek API
        try:
            payload = json.dumps(request_data, ensure_ascii=False).encode("utf-8")

            req = urllib.request.Request(
                DEEPSEEK_API_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {API_KEY}",
                    "Accept": "application/json"
                }
            )

            # Timeout de 5 minutos para reasoning (modelo é lento)
            ctx = ssl.create_default_context()
            response = urllib.request.urlopen(req, timeout=300, context=ctx)
            response_body = response.read().decode("utf-8")

            # Log de auditoria: tokens consumidos
            try:
                result = json.loads(response_body)
                usage = result.get("usage", {})
                model_used = result.get("model", request_data["model"])
                token_count = usage.get("total_tokens", 0)
                reasoning = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0) if isinstance(usage.get("completion_tokens_details"), dict) else 0
                print(f"[AUDIT] Modelo: {model_used} | Tokens: {token_count} | Reasoning: {reasoning} | Requisitado original: {original_model or '(default)'}")
            except json.JSONDecodeError:
                print(f"[AUDIT] Resposta recebida (não-JSON)")

            # Retornar resposta ao cliente
            self.send_response(response.status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            # Preservar headers relevantes
            for h in ["X-Request-Id", "X-RateLimit-Remaining"]:
                if response.headers.get(h):
                    self.send_header(h, response.headers[h])
            self.end_headers()
            self.wfile.write(response_body.encode("utf-8"))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            print(f"[ERRO] DeepSeek API retornou HTTP {e.code}: {error_body[:200]}")
            self._send_json(e.code, {
                "error": {
                    "message": f"DeepSeek API error: {e.code}",
                    "details": error_body[:500]
                }
            })
        except urllib.error.URLError as e:
            print(f"[ERRO] Não foi possível conectar à DeepSeek API: {e.reason}")
            self._send_error_json(502, f"Cannot reach DeepSeek API: {e.reason}")
        except Exception as e:
            print(f"[ERRO] Inesperado: {e}")
            self._send_error_json(500, f"Gateway error: {str(e)}")


def main():
    print("=" * 60)
    print("  NC-SVC-FR-102 - DeepSeek Gateway")
    print("=" * 60)
    print(f"  Porta:     {PORT}")
    print(f"  Modelo:    {DEFAULT_MODEL} (padrão)")
    print(f"  Whitelist: {', '.join(ALLOWED_MODELS)}")
    print(f"  API URL:   {DEEPSEEK_API_URL}")
    print(f"  API Key:   {API_KEY[:8]}...{API_KEY[-4:]}")
    print("-" * 60)
    print("  Qualquer modelo fora da whitelist será REJEITADO.")
    print("  Se o cliente não especificar modelo, usa o padrão.")
    print("=" * 60)

    server = http.server.HTTPServer(("0.0.0.0", PORT), DeepSeekGatewayHandler)
    print(f"\n  Gateway ouvindo em http://localhost:{PORT}")
    print(f"  Endpoint: http://localhost:{PORT}/v1/chat/completions")
    print(f"  Health:   http://localhost:{PORT}/health")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGateway encerrado.")
        server.server_close()


if __name__ == "__main__":
    # Garantir UTF-8 no Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    main()
