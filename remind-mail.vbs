Dim WinScriptHost
Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run Chr(34) & "remind-mail.bat" & Chr(34), 0
Set WinScriptHost = Nothing
