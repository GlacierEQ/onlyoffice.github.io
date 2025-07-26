@echo off
setlocal enabledelayedexpansion

:: MCP AI Setup Script
:: This script sets up a self-contained Python environment with all dependencies

set "PROJECT_ROOT=%~dp0"
set "VENDOR_DIR=%PROJECT_ROOT%mcp\ai\vendor"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PYTHON_ZIP=%VENDOR_DIR%\python.zip"
set "PYTHON_DIR=%VENDOR_DIR%\python"
set "PACKAGES_DIR=%VENDOR_DIR%\packages"
set "BIN_DIR=%VENDOR_DIR%\bin"
set "LIB_DIR=%VENDOR_DIR%\lib"
set "REQUIREMENTS=%PROJECT_ROOT%mcp\ai\requirements-ai.txt"

:: Create directories
mkdir "%VENDOR_DIR%" 2>nul
mkdir "%PYTHON_DIR%" 2>nul
mkdir "%PACKAGES_DIR%" 2>nul
mkdir "%BIN_DIR%" 2>nul
mkdir "%LIB_DIR%" 2>nul

:: Download Python if not exists
if not exist "%PYTHON_DIR%\python.exe" (
    echo Downloading Python...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%')"
    
    echo Extracting Python...
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
    del "%PYTHON_ZIP%"
    
    :: Enable pip
    echo import site > "%PYTHON_DIR%\sitecustomize.py"
    
    echo Python installed successfully
) else (
    echo Python already installed
)

:: Install pip if needed
if not exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo Installing pip...
    curl https://bootstrap.pypa.io/get-pip.py -o "%VENDOR_DIR%\get-pip.py"
    "%PYTHON_DIR%\python.exe" "%VENDOR_DIR%\get-pip.py" --no-warn-script-location --target="%PACKAGES_DIR%"
    del "%VENDOR_DIR%\get-pip.py"
)

:: Install requirements
echo Installing required packages...
"%PYTHON_DIR%\Scripts\pip.exe" install --no-warn-script-location --target="%PACKAGES_DIR%" -r "%REQUIREMENTS%"

:: Create launcher script
echo Creating launcher...
echo @echo off > "%PROJECT_ROOT%mcp-ai.bat"
echo setlocal enabledelayedexpansion >> "%PROJECT_ROOT%mcp-ai.bat"
echo. >> "%PROJECT_ROOT%mcp-ai.bat"
echo :: Set environment variables >> "%PROJECT_ROOT%mcp-ai.bat"
echo set PYTHONPATH=%%~dp0mcp\ai\vendor\packages;%%~dp0mcp\ai\vendor\lib >> "%PROJECT_ROOT%mcp-ai.bat"
echo set PATH=%%~dp0mcp\ai\vendor\python;%%~dp0mcp\ai\vendor\python\Scripts;%%PATH%% >> "%PROJECT_ROOT%mcp-ai.bat"
echo. >> "%PROJECT_ROOT%mcp-ai.bat"
echo :: Set API keys >> "%PROJECT_ROOT%mcp-ai.bat"
echo set OPENAI_API_KEY=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 >> "%PROJECT_ROOT%mcp-ai.bat"
echo set HUGGINGFACE_API_KEY=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 >> "%PROJECT_ROOT%mcp-ai.bat"
echo set LANGCHAIN_API_KEY=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 >> "%PROJECT_ROOT%mcp-ai.bat"
echo. >> "%PROJECT_ROOT%mcp-ai.bat"
echo :: Run the AI service >> "%PROJECT_ROOT%mcp-ai.bat"
echo python -m mcp.ai %%* >> "%PROJECT_ROOT%mcp-ai.bat"

echo.
echo Setup complete! You can now run the MCP AI service using:
echo   %PROJECT_ROOT%mcp-ai.bat
echo.
pause
