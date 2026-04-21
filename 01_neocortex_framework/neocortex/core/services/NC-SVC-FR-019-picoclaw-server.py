#!/usr/bin/env python3
"""
NC-SVC-FR-019 - Picoclaw IPC Server (Phase 4.2 SOTA)
Gateway A2A na porta 18790, otimizado com Memory-Mapped Files (mmap)
para zerar gargalos de TCP no tráfego de payloads gigantescos.
"""

import os
import sys
import json
import mmap
import uuid
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format="%(asctime)s - PICOCLAW - %(levelname)s - %(message)s")
logger = logging.getLogger("PicoClaw")

PORT = 18790
# Global dict to keep references to the mmap objects so they aren't garbage collected
SHM_REGISTRY = {}

def create_shared_memory(payload_bytes: bytes) -> tuple:
    shm_id = f"Local\\NeoCortex_PicoClaw_{uuid.uuid4().hex}" if sys.platform == "win32" else f"/tmp/neocortex_picoclaw_{uuid.uuid4().hex}"
    size = len(payload_bytes)
    
    if sys.platform == "win32":
        # Windows Named Shared Memory
        shm = mmap.mmap(-1, size, tagname=shm_id)
        shm.write(payload_bytes)
        SHM_REGISTRY[shm_id] = shm
    else:
        # POSIX File-backed Shared Memory
        with open(shm_id, "wb") as f:
            f.write(payload_bytes)
        f = open(shm_id, "r+b")
        shm = mmap.mmap(f.fileno(), 0)
        SHM_REGISTRY[shm_id] = shm

    return shm_id, size

def read_shared_memory(shm_id: str, size: int) -> bytes:
    if shm_id in SHM_REGISTRY:
        shm = SHM_REGISTRY[shm_id]
        shm.seek(0)
        return shm.read()
    else:
        if sys.platform != "win32" and os.path.exists(shm_id):
            with open(shm_id, "r+b") as f:
                shm = mmap.mmap(f.fileno(), 0)
                SHM_REGISTRY[shm_id] = shm
                return shm.read()
        elif sys.platform == "win32":
            # Attempt to map existing tagname
            try:
                shm = mmap.mmap(-1, size, tagname=shm_id)
                shm.seek(0)
                data = shm.read()
                return data
            except Exception as e:
                logger.error(f"Cannot map {shm_id}: {e}")
    return b""

class PicoClawHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        res = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(res)))
        self.end_headers()
        self.wfile.write(res)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/" or parsed.path == "/health":
            self._send_json({"status": "online", "service": "picoclaw-ipc", "version": "4.2", "port": PORT})
            return
            
        elif parsed.path == "/mmap_read":
            qs = parse_qs(parsed.query)
            shm_id = qs.get("shm_id", [""])[0]
            size = int(qs.get("size", ["0"])[0])
            if not shm_id or size == 0:
                self._send_json({"error": "Missing shm_id or size mapping parameters"}, 400)
                return
                
            data = read_shared_memory(shm_id, size)
            if data:
                self._send_json({"success": True, "shm_id": shm_id, "size": size, "payload": data.decode("utf-8", errors="replace")})
            else:
                self._send_json({"error": "Failed to map memory block"}, 404)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        if parsed.path == "/mmap_write":
            try:
                shm_id, size = create_shared_memory(post_data)
                logger.info(f"Buffered {size} bytes to RAM pointer: {shm_id}")
                self._send_json({"success": True, "shm_id": shm_id, "size": size, "note": "Pass this ptr to bypassing heavy TCP"})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self._send_json({"error": "Not Found"}, 404)

def serve():
    server = HTTPServer(('0.0.0.0', PORT), PicoClawHandler)
    logger.info(f"PicoClaw A2A Gateway (Phase 4.2 IPC) listening on 0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Service shutting down")
        server.server_close()

if __name__ == "__main__":
    serve()