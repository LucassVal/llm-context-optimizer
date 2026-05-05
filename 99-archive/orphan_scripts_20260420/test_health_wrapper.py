#!/usr/bin/env python3
"""
Quick test for health wrapper.
"""

import sys
import json
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from NC_SCR_FR_098_health_wrapper import (
    load_health_service,
    load_wal_service,
)


def test_load():
    print("Testing load_health_service...")
    health = load_health_service()
    print(f"Health module: {health}")
    print("Testing get_health_status...")
    status = health.get_health_status()
    print(json.dumps(status, indent=2))
    print("Testing load_wal_service...")
    WALService = load_wal_service()
    if WALService:
        print(f"WALService class: {WALService}")
        wal = WALService()
        print(f"WAL instance: {wal}")
    else:
        print("WAL service not loaded (expected if missing)")
    print("Load tests passed.")


if __name__ == "__main__":
    test_load()
