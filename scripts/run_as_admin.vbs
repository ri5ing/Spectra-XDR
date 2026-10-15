Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "c:\Users\rising\Documents\Spectra-XDR\scripts\activate_agent.bat", "", "", "runas", 1
