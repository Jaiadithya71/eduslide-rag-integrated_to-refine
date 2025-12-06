@echo off
REM EduSlide AI - Startup Script (Batch)
REM This script starts the backend (FastAPI) first, then the frontend (Streamlit)

echo.
echo ========================================
echo   Starting EduSlide AI
echo ========================================
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo [+] Virtual environment found at .venv
) else (
    echo [!] ERROR: No virtual environment found at .venv
    echo [!] Please create one with: python -m venv .venv
    echo [!] Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo   STEP 1: Starting Backend (FastAPI)
echo ========================================
echo.

REM Start backend in a new window with venv activated
start "EduSlide Backend" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate.bat && echo [+] Backend activated with venv && echo [+] Starting on http://localhost:8000 && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [*] Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   STEP 2: Starting Frontend (Streamlit)
echo ========================================
echo.

REM Start frontend in a new window with venv activated
start "EduSlide Frontend" cmd /k "cd /d "%~dp0frontend" && call ..\.venv\Scripts\activate.bat && echo [+] Frontend activated with venv && echo [+] Starting on http://localhost:8501 && streamlit run streamlit_app.py"

echo.
echo ========================================
echo   Both services are starting!
echo ========================================
echo.
echo Access Points:
echo   Backend API:  http://localhost:8000/docs
echo   Frontend UI:  http://localhost:8501
echo.
echo Tip: Close the terminal windows to stop the services
echo.
pause

