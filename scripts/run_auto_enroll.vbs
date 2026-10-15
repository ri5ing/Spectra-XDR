Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "c:\Users\rising\Documents\Spectra-XDR\scripts\auto_enroll.bat", "", "", "runas", 1
