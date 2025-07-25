@echo off
chcp 65001 >nul
title AI Assistant Launcher
color 0A

:: Request admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c ""%~dpnx0""' -Verb RunAs"
    exit /b
)

:: Set environment variables
cd /d "%~dp0"
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set "LOG_FILE=%PROJECT_ROOT%\logs\ollama_launcher.log"

:: Create log directory
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

echo [%date% %time%] Starting AI Assistant > "%LOG_FILE%"
echo Project root: %PROJECT_ROOT% >> "%LOG_FILE%"

:: Kill processes using ports
echo [STEP 1] Clearing ports...
echo [%date% %time%] Clearing ports >> "%LOG_FILE%"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":11435"') do (
    taskkill /f /pid %%a >nul 2>&1
    echo Killed process PID: %%a (port 11435) >> "%LOG_FILE%"
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /f /pid %%a >nul 2>&1
    echo Killed process PID: %%a (port 8000) >> "%LOG_FILE%"
)

timeout /t 2 >nul

:: Start Ollama service
echo [STEP 2] Starting Ollama service...
echo [%date% %time%] Starting Ollama service >> "%LOG_FILE%"

set OLLAMA_STARTED=0
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Ollama service already running >> "%LOG_FILE%"
    set OLLAMA_STARTED=1
) else (
    start "Ollama Service" ollama serve
    set OLLAMA_STARTED=1
)

:: Wait for Ollama
echo [STEP 3] Waiting for Ollama to start...
echo [%date% %time%] Waiting for Ollama >> "%LOG_FILE%"
timeout /t 10 >nul

:: Add firewall rules
echo [STEP 4] Configuring firewall...
echo [%date% %time%] Configuring firewall >> "%LOG_FILE%"

netsh advfirewall firewall add rule name="Ollama_Web" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="Ollama_API" dir=in action=allow protocol=TCP localport=11435

:: Start FastAPI service
echo [STEP 5] Starting web service...
echo [%date% %time%] Starting web service >> "%LOG_FILE%"

cd /d "%PROJECT_ROOT%\backend"
start "AI Web Service" python main.py
cd /d "%PROJECT_ROOT%"

:: Open browser
echo [STEP 6] Opening browser...
echo [%date% %time%] Opening browser >> "%LOG_FILE%"
timeout /t 5 >nul
start "" "http://localhost:8000"

:: Display success message
echo.
echo ==================================================
echo All services started successfully!
echo Local access: http://localhost:8000
echo.
echo Log file: %LOG_FILE%
echo ==================================================
echo.
echo Press any key to exit...
pause >nul