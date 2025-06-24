; AMIGOpy installer script for CI (no macros, literal values)

[Setup]
AppId={{E09A3FB0-4DF3-495E-817D-1EAE3753C818}}
AppName=AMIGOpy
AppVersion=0.1
AppPublisher=GPF
AppPublisherURL=https://www.amigo-medphys.com/
AppSupportURL=https://www.amigo-medphys.com/
AppUpdatesURL=https://www.amigo-medphys.com/
DefaultDirName={autopf}\AMIGOpy
DefaultGroupName=AMIGOpy
OutputBaseFilename=mysetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LINCENSE.txt
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
ChangesAssociations=yes
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Launch_ImGUI\Launch_ImGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Launch_ImGUI*";               DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icons\AMBpy.ico";                   DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKCR; Subkey: ".dcm\OpenWithProgids";            ValueType: string; ValueName: "AMIGOpy.dcm"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "AMIGOpydcm";                       ValueType: string; ValueName: "";           ValueData: "AMIGOpy.dcm"; Flags: uninsdeletekey
Root: HKCR; Subkey: "AMIGOpydcm\DefaultIcon";          ValueType: string; ValueName: "";           ValueData: """{app}\AMBpy.ico"""
Root: HKCR; Subkey: "AMIGOpydcm\shell\open\command"; ValueType: string; ValueName: "";           ValueData: """{app}\Launch_ImGUI.exe"" ""%1"""
Root: HKCR; Subkey: "Applications\Launch_ImGUI.exe\SupportedTypes"; ValueType: string; ValueName: ".dcm"; ValueData: ""
Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy";            ValueType: string; ValueName: ""; ValueData: "Open with AMIGOpy"; Flags: createvalueifdoesntexist
Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy\command";    ValueType: string; ValueName: ""; ValueData: """{app}\Launch_ImGUI.exe"" ""%1"""

[Icons]
Name: "{autoprograms}\AMIGOpy";  Filename: "{app}\Launch_ImGUI.exe"; IconFilename: "{app}\AMBpy.ico"
Name: "{autodesktop}\AMIGOpy";   Filename: "{app}\Launch_ImGUI.exe"; Tasks: desktopicon; IconFilename: "{app}\AMBpy.ico"

[Run]
Filename: "{app}\Launch_ImGUI.exe"; Description: "{cm:LaunchProgram,AMIGOpy}"; Flags: nowait postinstall skipifsilent