Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "c:\Users\rising\Documents\Spectra-XDR\scripts\set_permissions.bat", "", "", "runas", 1
