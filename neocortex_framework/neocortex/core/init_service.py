#!/usr/bin/env python3
"""
Init Service - Business logic for project initialization.

This service encapsulates business logic for project initialization,
using repository interfaces for storage abstraction.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import CortexRepository, LobeRepository


class InitService:
    """Service for project initialization business logic."""

    def __init__(
        self,
        cortex_repository: Optional[CortexRepository] = None,
        lobe_repository: Optional[LobeRepository] = None,
    ):
        """
        Initialize init service.

        Args:
            cortex_repository: Cortex repository implementation
            lobe_repository: Lobe repository implementation
        """
        if cortex_repository is None:
            from ..repositories import FileSystemCortexRepository

            self.cortex_repository = FileSystemCortexRepository()
        else:
            self.cortex_repository = cortex_repository

        if lobe_repository is None:
            from ..repositories import FileSystemLobeRepository

            self.lobe_repository = FileSystemLobeRepository()
        else:
            self.lobe_repository = lobe_repository

    def scan_project(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan project structure and analyze.

        Args:
            project_path: Optional project path (defaults to current directory)

        Returns:
            Dictionary with project analysis
        """
        if project_path is None:
            project_path = os.getcwd()

        path = Path(project_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"Project path does not exist: {project_path}",
            }

        # Analyze project structure
        detected_files = []
        detected_dirs = []
        detected_stack = "unknown"

        # Common file patterns
        stack_indicators = {
            "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "nodejs": ["package.json", "package-lock.json", "yarn.lock"],
            "go": ["go.mod", "go.sum"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        }

        # Scan for files
        for file_path in path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(path)
                detected_files.append(str(relative_path))

                # Detect stack
                for stack, indicators in stack_indicators.items():
                    if file_path.name in indicators:
                        detected_stack = stack

        # Scan for directories (first level)
        for dir_path in path.iterdir():
            if dir_path.is_dir():
                detected_dirs.append(dir_path.name)

        # Limit to reasonable number
        detected_files = detected_files[:100]  # First 100 files
        detected_dirs = detected_dirs[:20]  # First 20 directories

        # Generate suggested aliases
        suggested_aliases = self._generate_suggested_aliases(
            path, detected_files, detected_dirs
        )

        return {
            "success": True,
            "project_path": str(path),
            "analysis": {
                "detected_stack": detected_stack,
                "file_count": len(detected_files),
                "dir_count": len(detected_dirs),
                "main_files": self._identify_main_files(detected_files, detected_stack),
                "has_config_files": self._check_config_files(path, detected_stack),
                "suggested_aliases": suggested_aliases,
                "detected_files_sample": detected_files[:10],
                "detected_dirs_sample": detected_dirs[:5],
            },
        }

    def generate_cortex(
        self, project_name: str, template_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate initial cortex for a project.

        Args:
            project_name: Name of the project
            template_type: Type of template ("standard", "minimal", "full")

        Returns:
            Dictionary with generated cortex
        """
        if not project_name:
            return {"success": False, "error": "project_name is required"}

        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Define templates
        templates = {
            "standard": f"""---
alwaysApply: true
description: "Central Cortex for {project_name}. NeoCortex v4.2-Cortex."
created: "{current_date}"
---

# Cortex: {project_name}

## STEP 0 REGRESSION + GOAL CHECK
> 1. Read Regression Buffer
> 2. If similar to error → ADVISE
> 3. Reaffirm goal
> 4. Confirm scope

## Workspace Map
| File/Dir | Alias | Purpose |
|----------|-------|---------|
| main.py | $main | Entry point |
| src/ | @src | Source code |
| tests/ | @tests | Test files |
| docs/ | @docs | Documentation |

## Compact Encoding
| $ = file | @ = directory | ! = command |
|----------|---------------|-------------|
| $main | @src | !run |
| $readme | @tests | !test |
| $config | @docs | !build |

## Current State
- **Version:** NeoCortex v4.2-Cortex
- **Active Phase:** Initial Setup
- **Last Checkpoint:** CP-INIT Cortex generated
- **Project:** {project_name}
- **Created:** {current_date}

## Initial Goals
1. [ ] Setup project structure
2. [ ] Configure development environment
3. [ ] Implement core functionality
4. [ ] Write tests
5. [ ] Document the project

## Notes
- This is an auto-generated cortex
- Customize the Workspace Map with your actual files
- Add checkpoints as you progress
- Use regression buffer for learning from mistakes
""",
            "minimal": f"""---
alwaysApply: true
description: "Minimal Cortex for {project_name}"
created: "{current_date}"
---

# {project_name}

## Workspace Map
| File/Dir | Alias |
|----------|-------|
| main.py | $main |

## Goals
- [ ] Setup project
- [ ] Implement features

Created: {current_date}
""",
            "full": f"""---
alwaysApply: true
description: "Comprehensive Cortex for {project_name}"
created: "{current_date}"
version: "NeoCortex v4.2-Cortex"
---

# Cortex: {project_name}

## Meta Information
- **Project:** {project_name}
- **Created:** {current_date}
- **Version:** NeoCortex v4.2-Cortex
- **Template:** Full

## Architecture Overview
### System Components
1. Core Business Logic
2. Data Access Layer
3. API Layer
4. UI Layer
5. Testing Framework

### Development Workflow
1. Requirement Analysis
2. Design
3. Implementation
4. Testing
5. Deployment

## Workspace Map
| File/Dir | Alias | Category | Description |
|----------|-------|----------|-------------|
| src/ | @src | Source | Main source code |
| tests/ | @tests | Testing | Test files |
| docs/ | @docs | Documentation | Project documentation |
| config/ | @config | Configuration | Configuration files |
| scripts/ | @scripts | Scripts | Utility scripts |

## Checkpoint System
### Current Checkpoints
- CP-INIT: Project initialized
- CP-SETUP: Development environment ready
- CP-ARCH: Architecture defined
- CP-IMPL: Core implementation complete

### Future Checkpoints
- CP-TEST: Testing complete
- CP-DOC: Documentation complete
- CP-DEPLOY: Deployment ready

## Regression Buffer
> Use this space to record failures and learnings

## Action Queue
### Pending
- [ ] Setup CI/CD pipeline
- [ ] Configure logging
- [ ] Setup monitoring

### In Progress
- [ ] Implement core features

### Completed
- [x] Initialize project
- [x] Setup version control
""",
        }

        if template_type not in templates:
            return {
                "success": False,
                "error": f"Unknown template type: {template_type}. Available: {list(templates.keys())}",
            }

        cortex_content = templates[template_type]

        return {
            "success": True,
            "project_name": project_name,
            "template_type": template_type,
            "cortex_generated": True,
            "cortex_content": cortex_content,
            "size_chars": len(cortex_content),
            "lines": cortex_content.count("\n") + 1,
            "created": current_date,
        }

    def generate_lobe(self, lobe_name: str, lobe_type: str = "phase") -> Dict[str, Any]:
        """
        Generate initial lobe for a module or phase.

        Args:
            lobe_name: Name of the lobe
            lobe_type: Type of lobe ("phase", "module", "component", "task")

        Returns:
            Dictionary with generated lobe
        """
        if not lobe_name:
            return {"success": False, "error": "lobe_name is required"}

        # Ensure .mdc extension
        if not lobe_name.endswith(".mdc"):
            lobe_name = f"{lobe_name}.mdc"

        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Define templates based on lobe type
        templates = {
            "phase": f"""# Phase: {lobe_name.replace(".mdc", "")}

## Phase Overview
- **Start Date:** {current_date}
- **Expected Duration:** 2 weeks
- **Priority:** High

## Goals
- [ ] Define phase objectives
- [ ] Break down into tasks
- [ ] Assign resources
- [ ] Set milestones

## Tasks
### Week 1
- [ ] Task 1: Requirements gathering
- [ ] Task 2: Design phase
- [ ] Task 3: Initial implementation

### Week 2
- [ ] Task 4: Testing
- [ ] Task 5: Documentation
- [ ] Task 6: Review and refinement

## Checkpoints
- CP-PHASE-START: Phase initiated
- CP-PHASE-MID: Mid-phase review
- CP-PHASE-END: Phase completed

## Notes
This lobe tracks the {lobe_name.replace(".mdc", "")} phase.
""",
            "module": f"""# Module: {lobe_name.replace(".mdc", "")}

## Module Specification
- **Purpose:** Core functionality module
- **Dependencies:** None
- **Interface:** Clean API

## Implementation Tasks
- [ ] Define module interface
- [ ] Implement core functions
- [ ] Write unit tests
- [ ] Document public API
- [ ] Performance optimization

## API Design
### Public Functions
- `function1()`: Description
- `function2()`: Description

### Configuration
- `config_param1`: Default value
- `config_param2`: Default value

## Testing Strategy
- Unit tests for all public functions
- Integration tests with dependent modules
- Performance benchmarks

## Notes
Module-specific lobe for focused development.
""",
            "component": f"""# Component: {lobe_name.replace(".mdc", "")}

## Component Overview
- **Type:** UI/Service/Utility
- **Framework:** React/Python/Other
- **Status:** In development

## Specifications
### Properties
- Property 1: Description
- Property 2: Description

### Methods
- Method 1: Description
- Method 2: Description

## Development Tasks
- [ ] Create component skeleton
- [ ] Implement core logic
- [ ] Add error handling
- [ ] Write tests
- [ ] Document usage

## Integration Points
- Depends on: Component A
- Used by: Component B

## Notes
Component-specific development tracking.
""",
        }

        if lobe_type not in templates:
            return {
                "success": False,
                "error": f"Unknown lobe type: {lobe_type}. Available: {list(templates.keys())}",
            }

        lobe_content = templates[lobe_type]

        return {
            "success": True,
            "lobe_name": lobe_name,
            "lobe_type": lobe_type,
            "lobe_generated": True,
            "lobe_content": lobe_content,
            "size_chars": len(lobe_content),
            "lines": lobe_content.count("\n") + 1,
            "created": current_date,
        }

    def _generate_suggested_aliases(
        self, path: Path, files: List[str], dirs: List[str]
    ) -> List[Dict[str, str]]:
        """Generate suggested aliases based on project structure."""
        aliases = []

        # Common file patterns
        common_files = {
            "README.md": "$readme",
            "main.py": "$main",
            "app.py": "$app",
            "index.js": "$index",
            "package.json": "$package",
            "requirements.txt": "$requirements",
            "pyproject.toml": "$pyproject",
            "dockerfile": "$docker",
            ".env": "$env",
        }

        # Common directory patterns
        common_dirs = {
            "src": "@src",
            "lib": "@lib",
            "tests": "@tests",
            "docs": "@docs",
            "config": "@config",
            "scripts": "@scripts",
            "assets": "@assets",
            "public": "@public",
        }

        # Check for common files
        for file in files:
            basename = os.path.basename(file)
            if basename in common_files:
                aliases.append(
                    {"symbol": common_files[basename], "path": file, "type": "file"}
                )

        # Check for common directories
        for dir_name in dirs:
            if dir_name in common_dirs:
                aliases.append(
                    {
                        "symbol": common_dirs[dir_name],
                        "path": dir_name + "/",
                        "type": "directory",
                    }
                )

        # Add command aliases
        command_aliases = [
            {
                "symbol": "!run",
                "command": "python main.py",
                "description": "Run main application",
            },
            {"symbol": "!test", "command": "pytest", "description": "Run tests"},
            {
                "symbol": "!build",
                "command": "npm run build",
                "description": "Build project",
            },
            {
                "symbol": "!dev",
                "command": "npm run dev",
                "description": "Start development server",
            },
        ]

        # Add relevant command aliases based on stack detection
        # (simplified - in real implementation would detect stack)
        aliases.extend(command_aliases[:2])  # Add first two command aliases

        return aliases

    def _identify_main_files(self, files: List[str], stack: str) -> List[str]:
        """Identify main files based on stack."""
        main_file_patterns = {
            "python": ["main.py", "app.py", "manage.py", "wsgi.py"],
            "nodejs": ["index.js", "app.js", "server.js", "main.js"],
            "go": ["main.go"],
            "rust": ["src/main.rs"],
            "java": ["src/main/java/**/*.java"],
        }

        patterns = main_file_patterns.get(stack, [])
        identified = []

        for file in files:
            for pattern in patterns:
                if pattern in file:
                    identified.append(file)
                    break

        return identified[:5]  # Return up to 5 main files

    def _check_config_files(self, path: Path, stack: str) -> bool:
        """Check if config files exist for the stack."""
        config_files = {
            "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "nodejs": ["package.json"],
            "go": ["go.mod"],
            "rust": ["Cargo.toml"],
            "java": ["pom.xml", "build.gradle"],
        }

        files = config_files.get(stack, [])
        for file in files:
            if (path / file).exists():
                return True

        return False


# Singleton instance for convenience
_default_init_service = None


def get_init_service(
    cortex_repository: Optional[CortexRepository] = None,
    lobe_repository: Optional[LobeRepository] = None,
) -> InitService:
    """
    Get init service instance (singleton pattern).

    Args:
        cortex_repository: Optional cortex repository implementation
        lobe_repository: Optional lobe repository implementation

    Returns:
        InitService instance
    """
    global _default_init_service

    if cortex_repository is not None or lobe_repository is not None:
        return InitService(cortex_repository, lobe_repository)

    if _default_init_service is None:
        _default_init_service = InitService()

    return _default_init_service
