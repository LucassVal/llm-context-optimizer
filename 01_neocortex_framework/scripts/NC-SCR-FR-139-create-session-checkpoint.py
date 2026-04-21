#!/usr/bin/env python3
"""
Create a session checkpoint for end of day.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add neocortex_framework to path
neocortex_path = Path(__file__).parent.parent  # 01_neocortex_framework
sys.path.insert(0, str(neocortex_path))

try:
    from neocortex.core import get_checkpoint_service
except ImportError as e:
    print(f"ERROR: Cannot import neocortex.core: {e}")
    sys.exit(1)


def main():
    checkpoint_service = get_checkpoint_service()
    checkpoint_id = f"CP-SESSION-END-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

    checkpoint_result = checkpoint_service.set_current_checkpoint(
        checkpoint_id=checkpoint_id,
        lobe_id="NC-LBE-FR-002-claude-assistant",
        description="Ciclo 3 concluído — sessão encerrada 2026-04-16 | Handoffs:7 | Catalog:529PY,403YAML | PicoClaw:stopped | MC:active | MCP:started_not_responding | Protocol T0:implemented",
    )

    if checkpoint_result.get("success"):
        print(f"Checkpoint criado: {checkpoint_id}")
        print(f"Result: {checkpoint_result}")
        return 0
    else:
        print(f"Falha ao criar checkpoint: {checkpoint_result.get('error', 'Unknown')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
