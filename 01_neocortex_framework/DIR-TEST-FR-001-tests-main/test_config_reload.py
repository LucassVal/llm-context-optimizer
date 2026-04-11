#!/usr/bin/env python3
"""
Test config reload functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from neocortex.config import get_config


def test_reload():
    config = get_config()
    print("Initial LLM temperature:", config.llm_temperature)

    # Change environment variable with correct case (temperature lowercase)
    os.environ["NEOCORTEX_LLM__temperature"] = "0.9"
    print("Set env var NEOCORTEX_LLM__temperature = 0.9")

    # Reload config
    config.reload()

    print("After reload LLM temperature:", config.llm_temperature)
    print(
        "After reload LLM config temperature key:", config.llm_config.get("temperature")
    )

    # Check if value changed (should be 0.9)
    if abs(config.llm_temperature - 0.9) < 0.001:
        print("PASS Config reload successful")
        return True
    else:
        print("FAIL Config reload failed")
        # Debug: print all NEOCORTEX env vars
        for k, v in os.environ.items():
            if k.startswith("NEOCORTEX_"):
                print(f"  {k}={v}")
        return False


if __name__ == "__main__":
    success = test_reload()
    sys.exit(0 if success else 1)
