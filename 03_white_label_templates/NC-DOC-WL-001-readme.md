#  NeoCortex White Label Template

This directory contains a white-label template structure for NeoCortex v4.2-Cortex framework projects.

##  Purpose

Provide a ready-to-use template structure for client projects using the NeoCortex framework. This ensures consistency across projects while allowing customization for specific client needs.

##  Directory Structure

```
white_label/
 .agents/
    rules/
        00-cortex.mdc              # Main cortex rules (copy from templates)
        phase-1-discovery.mdc      # Example phase lobe
        local.mdc                  # Personal notes (gitignore)
        archive/                   # Completed lobes
 templates/                         # Project-specific templates
 examples/                          # Example implementations
 archive/                           # Auto-summaries of completed phases
 backup/                            # Timestamped backups
```

##  Getting Started

1. **Copy this structure** to your new project directory:
   ```bash
   cp -r white_label/ my_new_project/
   ```

2. **Initialize NeoCortex**:
   ```bash
   cd my_new_project
   # Copy the white label cortex template
   cp ../neocortex_framework/templates/00-cortex-WHITELABEL.mdc .agents/rules/00-cortex.mdc
   
   # Create initial ledger
   cp ../neocortex_framework/templates/memory-ledger-TEMPLATE.json memory_neocortex_myproject.json
   ```

3. **Customize**:
   - Edit `.agents/rules/00-cortex.mdc` with project-specific aliases and rules
   - Update `memory_neocortex_*.json` with project identity
   - Add phase lobes as needed

##  Core Components

### Cortex (`00-cortex.mdc`)
The central rule set containing:
- Workspace map with aliases
- Ubiquitous language definitions
- Workflows (Explore-Plan-Act, Debug, Wrap Up)
- Negative constraints and atomic locks

### Ledger (`memory_neocortex_*.json`)
JSON state file containing:
- Project identity and configuration
- Session timeline and action queue
- Regression buffer and audit trail
- Memory temperature (hot/cold context)

### Lobes (`phase-*.mdc`)
Phase-specific context files:
- Activated by glob patterns or semantic mention
- Contain checkpoint trees and local regression buffers
- Isolated namespace to prevent context pollution

##  Workflows

### Explore-Plan-Act
For complex feature implementation:
1. **STEP 0** - Regression check
2. **Explore** - Read-only mapping
3. **Plan** - Propose plan with `<thinking>` scratchpad
4. **Act** - Execute minimal diffs
5. **Observe** - Validate with tests
6. **Persist** - Update state and backup

### Wrap Up Session
**Always** run when finishing:
1. Update current state
2. Check off checkpoints
3. Add to session timeline
4. Compact hot context if >5 entries
5. Run `!backup`
6. Update changelog

##  Templates Provided

- `neocortex_framework/templates/00-cortex-WHITELABEL.mdc` - Main cortex template
- `neocortex_framework/templates/phase-lobe-TEMPLATE.mdc` - Phase lobe template
- `neocortex_framework/templates/memory-ledger-TEMPLATE.json` - JSON ledger template

##  Integration with NeoCortex Framework

This white label template is designed to work seamlessly with the NeoCortex framework. The framework provides:

- **MCP Server**: 16 multi-action tools for IDE integration (including hierarchical access control)
- **Benchmark Suite**: Drift Exhaustion, Omni-Reasoning, Titanomachy tests
- **Agent Orchestration**: Support for ephemeral agents and T0 cortex executor
- **Autonomous Evolution**: Adaptive knowledge lifecycle and semantic consolidation
- **Hierarchical User Profiles**: Unlimited levels of user hierarchy for enterprises, schools, governments
- **MCP Hub**: WebSocket multi-user server for collaborative environments

##  Hierarchical User Profiles

NeoCortex v4.2 includes a powerful hierarchical user profile system that supports unlimited nesting levels. This enables:

- **Unlimited hierarchical levels**: Users can be hosts for other users without limits
- **Granular access control**: Users can read equal, lateral, and inferior levels, but NOT superior levels
- **Multi-tenancy**: Support for enterprises, LAN houses, schools, government agencies
- **Profile conversion**: Convert existing user data (like Lucas.json) to NeoCortex schema

### Example: Creating a User Profile

```bash
# Use the profile loader to convert existing user data
python neocortex_framework/DIR-PRF-FR-001-profiles-main/NC-PRF-FR-003-profile-loader.py

# Or create a new profile from template
cp neocortex_framework/DIR-PRF-FR-001-profiles-main/templates/NC-PRF-TMP-001-dev-profile-template.json users/your_user_id/NC-PRF-USR-001-profile.json
```

### Access Control Example

```python
from NC_SEC_FR_001_security_utils import can_access

# Check if user "manager" can read user "employee"
allowed, reason = can_access("manager", "employee", "read")
print(f"Access allowed: {allowed}, Reason: {reason}")
```

##  MCP Hub (Multi-User Support)

For collaborative environments, NeoCortex includes an MCP Hub that provides:

- **WebSocket server**: Multiple users can connect simultaneously
- **Session management**: Authentication and session tracking
- **Hierarchical visibility**: Users see only those they have access to
- **Tool forwarding**: All NeoCortex MCP tools available through the hub

### Starting the Hub

```bash
# Start the hub on default port 8765
python neocortex_framework/DIR-MCP-FR-001-mcp-server/NC-HUB-FR-001-mcp-hub.py --host localhost --port 8765

# Connect with an MCP client (e.g., Antigravity with WebSocket transport)
```

### Hub Tools

The hub provides additional tools for user management:

- `hub_authenticate`: Authenticate user and create session
- `hub_list_users`: List users visible to current session
- `hub_validate_access`: Validate access between users
- `hub_get_profile`: Get user profile (with access control)

##  License

MIT - Use freely in any project, commercial or personal.

##  Next Steps

1. Review and customize `00-cortex.mdc` for your project
2. Add project-specific phase lobes
3. Integrate with your build system and commands
4. Run benchmarks to establish baseline metrics