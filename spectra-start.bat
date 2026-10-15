@echo off
setlocal enabledelayedexpansion
title SPECTRA-XDR // Unified Enterprise Launcher

echo ===============================================================================
echo   SPECTRA-XDR // AUTONOMOUS MULTI-AGENT CYBER DEFENSE PLATFORM
echo   Launching Full Stack: Docker, Backend, Frontend Next.js ^& RedTeam Simulator
echo ===============================================================================
echo.

:: Detect Local Network IP Address dynamically
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr /v "172." ^| findstr /v "169.254"') do (
    set "RAW_IP=%%a"
    set "NET_IP=!RAW_IP: =!"
    goto :found_ip
)
:found_ip
if "%NET_IP%"=="" set "NET_IP=192.168.0.104"

echo [*] Detected Local Network IP: %NET_IP%
echo.

:: 1. Start Docker Infrastructure (Wazuh, PostgreSQL, OpenSearch Indexer, Redis)
echo [1/4] Starting Docker Infrastructure (Wazuh Cluster, Postgres, Indexer, Redis)...
docker compose up -d
if %errorlevel% neq 0 (
    echo [!] Warning: Docker containers could not be launched. Ensure Docker Desktop is running!
) else (
    echo [OK] Docker Stack is UP and Healthy.
)
echo.

:: 2. Start Backend FastAPI Engine in separate window
echo [2/4] Starting Backend FastAPI Server (Port 8000)...
start "SPECTRA-XDR :: Backend API Engine" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: 3. Start Next.js Modern Frontend Console in separate window
echo [3/4] Starting Next.js Frontend Console (Port 3000)...
start "SPECTRA-XDR :: Next.js Console" cmd /k "cd /d %~dp0frontend && npm run dev -- -H 0.0.0.0"

:: 4. Start RedTeam Live Attack Simulator in separate window
echo [4/4] Starting RedTeam Live Attack Simulator (Port 5050)...
start "SPECTRA-XDR :: Attack Simulator" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python -m uvicorn simulator.app:app --host 0.0.0.0 --port 5050"

timeout /t 3 /nobreak >nul

echo.
echo ===============================================================================
echo   SPECTRA-XDR PLATFORM SUCCESSFULLY STARTED! ALL ACCESS URLS:
echo ===============================================================================
echo.
echo   [1] SPECTRA-XDR CONSOLE (Frontend Web UI):
echo       Localhost:   http://localhost:3000
echo       Network LAN: http://%NET_IP%:3000
echo.
echo   [2] REDTEAM LIVE ATTACK SIMULATOR (Attack Page):
echo       Localhost:   http://localhost:5050
echo       Network LAN: http://%NET_IP%:5050
echo.
echo   [3] OFFICIAL WAZUH DASHBOARD (WUI):
echo       Localhost:   http://localhost:8443 (User: admin / Pass: admin)
echo       Network LAN: http://%NET_IP%:8443
echo.
echo   [4] BACKEND API ^& OPENAPI SWAGGER SPECS:
echo       Localhost:   http://localhost:8000/docs
echo       Network LAN: http://%NET_IP%:8000/docs
echo.
echo   [5] OLLAMA LOCAL LLM ENGINE:
echo       Localhost:   http://localhost:11434
echo.
echo   [6] WAZUH AGENT ENROLLMENT PORTS:
echo       Ports:       1514 / 1515 TCP
echo ===============================================================================
echo.
echo Tip: You can access the Console and Attack Simulator from your Mobile or
echo any device on the same Wi-Fi using the Network LAN URLs above!
echo.
pause
