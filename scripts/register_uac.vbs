Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "cmd.exe", "/c cd /d ""C:\Program Files (x86)\ossec-agent"" & manage_agents.exe -i MDAyIExhemFzdXMgYW55IDU5MWNiNDUzMmZmNGNhMDJjZmNlZWI2ZDg1YTExZGY2YjdmMzI5ZWU0ZmE0MTg5M2M1MmEwYTJkZjMzNTlkOTk= & net stop WazuhSvc & net start WazuhSvc", "", "runas", 1
