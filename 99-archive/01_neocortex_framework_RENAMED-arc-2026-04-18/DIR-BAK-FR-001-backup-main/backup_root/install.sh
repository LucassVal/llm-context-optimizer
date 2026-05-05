#!/bin/bash

PROJECT_NAME=${1:-"my_project"}

echo -e "\033[0;36mInitializing TurboQuant v4.2 structure for: $PROJECT_NAME...\033[0m"

# Define required folders
DIRS=(
    ".agents/rules/archive"
    ".agents/workflows"
    "memory_lobes"
    "archive"
    "backup"
)

# Create folders
for d in "${DIRS[@]}"; do
    mkdir -p "$d"
    echo -e "\033[0;32m [OK] Directory created: $d\033[0m"
done

# Copy Starter Cortex
if [ -f "./templates/00-cortex-STARTER.mdc" ]; then
    cp "./templates/00-cortex-STARTER.mdc" "./.agents/rules/00-cortex.mdc"
    echo -e "\033[0;32m [OK] Template 00-cortex-STARTER.mdc copied to .agents/rules/00-cortex.mdc\033[0m"
else
    echo -e "\033[0;33mWarning: templates/00-cortex-STARTER.mdc not found. Copy manually.\033[0m"
fi

# Copy JSON Ledger
JSON_TARGET="memory_turboquant_${PROJECT_NAME}.json"
if [ -f "./templates/memory-ledger-TEMPLATE.json" ] && [ ! -f "$JSON_TARGET" ]; then
    cp "./templates/memory-ledger-TEMPLATE.json" "$JSON_TARGET"
    echo -e "\033[0;32m [OK] JSON Ledger template copied to $JSON_TARGET\033[0m"
fi

echo -e "\n\033[0;33m🚀 TurboQuant v4.2 initialized successfully in './'!\033[0m"
echo -e "\033[0;90m📝 Modify ./.agents/rules/00-cortex.mdc to define your project's rules.\033[0m"
