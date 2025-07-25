@echo off
chcp 65001 >nul
title Install Dependencies

echo Installing required dependencies...
echo Please ensure Python 3.12 is installed (Python 3.13 has compatibility issues)

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.12 and add to PATH.
    echo Download: https://www.python.org/downloads/release/python-3124/
    start "" "https://www.python.org/downloads/release/python-3124/"
    pause
    exit /b
)

:: Check Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set pyver=%%a
for /f "tokens=1,2 delims=." %%a in ("%pyver%") do set major=%%a& set minor=%%b

if "%major%"=="3" if "%minor%"=="13" (
    echo WARNING: Python 3.13 is not fully supported and may cause issues.
    echo It is recommended to use Python 3.12 instead.
    echo Download: https://www.python.org/downloads/release/python-3124/
    start "" "https://www.python.org/downloads/release/python-3124/"
    pause
)

:: Install Python dependencies
echo Installing Python packages...
pip install fastapi==0.100.0
pip install uvicorn==0.22.0
pip install requests==2.31.0
pip install pydantic==1.10.15
pip install python-dotenv==1.0.1
pip install python-multipart==0.0.9

:: Check Ollama installation
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama is not installed. Please download from:
    echo https://ollama.com/download
    start "" "https://ollama.com/download"
    pause
    exit /b
)

:: Download DeepSeek-Coder model
echo Downloading DeepSeek-Coder model (approx 2.8GB)...
ollama pull deepseek-coder:1.3b

echo All dependencies installed successfully!
echo You can now run scripts\start.bat to launch the service
pause