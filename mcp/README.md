# MCP Registry for Windsurf

This directory contains the Microservice Control Plane (MCP) registry and configuration for the Windsurf platform.

## Directory Structure

```
mcp/
├── registry/                 # MCP registry definitions
│   ├── mcp_registry.yaml     # Main MCP registry file
│   └── templates/            # Configuration templates for MCPs
│       ├── supervisor.conf.j2
│       ├── systemd.service.j2
│       └── ...
└── README.md                # This file
```

## MCP Registry Structure

The MCP registry is organized into functional zones, each containing related MCP components. Each MCP includes:

- `name`: Unique identifier for the MCP
- `desc`: Brief description
- `url`: Documentation URL
- `functions`: List of key functionalities
- `module`: Implementation module/file
- `status`: Current status (active/planned/optional)
- `config_template`: Template file for configuration

## Adding a New MCP

1. Add the MCP to the appropriate zone in `registry/mcp_registry.yaml`
2. Create a corresponding configuration template in `registry/templates/`
3. Update the documentation as needed

## Usage

To use an MCP in your Windsurf project:

1. Reference the MCP in your project configuration
2. Provide the required configuration parameters
3. The system will automatically apply the appropriate template and settings

## Available MCPs

### SYSTEM/PROCESS
- **Supervisor**: Process supervision and monitoring
- **systemd**: System service management
- **PM2**: Node.js process manager (planned)
- **Kubernetes**: Container orchestration

### AI/AGENT
- **LangChain**: Multi-LLM orchestration
- **LlamaIndex**: Vector DB and document fusion
- **HuggingFace Transformers**: NLP processing

### DATA/EVIDENCE
- **Google Drive API**: Cloud evidence handling
- **Whisper**: Audio transcription
- **Tesseract OCR**: Document OCR

## Configuration

Each MCP can be configured using YAML files that follow the template structure defined in the registry. See individual template files for specific configuration options.
