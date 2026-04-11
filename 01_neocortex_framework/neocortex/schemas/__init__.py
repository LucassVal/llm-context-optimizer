#!/usr/bin/env python3
"""
JSON Schemas for NeoCortex data contracts.
"""

import json
from pathlib import Path

# Load schemas
SCHEMAS_DIR = Path(__file__).parent

LEDGER_SCHEMA_PATH = SCHEMAS_DIR / "ledger_schema.json"
A2A_MESSAGE_SCHEMA_PATH = SCHEMAS_DIR / "a2a_message_schema.json"


def load_schema(schema_path: Path) -> dict:
    """Load a JSON schema from file."""
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to load schema from {schema_path}: {e}")


# Load available schemas
try:
    LEDGER_SCHEMA = load_schema(LEDGER_SCHEMA_PATH)
except ValueError:
    LEDGER_SCHEMA = None

try:
    A2A_MESSAGE_SCHEMA = load_schema(A2A_MESSAGE_SCHEMA_PATH)
except ValueError:
    A2A_MESSAGE_SCHEMA = None

__all__ = ["LEDGER_SCHEMA", "A2A_MESSAGE_SCHEMA", "load_schema"]
