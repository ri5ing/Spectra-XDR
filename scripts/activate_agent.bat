@echo off
cd /d "C:\Program Files (x86)\ossec-agent"

echo =========================================================
echo  SPECTRA-XDR // Wazuh Agent 002 Key Importer
echo =========================================================
echo.

set KEY=MDAyIExhemFzdXMgYW55IDU5MWNiNDUzMmZmNGNhMDJjZmNlZWI2ZDg1YTExZGY2YjdmMzI5ZWU0ZmE0MTg5M2M1MmEwYTJkZjMzNTlkOTk=

echo [*] Target Directory: %CD%
echo [*] Importing Key for Agent 002...
echo.
echo 002 Lazasus any 591cb4532ff4ca02cfceeb6d85a11df6b7f329ee4fa41893c52a0a2df3359d99> client.keys

echo [*] client.keys updated successfully!
echo [*] Contents of client.keys:
type client.keys
echo.

echo [*] Restarting Wazuh Windows Service (WazuhSvc)...
net stop WazuhSvc
net start WazuhSvc

echo.
echo =========================================================
echo  SUCCESS! Agent 002 is registered and service restarted.
echo =========================================================
echo.
pause
