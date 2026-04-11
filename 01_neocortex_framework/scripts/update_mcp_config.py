#!/usr/bin/env python3
import json
import os

config_path = r"C:\Users\Lucas Valério\.gemini\antigravity\mcp_config.json"
backup_path = config_path + ".backup"

# Read existing config
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# Update neocortex server entry
if "mcpServers" in config and "neocortex" in config["mcpServers"]:
    neocortex_config = config["mcpServers"]["neocortex"]
    # Update command path to Python executable (keep existing)
    neocortex_config["command"] = "C:/Program Files/Python312/pythonw.exe"
    # Update args to point to correct server file
    neocortex_config["args"] = [
        "C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/neocortex_framework/neocortex/mcp/server.py"
    ]
    # Update PYTHONPATH to include framework directory
    neocortex_config["env"] = {
        "PYTHONPATH": "C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/neocortex_framework"
    }
    neocortex_config["description"] = (
        "NeoCortex Framework MCP Server – 18 tools for context engineering and autonomous evolution"
    )

    print("Updated neocortex MCP server configuration:")
    print(f"  Command: {neocortex_config['command']}")
    print(f"  Args: {neocortex_config['args']}")
    print(f"  Env: {neocortex_config['env']}")

# Write updated config
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"\nConfig updated successfully. Backup saved to {backup_path}")
