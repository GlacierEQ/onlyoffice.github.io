"""
Configuration for the Word-GPT-Plus MCP plugin.
"""

from typing import Dict, Any
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    # API Configuration
    'api': {
        'provider': 'openai',  # 'openai', 'azure', 'local', etc.
        'api_key': '',
        'base_url': None,  # Only needed for custom endpoints
        'model': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 2000,
        'timeout': 30,  # seconds
    },
    
    # Document Processing
    'processing': {
        'chunk_size': 4000,  # Characters per chunk for processing
        'overlap': 200,  # Overlap between chunks
        'max_retries': 3,
        'retry_delay': 2,  # seconds
    },
    
    # UI Configuration
    'ui': {
        'show_toolbar': True,
        'show_context_menu': True,
        'dark_mode': True,
        'font_size': 14,
    },
    
    # Templates
    'templates': {
        'default_prompt': 'Improve the following text while maintaining its original meaning and style:',
        'translation_prompt': 'Translate the following text to {language}:',
        'summarize_prompt': 'Summarize the following text concisely:',
    },
    
    # Advanced Settings
    'advanced': {
        'enable_logging': True,
        'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
        'log_file': 'word_gpt_plus.log',
        'cache_enabled': True,
        'cache_ttl': 3600,  # seconds
    },
}

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate the configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    # Check required fields
    required_fields = [
        'api.provider',
        'api.api_key',
    ]
    
    for field in required_fields:
        keys = field.split('.')
        current = config
        for key in keys:
            if key not in current:
                return False
            current = current[key]
            
    # Validate provider
    valid_providers = ['openai', 'azure', 'local', 'ollama', 'groq']
    if config['api']['provider'] not in valid_providers:
        return False
        
    # Validate temperature
    if not 0 <= config['api']['temperature'] <= 2.0:
        return False
        
    return True

def merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge user configuration with defaults.
    
    Args:
        config: User configuration dictionary
        
    Returns:
        Dict[str, Any]: Merged configuration
    """
    result = {}
    
    # Deep merge dictionaries
    def merge(d1, d2):
        for k, v in d2.items():
            if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                d1[k] = merge(d1[k], v)
            else:
                d1[k] = v
        return d1
    
    # Start with defaults and merge with user config
    import copy
    result = copy.deepcopy(DEFAULT_CONFIG)
    return merge(result, config)
