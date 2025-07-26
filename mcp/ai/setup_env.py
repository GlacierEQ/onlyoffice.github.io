"""
MCP AI Environment Setup

This script sets up a self-contained Python environment with all dependencies
in the project directory, making it portable and easy to maintain.
"""

import os
import sys
import platform
import subprocess
import shutil
import stat
import urllib.request
import zipfile
import json
from pathlib import Path

# Configuration
PYTHON_VERSION = "3.11.9"
REQUIREMENTS = [
    "langchain>=0.0.200",
    "langchain-openai>=0.0.1",
    "openai>=1.0.0",
    "huggingface-hub>=0.16.0",
    "transformers>=4.30.0",
    "jinja2>=3.0.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
    "tqdm>=4.65.0",
]

# Platform-specific configuration
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
    PYTHON_EXE = "python.exe"
    PIP_EXE = "Scripts/pip.exe"
    BIN_DIR = "Scripts"
    PATH_SEP = ";"
else:
    PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/Python-{PYTHON_VERSION}.tgz"
    PYTHON_EXE = "bin/python3"
    PIP_EXE = "bin/pip"
    BIN_DIR = "bin"
    PATH_SEP = ":"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * len(text))

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def run_command(cmd, cwd=None, env=None):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=IS_WINDOWS
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print_error(f"Error: {e.stderr}")
        sys.exit(1)

def download_file(url, dest):
    """Download a file from URL to destination."""
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as response, open(dest, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print_error(f"Failed to download {url}: {e}")
        return False

def setup_virtualenv(env_dir):
    """Set up a virtual environment in the specified directory."""
    print_header("Setting up Python environment")
    
    # Create directories
    (env_dir / "lib").mkdir(parents=True, exist_ok=True)
    (env_dir / "bin").mkdir(parents=True, exist_ok=True)
    
    # Download and extract Python
    python_archive = env_dir / "python.zip"
    if not download_file(PYTHON_URL, python_archive):
        sys.exit(1)
    
    print(f"Extracting Python to {env_dir}...")
    with zipfile.ZipFile(python_archive, 'r') as zip_ref:
        zip_ref.extractall(env_dir)
    
    python_archive.unlink()
    
    # Create a .pth file to include our packages
    with open(env_dir / "site-packages.pth", 'w') as f:
        f.write("""
import sys
import os

# Add vendor packages to path
vendor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vendor')
if os.path.exists(vendor_path):
    sys.path.insert(0, vendor_path)
""")
    
    print_success("Python environment set up successfully")

def install_packages(env_dir):
    """Install required packages into the environment."""
    print_header("Installing dependencies")
    
    # Create requirements file
    requirements = env_dir / "requirements.txt"
    with open(requirements, 'w') as f:
        f.write("\n".join(REQUIREMENTS))
    
    # Install packages using pip
    python_exe = env_dir / PYTHON_EXE
    pip_cmd = [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"]
    run_command(pip_cmd, cwd=env_dir)
    
    pip_install = [str(python_exe), "-m", "pip", "install", "-r", str(requirements)]
    if IS_WINDOWS:
        pip_install.extend(["--target", str(env_dir / "Lib" / "site-packages")])
    else:
        pip_install.extend(["--prefix", str(env_dir)])
    
    run_command(pip_install, cwd=env_dir)
    
    print_success("Dependencies installed successfully")

def create_launcher_script(env_dir):
    """Create launcher scripts for the application."""
    print_header("Creating launcher scripts")
    
    # Create a .env file with API keys
    env_file = env_dir.parent / ".env"
    with open(env_file, 'w') as f:
        f.write("""# MCP AI Environment Variables
OPENAI_API_KEY=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
HUGGINGFACE_API_KEY=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
LANGCHAIN_API_KEY=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
""")
    
    # Create launcher script
    if IS_WINDOWS:
        launcher = env_dir.parent / "mcp-ai.bat"
        with open(launcher, 'w') as f:
            f.write("""@echo off
setlocal

:: Set environment variables
set PYTHONPATH=%~dp0vendor\Lib;%~dp0vendor\Lib\site-packages
set PATH=%~dp0vendor\Scripts;%PATH%

:: Load .env file if it exists
if exist "%~dp0.env" (
    for /f "tokens=*" %%i in ("%~dp0.env") do set %%i
)

:: Run the AI service
python -m mcp.ai %*
""")
    else:
        launcher = env_dir.parent / "mcp-ai.sh"
        with open(launcher, 'w') as f:
            f.write("""#!/bin/bash

# Set environment variables
export PYTHONPATH="$(dirname "$0")/vendor/lib/python3.11/site-packages:$PYTHONPATH"
export PATH="$(dirname "$0")/vendor/bin:$PATH"

# Load .env file if it exists
if [ -f "$(dirname "$0")/.env" ]; then
    export $(grep -v '^#' "$(dirname "$0")/.env" | xargs)
fi

# Run the AI service
python -m mcp.ai "$@"
""")
        # Make the script executable
        launcher.chmod(launcher.stat().st_mode | 0o755)
    
    print_success(f"Launcher script created: {launcher}")

def main():
    """Main entry point for the setup script."""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        env_dir = project_root / "vendor"
        
        print_header("MCP AI Environment Setup")
        print(f"Project root: {project_root}")
        print(f"Environment: {env_dir}")
        
        # Set up the environment
        setup_virtualenv(env_dir)
        install_packages(env_dir)
        create_launcher_script(env_dir)
        
        print_header("Setup Complete!")
        print("You can now run the MCP AI service using:")
        print(f"  {project_root / 'mcp-ai.bat' if IS_WINDOWS else './mcp-ai.sh'}")
        
    except Exception as e:
        print_error(f"Setup failed: {e}")
        if hasattr(e, 'output'):
            print(e.output.decode())
        sys.exit(1)

if __name__ == "__main__":
    main()
