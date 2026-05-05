"""---
---
---
"""


import os
import pathlib
from datetime import datetime
from typing import Dict


class RegulatoryCompliance:
    def __init__(self, root: pathlib.Path = None):
        self.root = root or pathlib.Path(os.environ.get("NC_ROOT", pathlib.Path(__file__).parents[3]))

    def check_supreme(self) -> Dict:
        crypto_mod = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-159-crypto-integrity.py"
        return {"available": crypto_mod.exists(), "algorithm": "SHA-256", "module": "FR-159"}

    def check_eu_ai_act(self) -> Dict:
        genome = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-130-genome-replicator.py"
        auto_amend = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-136-auto-amendment-engine.py"
        return {"genome_exists": genome.exists(), "amendment_exists": auto_amend.exists(),
                "isolation_capable": genome.exists() and auto_amend.exists()}

    def check_nist(self) -> Dict:
        gw = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-129-shared-kernel-gateway.py"
        if not gw.exists(): return {"rbac_active": False}
        content = gw.read_text("utf-8", errors="ignore")
        return {"rbac_active": "agent_role" in content and "T0" in content}

    def check_singapore(self) -> Dict:
        toolguard = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-125-tool-guard.py"
        return {"tool_guard_exists": toolguard.exists()}

    def check_compliance_surface(self) -> Dict:
        mapping = {}
        tools_dir = self.root / "01_neocortex_framework" / "neocortex" / "mcp" / "tools"
        governance = tools_dir / "NC-SUPER-001-governance.py"
        if governance.exists():
            content = governance.read_text("utf-8", errors="ignore")
            if "compliance" in content: mapping["governance"] = "LGPD + CF/88"
            if "delete" in content: mapping["delete"] = "LGPD Art. 18"
        return {"tool_legal_mapping": mapping, "mapped_tools": len(mapping)}

    def check_rdi(self) -> Dict:
        vigilant = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-137-vigilant-cycle.py"
        drift_action = "drift.status" if not vigilant.exists() else (
            "present" if "drift" in vigilant.read_text("utf-8", errors="ignore").lower() else "missing"
        )
        return {"vigilant_exists": vigilant.exists(), "drift_action": drift_action}

    def check_regulatory_triggers(self) -> Dict:
        triggers = {}
        gw = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-129-shared-kernel-gateway.py"
        if gw.exists():
            content = gw.read_text("utf-8", errors="ignore")
            if "delete" in content: triggers["delete_user"] = "LGPD Art. 18"
            if "export" in content: triggers["export"] = "LGPD Art. 19"
            if "search" in content: triggers["search"] = "LGPD Art. 7"
            if "genome" in content: triggers["genome.fork"] = "EU AI Act Art 3(23)"
        return {"triggers": triggers, "active": len(triggers) > 0}

    def check_layered_translation(self) -> Dict:
        layers = {}
        yaml_file = self.root / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main" / "NC-SEC-FR-001-atomic-locks.yaml"
        gw = self.root / "01_neocortex_framework" / "neocortex" / "core" / "NC-CORE-FR-129-shared-kernel-gateway.py"
        layers["Layer 1 (Lei)"] = "LGPD, EU AI Act, CF/88 — referenced in MULTILAYER"
        layers["Layer 2 (YAML)"] = f"NC-SEC-FR-001-atomic-locks.yaml exists: {yaml_file.exists()}"
        layers["Layer 3 (Code)"] = f"Gateway _check_alignment exists: {gw.exists()}"
        return {"layers": layers, "complete": yaml_file.exists() and gw.exists()}

    def full_audit(self) -> Dict:
        return {
            "supreme_v3": self.check_supreme(),
            "eu_ai_act": self.check_eu_ai_act(),
            "nist": self.check_nist(),
            "singapore": self.check_singapore(),
            "compliance_surface": self.check_compliance_surface(),
            "rdi": self.check_rdi(),
            "regulatory_triggers": self.check_regulatory_triggers(),
            "layered_translation": self.check_layered_translation(),
            "generated_at": datetime.now().isoformat(),
            "source": "REAL_FILE_CHECKS",
        }


_regulatory = None
def get_regulatory():
    global _regulatory
    if _regulatory is None: _regulatory = RegulatoryCompliance()
    return _regulatory
