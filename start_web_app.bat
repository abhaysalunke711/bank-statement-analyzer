@echo off
echo 🏦 Bank Statement Analyzer - Web App Launcher
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ app.py not found
    echo Please run this from the bankstatementanalyzer directory
    pause
    exit /b 1
)

echo ✅ Found app.py
echo.

REM Start the web application
echo 🚀 Starting Bank Statement Analyzer Web App...
echo 📍 Server will be available at: http://localhost:5000
echo 📁 Upload your PDF bank statements through the web interface
echo ⏹️  Press Ctrl+C to stop the server
echo.

python start_web_app.py

echo.
echo 👋 Thank you for using Bank Statement Analyzer!
pause
