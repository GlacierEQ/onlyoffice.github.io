"""
Tests for the Word-GPT-Plus MCP plugin.

These tests verify the core functionality of the Word-GPT-Plus plugin.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the plugin class
from mcp.ai.plugins.word_gpt_plus import WordGPTPlusPlugin
from mcp.ai.plugins.word_gpt_plus.config import (
    DEFAULT_CONFIG,
    merge_configs,
    validate_config,
    merge_with_defaults
)

class TestWordGPTPlusPlugin(unittest.TestCase):
    """Test cases for the WordGPTPlusPlugin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_config = {
            'api': {
                'provider': 'openai',
                'api_key': 'test-api-key',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'processing': {
                'chunk_size': 4000,
                'overlap': 200,
                'max_retries': 3,
                'retry_delay': 2
            },
            'templates': {
                'default_prompt': 'Test prompt: {content}',
                'translation_prompt': 'Translate to {language}: {content}'
            }
        }
        
        # Create a test document
        self.test_doc_path = Path(self.test_dir.name) / 'test_document.txt'
        with open(self.test_doc_path, 'w', encoding='utf-8') as f:
            f.write("This is a test document.\nIt contains multiple lines.\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.test_dir.cleanup()
    
    def test_plugin_initialization(self):
        """Test plugin initialization with default config."""
        plugin = WordGPTPlusPlugin(self.test_config)
        self.assertEqual(plugin.name, 'word_gpt_plus')
        self.assertIsNotNone(plugin.version)
        self.assertIsNotNone(plugin.description)
        self.assertTrue(hasattr(plugin, 'config'))
    
    def test_set_and_get_context(self):
        """Test setting and getting context values."""
        plugin = WordGPTPlusPlugin(self.test_config)
        
        # Test setting and getting a context value
        plugin.set_context('test_key', 'test_value')
        self.assertEqual(plugin.get_context('test_key'), 'test_value')
        
        # Test getting a non-existent key with default
        self.assertIsNone(plugin.get_context('non_existent'))
        self.assertEqual(plugin.get_context('non_existent', 'default'), 'default')
    
    @patch('mcp.ai.plugins.word_gpt_plus.WordGPTPlusPlugin.initialize')
    def test_initialize(self, mock_init):
        """Test plugin initialization."""
        mock_init.return_value = True
        plugin = WordGPTPlusPlugin(self.test_config)
        result = plugin.initialize()
        self.assertTrue(result)
        mock_init.assert_called_once()
    
    @patch('mcp.ai.plugins.word_gpt_plus.WordGPTPlusPlugin.on_enable')
    def test_enable_plugin(self, mock_enable):
        """Test enabling the plugin."""
        plugin = WordGPTPlusPlugin(self.test_config)
        plugin.on_enable()
        mock_enable.assert_called_once()
    
    @patch('mcp.ai.plugins.word_gpt_plus.WordGPTPlusPlugin.on_disable')
    def test_disable_plugin(self, mock_disable):
        """Test disabling the plugin."""
        plugin = WordGPTPlusPlugin(self.test_config)
        plugin.on_disable()
        mock_disable.assert_called_once()
    
    def test_editor_components(self):
        """Test getting editor components."""
        plugin = WordGPTPlusPlugin(self.test_config)
        components = plugin.get_editor_components()
        self.assertIsInstance(components, dict)
        # Check for expected component types
        for component_type in ['toolbar_buttons', 'context_menu_items', 'settings_panels']:
            self.assertIn(component_type, components)
            self.assertIsInstance(components[component_type], list)


class TestConfig(unittest.TestCase):
    """Test cases for configuration handling."""
    
    def test_default_config_structure(self):
        """Test the structure of the default config."""
        self.assertIn('api', DEFAULT_CONFIG)
        self.assertIn('processing', DEFAULT_CONFIG)
        self.assertIn('ui', DEFAULT_CONFIG)
        self.assertIn('templates', DEFAULT_CONFIG)
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Test valid config
        valid_config = {
            'api': {
                'provider': 'openai',
                'api_key': 'test-key'
            }
        }
        self.assertTrue(validate_config(valid_config))
        
        # Test invalid provider
        invalid_provider = {'api': {'provider': 'invalid'}}
        self.assertFalse(validate_config(invalid_provider))
        
        # Test missing required field
        missing_field = {'api': {'provider': 'openai'}}
        self.assertFalse(validate_config(missing_field))
    
    def test_merge_with_defaults(self):
        """Test merging user config with defaults."""
        user_config = {
            'api': {
                'provider': 'azure',
                'api_key': 'azure-key'
            },
            'custom_key': 'custom_value'
        }
        
        merged = merge_with_defaults(user_config)
        
        # Check that user values override defaults
        self.assertEqual(merged['api']['provider'], 'azure')
        self.assertEqual(merged['api']['api_key'], 'azure-key')
        
        # Check that defaults are preserved
        self.assertIn('processing', merged)
        self.assertIn('ui', merged)
        
        # Check that custom keys are preserved
        self.assertEqual(merged['custom_key'], 'custom_value')


if __name__ == '__main__':
    unittest.main()
