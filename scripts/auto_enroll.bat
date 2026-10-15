@echo off
cd /d "C:\Program Files (x86)\ossec-agent"

echo ==============================================================
echo  SPECTRA-XDR // Wazuh Agent Automatic Enrollment & Sync
echo ==============================================================
echo.

echo [*] Requesting new key from Wazuh Manager (127.0.0.1:1515)...
agent-auth.exe -m 127.0.0.1 -p 1515 -A Lazasus

echo.
echo [*] Current client.keys entry:
type client.keys
echo.

echo [*] Restarting Wazuh Service...
net stop WazuhSvc
net start WazuhSvc

echo.
echo ==============================================================
echo  Agent enrollment complete! Checking connection...
echo ==============================================================
echo.
pause
