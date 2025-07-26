"""
Test script to verify Python imports and paths.
"""

import sys
import os

print("=" * 80)
print("Python Path:")
for path in sys.path:
    print(f"- {path}")
print("=" * 80)

# Try importing the mcp package
try:
    import mcp
    print("Successfully imported mcp package!")
    print(f"mcp package location: {mcp.__file__}")
    
    # Try importing the AI module
    try:
        from mcp.ai import service
        print("Successfully imported mcp.ai.service!")
        print(f"AI service module location: {service.__file__}")
    except ImportError as e:
        print(f"Failed to import mcp.ai.service: {e}")
        
except ImportError as e:
    print(f"Failed to import mcp package: {e}")
    print("\nTroubleshooting steps:")
    print("1. Make sure the 'mcp' directory is in the Python path")
    print("2. Check that __init__.py files exist in the mcp and mcp/ai directories")
    print("3. Verify the directory structure matches the package structure")

print("=" * 80)
