#!/usr/bin/env python3
"""
MCP Registry Validator

This script validates the structure and content of the MCP registry YAML file.
"""

import yaml
import jsonschema
from pathlib import Path

# Define the schema for MCP registry
SCHEMA = {
    "type": "object",
    "required": ["mcp_zones"],
    "properties": {
        "mcp_zones": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["zone", "mcps"],
                "properties": {
                    "zone": {"type": "string"},
                    "description": {"type": "string"},
                    "mcps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "desc", "url", "module", "status"],
                            "properties": {
                                "name": {"type": "string"},
                                "desc": {"type": "string"},
                                "url": {"type": "string", "format": "uri"},
                                "functions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "module": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["active", "planned", "optional", "deprecated"]
                                },
                                "config_template": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
}

def load_yaml(file_path):
    """Load and parse YAML file."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

def validate_registry(registry_path):
    """Validate the MCP registry against the schema."""
    # Load the registry
    registry = load_yaml(registry_path)
    if not registry:
        return False
    
    # Validate against schema
    try:
        jsonschema.validate(instance=registry, schema=SCHEMA)
        print("✅ MCP registry is valid!")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False

def check_templates_exist(registry_path):
    """Check if all referenced template files exist."""
    registry = load_yaml(registry_path)
    if not registry:
        return False
    
    base_dir = Path(registry_path).parent
    missing_templates = []
    
    for zone in registry.get('mcp_zones', []):
        for mcp in zone.get('mcps', []):
            if 'config_template' in mcp:
                template_path = base_dir / 'templates' / mcp['config_template']
                if not template_path.exists():
                    missing_templates.append({
                        'mcp': mcp['name'],
                        'zone': zone['zone'],
                        'template': mcp['config_template']
                    })
    
    if missing_templates:
        print("\n⚠️  Missing template files:")
        for item in missing_templates:
            print(f"- {item['mcp']} ({item['zone']}): {item['template']}")
        return False
    
    print("✅ All template files exist.")
    return True

if __name__ == "__main__":
    registry_path = Path(__file__).parent / "mcp_registry.yaml"
    
    print(f"Validating MCP registry: {registry_path}")
    print("-" * 50)
    
    schema_valid = validate_registry(registry_path)
    templates_exist = check_templates_exist(registry_path)
    
    if schema_valid and templates_exist:
        print("\n✅ MCP registry validation successful!")
    else:
        print("\n❌ MCP registry validation failed.")
        exit(1)
