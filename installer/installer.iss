#define MyAppName "Desktop AI Automation"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Rachel Davidovitch"
#define MyAppExeName "DesktopAiAutomation.exe"

[Setup]
AppId={{A7D8C5E2-4F31-4A92-9B76-2C8D1E6F5A03}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\DesktopAiAutomation
DefaultGroupName={#MyAppName}

OutputDir=Output
OutputBaseFilename=DesktopAiAutomation-Setup

Compression=lzma
SolidCompression=yes

ArchitecturesInstallIn64BitMode=x64compatible

UninstallDisplayName={#MyAppName}

[Files]
Source: "..\dist\DesktopAiAutomation\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent