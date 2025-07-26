# MCP AI Setup Script
# This script sets up a self-contained Python environment with all dependencies

# Configuration
$pythonVersion = "3.11.9"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-embed-amd64.zip"
$projectRoot = Split-Path -Parent $PSScriptRoot
$vendorDir = Join-Path $PSScriptRoot "ai\vendor"
$pythonDir = Join-Path $vendorDir "python"
$packagesDir = Join-Path $vendorDir "packages"
$binDir = Join-Path $vendorDir "bin"
$libDir = Join-Path $vendorDir "lib"
$requirementsFile = Join-Path $PSScriptRoot "ai\requirements-ai.txt"

# Create directories
$directories = @($vendorDir, $pythonDir, $packagesDir, $binDir, $libDir)
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created directory: $dir"
    }
}

# Download and extract Python if not exists
$pythonExe = Join-Path $pythonDir "python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonZip = Join-Path $vendorDir "python.zip"
    Write-Host "Downloading Python $pythonVersion..."
    
    # Use WebClient for better progress reporting
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadProgressChanged += {
        $progress = [math]::Round(($_.BytesReceived / 1MB), 2)
        $total = [math]::Round(($_.TotalBytesToReceive / 1MB), 2)
        $percent = [math]::Round(($_.BytesReceived / $_.TotalBytesToReceive) * 100, 2)
        Write-Progress -Activity "Downloading Python $pythonVersion" -Status "$progress MB of $total MB ($percent%)" -PercentComplete $percent
    }
    $webClient.DownloadFileAsync([uri]$pythonUrl, $pythonZip)
    
    # Wait for download to complete
    while ($webClient.IsBusy) { Start-Sleep -Milliseconds 100 }
    Write-Progress -Activity "Downloading Python $pythonVersion" -Completed
    
    # Extract Python
    Write-Host "Extracting Python..."
    Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
    Remove-Item $pythonZip -Force
    
    # Enable pip
    $pthFile = Get-ChildItem -Path $pythonDir -Filter "python*._pth" | Select-Object -First 1
    if ($pthFile) {
        Add-Content -Path $pthFile.FullName -Value "import site"
    }
}

# Install pip if needed
$pipExe = Join-Path $pythonDir "Scripts\pip.exe"
if (-not (Test-Path $pipExe)) {
    Write-Host "Installing pip..."
    $getPip = Join-Path $vendorDir "get-pip.py"
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip
    & $pythonExe $getPip --no-warn-script-location --target=$packagesDir
    Remove-Item $getPip -Force
}

# Install requirements
if (Test-Path $requirementsFile) {
    Write-Host "Installing required packages..."
    $env:PYTHONPATH = $packagesDir
    & $pipExe install --no-warn-script-location --target=$packagesDir -r $requirementsFile
}

# Create launcher script
$launcherPath = Join-Path $projectRoot "mcp-ai.bat"
@"
@echo off
setlocal

:: Set environment variables
set PYTHONPATH=%~dp0mcp\ai\vendor\packages;%~dp0mcp\ai\vendor\lib
set PATH=%~dp0mcp\ai\vendor\python;%~dp0mcp\ai\vendor\python\Scripts;%PATH%

:: Set API keys
set OPENAI_API_KEY=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
set HUGGINGFACE_API_KEY=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
set LANGCHAIN_API_KEY=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

:: Run the AI service
python -m mcp.ai %*
"@ | Out-File -FilePath $launcherPath -Encoding ascii

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "You can now run the MCP AI service using:"
Write-Host "  $launcherPath" -ForegroundColor Cyan
Write-Host "`nTo get started, run:"
Write-Host "  .\mcp-ai.bat --help" -ForegroundColor Cyan
