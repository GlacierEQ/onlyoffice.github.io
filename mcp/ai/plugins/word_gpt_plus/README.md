# Word-GPT-Plus MCP Plugin

A plugin for the MCP AI system that integrates Word-GPT-Plus functionality, enabling AI-powered document editing and processing within the MCP ecosystem.

## Features

- **AI-Powered Document Editing**: Enhance, rewrite, and generate document content using state-of-the-art language models
- **Multiple AI Providers**: Support for OpenAI, Azure OpenAI, local models, and more
- **Document Processing**: Chunking and processing of large documents with context preservation
- **Customizable UI**: Toolbar buttons, context menus, and settings panels for seamless integration
- **Plugin Architecture**: Extensible design for adding new features and integrations

## Installation

1. Ensure you have the MCP AI system installed and configured
2. Copy the `word_gpt_plus` directory to your MCP plugins directory
3. Install the required dependencies:
   ```bash
   pip install -r word_gpt_plus/requirements.txt
   ```
4. Configure the plugin by editing the MCP configuration file or using the settings UI

## Configuration

Add the following to your MCP configuration file:

```yaml
plugins:
  word_gpt_plus:
    enabled: true
    api:
      provider: openai  # openai, azure, local, ollama, groq
      api_key: your-api-key
      model: gpt-4
      temperature: 0.7
      max_tokens: 2000
    processing:
      chunk_size: 4000
      overlap: 200
      max_retries: 3
      retry_delay: 2
```

## Usage

### Basic Usage

```python
from mcp.ai import get_ai_service

# Get the AI service
service = get_ai_service()

# Get the Word-GPT-Plus plugin
word_gpt = service.get_plugin('word_gpt_plus')

# Process a document
result = word_gpt.process_document(
    document_path='path/to/input.docx',
    instructions='Improve the clarity and conciseness of this document',
    output_path='path/to/output.docx'
)
```

### Advanced Usage

```python
# Get the API client for direct model access
api_client = word_gpt.get_api_client()

# Generate text
response = api_client.generate_text(
    prompt='Write a short story about an AI that writes stories',
    temperature=0.8,
    max_tokens=1000
)

# Get available models
models = api_client.get_available_models()

# Process document in chunks with progress callback
def progress_callback(current, total):
    print(f"Processing: {current}/{total} chunks")

result = word_gpt.process_document(
    document_path='large_document.docx',
    instructions='Summarize each section',
    progress_callback=progress_callback
)
```

## UI Integration

The plugin provides the following UI components:

### Toolbar Buttons
- **AI Edit**: Open the AI editor for the current selection
- **AI Generate**: Generate new content using AI

### Context Menu Items
- **Enhance with AI**: Improve the selected text
- **Summarize**: Create a summary of the selected text

### Settings Panel
Configure API settings, model parameters, and processing options through the MCP settings UI.

## Development

### Adding New Features

1. Create a new Python module in the `word_gpt_plus` directory
2. Implement your feature following the plugin architecture
3. Register any UI components using the `UIManager`
4. Update the documentation

### Testing

Run the test suite:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of the MCP AI platform
- Inspired by the original Word-GPT-Plus project
