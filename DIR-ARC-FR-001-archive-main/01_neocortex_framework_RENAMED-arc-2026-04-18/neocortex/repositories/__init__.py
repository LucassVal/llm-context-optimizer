"""---
domain: "persistence"
layer: "infra"
type: "repository"
tags: ["init"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
Repository Pattern implementations for NeoCortex storage abstraction.
"""

from .base import (
    CortexRepository,
    LedgerRepository,
    LobeRepository,
    ProfileRepository,
    Repository,
)
from .file_system_repository import (
    FileSystemCortexRepository,
    FileSystemLedgerRepository,
    FileSystemLobeRepository,
    FileSystemProfileRepository,
    FileSystemRepositoryFactory,
)

__all__ = [
    "Repository",
    "CortexRepository",
    "LedgerRepository",
    "ProfileRepository",
    "LobeRepository",
    "FileSystemCortexRepository",
    "FileSystemLedgerRepository",
    "FileSystemProfileRepository",
    "FileSystemLobeRepository",
    "FileSystemRepositoryFactory",
]
