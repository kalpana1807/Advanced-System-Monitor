[Setup]
AppName=Advanced System Monitor & Health Dashboard
AppVersion=1.0
DefaultDirName={pf}\AdvancedSystemMonitor
DefaultGroupName=AdvancedSystemMonitor
OutputDir=installer_output
OutputBaseFilename=Advanced_System_Monitor_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\system_monitor.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Advanced System Monitor"; Filename: "{app}\system_monitor.exe"
Name: "{commondesktop}\Advanced System Monitor"; Filename: "{app}\system_monitor.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked