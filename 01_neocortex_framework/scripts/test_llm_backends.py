#!/usr/bin/env python3
"""
Test script for LLM backends integration.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from neocortex.infra.llm.factory import LLMBackendFactory
from neocortex.config import get_config

logging.basicConfig(level=logging.INFO)


def test_backend_creation():
    """Test creating LLM backends from factory."""
    config = get_config()
    llm_config = config.llm_config
    print("LLM Configuration:")
    for key, value in llm_config.items():
        print(f"  {key}: {value}")

    # Create primary backend
    try:
        backend = LLMBackendFactory.create_from_config(llm_config)
        print(f"\n✅ Successfully created backend: {backend}")
        print(f"  Backend type: {type(backend).__name__}")
        print(f"  Provider: {backend.provider.value}")

        # Test simple completion (short)
        print("\nTesting completion with short prompt...")
        prompt = "Say 'Hello, NeoCortex!' in one sentence."
        response = backend.generate(prompt, max_tokens=20)
        print(f"  Response: {response}")

        return True
    except Exception as e:
        print(f"\n❌ Failed to create backend: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_fallback_chain():
    """Test fallback chain functionality."""
    config = get_config()
    fallback_chain = config.llm_fallback_chain

    if not fallback_chain:
        print("\nNo fallback chain configured.")
        return

    print(f"\nTesting fallback chain ({len(fallback_chain)} backends):")

    try:
        chain = LLMBackendFactory.create_fallback_chain(fallback_chain)
        print(f"  ✅ Created fallback chain with {len(chain.backends)} backends")

        # Test chain health
        for i, backend in enumerate(chain.backends, 1):
            print(f"    Backend #{i}: {backend.provider.value} / {backend.model}")
            if hasattr(backend, "health_check"):
                try:
                    health = backend.health_check()
                    print(f"      Health: {health}")
                except Exception as e:
                    print(f"      Health check failed: {e}")
    except Exception as e:
        print(f"  ❌ Failed to create fallback chain: {e}")
        import traceback

        traceback.print_exc()


def main():
    print("=" * 60)
    print("NeoCortex LLM Backends Test")
    print("=" * 60)

    # Test primary backend
    if not test_backend_creation():
        print("\nPrimary backend test failed.")
        return 1

    # Test fallback chain
    test_fallback_chain()

    print("\n" + "=" * 60)
    print("All tests completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
