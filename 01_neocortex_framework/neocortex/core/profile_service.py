#!/usr/bin/env python3
"""
Profile Service - Business logic for profile operations.

This service encapsulates business logic for profile operations,
using repository interfaces for storage abstraction.
"""

import json
from typing import Dict, Any, List, Optional
from ..repositories import ProfileRepository


class ProfileService:
    """Service for profile-related business logic."""

    def __init__(self, repository: Optional[ProfileRepository] = None):
        """
        Initialize profile service.

        Args:
            repository: Profile repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemProfileRepository.
        """
        if repository is None:
            from ..repositories import FileSystemProfileRepository

            self.repository = FileSystemProfileRepository()
        else:
            self.repository = repository

    def list_profiles(self) -> Dict[str, Any]:
        """
        List all available profiles with metadata.

        Returns:
            Dictionary with profile list and metadata
        """
        profile_ids = self.repository.list_profiles()

        profiles = []
        for profile_id in profile_ids:
            profile = self.repository.read_profile(profile_id)
            if profile:
                metadata = self._extract_profile_metadata(profile_id, profile)
                profiles.append({"id": profile_id, **metadata})

        return {
            "profiles": profiles,
            "total": len(profiles),
            "access_levels": self._summarize_access_levels(profiles),
        }

    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get a specific profile with content and metadata.

        Args:
            profile_id: ID of the profile

        Returns:
            Profile dictionary with content and metadata
        """
        profile = self.repository.read_profile(profile_id)

        if not profile:
            return {
                "id": profile_id,
                "exists": False,
                "error": f"Profile '{profile_id}' not found",
            }

        metadata = self._extract_profile_metadata(profile_id, profile)

        return {"id": profile_id, "exists": True, "profile": profile, **metadata}

    def create_profile(
        self, profile_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new profile.

        Args:
            profile_id: ID of the profile
            profile_data: Profile data dictionary

        Returns:
            Creation result dictionary
        """
        # Validate profile ID
        if not profile_id.strip():
            return {"success": False, "error": "Profile ID cannot be empty"}

        # Check if profile already exists
        if self.repository.exists(profile_id):
            return {"success": False, "error": f"Profile '{profile_id}' already exists"}

        # Validate profile data
        validation_result = self._validate_profile_data(profile_data)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": f"Invalid profile data: {validation_result['errors']}",
            }

        # Ensure required fields
        if "access_level" not in profile_data:
            profile_data["access_level"] = "developer"

        if "created_at" not in profile_data:
            from datetime import datetime

            profile_data["created_at"] = datetime.utcnow().isoformat() + "Z"

        # Write profile
        success = self.repository.write_profile(profile_id, profile_data)

        if success:
            metadata = self._extract_profile_metadata(profile_id, profile_data)

            return {
                "success": True,
                "message": f"Profile '{profile_id}' created successfully",
                "id": profile_id,
                "metadata": metadata,
                "access_level": profile_data["access_level"],
            }
        else:
            return {
                "success": False,
                "error": f"Failed to create profile '{profile_id}'",
            }

    def update_profile(
        self, profile_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing profile.

        Args:
            profile_id: ID of the profile
            profile_data: Updated profile data

        Returns:
            Update result dictionary
        """
        # Check if profile exists
        existing_profile = self.repository.read_profile(profile_id)
        if not existing_profile:
            return {"success": False, "error": f"Profile '{profile_id}' does not exist"}

        # Validate profile data
        validation_result = self._validate_profile_data(profile_data)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": f"Invalid profile data: {validation_result['errors']}",
            }

        # Merge with existing data (preserve fields not in update)
        merged_data = {**existing_profile, **profile_data}

        # Update timestamp
        from datetime import datetime

        merged_data["updated_at"] = datetime.utcnow().isoformat() + "Z"

        # Write updated profile
        success = self.repository.write_profile(profile_id, merged_data)

        if success:
            metadata = self._extract_profile_metadata(profile_id, merged_data)

            return {
                "success": True,
                "message": f"Profile '{profile_id}' updated successfully",
                "id": profile_id,
                "metadata": metadata,
                "access_level": merged_data.get("access_level", "developer"),
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update profile '{profile_id}'",
            }

    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Delete a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            Deletion result dictionary
        """
        # Note: This implementation assumes the repository supports deletion.
        # FileSystemProfileRepository doesn't have delete method yet.
        # For now, we'll archive instead of delete.

        profile = self.repository.read_profile(profile_id)
        if not profile:
            return {"success": False, "error": f"Profile '{profile_id}' does not exist"}

        # Archive profile data
        from datetime import datetime

        archive_data = {
            **profile,
            "archived_at": datetime.utcnow().isoformat() + "Z",
            "archived": True,
        }

        # Write archived version
        archive_id = f"{profile_id}.archived"
        success = self.repository.write_profile(archive_id, archive_data)

        if success:
            return {
                "success": True,
                "message": f"Profile '{profile_id}' archived successfully",
                "archive_id": archive_id,
                "note": "Profile was archived rather than deleted",
            }
        else:
            return {
                "success": False,
                "error": f"Failed to archive profile '{profile_id}'",
            }

    def validate_access(
        self, profile_id: str, resource: str, operation: str = "read"
    ) -> Dict[str, Any]:
        """
        Validate if a profile has access to a resource.

        Args:
            profile_id: ID of the profile
            resource: Resource path (e.g., "cortex", "ledger", "lobes/NC-LBE-*")
            operation: Operation type ("read", "write", "admin")

        Returns:
            Access validation result dictionary
        """
        profile = self.repository.read_profile(profile_id)
        if not profile:
            return {"allowed": False, "error": f"Profile '{profile_id}' not found"}

        access_level = profile.get("access_level", "developer")
        permissions = profile.get("permissions", {})

        # Check explicit permissions first
        if operation in permissions:
            allowed_resources = permissions[operation]
            if resource in allowed_resources:
                return {
                    "allowed": True,
                    "reason": f"Explicit permission for {operation} on {resource}",
                    "access_level": access_level,
                }

            # Check wildcard permissions
            for allowed_resource in allowed_resources:
                if "*" in allowed_resource:
                    import fnmatch

                    if fnmatch.fnmatch(resource, allowed_resource):
                        return {
                            "allowed": True,
                            "reason": f"Wildcard permission {allowed_resource} matches {resource}",
                            "access_level": access_level,
                        }

        # Fallback to access level rules
        access_rules = self._get_access_rules(access_level)

        if operation in access_rules:
            operation_rules = access_rules[operation]
            for rule_resource, rule_allowed in operation_rules.items():
                if rule_resource == resource or rule_resource == "*":
                    if rule_allowed:
                        return {
                            "allowed": True,
                            "reason": f"Access level '{access_level}' allows {operation} on {resource}",
                            "access_level": access_level,
                        }

        return {
            "allowed": False,
            "reason": f"Access level '{access_level}' does not allow {operation} on {resource}",
            "access_level": access_level,
            "suggestion": f"Request elevated permissions or specific resource access",
        }

    def get_profile_access_level(self, profile_id: str) -> Dict[str, Any]:
        """
        Get access level for a profile.

        Args:
            profile_id: ID of the profile

        Returns:
            Access level information dictionary
        """
        access_level = self.repository.get_profile_access_level(profile_id)
        access_rules = self._get_access_rules(access_level)

        return {
            "profile_id": profile_id,
            "access_level": access_level,
            "rules": access_rules,
            "description": self._describe_access_level(access_level),
        }

    def _extract_profile_metadata(
        self, profile_id: str, profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metadata from profile data."""
        metadata = {
            "access_level": profile.get("access_level", "developer"),
            "has_permissions": "permissions" in profile,
            "has_metadata": "metadata" in profile,
            "created": "created_at" in profile,
            "updated": "updated_at" in profile,
        }

        # Count permissions
        if "permissions" in profile:
            permissions = profile["permissions"]
            metadata["permissions_count"] = sum(
                len(v) for v in permissions.values() if isinstance(v, list)
            )

        # Extract name and email if available
        if "name" in profile:
            metadata["name"] = profile["name"]

        if "email" in profile:
            metadata["email"] = profile["email"]

        # Calculate profile size
        metadata["size_bytes"] = len(json.dumps(profile, ensure_ascii=False))

        return metadata

    def _validate_profile_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate profile data structure."""
        errors = []

        # Check required fields for different access levels
        if "access_level" in profile_data:
            access_level = profile_data["access_level"]
            valid_levels = ["developer", "manager", "owner", "admin"]
            if access_level not in valid_levels:
                errors.append(
                    f"Invalid access_level: {access_level}. Must be one of: {valid_levels}"
                )

        # Validate permissions structure if present
        if "permissions" in profile_data:
            permissions = profile_data["permissions"]
            if not isinstance(permissions, dict):
                errors.append("Permissions must be a dictionary")
            else:
                valid_operations = ["read", "write", "admin", "execute"]
                for operation, resources in permissions.items():
                    if operation not in valid_operations:
                        errors.append(f"Invalid permission operation: {operation}")
                    if not isinstance(resources, list):
                        errors.append(f"Permissions for {operation} must be a list")

        return {"valid": len(errors) == 0, "errors": errors}

    def _summarize_access_levels(
        self, profiles: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Summarize access level distribution."""
        summary = {}
        for profile in profiles:
            level = profile.get("access_level", "developer")
            summary[level] = summary.get(level, 0) + 1
        return summary

    def _get_access_rules(self, access_level: str) -> Dict[str, Dict[str, bool]]:
        """Get access rules for a given access level."""
        # Default access rules
        rules = {
            "developer": {
                "read": {"cortex": True, "ledger": True, "lobes": True},
                "write": {"lobes/temp": True, "scratchpad": True},
                "admin": {},
            },
            "manager": {
                "read": {"*": True},
                "write": {"lobes": True, "profiles": True},
                "admin": {"projects": True},
            },
            "owner": {"read": {"*": True}, "write": {"*": True}, "admin": {"*": True}},
            "admin": {"read": {"*": True}, "write": {"*": True}, "admin": {"*": True}},
        }

        return rules.get(access_level, rules["developer"])

    def _describe_access_level(self, access_level: str) -> str:
        """Get description for an access level."""
        descriptions = {
            "developer": "Can read all resources, write to temporary areas",
            "manager": "Can read/write most resources, manage profiles",
            "owner": "Full access to all resources",
            "admin": "Full access plus system administration",
        }
        return descriptions.get(access_level, "Unknown access level")


# Singleton instance for convenience
_default_profile_service = None


def get_profile_service(
    repository: Optional[ProfileRepository] = None,
) -> ProfileService:
    """
    Get profile service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        ProfileService instance
    """
    global _default_profile_service

    if repository is not None:
        return ProfileService(repository)

    if _default_profile_service is None:
        _default_profile_service = ProfileService()

    return _default_profile_service
