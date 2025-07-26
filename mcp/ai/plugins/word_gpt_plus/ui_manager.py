"""
UI Manager for Word-GPT-Plus MCP plugin.

Handles user interface components and interactions.
"""

from typing import Dict, List, Optional, Callable, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UIManager:
    """Manages UI components for the Word-GPT-Plus plugin."""
    
    def __init__(self, config: Dict[str, Any], plugin):
        """Initialize the UI manager."""
        self.config = config
        self.plugin = plugin
        self.components: Dict[str, Dict] = {}
        
    def initialize(self) -> bool:
        """Initialize UI components."""
        try:
            # Register default UI components
            self._register_default_components()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize UI manager: {str(e)}")
            return False
    
    def _register_default_components(self) -> None:
        """Register default UI components."""
        # Toolbar buttons
        self.register_component(
            'toolbar_button',
            'ai_edit',
            {
                'label': 'AI Edit',
                'icon': 'edit',
                'tooltip': 'Edit selection with AI',
                'action': 'ai_edit',
                'category': 'ai'
            }
        )
        
        self.register_component(
            'toolbar_button',
            'ai_generate',
            {
                'label': 'AI Generate',
                'icon': 'auto_awesome',
                'tooltip': 'Generate content with AI',
                'action': 'ai_generate',
                'category': 'ai'
            }
        )
        
        # Context menu items
        self.register_component(
            'context_menu',
            'enhance_text',
            {
                'label': 'Enhance with AI',
                'action': 'enhance_text',
                'icon': 'auto_fix_high',
                'contexts': ['selection']
            }
        )
        
        self.register_component(
            'context_menu',
            'summarize_text',
            {
                'label': 'Summarize',
                'action': 'summarize_text',
                'icon': 'summarize',
                'contexts': ['selection']
            }
        )
        
        # Settings panel
        self.register_component(
            'settings_panel',
            'ai_settings',
            {
                'title': 'AI Settings',
                'icon': 'settings',
                'component': 'AISettingsPanel',
                'priority': 100
            }
        )
    
    def register_component(
        self,
        component_type: str,
        component_id: str,
        config: Dict[str, Any],
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Register a UI component.
        
        Args:
            component_type: Type of component ('toolbar_button', 'context_menu', etc.)
            component_id: Unique identifier for the component
            config: Component configuration
            callback: Optional callback function for component actions
            
        Returns:
            bool: True if registration was successful
        """
        if component_type not in self.components:
            self.components[component_type] = {}
            
        if component_id in self.components[component_type]:
            logger.warning(f"Component {component_id} of type {component_type} already exists. Overwriting.")
            
        self.components[component_type][component_id] = {
            'config': config,
            'callback': callback
        }
        
        logger.info(f"Registered UI component: {component_type}.{component_id}")
        return True
    
    def unregister_component(self, component_type: str, component_id: str) -> bool:
        """
        Unregister a UI component.
        
        Args:
            component_type: Type of component
            component_id: Component identifier
            
        Returns:
            bool: True if component was found and removed
        """
        if component_type in self.components and component_id in self.components[component_type]:
            del self.components[component_type][component_id]
            logger.info(f"Unregistered UI component: {component_type}.{component_id}")
            return True
        return False
    
    def get_component(self, component_type: str, component_id: str) -> Optional[Dict]:
        """
        Get a UI component by type and ID.
        
        Args:
            component_type: Type of component
            component_id: Component identifier
            
        Returns:
            Optional[Dict]: Component configuration and callback, or None if not found
        """
        return self.components.get(component_type, {}).get(component_id)
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Dict]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            Dict[str, Dict]: Dictionary of component configurations keyed by component ID
        """
        return self.components.get(component_type, {})
    
    def handle_action(self, component_type: str, component_id: str, data: Any = None) -> Any:
        """
        Handle a UI action.
        
        Args:
            component_type: Type of component that triggered the action
            component_id: ID of the component
            data: Additional data for the action
            
        Returns:
            Any: Result of the action, or None if no callback was found
        """
        component = self.get_component(component_type, component_id)
        if component and component['callback']:
            try:
                return component['callback'](data)
            except Exception as e:
                logger.error(f"Error in action handler for {component_type}.{component_id}: {str(e)}")
                raise
        return None
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the UI configuration.
        
        Args:
            config: New configuration values
        """
        self.config.update(config)
        # TODO: Notify UI components of config changes
    
    def show_notification(
        self,
        message: str,
        title: str = "Word-GPT-Plus",
        type: str = "info",
        duration: int = 5000
    ) -> None:
        """
        Show a notification to the user.
        
        Args:
            message: Notification message
            title: Notification title
            type: Notification type ('info', 'success', 'warning', 'error')
            duration: Duration in milliseconds (0 for persistent)
        """
        # This would be implemented to work with the host application's notification system
        logger.info(f"[{type.upper()}] {title}: {message}")
        # TODO: Implement actual UI notification
    
    def show_modal(
        self,
        component: str,
        props: Optional[Dict] = None,
        options: Optional[Dict] = None
    ) -> Any:
        """
        Show a modal dialog.
        
        Args:
            component: Name of the component to render in the modal
            props: Props to pass to the component
            options: Modal options (size, title, etc.)
            
        Returns:
            Any: Result from the modal, if any
        """
        logger.info(f"Showing modal: {component}")
        # TODO: Implement modal dialog
        return None
    
    def update_status(self, message: str, type: str = "info") -> None:
        """
        Update the status bar message.
        
        Args:
            message: Status message
            type: Message type ('info', 'success', 'warning', 'error')
        """
        logger.info(f"Status ({type}): {message}")
        # TODO: Update status bar in UI
