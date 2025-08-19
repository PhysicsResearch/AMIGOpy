; AMIGOpy installer script for CI (GUI only, no TS/torch)

[Setup]
AppId={{E09A3FB0-4DF3-495E-817D-1EAE3753C818}}
AppName=AMIGOpy
AppVersion=0.1.0
AppPublisher=GPF
AppPublisherURL=https://www.amigo-medphys.com/
AppSupportURL=https://www.amigo-medphys.com/
AppUpdatesURL=https://www.amigo-medphys.com/
DefaultDirName={localappdata}\AMIGOpy
DefaultGroupName=AMIGOpy
OutputDir=Output
OutputBaseFilename=AMIGOpy-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE.txt
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
ChangesAssociations=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; PyInstaller onedir output for the GUI
Source: "dist\Launch_ImGUI\Launch_ImGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Launch_ImGUI\*";               DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; \
  Excludes: "segmentator_api\*"
Source: "AMBpy.ico";                          DestDir: "{app}"; Flags: ignoreversion

[Registry]
; File association for .dcm (per-user; HKCR maps to HKCU\Software\Classes with PrivilegesRequired=lowest)
Root: HKCR; Subkey: ".dcm\OpenWithProgids"; ValueType: string; ValueName: "AMIGOpy.dcm"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "AMIGOpy.dcm";                        ValueType: string; ValueName: "";           ValueData: "AMIGOpy DICOM"
Root: HKCR; Subkey: "AMIGOpy.dcm\DefaultIcon";            ValueType: string; ValueName: "";           ValueData: """{app}\AMBpy.ico"""
Root: HKCR; Subkey: "AMIGOpy.dcm\shell\open\command";     ValueType: string; ValueName: "";           ValueData: """{app}\Launch_ImGUI.exe"" ""%1"""
; Optional Explorer context menu on folders: “Open with AMIGOpy”
Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy";         ValueType: string; ValueName: ""; ValueData: "Open with AMIGOpy"; Flags: createvalueifdoesntexist
Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Launch_ImGUI.exe"" ""%1"""

[Icons]
Name: "{autoprograms}\AMIGOpy";  Filename: "{app}\Launch_ImGUI.exe"; IconFilename: "{app}\AMBpy.ico"
Name: "{autodesktop}\AMIGOpy";   Filename: "{app}\Launch_ImGUI.exe"; Tasks: desktopicon; IconFilename: "{app}\AMBpy.ico"

[Run]
Filename: "{app}\Launch_ImGUI.exe"; Description: "{cm:LaunchProgram,AMIGOpy}"; Flags: nowait postinstall skipifsilent
