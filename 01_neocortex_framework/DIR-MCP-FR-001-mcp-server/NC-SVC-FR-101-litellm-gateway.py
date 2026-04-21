#!/usr/bin/env python3
"""
NC-SVC-FR-101 - LiteLLM Gateway Service
Proxy simples para Ollama, porta 4000
Conforme NC-NAM-FR-001-naming-convention.md
"""

import socket
import threading
import json
import time
import sys
import urllib.request
import urllib.error
import io

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print('NC-SVC-FR-101 - LiteLLM Gateway Service (porta 4000)')

class SimpleLiteLLM:
    def __init__(self, port=4000):
        self.port = port
        self.running = True
        self.ollama_url = "http://localhost:11434"
        
    def call_ollama(self, model, prompt):
        """Chama Ollama API local"""
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "encoding": "utf-8"
                }
            }
            
            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                # Garantir que a resposta seja UTF-8
                response_text = result.get('response', '')
                if isinstance(response_text, str):
                    return response_text.encode('utf-8').decode('utf-8')
                return str(response_text)
                
        except Exception as e:
            return f"Erro Ollama: {str(e)}"
    
    def process_openai_request(self, request_data):
        """Processa requisições no formato OpenAI API"""
        try:
            request = json.loads(request_data)
            
            # Extrair parâmetros
            model = request.get('model', 'qwen2.5-coder:1.5b-instruct')
            
            # Remover prefixo "ollama/" se presente
            if model.startswith('ollama/'):
                model = model[7:]  # Remove "ollama/"
            
            messages = request.get('messages', [])
            prompt = ""
            
            # Converter messages para prompt
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt += f"{role}: {content}\n"
            
            # Chamar Ollama
            response_text = self.call_ollama(model, prompt)
            
            # Formatar resposta OpenAI
            return {
                "id": "chatcmpl-" + str(int(time.time())),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(prompt.split()) + len(response_text.split())
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def handle_client(self, conn, addr):
        """Handle client connection"""
        try:
            # Receber requisição
            data = conn.recv(8192)
            if not data:
                return
            
            request_text = data.decode('utf-8')
            
            # Verificar se é health check
            if 'GET /health' in request_text:
                response = json.dumps({"status": "healthy", "gateway": "simple-litellm"})
                headers = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
                conn.send((headers + response).encode('utf-8'))
                
            # Verificar se é OpenAI API
            elif 'POST /v1/chat/completions' in request_text:
                # Extrair JSON do body
                lines = request_text.split('\r\n')
                body_start = False
                body = ""
                
                for line in lines:
                    if body_start:
                        body += line
                    if line == '':
                        body_start = True
                
                # Processar
                result = self.process_openai_request(body)
                response = json.dumps(result)
                headers = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
                conn.send((headers + response).encode('utf-8'))
                
            else:
                # Default response
                response = json.dumps({
                    "gateway": "NeoCortex LiteLLM Simple",
                    "version": "1.0",
                    "models": ["qwen2.5-coder:1.5b-instruct", "qwen2.5-coder:3b-instruct"],
                    "endpoints": ["/v1/chat/completions", "/health"]
                })
                headers = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
                conn.send((headers + response).encode('utf-8'))
                
        except Exception as e:
            print(f"Client error {addr}: {e}")
        finally:
            conn.close()
    
    def start(self):
        """Start the gateway server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind(('0.0.0.0', self.port))
            server.listen(20)
            server.settimeout(1)
            
            print(f'✅ LiteLLM Gateway ativo na porta {self.port}')
            print(f'🔗 Ollama: {self.ollama_url}')
            print('🎯 Aguardando requisições...')
            
            while self.running:
                try:
                    conn, addr = server.accept()
                    thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    thread.daemon = True
                    thread.start()
                    
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Server error: {e}")
                    continue
                    
        except Exception as e:
            print(f"Fatal error: {e}")
        finally:
            server.close()

def main():
    """Main entry point"""
    gateway = SimpleLiteLLM(port=4000)
    
    # Signal handling
    import signal
    def signal_handler(sig, frame):
        print('\n🛑 Parando gateway...')
        gateway.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    gateway.start()

if __name__ == '__main__':
    main()