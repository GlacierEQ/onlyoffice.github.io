# MCP AI Integration

This module provides AI-powered features for the MCP (Microservice Control Plane) system, including documentation generation, code analysis, and intelligent editing capabilities.

## Features

- **Pluggable Architecture**: Easily extendable with custom AI plugins
- **Documentation Generation**: AI-powered documentation for MCP components
- **Multiple AI Backends**: Support for OpenAI, HuggingFace, and other LLM providers
- **Self-Contained**: Manages its own dependencies and environment

## Quick Start

### Prerequisites

- Python 3.8+
- Git
- pip

### Installation

1. **Bootstrap the Environment**:
   ```bash
   # Run the bootstrap script
   python -m mcp.ai.bootstrap
   ```

2. **Activate the Virtual Environment**:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

3. **Run the AI Service**:
   ```bash
   python -m mcp.ai
   ```
   Or use the generated launcher script:
   - Windows: `launch_ai.bat`
   - Linux/Mac: `./launch_ai.sh`

## Configuration

Configuration is managed through environment variables. The bootstrap script creates a `.env` file with default values.

### Important Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `HUGGINGFACE_API_KEY`: Your HuggingFace API key
- `LANGCHAIN_API_KEY`: Your LangChain API key (optional)
- `DEEPSEEK_API_KEY`: Your DeepSeek API key (optional)

## Using the Documentation Generator

```python
from mcp.ai.service import get_ai_service

# Initialize the AI service
ai_service = get_ai_service()

# Generate documentation for an MCP component
mcp_data = {
    "name": "Supervisor",
    "desc": "Process supervisor for agent restart and monitoring",
    "url": "http://supervisord.org/",
    "functions": ["Auto-restart agents/services", "Log process incidents"],
    "module": "supervisor.conf",
    "status": "active"
}

docs = ai_service.generate_documentation(mcp_data)
print(docs)
```

## Plugin Development

To create a custom AI plugin:

1. Create a new Python module in `mcp/ai/plugins/`
2. Create a class that inherits from `AIPlugin`
3. Implement the required methods
4. Add a `create_plugin` function that returns an instance of your plugin

Example plugin:

```python
from mcp.ai.plugin import AIPlugin

class MyPlugin(AIPlugin):
    name = "my_plugin"
    version = "0.1.0"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Initialize your plugin

def create_plugin(config=None):
    return MyPlugin(config)
```

## Directory Structure

```
mcp/ai/
├── __init__.py           # Package initialization
├── __main__.py          # Main entry point
├── bootstrap.py         # Environment setup script
├── config.py            # Configuration management
├── plugin.py            # Plugin system
├── service.py           # Core AI service
├── plugins/             # AI plugins
│   ├── __init__.py
│   └── documentation/   # Documentation generation plugins
│       ├── __init__.py
│       └── langchain_docs.py
└── templates/           # Documentation templates
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
