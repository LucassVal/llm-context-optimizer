"""---
domain: "core"
layer: "core"
type: "file"
tags: ["init"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NeoCortex Adapters Module

Framework adapters for integrating with external systems (Mission Control, etc.).
"""

#  Camada 3  NC- named modules (R09: importlib obrigatrio para hyphens)
import importlib as _il

# Import hyphenated adapter modules via importlib
_adp = _il.import_module(
    ".NC-ADP-FR-001-mission-control", package="neocortex.core.adapters"
)

# Re-export public symbols
MissionControlAdapter = _adp.MissionControlAdapter
MissionControlConfig = _adp.MissionControlConfig
get_mission_control_adapter = _adp.get_mission_control_adapter

__all__ = [
    "MissionControlAdapter",
    "MissionControlConfig",
    "get_mission_control_adapter",
]
