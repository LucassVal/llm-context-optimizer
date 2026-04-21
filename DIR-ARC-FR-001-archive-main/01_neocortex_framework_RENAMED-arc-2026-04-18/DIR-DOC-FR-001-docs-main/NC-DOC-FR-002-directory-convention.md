#  NC-DOC-FR-002 - Directory Structure Convention

> **Standardized naming and organization for all NeoCortex directories**

---

##  Directory Naming Format

```
DIR-{TYPE}-{CAT}-{ID}-{name}
```

| Segment | Description | Values | Example |
|---------|-------------|---------|---------|
| **DIR** | Directory prefix | Always `DIR` | `DIR` |
| **{TYPE}** | Directory type | 3-4 uppercase letters | `CORE`, `MCP`, `TMP`, `ARC`, `BAK`, `DOC`, `SRC` |
| **{CAT}** | Category | 2-letter code | `FR` (framework), `WL` (white label), `EX` (example) |
| **{ID}** | Sequential ID | 3-digit number (001-999) | `001`, `002`, `003` |
| **{name}** | Descriptive name | lowercase-with-hyphens | `core-central`, `mcp-server`, `templates-main` |

---

##  Directory Types (TYPE)

| Code | Type | Description | Examples |
|------|------|-------------|----------|
| **CORE** | Core Framework | Central framework directories | `DIR-CORE-FR-001-core-central` |
| **MCP** | MCP Server | MCP server and tools directories | `DIR-MCP-FR-001-mcp-server` |
| **TMP** | Templates | Template directories | `DIR-TMP-WL-001-templates-main` |
| **ARC** | Archive | Archived content directories | `DIR-ARC-FR-001-archive-main` |
| **BAK** | Backup | Backup directories | `DIR-BAK-FR-001-backup-main` |
| **DOC** | Documentation | Documentation directories | `DIR-DOC-FR-001-docs-main` |
| **SRC** | Source Code | Source code directories | `DIR-SRC-FR-001-source-main` |
| **CFG** | Configuration | Configuration directories | `DIR-CFG-FR-001-config-main` |
| **BIN** | Binary/Executable | Executable directories | `DIR-BIN-FR-001-binaries` |
| **TEST** | Tests | Test directories | `DIR-TEST-FR-001-tests-main` |
| **DATA** | Data | Data storage directories | `DIR-DATA-FR-001-data-main` |

---

##  Directory Hierarchy

### Framework Root (`neocortex_framework/`)
```
neocortex_framework/
 DIR-CORE-FR-001-core-central/          # Core framework components
    .agents/
       rules/
    memory_lobes/
    NC-LED-FR-001-framework-ledger.json
 DIR-MCP-FR-001-mcp-server/             # MCP server and tools
    NC-MCP-FR-001-mcp-server.py
 DIR-TMP-FR-001-templates-main/         # Framework templates
    NC-TMP-WL-001-cortex-template.mdc
 DIR-ARC-FR-001-archive-main/           # Archived content
 DIR-BAK-FR-001-backup-main/            # Backups
 DIR-DOC-FR-001-docs-main/              # Documentation
    NC-NAM-FR-001-naming-convention.md
    NC-DOC-FR-002-directory-convention.md
    NC-TODO-FR-001-project-roadmap.md
 DIR-SRC-FR-001-source-main/            # Source code utilities
```

### White Label Root (`white_label/`)
```
white_label/
 DIR-TMP-WL-001-templates-main/         # White label templates
    NC-TMP-WL-001-cortex-template.mdc
 DIR-DOC-WL-001-docs-main/              # White label documentation
     NC-DOC-WL-001-readme.md
```

---

##  Migration Plan

### Step 1: Create New Directory Structure
1. Create all DIR-* directories in `neocortex_framework/`
2. Move files to appropriate directories
3. Update all references (aliases, imports, configs)

### Step 2: Update Compact Encoding
Update `compact_encoding.directories` in ledger to use new DIR- aliases:

```json
"directories": {
  "core": "DIR-CORE-FR-001-core-central/",
  "mcp": "DIR-MCP-FR-001-mcp-server/",
  "tpl": "DIR-TMP-FR-001-templates-main/",
  "arc": "DIR-ARC-FR-001-archive-main/",
  "bak": "DIR-BAK-FR-001-backup-main/",
  "doc": "DIR-DOC-FR-001-docs-main/",
  "src": "DIR-SRC-FR-001-source-main/"
}
```

### Step 3: Update Cortex References
Update `$ctx` workspace map with new directory aliases.

### Step 4: Update MCP Server Paths
Update `CORTEX_PATH` and `LEDGER_PATH` constants in MCP server.

### Step 5: Test Integration
Verify all components work with new directory structure.

---

##  Current Directory Mapping

| Current Directory | New Directory | Status |
|-------------------|---------------|--------|
| `.agents/` | `DIR-CORE-FR-001-core-central/.agents/` | To be moved |
| `archive/` | `DIR-ARC-FR-001-archive-main/` | To be moved |
| `backup/` | `DIR-BAK-FR-001-backup-main/` | To be moved |
| `mcp/` | `DIR-MCP-FR-001-mcp-server/` | To be moved |
| `memory_lobes/` | `DIR-CORE-FR-001-core-central/memory_lobes/` | To be moved |
| `templates/` | `DIR-TMP-FR-001-templates-main/` | To be moved |
| (root files) | `DIR-CORE-FR-001-core-central/` | To be moved |

---

##  ID Assignment for Directories

| ID Range | Purpose |
|----------|---------|
| **001-099** | Core framework directories |
| **100-199** | MCP server directories |
| **200-299** | Template directories |
| **300-399** | Archive/backup directories |
| **400-499** | Documentation directories |
| **500-599** | Source code directories |
| **600-699** | Configuration directories |
| **700-799** | Test directories |
| **800-899** | Data directories |
| **900-999** | Experimental/development |

---

##  Relationship with NC File Convention

- **Files** use `NC-{TYPE}-{CAT}-{ID}-{name}.{ext}`
- **Directories** use `DIR-{TYPE}-{CAT}-{ID}-{name}`
- **TYPE codes** are aligned where possible (CORE  CTX, MCP  MCP, etc.)
- **CAT codes** are identical (FR, WL, EX, etc.)
- **ID ranges** are coordinated between files and directories

---

**Version:** 1.0  
**Date:** 2026-04-09  
**Applied to:** All NeoCortex directories  
**Maintainer:** OpenCode (T0 cortex executor)