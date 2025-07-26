"""
MCP AI Service

Core service for managing AI plugins and providing AI capabilities.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable

from .plugin import AIPlugin, AIPluginManager, AIDocumentationGenerator, AIEditorIntegration
from .config import get_config

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=AIPlugin)

class AIService:
    """Core AI service for the MCP system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI service."""
        self.config = get_config()
        self.plugin_manager = AIPluginManager(
            plugin_dirs=self.config.get('ai.plugin_dirs', [])
        )
        self._plugins_loaded = False
        self._initialized = False
        self._event_handlers = {
            'documentation_generated': [],
            'editor_update': [],
            'ai_error': []
        }
    
    def initialize(self) -> bool:
        """Initialize the AI service and load plugins."""
        if self._initialized:
            return True
            
        try:
            # Discover and load plugins
            self.plugin_manager.discover_plugins()
            
            # Load default plugins
            for plugin_name in self.config.get('ai.default_plugins', []):
                plugin_config = self.config.get_plugin_config(plugin_name)
                self.load_plugin(plugin_name, plugin_config)
            
            self._initialized = True
            logger.info("AI service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}", exc_info=True)
            return False
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[AIPlugin]:
        """Load a specific plugin."""
        plugin = self.plugin_manager.load_plugin(plugin_name, config)
        if plugin:
            self._register_plugin_handlers(plugin)
        return plugin
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin."""
        self._unregister_plugin_handlers(plugin_name)
        return self.plugin_manager.unload_plugin(plugin_name)
    
    def _register_plugin_handlers(self, plugin: AIPlugin) -> None:
        """Register event handlers for a plugin."""
        if hasattr(plugin, 'on_documentation_generated'):
            self._event_handlers['documentation_generated'].append(
                plugin.on_documentation_generated
            )
        
        if hasattr(plugin, 'on_editor_update'):
            self._event_handlers['editor_update'].append(
                plugin.on_editor_update
            )
    
    def _unregister_plugin_handlers(self, plugin_name: str) -> None:
        """Unregister event handlers for a plugin."""
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return
            
        for event, handlers in self._event_handlers.items():
            if hasattr(plugin, f'on_{event}'):
                handler = getattr(plugin, f'on_{event}')
                if handler in handlers:
                    handlers.remove(handler)
    
    def get_plugin(self, plugin_name: str, plugin_type: Type[T] = None) -> Optional[T]:
        """Get a loaded plugin by name and optionally type."""
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin and (plugin_type is None or isinstance(plugin, plugin_type)):
            return plugin
        return None
    
    def get_documentation_generators(self) -> List[AIDocumentationGenerator]:
        """Get all loaded documentation generator plugins."""
        return [
            plugin for plugin in self.plugin_manager.get_all_plugins()
            if isinstance(plugin, AIDocumentationGenerator)
        ]
    
    def get_editor_integrations(self) -> List[AIEditorIntegration]:
        """Get all loaded editor integration plugins."""
        return [
            plugin for plugin in self.plugin_manager.get_all_plugins()
            if isinstance(plugin, AIEditorIntegration)
        ]
    
    def generate_documentation(self, mcp_data: Dict[str, Any], **kwargs) -> str:
        """
        Generate documentation for an MCP component.
        
        Args:
            mcp_data: Dictionary containing MCP component data
            **kwargs: Additional arguments for documentation generation
            
        Returns:
            str: Generated documentation
        """
        if not self._initialized:
            self.initialize()
            
        # Get the first available documentation generator
        doc_generators = self.get_documentation_generators()
        if not doc_generators:
            raise RuntimeError("No documentation generator plugins available")
            
        # Use the first available generator (can be extended to support multiple)
        generator = doc_generators[0]
        try:
            result = generator.generate_documentation(mcp_data, **kwargs)
            self._emit_event('documentation_generated', {
                'mcp_data': mcp_data,
                'result': result,
                'generator': generator.name
            })
            return result
        except Exception as e:
            self._emit_event('ai_error', {
                'error': str(e),
                'context': 'documentation_generation',
                'mcp_data': mcp_data
            })
            raise
    
    def update_editor_state(self, state: Dict[str, Any]) -> None:
        """
        Update the editor state and notify all editor integration plugins.
        
        Args:
            state: Dictionary containing the current editor state
        """
        if not self._initialized:
            self.initialize()
            
        self._emit_event('editor_update', state)
    
    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers."""
        if event_name not in self._event_handlers:
            logger.warning(f"Unknown event: {event_name}")
            return
            
        for handler in self._event_handlers[event_name]:
            try:
                handler(data)
            except Exception as e:
                logger.error(
                    f"Error in {event_name} handler {handler.__name__}: {e}",
                    exc_info=True
                )


# Global AI service instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get the global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
        _ai_service.initialize()
    return _ai_service
