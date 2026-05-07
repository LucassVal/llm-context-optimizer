#!/usr/bin/env python3
"""NC-MDC-FR-001 — MDC Loader stub
Injects governance rules from .mdc lobe files into FastMCP server context.
Minimal implementation — full .mdc parser deferred to NC-DS-MDC-PARSER.
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_mdc_rules(root: Path | None = None) -> dict[str, Any]:
    """Load governance rules from .mdc files in 02_memory_lobes/.
    Returns dict of rule_name -> content suitable for injection.
    """
    if root is None:
        root = Path(__file__).parent.parent.parent.parent
    lobes_dir = root / "02_memory_lobes"
    if not lobes_dir.exists():
        return {}

    rules = {}
    for mdc_file in sorted(lobes_dir.rglob("*.mdc")):
        if "archive" in str(mdc_file).lower() or "deprecated" in str(mdc_file).lower():
            continue
        try:
            content = mdc_file.read_text(encoding="utf-8", errors="replace")
            key = mdc_file.stem
            rules[key] = content
        except Exception:
            pass

    logger.info(f"MDC Loader: {len(rules)} rules carregadas de {lobes_dir}")
    return rules


def inject_rules_into_fastmcp(server: Any) -> bool:
    """Inject governance rules into the FastMCP server's metadata/instructions.
    Uses NC-CFG-FR-010 canonical order for KV cache stability.
    Returns True if injection succeeded.
    """
    try:
        rules = load_mdc_rules()
        if not rules:
            logger.warning("MDC Loader: nenhuma regra encontrada para injetar")
            return False

        # NC-CFG-FR-010: canonical prefix order for KV cache stability
        canonical_order = _load_canonical_order()
        ordered_keys = [k for k in canonical_order if k in rules]
        remaining = [k for k in rules if k not in canonical_order]
        ordered_keys.extend(sorted(remaining))

        top_rules = []
        for key in ordered_keys[:15]:
            content = rules[key]
            top_rules.append(content[:800])

        if hasattr(server, "instructions"):
            existing = getattr(server, "instructions", "") or ""
            injected = "\n\n--- Governance Rules (MDC - Canonical Order) ---\n" + "\n---\n".join(top_rules)
            try:
                server.instructions = (existing + injected)[:8192]
            except Exception:
                pass
            logger.info(f"MDC Loader: {len(ordered_keys)} regras injetadas em ordem canônica")
            return True
    except Exception as e:
        logger.warning(f"MDC Loader: falha ao injetar regras — {e}")
    return False


def _load_canonical_order() -> list[str]:
    """Load canonical lobe order from NC-CFG-FR-010-stable-prefix.yaml."""
    try:
        import yaml
        cfg_path = Path(__file__).parent.parent.parent.parent / "07-agent-config" / "NC-CFG-FR-010-stable-prefix.yaml"
        if not cfg_path.exists():
            return []
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        order = []
        for section in ["constitution", "semantics", "governance", "integrations"]:
            items = cfg.get(section, [])
            order.extend([i for i in items if isinstance(i, str)])
        return order
    except Exception:
        return []
