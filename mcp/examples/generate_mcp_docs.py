"""
MCP Documentation Generator Example

This example demonstrates how to use the AI-powered documentation generator
with the MCP registry.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.ai.service import get_ai_service

def load_mcp_registry(registry_path: str) -> dict:
    """Load the MCP registry from a JSON or YAML file."""
    registry_path = Path(registry_path)
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry file not found: {registry_path}")
    
    if registry_path.suffix.lower() == '.json':
        with open(registry_path, 'r') as f:
            return json.load(f)
    elif registry_path.suffix.lower() in ('.yaml', '.yml'):
        import yaml
        with open(registry_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported registry format. Use .json or .yaml")

def generate_documentation(registry_data: dict, output_dir: str) -> None:
    """Generate documentation for all MCPs in the registry."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the AI service
    ai_service = get_ai_service()
    
    # Process each zone and MCP
    for zone in registry_data.get('mcp_zones', []):
        zone_name = zone.get('zone', 'unknown').replace('/', '_')
        zone_dir = output_dir / zone_name
        zone_dir.mkdir(exist_ok=True)
        
        print(f"\nProcessing zone: {zone_name}")
        print("-" * 40)
        
        for mcp in zone.get('mcps', []):
            mcp_name = mcp.get('name', 'unnamed').replace(' ', '_').lower()
            output_file = zone_dir / f"{mcp_name}.md"
            
            print(f"  - Generating docs for: {mcp.get('name')}...", end=' ')
            
            try:
                # Generate documentation using AI
                docs = ai_service.generate_documentation(mcp)
                
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(docs)
                
                print("✓")
                
            except Exception as e:
                print(f"✗ Error: {e}")

def main():
    """Main entry point for the example."""
    # Path to the MCP registry file
    registry_path = Path(__file__).parent.parent / "mcp" / "registry" / "mcp_registry.json"
    
    # Output directory for generated docs
    output_dir = Path(__file__).parent.parent / "docs" / "generated"
    
    try:
        # Load the registry
        print(f"Loading MCP registry from: {registry_path}")
        registry_data = load_mcp_registry(registry_path)
        
        # Generate documentation
        print(f"\nGenerating documentation in: {output_dir}")
        generate_documentation(registry_data, output_dir)
        
        print("\nDocumentation generation complete!")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
