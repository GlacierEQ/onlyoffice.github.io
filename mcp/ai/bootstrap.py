"""
MCP AI Bootstrap Script

This script sets up a self-contained Python environment with all required
dependencies for the MCP AI integration.
"""

import os
import sys
import venv
import subprocess
import platform
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS = PROJECT_ROOT / "requirements-ai.txt"
PYTHON = sys.executable
IS_WINDOWS = platform.system() == "Windows"

# Environment variables to set
ENV_VARS = {
    "PYTHONPATH": str(PROJECT_ROOT),
    "OPENAI_API_KEY": "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",
    "HUGGINGFACE_API_KEY": "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",
    "ANTHROPIC_API_KEY": "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",
    "ELEVENLABS_API_KEY": "sk_7ba5561fd9b8e04636ed42aa76556682e55066d470968ad6",
    "DEEPSEEK_API_KEY": "sk-c9e21ddc0f8d4ec8a32312492e961f7d",
    "PERPLEXITY_API_KEY": "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",
    "GROQ_API_KEY": "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",
    "LANGCHAIN_API_KEY": "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",
}

def create_virtualenv():
    """Create a new virtual environment if it doesn't exist."""
    if not VENV_DIR.exists():
        print(f"Creating virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        print("Virtual environment created.")
    else:
        print(f"Using existing virtual environment at {VENV_DIR}")

def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if IS_WINDOWS:
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def install_dependencies():
    """Install required packages into the virtual environment."""
    python = get_venv_python()
    
    # Upgrade pip first
    print("Upgrading pip...")
    subprocess.check_call([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    print("Installing dependencies...")
    subprocess.check_call([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    
    # Install development tools
    subprocess.check_call([str(python), "-m", "pip", "install", "black", "mypy", "pylint", "pytest"])

def setup_environment():
    """Set up the environment variables."""
    # Create .env file
    env_file = PROJECT_ROOT / ".env"
    with open(env_file, "w") as f:
        for key, value in ENV_VARS.items():
            f.write(f"{key}={value}\n")
    
    print(f"Environment variables written to {env_file}")
    
    # Set environment variables in current process
    os.environ.update(ENV_VARS)

def create_launch_script():
    """Create a launch script for the AI service."""
    script_content = """#!/usr/bin/env bash
# Launch the MCP AI service with the correct environment

# Set up environment
cd "$(dirname "$0")/.."
source .venv/bin/activate

# Set environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the AI service
python -m mcp.ai.service
"""
    
    if IS_WINDOWS:
        script_path = PROJECT_ROOT / "launch_ai.bat"
        with open(script_path, "w") as f:
            f.write("@echo off\n")
            f.write(f"call {VENV_DIR}\\Scripts\\activate.bat\n")
            f.write("python -m mcp.ai.service\n")
            f.write("pause\n")
    else:
        script_path = PROJECT_ROOT / "launch_ai.sh"
        with open(script_path, "w") as f:
            f.write(script_content)
        script_path.chmod(0o755)  # Make it executable
    
    print(f"Launch script created at {script_path}")

def main():
    """Main entry point for the bootstrap script."""
    print("Setting up MCP AI environment...")
    print(f"Project root: {PROJECT_ROOT}")
    
    try:
        # Create virtual environment
        create_virtualenv()
        
        # Install dependencies
        install_dependencies()
        
        # Set up environment
        setup_environment()
        
        # Create launch script
        create_launch_script()
        
        print("\nSetup completed successfully!")
        print("\nTo start the AI service, run:")
        if IS_WINDOWS:
            print(f"  .\\launch_ai.bat")
        else:
            print(f"  ./launch_ai.sh")
            
    except Exception as e:
        print(f"\nError during setup: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
