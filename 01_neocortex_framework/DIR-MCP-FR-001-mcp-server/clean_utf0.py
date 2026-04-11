#!/usr/bin/env python3
"""
UTF-0 Cleaner for NeoCortex MCP project.
Removes emojis, accents, and non-ASCII characters from code files.
Converts to international language (English ASCII).
"""

import os
import re
import sys
from pathlib import Path


def remove_accents_and_emojis(text: str) -> str:
    """Remove accents and emojis, convert to ASCII-safe text."""
    # Simple accent mapping for Portuguese
    accent_map = {
        "a": "a",
        "a": "a",
        "a": "a",
        "a": "a",
        "a": "a",
        "e": "e",
        "e": "e",
        "e": "e",
        "e": "e",
        "i": "i",
        "i": "i",
        "i": "i",
        "i": "i",
        "o": "o",
        "o": "o",
        "o": "o",
        "o": "o",
        "o": "o",
        "u": "u",
        "u": "u",
        "u": "u",
        "u": "u",
        "c": "c",
        "A": "A",
        "A": "A",
        "A": "A",
        "A": "A",
        "A": "A",
        "E": "E",
        "E": "E",
        "E": "E",
        "E": "E",
        "I": "I",
        "I": "I",
        "I": "I",
        "I": "I",
        "O": "O",
        "O": "O",
        "O": "O",
        "O": "O",
        "O": "O",
        "U": "U",
        "U": "U",
        "U": "U",
        "U": "U",
        "C": "C",
        "n": "n",
        "N": "N",
    }

    # First replace accented characters
    for acc, repl in accent_map.items():
        text = text.replace(acc, repl)

    # Remove emojis and other non-ASCII characters
    # Keep basic ASCII (0-127) except control characters
    cleaned = []
    for char in text:
        code = ord(char)
        if code < 128 and code >= 32:  # Printable ASCII
            cleaned.append(char)
        elif code == 9 or code == 10 or code == 13:  # Tab, LF, CR
            cleaned.append(char)
        # else: discard character

    return "".join(cleaned)


def clean_file(filepath: Path):
    """Clean a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        cleaned = remove_accents_and_emojis(content)

        if original != cleaned:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"Cleaned: {filepath}")
            return True
        else:
            print(f"Already clean: {filepath}")
            return False
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")
        return False


def main():
    """Clean all Python and Markdown files in the project."""
    project_root = Path(__file__).parent.parent.parent
    mcp_dir = project_root / "DIR-MCP-FR-001-mcp-server"
    core_dir = project_root / "DIR-CORE-FR-001-core-central"
    profiles_dir = project_root / "DIR-PRF-FR-001-profiles-main"

    # Patterns to clean
    patterns = ["*.py", "*.md", "*.mdc", "*.json", "*.txt"]

    cleaned_count = 0
    total_count = 0

    for pattern in patterns:
        for filepath in project_root.rglob(pattern):
            # Skip virtual environment directories
            if any(
                part.startswith(".") or part == "__pycache__" for part in filepath.parts
            ):
                continue

            total_count += 1
            if clean_file(filepath):
                cleaned_count += 1

    print(f"\nTotal files processed: {total_count}")
    print(f"Files cleaned: {cleaned_count}")


if __name__ == "__main__":
    main()
