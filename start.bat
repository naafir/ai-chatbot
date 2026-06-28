@echo off
echo.
echo ==========================================
echo       AI Chat -- Starting Up
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Create virtualenv if not exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt -q

:: Create database directory
if not exist "database\" mkdir database

:: Copy .env
if not exist ".env" (
    copy .env.example .env
    echo Created .env from .env.example
)

echo.
echo NOTE: Make sure Ollama is running!
echo   1. Download Ollama from https://ollama.ai
echo   2. Run: ollama pull llama3
echo   3. Ollama will start automatically
echo.

echo Starting FastAPI server...
echo   App:      http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.

cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

pause
