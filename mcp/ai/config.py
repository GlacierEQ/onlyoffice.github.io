"""
AI Integration Configuration

This module handles configuration management for the MCP AI system.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class AIConfig:
    """
    Configuration manager for MCP AI system.
    
    This class handles loading, validating, and accessing configuration
    settings from YAML files and environment variables.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            config_path: Optional path to a YAML configuration file.
                        If not provided, will look for 'config.yaml' in the
                        standard locations.
        """
        self.config: Dict[str, Any] = {}
        self.config_path = self._find_config_file(config_path)
        self._load_config()
    
    def _find_config_file(self, config_path: Optional[str] = None) -> Optional[Path]:
        """Find the configuration file in standard locations."""
        if config_path and os.path.isfile(config_path):
            return Path(config_path)
            
        # Check standard locations
        search_paths = [
            Path('config.yaml'),
            Path('config/config.yaml'),
            Path('mcp/ai/config.yaml'),
            Path.home() / '.config' / 'mcp' / 'ai.yaml',
        ]
        
        for path in search_paths:
            if path.exists() and path.is_file():
                return path
        return None
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Default configuration
        self.config = {
            'ai': {
                'providers': {
                    'openai': {
                        'api_key': os.getenv('OPENAI_API_KEY', ''),
                        'model': 'gpt-4',
                    },
                    'huggingface': {
                        'api_key': os.getenv('HUGGINGFACE_API_KEY', ''),
                        'model': 'gpt2',
                    },
                    'langchain': {
                        'api_key': os.getenv('LANGCHAIN_API_KEY', ''),
                    },
                },
                'plugins': {
                    'documentation': {
                        'enabled': True,
                        'templates_dir': str(Path(__file__).parent / 'templates'),
                    },
                    'editor': {
                        'enabled': True,
                    },
                },
            },
            'logging': {
                'level': 'INFO',
                'file': 'mcp_ai.log',
            },
        }
        
        # Load from file if exists
        if self.config_path and self.config_path.exists():
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
                self._merge_dicts(self.config, file_config)
    
    def _merge_dicts(self, base: Dict, update: Dict) -> Dict:
        """Recursively merge two dictionaries."""
        for key, value in update.items():
            if (key in base and isinstance(base[key], dict) and 
                isinstance(value, dict)):
                self._merge_dicts(base[key], value)
            else:
                base[key] = value
        return base
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot notation."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot notation."""
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save the current configuration to a file."""
        save_path = Path(path) if path else self.config_path
        if not save_path:
            save_path = Path('config.yaml')
            
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

# Global configuration instance
config: Optional[AIConfig] = None

def get_config() -> AIConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = AIConfig()
    return config

def init_config(config_path: Optional[str] = None) -> AIConfig:
    """Initialize the global configuration."""
    global config
    config = AIConfig(config_path)
    return config
