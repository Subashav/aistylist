@echo off
title AI Stylist - Local Development Launcher
color 0A

echo ================================================================
echo                AI STYLIST - ONE-CLICK LAUNCHER
echo ================================================================
echo.

cd /d "%~dp0backend"

set "PY_CMD=python"
if exist "%~dp0backend\venv\Scripts\python.exe" (
    set "PY_CMD=%~dp0backend\venv\Scripts\python.exe"
)

echo [1/3] Starting FastAPI Backend on 0.0.0.0:8000 (http://127.0.0.1:8000) ...
start "AI Stylist Backend (FastAPI)" cmd /k ""%PY_CMD%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Checking Flutter Web Frontend ...
cd /d "%~dp0frontend"

where flutter >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Flutter found in PATH. Starting Flutter on Chrome...
    start "AI Stylist Frontend (Flutter)" cmd /k "flutter run -d chrome --web-port=3000"
) else (
    echo [INFO] Starting built Flutter Web server on http://127.0.0.1:3000 ...
    start "AI Stylist Frontend (Web Server)" cmd /k ""%PY_CMD%" -m http.server 3000 --directory build\web"
)

echo [3/3] Opening AI Stylist in browser...
ping 127.0.0.1 -n 4 >nul
start http://127.0.0.1:3000
start http://127.0.0.1:8000/docs

echo.
echo ================================================================
echo   Backend URL:   http://127.0.0.1:8000 (Swagger: /docs)
echo   Frontend URL:  http://127.0.0.1:3000
echo ================================================================
echo.
pause
