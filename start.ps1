# EduSlide AI - Startup Script (PowerShell)
# This script starts the backend (FastAPI) first, then the frontend (Streamlit)

Write-Host "Starting EduSlide AI..." -ForegroundColor Cyan
Write-Host ""

# Get the project root directory
$ProjectRoot = $PSScriptRoot

# Function to find an available port
function Find-AvailablePort {
    param (
        [int]$StartPort = 8000,
        [int]$MaxPort = 8100
    )
    
    for ($port = $StartPort; $port -le $MaxPort; $port++) {
        $tcpConnection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if (-not $tcpConnection) {
            return $port
        }
    }
    throw "No available ports found between $StartPort and $MaxPort"
}

# Check if virtual environment exists
if (Test-Path "$ProjectRoot\.venv\Scripts\Activate.ps1") {
    Write-Host "[OK] Virtual environment found at .venv" -ForegroundColor Green
} else {
    Write-Host "[ERROR] No virtual environment found at .venv" -ForegroundColor Red
    Write-Host "   Please create one with: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "   Then install dependencies: pip install -r requirements.txt" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  STEP 1: Starting Backend (FastAPI)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Find available port for backend
try {
    Write-Host "Searching for available port..." -ForegroundColor Yellow
    $BackendPort = Find-AvailablePort -StartPort 8000
    Write-Host "[OK] Found available port: $BackendPort" -ForegroundColor Green
    
    # Save port to temporary file for frontend to read
    $BackendPort | Out-File -FilePath "$ProjectRoot\.backend_port" -Encoding ascii -Force
    
} catch {
    Write-Host "[ERROR] Error finding port: $_" -ForegroundColor Red
    pause
    exit 1
}

# Start backend in a new window with venv activated and dynamic port
$BackendCommand = "Set-Location '$ProjectRoot'; & '$ProjectRoot\.venv\Scripts\Activate.ps1'; Write-Host 'Backend activated with venv' -ForegroundColor Green; Write-Host 'Starting on http://localhost:$BackendPort' -ForegroundColor Cyan; uvicorn backend.app.main:app --host 0.0.0.0 --port $BackendPort --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCommand

Write-Host "Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  STEP 2: Starting Frontend (Streamlit)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Start frontend in a new window with venv activated
# Note: Frontend config must read .backend_port file to know where backend is running
$FrontendCommand = "Set-Location '$ProjectRoot\frontend'; & '$ProjectRoot\.venv\Scripts\Activate.ps1'; Write-Host 'Frontend activated with venv' -ForegroundColor Green; Write-Host 'Starting on http://localhost:8501' -ForegroundColor Cyan; streamlit run streamlit_app.py"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCommand

Write-Host ""
Write-Host "[SUCCESS] Both services are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "   Backend API:  http://localhost:$BackendPort/docs" -ForegroundColor White
Write-Host "   Frontend UI:  http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Tip: Close the terminal windows to stop the services" -ForegroundColor Yellow
Write-Host ""
