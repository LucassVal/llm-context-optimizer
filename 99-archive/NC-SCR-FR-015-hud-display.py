#!/usr/bin/env python3
"""NC-SCR-FR-015-hud-display.py - NeoCortex HUD Display Helper v1.0 - 2026-04-13
Chamado por NeoCortex_HUD.bat para exibir lobes e tickets formatados.
"""
import sys
import os
import re

# PYTHONPATH: TURBOQUANT_V42/01_neocortex_framework
BASE = os.path.dirname(os.path.abspath(__file__))
NC_ROOT = os.path.join(BASE, "01_neocortex_framework")
sys.path.insert(0, NC_ROOT)


def print_lobes():
    try:
        from neocortex.core.services.lobe_service import LobeService
        from neocortex.core.config import get_config
        cfg = get_config()
        svc = LobeService(cfg)
        active = svc.list_active_lobes()
        active_names = [lobe["name"] for lobe in active] if active else []

        all_lobes = {}
        if hasattr(svc, "get_all_lobes"):
            all_lobes = {lobe["name"]: lobe for lobe in svc.get_all_lobes()}

        TIERS = [
            ("TIER-0 CORTEX",   ["NC-CTX-FR-001"]),
            ("TIER-1 SSOT",     ["NC-LBE-FR-ARCHITECTURE-001", "NC-LBE-FR-MCP-001",
                                  "NC-LBE-FR-SECURITY-001", "NC-LBE-FR-DEVELOPMENT-001",
                                  "NC-LBE-FR-PROFILES-001", "NC-LBE-FR-WHITELABEL-001",
                                  "NC-LBE-FR-BENCHMARKS-001"]),
            ("TIER-2 CORE",     ["NC-LBE-FR-CORE-001", "NC-LBE-FR-CLI-001",
                                  "NC-LBE-FR-KNOWLEDGE-001", "NC-LBE-FR-LEGACY-001",
                                  "NC-LBE-FR-PULSE-001", "NC-LBE-FR-TESTING-001",
                                  "NC-LBE-FR-002"]),
            ("TIER-3 SUGERIDO", ["NC-LBE-FR-DEPLOYMENT-001", "NC-LBE-FR-DOCUMENTATION-001",
                                  "NC-LBE-FR-INTEGRATION-001", "NC-LBE-FR-MONITORING-001",
                                  "NC-LBE-FR-PERFORMANCE-001"]),
            ("TIER-4 DS/CC",    ["NC-LBE-DS-000", "NC-LBE-DS-001", "NC-LBE-DS-002",
                                  "NC-LBE-CC-001"]),
            ("TIER-5 INT",      ["NC-LBE-INT-001", "NC-LBE-INT-002", "NC-LBE-INT-003"]),
        ]

        for tier_name, prefixes in TIERS:
            print(f"  [{tier_name}]")
            for prefix in prefixes:
                match = next((n for n in active_names if prefix in n), None)
                if match:
                    lobe = all_lobes.get(match, {})
                    sz = lobe.get("size_chars", 0)
                    sz_str = f"{sz // 1024}KB" if sz > 1024 else f"{sz}B"
                    print(f"    [ON ] {match:<45} {sz_str}")
                else:
                    print(f"    [---] {prefix}")
            print()

    except Exception as e:
        print(f"  [ERRO] MCP offline ou lobe_service indisponivel: {e}")
        print()
        print("  LOBES ATIVOS CONHECIDOS:")
        fallback = [
            "NC-LBE-FR-ARCHITECTURE-001 (133KB)",
            "NC-LBE-FR-MCP-001         (29KB) ",
            "NC-LBE-FR-SECURITY-001    (14KB) ",
            "NC-LBE-INT-001-picoclaw   (12KB) ",
            "NC-LBE-INT-002-opencode   (12KB) ",
            "NC-LBE-INT-003-antigravity(10KB) ",
        ]
        for lobe in fallback:
            print(f"    [ON ] {lobe}")


def print_tickets():
    cfg_path = os.path.join(BASE, "DIR-DS-000-agent-config", "NC-CFG-DS-003-coordination.yaml")
    try:
        with open(cfg_path, encoding="utf-8") as f:
            content = f.read()
        for frente in ["DS-A", "DS-B"]:
            block_start = content.find(frente + ":")
            if block_start == -1:
                continue
            block = content[block_start:block_start + 400]
            m = re.search(r"tickets_ativos:\s*\[([^\]]*)\]", block)
            tickets = m.group(1).strip() if m else "N/A"
            wz = re.search(r'write_zone:\s*"([^"]+)"', block)
            zone = wz.group(1)[-30:] if wz else ""
            print(f"  {frente}: {tickets:<25} zone: ...{zone}")
    except Exception as e:
        print(f"  [ERRO] {e}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lobes"
    if cmd == "lobes":
        print_lobes()
    elif cmd == "tickets":
        print_tickets()
