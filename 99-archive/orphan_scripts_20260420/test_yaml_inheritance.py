#!/usr/bin/env python3
"""Test YAML inheritance loader."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from neocortex.core.utils import load_yaml_with_inheritance


def main():
    # Test 1: Load root template (no inheritance)
    print("=== Test 1: Root Template ===")
    root_path = (
        Path(__file__).parent.parent
        / "DIR-TMP-FR-001-templates-main"
        / "NC-GOV-TPL-000-root-template.yaml"
    )
    try:
        root_data = load_yaml_with_inheritance(root_path)
        print(f"Level: {root_data.get('level')}")
        print(f"Tags count: {len(root_data.get('tags', []))}")
        print(f"Validation rules: {len(root_data.get('validation_rules', []))}")
        print("[OK] Root template loaded successfully")
    except Exception as e:
        print(f"[ERROR] Error loading root template: {e}")

    # Test 2: Load agent-courier template (inherits from root)
    print("\n=== Test 2: Agent Courier Template ===")
    courier_path = (
        Path(__file__).parent.parent
        / "DIR-TMP-FR-001-templates-main"
        / "NC-GOV-TPL-001-agent-courier.yaml"
    )
    try:
        courier_data = load_yaml_with_inheritance(courier_path)
        print(f"Level: {courier_data.get('level')}")
        print(f"Topology: {courier_data.get('topology')}")
        print(f"Agent role: {courier_data.get('agent_role')}")
        print(f"Tags count: {len(courier_data.get('tags', []))}")
        print(f"Validation rules: {len(courier_data.get('validation_rules', []))}")
        print(f"Configuration: {courier_data.get('configuration')}")
        print("[OK] Agent courier template loaded successfully")
    except Exception as e:
        print(f"[ERROR] Error loading agent courier template: {e}")
        import traceback

        traceback.print_exc()

    # Test 3: Load courier-01 instance (inherits from agent-courier)
    print("\n=== Test 3: Courier-01 Instance ===")
    instance_path = (
        Path(__file__).parent.parent / "lobes" / "courier-01" / "config.yaml"
    )
    try:
        instance_data = load_yaml_with_inheritance(instance_path)
        print(f"Level: {instance_data.get('level')}")
        print(f"Instance name: {instance_data.get('instance_name')}")
        print(f"Tags count: {len(instance_data.get('tags', []))}")
        print(f"Validation rules: {len(instance_data.get('validation_rules', []))}")
        print(
            f"Configuration max_concurrent_tasks: {instance_data.get('configuration', {}).get('max_concurrent_tasks')}"
        )
        print(f"Backend model: {instance_data.get('backend', {}).get('model')}")
        print("[OK] Courier-01 instance loaded successfully")

        # Check inheritance chain
        print("\n--- Inheritance Chain ---")
        from neocortex.core.utils import validate_inheritance_chain

        chain = validate_inheritance_chain(instance_path)
        for i, path in enumerate(chain):
            rel_path = Path(path).relative_to(Path(__file__).parent.parent)
            print(f"{i}: {rel_path}")

    except Exception as e:
        print(f"[ERROR] Error loading courier-01 instance: {e}")
        import traceback

        traceback.print_exc()

    print("\n=== All tests completed ===")


if __name__ == "__main__":
    main()
