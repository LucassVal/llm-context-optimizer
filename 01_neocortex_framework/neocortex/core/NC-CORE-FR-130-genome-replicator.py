# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
"""---
@Replicator NC-CORE-FR-130-genome-replicator mcp NC-CORE-FR-130-genome-replicator.py — DNA/RNA + Fo
---
"""


import hashlib
import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class GenomeReplicator:
    """DNA/RNA replication system — fork with inheritance + sandbox."""

    def __init__(self, root: Path | None = None):
        import os as _os
        self.root = root or Path(_os.environ.get("NC_ROOT", Path(__file__).parents[3]))

    # ── DNA (Imutável pelo child) ─────────────────────────────

    def create_dna(self, instance_name: str = "") -> dict[str, Any]:
        """Generate DNA.json — structural identity. Imutável para o child."""
        dna = {
            "genome_version": "1.0",
            "species": "NeoCortex MCP Framework",
            "instance_name": instance_name or f"nc-instance-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "parent_lineage": self._get_lineage(),
            "immutable_genes": {
                "atomic_locks": "NC-SEC-FR-001-atomic-locks.yaml",
                "constitution": "NC-LBE-FR-CONSTITUTION-001.mdc",
                "tool_guard": "NC-CORE-FR-125-tool-guard.py",
                "gateway": "NC-CORE-FR-129-shared-kernel-gateway.py",
                "step_zero": "NC-CORE-FR-123-regression-service.py",
                "wal_service": "NC-SVC-FR-016-wal-service.py",
                "crypto_hub": "NC-SVC-FR-017-crypto-hub.py",
            },
            "structure": {
                "required_dirs": [
                    ".agents/rules/",
                    "01_neocortex_framework/neocortex/",
                    "02_memory_lobes/",
                    "DIR-DS-001-tickets/",
                    "DIR-DS-002-audit-logs/",
                ],
                "required_files": [
                    "NC-LBE-FR-CONSTITUTION-001.mdc",
                    "NC-ARC-FR-002-architecture-blueprint.yaml",
                ],
            },
            "checksum": "",  # filled on save
        }
        return dna

    def save_dna(self, dna: dict[str, Any], target_dir: Path) -> Path:
        """Save DNA.json — includes SHA-256 checksum."""
        dna_file = target_dir / "DNA.json"
        content = json.dumps(dna, indent=2, ensure_ascii=False)
        dna["checksum"] = hashlib.sha256(content.encode()).hexdigest()[:16]
        content = json.dumps(dna, indent=2, ensure_ascii=False)  # regenerate with checksum
        dna_file.write_text(content, encoding="utf-8")
        logger.info(f"[Genome] DNA saved: {dna_file} (checksum={dna['checksum']})")
        return dna_file

    # ── RNA (Mutável pelo próprio agente) ──────────────────────

    def create_rna(self) -> dict[str, Any]:
        """Generate RNA.json — runtime state. Mutável pelo child."""
        return {
            "mode": "sandbox_bsl1",
            "lifecycle_stage": "newborn",
            "objective": "passar nos testes de conformidade",
            "capabilities": [],
            "parent_id": "",
            "started_at": datetime.now().isoformat(),
            "heartbeat": datetime.now().isoformat(),
            "ttl_seconds": 300,  # 5 minutos no sandbox
        }

    def save_rna(self, rna: dict[str, Any], target_dir: Path) -> Path:
        """Save RNA.json."""
        rna_file = target_dir / "RNA.json"
        rna_file.write_text(json.dumps(rna, indent=2, ensure_ascii=False), encoding="utf-8")
        return rna_file

    # ── FORK: criar child ──────────────────────────────────────

    def fork(
        self,
        child_name: str = "",
        bsl_level: int = 1,
        inherit_policies: bool = True,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Create a child instance via fork.

        Args:
            child_name: Nome da instância filha
            bsl_level: Biosafety level (1-4)
            inherit_policies: Se True, herda todas as políticas do parent

        Returns:
            (success, report)
        """
        ts = datetime.now().isoformat()
        sandbox_dir = self.root / ".neocortex" / "sandbox"
        sandbox_dir.mkdir(parents=True, exist_ok=True)

        child_id = child_name or f"nc-child-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        child_dir = sandbox_dir / child_id

        report = {
            "action": "fork",
            "child_id": child_id,
            "child_dir": str(child_dir),
            "bsl_level": bsl_level,
            "timestamp": ts,
            "checks": {},
        }

        # 1. VALIDATE: check R0 (max 5/hour)
        recent_forks = list(sandbox_dir.glob("nc-child-*"))
        recent_1h = [d for d in recent_forks if (time.time() - d.stat().st_mtime) < 3600]
        if len(recent_1h) >= 5:
            report["success"] = False
            report["error"] = f"R0 LIMIT: max 5 forks/hora. {len(recent_1h)} já realizados."
            return False, report

        # 2. CREATE sandbox directory
        child_dir.mkdir(parents=True, exist_ok=False)
        report["checks"]["directory_created"] = True

        # 3. COPY DNA (inherited)
        dna = self.create_dna(child_id)
        self.save_dna(dna, child_dir)
        report["checks"]["dna_saved"] = True
        report["dna_checksum"] = dna["checksum"]

        # 4. COPY RNA (fresh, mutable)
        rna = self.create_rna()
        rna["parent_id"] = self._get_instance_id()
        rna["mode"] = f"sandbox_bsl{bsl_level}"
        self.save_rna(rna, child_dir)
        report["checks"]["rna_saved"] = True

        # 5. COPY constitution + atomic locks (policy inheritance)
        if inherit_policies:
            self._copy_policies(child_dir)
            report["checks"]["policies_inherited"] = True

        # 6. COPY essential lobes
        self._copy_essential_lobes(child_dir)
        report["checks"]["lobes_inherited"] = True

        # 7. SHA-256 integrity check
        integrity_ok = self._verify_integrity(child_dir, dna)
        report["checks"]["integrity_ok"] = integrity_ok

        # 8. APPLY sandbox restrictions (BSL level)
        self._apply_sandbox(child_dir, bsl_level)
        report["checks"]["sandbox_applied"] = f"BSL-{bsl_level}"

        # 9. WAL lineage record
        self._log_fork_to_wal(child_id, dna["checksum"])

        report["success"] = True
        logger.info(f"[Genome] Fork complete: {child_id} (BSL-{bsl_level})")
        return True, report

    # ── SANDBOX: aplicar restrições ────────────────────────────

    def _apply_sandbox(self, child_dir: Path, bsl_level: int) -> None:
        """Apply biosafety restrictions."""
        restrictions = {
            1: {"network": False, "filesystem": "read-write", "ttl": 300},
            2: {"network": "localhost_only", "filesystem": "read-write", "ttl": 1800},
            3: {"network": False, "filesystem": "read-only", "ttl": 3600, "air_gapped": True},
            4: {"network": False, "filesystem": "none", "ttl": 7200, "theoretical_only": True},
        }
        cfg = restrictions.get(bsl_level, restrictions[1])
        sandbox_cfg = child_dir / ".sandbox.json"
        sandbox_cfg.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

        if cfg.get("air_gapped"):
            # Firewall rule placeholder
            logger.info(f"[Genome] BSL-{bsl_level} air-gapped sandbox: {child_dir}")

    def _verify_integrity(self, child_dir: Path, dna: dict[str, Any]) -> bool:
        """Verify child integrity via SHA-256."""
        try:
            dna_file = child_dir / "DNA.json"
            if not dna_file.exists():
                return False
            content = dna_file.read_text(encoding="utf-8")
            expected = dna.get("checksum", "")
            actual = hashlib.sha256(content.encode()).hexdigest()[:16]
            return expected == actual
        except Exception:
            return False

    # ── HELPERS ─────────────────────────────────────────────────

    def _get_lineage(self) -> list[str]:
        """Get lineage from current instance."""
        lineage = [self._get_instance_id()]
        return lineage

    def _get_instance_id(self) -> str:
        """Get current instance ID."""
        dna_file = self.root / ".neocortex" / "DNA.json"
        if dna_file.exists():
            try:
                dna = json.loads(dna_file.read_text(encoding="utf-8"))
                return dna.get("instance_name", "unknown")
            except Exception:
                pass
        return "nc-parent-root"

    def _copy_policies(self, child_dir: Path) -> None:
        """Copy atomic locks + constitution to child."""
        policies = [
            "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml",
            "01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-CFG-FR-001-agent-policy-template.yaml",
        ]
        for p in policies:
            src = self.root / p
            if src.exists():
                dst = child_dir / Path(p).name
                shutil.copy2(src, dst)

    def _copy_essential_lobes(self, child_dir: Path) -> None:
        """Copy constitution + evolution lobes to child."""
        lobes = [
            "02_memory_lobes/01_framework/NC-LBE-FR-CONSTITUTION-001.mdc",
            "02_memory_lobes/01_framework/NC-LBE-FR-GOVERNANCE-001.mdc",
        ]
        lobes_dir = child_dir / "02_memory_lobes" / "inherited"
        lobes_dir.mkdir(parents=True, exist_ok=True)
        for l in lobes:
            src = self.root / l
            if src.exists():
                dst = lobes_dir / Path(l).name
                shutil.copy2(src, dst)

    def _log_fork_to_wal(self, child_id: str, dna_checksum: str) -> None:
        """Log fork event to WAL."""
        wal_dir = self.root / "DIR-DS-002-audit-logs"
        wal_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "event": "fork",
            "child_id": child_id,
            "parent_id": self._get_instance_id(),
            "dna_checksum": dna_checksum,
            "timestamp": datetime.now().isoformat(),
        }
        wal_file = wal_dir / f"NC-WAL-REPLICATION-{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(wal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def list_children(self) -> list[dict[str, Any]]:
        """List all children in sandbox."""
        sandbox_dir = self.root / ".neocortex" / "sandbox"
        if not sandbox_dir.exists():
            return []
        children = []
        for d in sandbox_dir.iterdir():
            if d.is_dir() and d.name.startswith("nc-child-"):
                dna_file = d / "DNA.json"
                rna_file = d / "RNA.json"
                sandbox_cfg = d / ".sandbox.json"
                child = {
                    "id": d.name,
                    "path": str(d),
                    "created": datetime.fromtimestamp(d.stat().st_mtime).isoformat(),
                }
                if dna_file.exists():
                    child["dna"] = dna_file.name
                if rna_file.exists():
                    try:
                        rna = json.loads(rna_file.read_text(encoding="utf-8"))
                        child["mode"] = rna.get("mode", "unknown")
                        child["ttl"] = rna.get("ttl_seconds", 0)
                    except Exception:
                        pass
                if sandbox_cfg.exists():
                    try:
                        cfg = json.loads(sandbox_cfg.read_text(encoding="utf-8"))
                        child["bsl"] = (cfg.get("air_gapped", False) and 3) or 1
                    except Exception:
                        pass
                children.append(child)
        return children


# Singleton
_genome_instance: GenomeReplicator | None = None


def get_genome() -> GenomeReplicator:
    global _genome_instance
    if _genome_instance is None:
        _genome_instance = GenomeReplicator()
    return _genome_instance
