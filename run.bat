@echo off
echo =====================================================================
echo  Starting Smart Mess Food Feedback & Waste Analytics Tracker
echo =====================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

:: 2. Install dependencies
echo [1/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Dependency installation encountered issues. Attempting to continue...
)

:: 3. Seed initial historical demo data if database not created
echo.
echo [2/3] Initializing database and verifying seed data...
python seed_data.py

:: 4. Start the FastAPI server
echo.
echo [3/3] Launching web server at http://127.0.0.1:8000 ...
echo Press CTRL+C to stop the server at any time.
echo.
python main.py

pause
