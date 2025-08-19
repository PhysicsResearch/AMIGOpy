; SegmentatorAPI.iss — Inno Setup script for the AMIGOpy Segmentator API

[Setup]
AppId={{76C6B1B7-5F7C-4E3D-9B95-1E43B0C2B9D9}
AppName=AMIGOpy Segmentator API
AppVersion=1.0.0
AppPublisher=AMIGO
DefaultDirName={localappdata}\AMIGOpy\SegmentatorAPI
DefaultGroupName=AMIGOpy
OutputDir=Output
OutputBaseFilename=SegmentatorAPI-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
DisableDirPage=no
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Install the PyInstaller OneDir output (must exist at build time)
; e.g., dist\segmentator_api\segmentator_api.exe and its files
Source: "dist\segmentator_api\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

; (Optional) bundle pre-downloaded models into installer
; They will be installed at: {app}\models\TotalSegmentator
; If models are huge (>1GB), consider separate installer or online download
; Source: "C:\Models\TotalSegmentator\*"; DestDir: "{app}\models\TotalSegmentator"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Segmentator API"; Filename: "{app}\segmentator_api.exe"
Name: "{userdesktop}\Segmentator API"; Filename: "{app}\segmentator_api.exe"; Tasks: desktopicon

[Registry]
; Tell AMIGOpy where Segmentator API is installed
Root: HKCU; Subkey: "SOFTWARE\AMIGOpy\Segmentator"; \
    ValueType: string; ValueName: "InstalledPath"; ValueData: "{app}\segmentator_api.exe"; \
    Flags: uninsdeletevalue

; Environment variable for apps to find API exe
Root: HKCU; Subkey: "Environment"; \
    ValueType: expandsz; ValueName: "AMIGO_API_EXE"; \
    ValueData: "{app}\segmentator_api.exe"; \
    Flags: preservestringtype uninsdeletevalue

; If you ship models, set TOTALSEG_HOME automatically
Root: HKCU; Subkey: "Environment"; \
    ValueType: expandsz; ValueName: "TOTALSEG_HOME"; \
    ValueData: "{app}\models\TotalSegmentator"; \
    Flags: preservestringtype uninsdeletevalue

[Run]
Filename: "{app}\segmentator_api.exe"; \
    Description: "Start Segmentator API"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove empty models folder on uninstall
Type: filesandordirs; Name: "{app}\models"
