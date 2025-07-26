@echo off
setlocal enabledelayedexpansion

:: Set base directory
set "BASEDIR=%~dp0"

:: Set Python paths
set "PYTHONHOME=%BASEDIR%mcp\ai\vendor\python"
set "PYTHONPATH=%BASEDIR%;%BASEDIR%mcp\ai\vendor\packages"
set "PATH=%PYTHONHOME%;%PYTHONHOME%\Scripts;%PATH%"

:: Set API keys
set "OPENAI_API_KEY=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"
set "HUGGINGFACE_API_KEY=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"
set "LANGCHAIN_API_KEY=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"

:: Debug info
echo [DEBUG] Python Home: %PYTHONHOME%
echo [DEBUG] Python Path: %PYTHONPATH%
echo [DEBUG] Path: %PATH%

:: Run the AI service
"%PYTHONHOME%\python.exe" -c "import sys; print('Python Path:', sys.path)"
"%PYTHONHOME%\python.exe" -m mcp.ai %*
