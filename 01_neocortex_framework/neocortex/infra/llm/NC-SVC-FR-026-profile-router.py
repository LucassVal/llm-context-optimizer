# @UBL @UBL @SVC-FR | LEXICO: #INFRA
"""---
@Service  mcp domain: "infrastructure" layer: "infra" type: "ser
---
"""


#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

class ProfileRouter:
    """
    Decides between PRO, FLASH based on intent, domain and configuration.
    """

    def __init__(self, config_path: str = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-OP-001-operation-profiles.yaml"):
        self.config_path = Path(config_path)
        self.profiles = {}
        self.routing_rules = {}
        self.domain_routing = {}
        self._load_config()

    def _load_config(self):
        """Loads the profile configuration entry."""
        if not self.config_path.exists():
            logger.error(f"Profile configuration NOT FOUND at {self.config_path}")
            return

        try:
            with open(self.config_path, encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.profiles = {
                    "pro": config.get("pro", {}),
                    "flash": config.get("flash", {}),
                    "auto": config.get("auto", {})
                }
                auto_cfg = self.profiles.get("auto", {})
                self.routing_rules = auto_cfg.get("routing_rules", {})
                self.domain_routing = self.routing_rules.get("domain_routing", {})
                logger.info("Profile configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load profile config: {e}")

    def resolve_profile(self, intent: str, domain: str | None = None) -> dict[str, Any]:
        """
        Resolves the appropriate profile (PRO or FLASH) based on input.
        """
        # 1. Check Domain Precedence
        if domain:
            if domain in self.domain_routing.get("pro_domains", []):
                logger.info(f"Domain '{domain}' routed to PRO profile.")
                return self.profiles["pro"]
            if domain in self.domain_routing.get("flash_domains", []):
                logger.info(f"Domain '{domain}' routed to FLASH profile.")
                return self.profiles["flash"]

        # 2. Intent Classification (Keyword based)
        intent_lower = intent.lower()

        pro_keywords = self.routing_rules.get("route_to_pro", {}).get("keywords", [])
        if any(kw in intent_lower for kw in pro_keywords):
            logger.info("Intent keyword matched for PRO profile.")
            return self.profiles["pro"]

        flash_keywords = self.routing_rules.get("route_to_flash", {}).get("keywords", [])
        if any(kw in intent_lower for kw in flash_keywords):
            logger.info("Intent keyword matched for FLASH profile.")
            return self.profiles["flash"]

        # 3. Default Fallback
        default = self.routing_rules.get("default_profile", "pro")
        logger.info(f"No match found. Falling back to default profile: {default}")
        return self.profiles.get(default, self.profiles.get("pro"))

if __name__ == "__main__":
    # Quick sanity check
    logging.basicConfig(level=logging.INFO)
    router = ProfileRouter()

    test_cases = [
        {"intent": "planejar nova arquitetura", "domain": None},
        {"intent": "corrigir bug no script", "domain": "development"},
        {"intent": "auditoria de segurança", "domain": "security"},
        {"intent": "fazer commit", "domain": None}
    ]

    for case in test_cases:
        p = router.resolve_profile(case["intent"], case["domain"])
        print(f"CASE: {case} -> PROFILE: {p.get('label', 'UNKNOWN')}")
