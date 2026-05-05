#!/usr/bin/env python3
"""
Test vector scan functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neocortex.core.manifest_service import ManifestService


def main():
    service = ManifestService()
    print("Starting vector scan...")
    result = service.vector_scan()
    print("Result:", result)
    if result["success"]:
        print(f"Output file: {result['output_file']}")
        print(f"Processed files: {result['file_count']}")
    else:
        print(f"Error: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
