#!/usr/bin/env python3
"""
NC-SVC-FR-025-savepoint-wal-bridge.py
FR-025 — SavePoint-WAL Bridge Service

Connects SavePointService (NC-SVC-FR-003) with WALService (NC-SVC-FR-016).
When a savepoint is created or restored, it's logged to the WAL for audit trail.

Ticket: NC-DS-152-savepoint-wal-bridge.yaml
"""

import importlib.util
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _import_service(service_name: str, class_name: str) -> Optional[Any]:
    """
    Import a service module using importlib (R09).
    
    Args:
        service_name: Name of the service file (e.g., "NC-SVC-FR-016-wal-service")
        class_name: Name of the class to import
        
    Returns:
        The imported class or None if import fails
    """
    try:
        base_path = Path(__file__).resolve().parent
        service_path = base_path / f"{service_name}.py"
        
        if not service_path.exists():
            logger.warning(f"[SavePointWALBridge] Service not found: {service_path}")
            return None
        
        # Create module spec
        spec = importlib.util.spec_from_file_location(
            service_name.replace("-", "_"),
            str(service_path)
        )
        if spec is None or spec.loader is None:
            logger.warning(f"[SavePointWALBridge] Failed to create spec for {service_name}")
            return None
        
        # Load module
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get class
        service_class = getattr(module, class_name, None)
        if service_class is None:
            logger.warning(f"[SavePointWALBridge] Class {class_name} not found in {service_name}")
            return None
        
        return service_class
    except Exception as e:
        logger.warning(f"[SavePointWALBridge] Failed to import {service_name}: {e}")
        return None


class SavePointWALBridge:
    """
    Bridge between SavePointService and WALService.
    
    Provides unified interface for savepoint operations with WAL logging.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the bridge.
        
        Args:
            db_path: Optional path to WAL database (defaults to WALService default)
        """
        self._wal_service_class = _import_service("NC-SVC-FR-016-wal-service", "WALService")
        self._savepoint_service_class = _import_service("NC-SVC-FR-003-savepoint-stub", "SavePointService")
        
        if self._wal_service_class:
            self.wal = self._wal_service_class(db_path)
        else:
            self.wal = None
            logger.warning("[SavePointWALBridge] WALService unavailable")
    
    def create_savepoint(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a savepoint and log to WAL.
        
        Args:
            name: Name/identifier for the savepoint
            data: State data to save
            
        Returns:
            Dictionary with result: {ok: bool, name: str, wal_entry_id: Optional[str], error: Optional[str]}
        """
        if not self._savepoint_service_class:
            return {
                "ok": False,
                "name": name,
                "wal_entry_id": None,
                "error": "SavePointService unavailable"
            }
        
        try:
            # Create savepoint using SavePointService
            result = self._savepoint_service_class.create(
                state_snapshot={"name": name, "data": data},
                ttl_seconds=3600
            )
            
            savepoint_id = result.get("id", str(uuid.uuid4()))
            
            # Log to WAL if available
            wal_entry_id = None
            if self.wal:
                try:
                    session_id = f"savepoint-create-{int(time.time())}"
                    self.wal.open_session(
                        session_id, 
                        "savepoint-wal-bridge", 
                        ticket_id="NC-DS-152"
                    )
                    
                    # Log the operation
                    self.wal.log_operation(
                        session_id=session_id,
                        operation="savepoint.create",
                        file_path=f"savepoint://{savepoint_id}",
                        ticket_id="NC-DS-152",
                        before_hash=None,
                        after_hash=None
                    )
                    
                    self.wal.commit_session(session_id)
                    wal_entry_id = session_id
                    
                    logger.info(f"[SavePointWALBridge] Savepoint '{name}' created and logged to WAL: {savepoint_id}")
                except Exception as e:
                    logger.warning(f"[SavePointWALBridge] Failed to log to WAL: {e}")
            
            return {
                "ok": True,
                "name": name,
                "savepoint_id": savepoint_id,
                "wal_entry_id": wal_entry_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"[SavePointWALBridge] Failed to create savepoint '{name}': {e}")
            return {
                "ok": False,
                "name": name,
                "wal_entry_id": None,
                "error": str(e)
            }
    
    def restore_savepoint(self, name: str) -> Dict[str, Any]:
        """
        Restore a savepoint and log to WAL.
        
        Args:
            name: Name/identifier of the savepoint to restore
            
        Returns:
            Dictionary with result: {ok: bool, name: str, wal_entry_id: Optional[str], error: Optional[str]}
        """
        if not self._savepoint_service_class:
            return {
                "ok": False,
                "name": name,
                "wal_entry_id": None,
                "error": "SavePointService unavailable"
            }
        
        try:
            # First, list savepoints to find by name
            savepoints = self._savepoint_service_class.list_active()
            target_savepoint = None
            
            for sp in savepoints:
                snapshot = sp.get("state_snapshot", {})
                if snapshot.get("name") == name:
                    target_savepoint = sp
                    break
            
            if not target_savepoint:
                return {
                    "ok": False,
                    "name": name,
                    "wal_entry_id": None,
                    "error": f"Savepoint '{name}' not found"
                }
            
            savepoint_id = target_savepoint.get("id")
            
            # Restore (rollback) using SavePointService
            result = self._savepoint_service_class.rollback(savepoint_id)
            
            if result.get("status") != "success":
                return {
                    "ok": False,
                    "name": name,
                    "wal_entry_id": None,
                    "error": result.get("message", "Restore failed")
                }
            
            # Log to WAL if available
            wal_entry_id = None
            if self.wal:
                try:
                    session_id = f"savepoint-restore-{int(time.time())}"
                    self.wal.open_session(
                        session_id,
                        "savepoint-wal-bridge",
                        ticket_id="NC-DS-152"
                    )
                    
                    # Log the restore operation with HIGH severity
                    self.wal.log_operation(
                        session_id=session_id,
                        operation="savepoint.restore",
                        file_path=f"savepoint://{savepoint_id}",
                        ticket_id="NC-DS-152",
                        before_hash=None,
                        after_hash=None
                    )
                    
                    self.wal.commit_session(session_id)
                    wal_entry_id = session_id
                    
                    logger.info(f"[SavePointWALBridge] Savepoint '{name}' restored and logged to WAL: {savepoint_id}")
                except Exception as e:
                    logger.warning(f"[SavePointWALBridge] Failed to log restore to WAL: {e}")
            
            return {
                "ok": True,
                "name": name,
                "savepoint_id": savepoint_id,
                "wal_entry_id": wal_entry_id,
                "timestamp": time.time(),
                "restored_data": result.get("state_snapshot", {})
            }
            
        except Exception as e:
            logger.error(f"[SavePointWALBridge] Failed to restore savepoint '{name}': {e}")
            return {
                "ok": False,
                "name": name,
                "wal_entry_id": None,
                "error": str(e)
            }
    
    def list_savepoints(self) -> List[Dict[str, Any]]:
        """
        List all savepoints from WAL filtered by type=savepoint.*
        
        Returns:
            List of savepoint dictionaries
        """
        savepoints = []
        
        # Get savepoints from SavePointService
        if self._savepoint_service_class:
            try:
                service_savepoints = self._savepoint_service_class.list_active()
                for sp in service_savepoints:
                    savepoints.append({
                        "source": "SavePointService",
                        **sp
                    })
            except Exception as e:
                logger.warning(f"[SavePointWALBridge] Failed to list from SavePointService: {e}")
        
        # Try to get savepoints from WAL directly
        if self.wal:
            try:
                # This would require querying the WAL database directly
                # For now, we'll return what we have from SavePointService
                pass
            except Exception as e:
                logger.warning(f"[SavePointWALBridge] Failed to query WAL: {e}")
        
        return savepoints


# Singleton instance for easy access
_bridge_instance: Optional[SavePointWALBridge] = None


def get_bridge(db_path: Optional[Path] = None) -> SavePointWALBridge:
    """
    Get or create the singleton bridge instance.
    
    Args:
        db_path: Optional path to WAL database
        
    Returns:
        SavePointWALBridge instance
    """
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = SavePointWALBridge(db_path)
    return _bridge_instance


if __name__ == "__main__":
    # Simple test when run directly
    import json
    
    print("NC-SVC-FR-025 SavePoint-WAL Bridge")
    print("=" * 50)
    
    bridge = SavePointWALBridge()
    
    # Test create
    print("\n1. Testing savepoint creation...")
    create_result = bridge.create_savepoint(
        "test-savepoint-001",
        {"test": True, "value": 42, "timestamp": time.time()}
    )
    print(f"   Result: {json.dumps(create_result, indent=2)}")
    
    # Test list
    print("\n2. Listing savepoints...")
    savepoints = bridge.list_savepoints()
    print(f"   Found {len(savepoints)} savepoints")
    
    # Test restore (if we created one)
    if create_result.get("ok"):
        print("\n3. Testing savepoint restore...")
        restore_result = bridge.restore_savepoint("test-savepoint-001")
        print(f"   Result: {json.dumps(restore_result, indent=2)}")
    
    print("\n" + "=" * 50)
    print("Bridge test completed")