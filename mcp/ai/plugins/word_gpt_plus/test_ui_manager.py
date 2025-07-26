"""
Tests for the UIManager class in the Word-GPT-Plus MCP plugin.
"""

import unittest
from unittest.mock import MagicMock, patch

# Add the plugin directory to the path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from word_gpt_plus.ui_manager import UIManager

class TestUIManager(unittest.TestCase):
    """Test cases for the UIManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            'ui': {
                'theme': 'light',
                'font_size': 14,
                'show_toolbar': True,
                'show_status_bar': True
            },
            'templates': {
                'default_prompt': 'Process this text: {content}'
            }
        }
        
        # Create a mock plugin
        self.plugin = MagicMock()
        self.plugin.name = 'word_gpt_plus'
        
        # Create the UI manager
        self.ui_manager = UIManager(self.config, self.plugin)
    
    def test_initialization(self):
        """Test UI manager initialization."""
        self.assertEqual(self.ui_manager.config, self.config)
        self.assertEqual(self.ui_manager.plugin, self.plugin)
        self.assertEqual(len(self.ui_manager.components), 0)
    
    def test_initialize(self):
        """Test UI manager initialization with default components."""
        # Initialize the UI manager (should register default components)
        result = self.ui_manager.initialize()
        
        # Should return True on success
        self.assertTrue(result)
        
        # Should have registered components
        self.assertGreater(len(self.ui_manager.components), 0)
        
        # Check that default components were registered
        self.assertIn('toolbar_button', self.ui_manager.components)
        self.assertIn('context_menu', self.ui_manager.components)
        self.assertIn('settings_panel', self.ui_manager.components)
    
    def test_register_component(self):
        """Test registering a UI component."""
        # Define a test component
        component_type = 'test_component'
        component_id = 'test_button'
        component_config = {
            'label': 'Test Button',
            'action': 'test_action',
            'icon': 'test_icon'
        }
        
        # Register the component
        result = self.ui_manager.register_component(
            component_type=component_type,
            component_id=component_id,
            config=component_config,
            callback=lambda: 'test_callback'
        )
        
        # Should return True on success
        self.assertTrue(result)
        
        # Should be able to retrieve the component
        component = self.ui_manager.get_component(component_type, component_id)
        self.assertIsNotNone(component)
        self.assertEqual(component['config'], component_config)
        self.assertIsNotNone(component['callback'])
    
    def test_unregister_component(self):
        """Test unregistering a UI component."""
        # Register a test component
        self.ui_manager.register_component(
            'test_component',
            'test_button',
            {'label': 'Test Button'}
        )
        
        # Should be able to retrieve the component
        self.assertIsNotNone(
            self.ui_manager.get_component('test_component', 'test_button')
        )
        
        # Unregister the component
        result = self.ui_manager.unregister_component('test_component', 'test_button')
        
        # Should return True on success
        self.assertTrue(result)
        
        # Should no longer be able to retrieve the component
        self.assertIsNone(
            self.ui_manager.get_component('test_component', 'test_button')
        )
    
    def test_get_components_by_type(self):
        """Test getting all components of a specific type."""
        # Register some test components
        self.ui_manager.register_component('toolbar_button', 'button1', {'label': 'Button 1'})
        self.ui_manager.register_component('toolbar_button', 'button2', {'label': 'Button 2'})
        self.ui_manager.register_component('context_menu', 'menu1', {'label': 'Menu 1'})
        
        # Get all toolbar buttons
        toolbar_buttons = self.ui_manager.get_components_by_type('toolbar_button')
        
        # Should have 2 toolbar buttons
        self.assertEqual(len(toolbar_buttons), 2)
        self.assertIn('button1', toolbar_buttons)
        self.assertIn('button2', toolbar_buttons)
        
        # Get all context menus
        context_menus = self.ui_manager.get_components_by_type('context_menu')
        
        # Should have 1 context menu
        self.assertEqual(len(context_menus), 1)
        self.assertIn('menu1', context_menus)
    
    def test_handle_action(self):
        """Test handling a UI action with a callback."""
        # Create a mock callback
        callback_mock = MagicMock(return_value='test_result')
        
        # Register a test component with the callback
        self.ui_manager.register_component(
            'test_component',
            'test_button',
            {'label': 'Test Button'},
            callback=callback_mock
        )
        
        # Handle the action
        test_data = {'param1': 'value1'}
        result = self.ui_manager.handle_action(
            component_type='test_component',
            component_id='test_button',
            data=test_data
        )
        
        # Should have called the callback with the test data
        callback_mock.assert_called_once_with(test_data)
        
        # Should have returned the callback result
        self.assertEqual(result, 'test_result')
    
    def test_show_notification(self):
        """Test showing a notification."""
        # This is a simple test that just verifies the method exists and logs the notification
        with patch('word_gpt_plus.ui_manager.logger.info') as mock_logger:
            self.ui_manager.show_notification(
                'Test message',
                title='Test Title',
                type='info',
                duration=5000
            )
            
            # Should have logged the notification
            mock_logger.assert_called()
            log_message = mock_logger.call_args[0][0]
            self.assertIn('Test Title', log_message)
            self.assertIn('Test message', log_message)
    
    def test_show_modal(self):
        """Test showing a modal dialog."""
        # This is a simple test that just verifies the method exists and logs the action
        with patch('word_gpt_plus.ui_manager.logger.info') as mock_logger:
            result = self.ui_manager.show_modal(
                component='TestComponent',
                props={'title': 'Test Modal'},
                options={'size': 'large'}
            )
            
            # Should have logged the modal show action
            mock_logger.assert_called_once()
            self.assertIn('TestComponent', mock_logger.call_args[0][0])
            
            # Should return None (placeholder implementation)
            self.assertIsNone(result)
    
    def test_update_status(self):
        """Test updating the status bar."""
        # This is a simple test that just verifies the method exists and logs the status
        with patch('word_gpt_plus.ui_manager.logger.info') as mock_logger:
            self.ui_manager.update_status(
                message='Processing document...',
                type='info'
            )
            
            # Should have logged the status update
            mock_logger.assert_called_once()
            log_message = mock_logger.call_args[0][0]
            self.assertIn('Processing document...', log_message)
    
    def test_update_config(self):
        """Test updating the UI configuration."""
        # Initial config should have 'light' theme
        self.assertEqual(self.ui_manager.config['ui']['theme'], 'light')
        
        # Update the config
        self.ui_manager.update_config({
            'ui': {
                'theme': 'dark',
                'font_size': 16
            },
            'new_setting': 'value'
        })
        
        # Should have updated the theme and font size
        self.assertEqual(self.ui_manager.config['ui']['theme'], 'dark')
        self.assertEqual(self.ui_manager.config['ui']['font_size'], 16)
        
        # Should have preserved other settings
        self.assertEqual(self.ui_manager.config['ui']['show_toolbar'], True)
        
        # Should have added the new setting
        self.assertEqual(self.ui_manager.config['new_setting'], 'value')


if __name__ == '__main__':
    unittest.main()
