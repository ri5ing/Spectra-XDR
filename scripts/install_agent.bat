@echo off
:: Batch script to install and register Wazuh Agent on Windows
:: Must be executed in 'Run as administrator' Command Prompt or PowerShell

echo ========================================================
echo  SPECTRA-XDR // Wazuh Windows Agent Local Installer
echo ========================================================
echo.

cd /d "%~dp0"

if not exist "wazuh-agent.msi" (
    echo [ERROR] wazuh-agent.msi file not found in current directory!
    pause
    exit /b 1
)

echo [*] Installing Wazuh Agent pointing to Manager at 127.0.0.1...
msiexec.exe /i wazuh-agent.msi /qn WAZUH_MANAGER="127.0.0.1" WAZUH_REGISTRATION_SERVER="127.0.0.1"

echo [*] Starting Wazuh Windows Service...
net start WazuhSvc

echo.
echo [*] Checking Service Status:
sc query WazuhSvc

echo.
echo ========================================================
echo  Wazuh Agent installation complete.
echo  Telemetry will now sync to Spectra-XDR console!
echo ========================================================
pause
