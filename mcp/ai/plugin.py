"""
MCP AI Plugin System

Defines the base interfaces and core functionality for AI plugins.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from pathlib import Path
import importlib.util
import inspect
import logging
import pkgutil
import sys

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='AIPlugin')

class AIPlugin(ABC):
    """Base class for all AI plugins."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the plugin with optional configuration."""
        self.config = config or {}
        self._context = {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the plugin."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return the version of the plugin."""
        pass
    
    @property
    def description(self) -> str:
        """Return a description of the plugin."""
        return ""
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a value in the plugin's context."""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a value from the plugin's context."""
        return self._context.get(key, default)
    
    def on_enable(self) -> None:
        """Called when the plugin is enabled."""
        pass
    
    def on_disable(self) -> None:
        """Called when the plugin is disabled."""
        pass


class AIPluginManager:
    """Manages the lifecycle of AI plugins."""
    
    def __init__(self, plugin_dirs: List[str] = None):
        """Initialize the plugin manager with optional plugin directories."""
        self.plugins: Dict[str, AIPlugin] = {}
        self.plugin_dirs = plugin_dirs or []
        self._discovered_plugins: Dict[str, Type[AIPlugin]] = {}
    
    def discover_plugins(self) -> None:
        """Discover all available plugins in the configured directories."""
        self._discovered_plugins.clear()
        
        # Add the current directory to the Python path
        for plugin_dir in self.plugin_dirs:
            if not Path(plugin_dir).exists():
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue
                
            # Add the directory to the Python path
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            
            # Find all Python modules in the directory
            for finder, name, _ in pkgutil.iter_modules([plugin_dir]):
                try:
                    module = importlib.import_module(name)
                    self._find_plugins_in_module(module)
                except ImportError as e:
                    logger.error(f"Failed to import plugin module {name}: {e}")
    
    def _find_plugins_in_module(self, module) -> None:
        """Find all plugin classes in a module."""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, AIPlugin) and 
                obj is not AIPlugin):
                plugin_name = getattr(obj, 'name', None) or obj.__name__
                self._discovered_plugins[plugin_name] = obj
                logger.debug(f"Discovered plugin: {plugin_name}")
    
    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> Optional[AIPlugin]:
        """Load a specific plugin by name."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
            
        if plugin_name not in self._discovered_plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return None
            
        try:
            plugin_class = self._discovered_plugins[plugin_name]
            plugin = plugin_class(config or {})
            self.plugins[plugin_name] = plugin
            plugin.on_enable()
            logger.info(f"Loaded plugin: {plugin_name}")
            return plugin
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}", exc_info=True)
            return None
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            return False
            
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_disable()
            del self.plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}", exc_info=True)
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[AIPlugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[AIPlugin]:
        """Get all loaded plugins."""
        return list(self.plugins.values())
    
    def get_available_plugins(self) -> List[str]:
        """Get names of all available (discovered) plugins."""
        return list(self._discovered_plugins.keys())


class AIDocumentationGenerator(AIPlugin):
    """Base class for documentation generation plugins."""
    
    @abstractmethod
    def generate_documentation(self, mcp_data: Dict[str, Any], **kwargs) -> str:
        """Generate documentation for an MCP component."""
        pass


class AIEditorIntegration(AIPlugin):
    """Base class for editor integration plugins."""
    
    @abstractmethod
    def get_editor_components(self) -> Dict[str, Any]:
        """Return editor UI components provided by this plugin."""
        pass
    
    @abstractmethod
    def update_editor_state(self, state: Dict[str, Any]) -> None:
        """Update the editor state."""
        pass
