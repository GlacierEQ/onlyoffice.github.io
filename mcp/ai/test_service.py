"""
Test script for the MCP AI Service.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from mcp.ai.service import AIService, get_ai_service
from mcp.ai.config import AIConfig
from mcp.ai.plugin import AIPlugin, AIPluginManager

# Test plugin directory
TEST_PLUGIN_DIR = Path(__file__).parent / "test_plugins"

# Sample plugin content
SAMPLE_PLUGIN = '''
"""Test plugin for MCP AI Service."""

from mcp.ai.plugin import AIPlugin

class TestPlugin(AIPlugin):
    """Test plugin implementation."""
    
    def __init__(self, config=None):
        super().__init__(config or {})
        self.initialized = False
        self.shutdown_called = False
    
    @property
    def name(self):
        return "test_plugin"
        
    @property
    def version(self):
        return "1.0.0"
        
    @property
    def description(self):
        return "Test plugin for MCP AI Service"
    
    def on_enable(self):
        """Called when the plugin is enabled."""
        self.initialized = True
    
    def on_disable(self):
        """Called when the plugin is disabled."""
        self.shutdown_called = True
'''

def create_test_plugin_dir():
    """Create a test plugin directory with a sample plugin."""
    # Create test plugin directory
    os.makedirs(TEST_PLUGIN_DIR, exist_ok=True)
    
    # Create test plugin file
    plugin_file = TEST_PLUGIN_DIR / "test_plugin.py"
    with open(plugin_file, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_PLUGIN)
    
    # Create __init__.py if it doesn't exist
    init_file = TEST_PLUGIN_DIR / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    
    return TEST_PLUGIN_DIR

def cleanup_test_plugin_dir():
    """Clean up the test plugin directory."""
    if TEST_PLUGIN_DIR.exists():
        shutil.rmtree(TEST_PLUGIN_DIR, ignore_errors=True)

def test_ai_service_initialization():
    """Test AIService initialization."""
    # Create a test config
    config = AIConfig()
    config.set('logging.level', 'DEBUG')
    
    # Initialize the service
    service = AIService()
    
    # Test initialization
    assert service.initialize()
    
    # Test shutdown
    service.shutdown()

def test_ai_service_with_plugins():
    """Test AIService with plugins."""
    # Create test plugin directory
    plugin_dir = create_test_plugin_dir()
    
    try:
        # Create a test config with plugin settings
        config = AIConfig()
        config.set('logging.level', 'DEBUG')
        
        # Add test plugin directory to Python path
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))
        
        # Initialize the plugin manager directly for testing
        plugin_manager = AIPluginManager(plugin_dirs=[str(plugin_dir)])
        
        # Discover and load the test plugin
        plugin_manager.discover_plugins()
        assert 'test_plugin' in plugin_manager.get_available_plugins()
        
        # Load the plugin
        plugin = plugin_manager.load_plugin('test_plugin')
        assert plugin is not None
        assert plugin.name == 'test_plugin'
        
        # Test plugin initialization
        assert not plugin.initialized
        plugin.on_enable()
        assert plugin.initialized
        
        # Test plugin shutdown
        assert not plugin.shutdown_called
        plugin.on_disable()
        assert plugin.shutdown_called
        
    finally:
        # Clean up
        cleanup_test_plugin_dir()
        if str(plugin_dir) in sys.path:
            sys.path.remove(str(plugin_dir))

def test_global_ai_service():
    """Test the global AIService instance."""
    # Get the global service
    service1 = get_ai_service()
    service2 = get_ai_service()
    
    # Should be the same instance
    assert service1 is service2
    
    # Test initialization
    assert service1.initialize()
    
    # Clean up
    service1.shutdown()

if __name__ == "__main__":
    # Run tests
    import sys
    import pytest
    
    # Create a test plugin directory for the tests
    create_test_plugin_dir()
    
    try:
        # Run pytest
        exit_code = pytest.main([__file__, '-v'])
    finally:
        # Clean up
        cleanup_test_plugin_dir()
    
    sys.exit(exit_code)
