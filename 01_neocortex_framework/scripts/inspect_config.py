#!/usr/bin/env python3
import sys

sys.path.insert(0, ".")
from neocortex.config import get_config

config = get_config()
print("llm_config:", config.llm_config)
print("Type:", type(config.llm_config))
if isinstance(config.llm_config, dict):
    print("Keys:", list(config.llm_config.keys()))
elif isinstance(config.llm_config, list):
    print("Length:", len(config.llm_config))
    print("First item:", config.llm_config[0] if config.llm_config else None)
