; AMIGOpy installer script (GUI + Segmentator worker in one)
; Outputs a single app folder with Launch_ImGUI.exe and segmentator_worker.exe,
; sets TOTALSEG_HOME to a writeable models cache in LocalAppData.

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
OutputBaseFilename=AMIGOpy-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=LINCENSE.txt
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
ChangesAssociations=yes
DisableProgramGroupPage=yes
; Needed so environment variables (TOTALSEG_HOME, etc.) are persisted
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
; Ensure a writeable models directory (for TS weights) exists for the user
Name: "{localappdata}\AMIGOpy\models"; Flags: uninsalwaysuninstall

[Files]
; Use the single-folder build produced by amigopy_all.spec (dist\AMIGOpy\*)
; This includes Launch_ImGUI.exe, segmentator_worker.exe, and all deps.
Source: "dist\AMIGOpy\Launch_ImGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\AMIGOpy\*";               DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "AMBpy.ico";                    DestDir: "{app}"; Flags: ignoreversion

[Registry]
; -------- File association for .dcm to open with AMIGOpy GUI ----------
Root: HKCR; Subkey: ".dcm\OpenWithProgids"; ValueType: string; ValueName: "AMIGOpy.dcm"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "AMIGOpydcm"; ValueType: string; ValueName: ""; ValueData: "AMIGOpy.dcm"; Flags: uninsdeletekey
Root: HKCR; Subkey: "AMIGOpydcm\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\AMBpy.ico"""
Root: HKCR; Subkey: "AMIGOpydcm\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Launch_ImGUI.exe"" ""%1"""
Root: HKCR; Subkey: "Applications\Launch_ImGUI.exe\SupportedTypes"; ValueType: string; ValueName: ".dcm"; ValueData: ""
; Right-click "Open with AMIGOpy" on folders
Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy"; ValueType: string; ValueName: ""; ValueData: "Open with AMIGOpy"; Flags: createvalueifdoesntexist
Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Launch_ImGUI.exe"" ""%1"""

; -------- Segmentator worker discovery + environment variables ----------
; Path to the worker exe for external tools (compat with prior API script)
Root: HKCU; Subkey: "SOFTWARE\AMIGOpy\Segmentator"; \
    ValueType: string; ValueName: "InstalledPath"; ValueData: "{app}\segmentator_worker.exe"; \
    Flags: uninsdeletevalue

; Environment variable for apps/scripts to find the worker
Root: HKCU; Subkey: "Environment"; \
    ValueType: expandsz; ValueName: "AMIGO_TS_WORKER"; \
    ValueData: "{app}\segmentator_worker.exe"; \
    Flags: preservestringtype uninsdeletevalue

; Back-compat with older code that expected AMIGO_API_EXE
Root: HKCU; Subkey: "Environment"; \
    ValueType: expandsz; ValueName: "AMIGO_API_EXE"; \
    ValueData: "{app}\segmentator_worker.exe"; \
    Flags: preservestringtype uninsdeletevalue

; Set a writeable model cache path for TotalSegmentator (your code will use this if present)
Root: HKCU; Subkey: "Environment"; \
    ValueType: expandsz; ValueName: "TOTALSEG_HOME"; \
    ValueData: "{localappdata}\AMIGOpy\models"; \
    Flags: preservestringtype uninsdeletevalue

[Icons]
Name: "{autoprograms}\AMIGOpy";  Filename: "{app}\Launch_ImGUI.exe"; IconFilename: "{app}\AMBpy.ico"
Name: "{autodesktop}\AMIGOpy";   Filename: "{app}\Launch_ImGUI.exe"; Tasks: desktopicon; IconFilename: "{app}\AMBpy.ico"

[Run]
Filename: "{app}\Launch_ImGUI.exe"; Description: "{cm:LaunchProgram,AMIGOpy}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Optionally remove the models cache on uninstall (comment out to keep models between installs)
Type: filesandordirs; Name: "{localappdata}\AMIGOpy\models"
