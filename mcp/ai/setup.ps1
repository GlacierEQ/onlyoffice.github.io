# Self-contained environment setup for MCP AI
# This script creates a portable Python environment with all dependencies

param (
    [string]$PythonVersion = "3.11.9",
    [string]$Architecture = "amd64",
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Set up paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$vendorDir = Join-Path $scriptDir "vendor"
$pythonDir = Join-Path $vendorDir "python"
$pythonExe = Join-Path $pythonDir "python.exe"
$pipExe = Join-Path $pythonDir "Scripts\pip.exe"
$requirementsFile = Join-Path $scriptDir "requirements-ai.txt"
$packagesDir = Join-Path $vendorDir "packages"

# Create necessary directories
$dirs = @(
    $vendorDir,
    $pythonDir,
    $packagesDir,
    (Join-Path $vendorDir "bin"),
    (Join-Path $vendorDir "lib")
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir"
    }
}

# Download and extract Python if needed
function Install-Python {
    param (
        [string]$version,
        [string]$arch
    )
    
    $pythonUrl = "https://www.python.org/ftp/python/${version}/python-${version}-embed-${arch}.zip"
    $pythonZip = Join-Path $vendorDir "python-${version}-embed-${arch}.zip"
    
    if (-not (Test-Path $pythonExe) -or $Force) {
        Write-Host "Downloading Python ${version} ${arch}..."
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
        
        Write-Host "Extracting Python..."
        Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
        
        # Clean up
        Remove-Item $pythonZip -Force -ErrorAction SilentlyContinue
        
        # Enable pip
        $pthFile = Join-Path $pythonDir "python${version//./}_pkg.pth"
        Add-Content -Path $pthFile -Value "import sys; sys.path.append(r'$pythonDir\Lib\site-packages')"
    } else {
        Write-Host "Python is already installed at $pythonDir"
    }
}

# Install packages using pip
function Install-Packages {
    if (-not (Test-Path $pipExe)) {
        Write-Host "Bootstrapping pip..."
        $getPip = Join-Path $vendorDir "get-pip.py"
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip
        & $pythonExe $getPip --no-warn-script-location --target=$packagesDir
        Remove-Item $getPip -Force -ErrorAction SilentlyContinue
    }
    
    # Install packages
    Write-Host "Installing required packages..."
    $env:PYTHONPATH = $packagesDir
    & $pythonExe -m pip install --no-warn-script-location --target=$packagesDir -r $requirementsFile
    
    # Create a .pth file to include our packages
    $pthFile = Join-Path $pythonDir "site-packages.pth"
    Get-ChildItem -Path $packagesDir -Directory | ForEach-Object {
        $path = $_.FullName
        Add-Content -Path $pthFile -Value $path
    }
}

# Create launcher script
function New-Launcher {
    $launcher = @"
@echo off
setlocal

:: Set environment variables
set PYTHONPATH=%~dp0vendor\packages;%~dp0vendor\lib
set PATH=%~dp0vendor\python;%~dp0vendor\python\Scripts;%PATH%

:: Set API keys
set OPENAI_API_KEY=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
set HUGGINGFACE_API_KEY=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
set LANGCHAIN_API_KEY=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

:: Run the AI service
python -m mcp.ai %*
"@

    $launcherPath = Join-Path $rootDir "mcp-ai.bat"
    $launcher | Out-File -FilePath $launcherPath -Encoding ASCII
    Write-Host "Created launcher: $launcherPath"
}

# Main execution
try {
    # Install Python
    Install-Python -version $PythonVersion -arch $Architecture
    
    # Install packages
    Install-Packages
    
    # Create launcher
    New-Launcher
    
    Write-Host "`nSetup completed successfully!" -ForegroundColor Green
    Write-Host "You can now run the MCP AI service using 'mcp-ai.bat'"
} catch {
    Write-Host "`nAn error occurred during setup:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
