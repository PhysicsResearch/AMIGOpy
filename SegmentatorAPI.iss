; SegmentatorAPI.iss — installs the API plugin only into LocalAppData (no admin)

[Setup]
AppId={{A9838E7C-2BBB-4C52-AB9C-8B2B8F2F7F10}}
AppName=AMIGOpy Segmentator API
AppVersion=0.1.0
AppPublisher=GPF
AppPublisherURL=https://www.amigo-medphys.com/
DefaultDirName={localappdata}\AMIGOpy\Segmentator
DefaultGroupName=AMIGOpy
OutputBaseFilename=AMIGOpy_SegmentatorAPI_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
UsePreviousPrivileges=yes
LicenseFile=LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Put your built onefile console exe here:
; dist\segmentator_api.exe is the PyInstaller output from your API build
Source: "dist\segmentator_api.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Segmentator API (console)"; Filename: "{app}\segmentator_api.exe"
; No desktop icon by default—API is a background tool

[Tasks]
Name: "runapi"; Description: "Start API now"; Flags: unchecked

[Run]
; Allow user to start it immediately after install (unchecked by default)
Filename: "{app}\segmentator_api.exe"; Tasks: runapi; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up empty parent folder if it becomes empty
Type: filesandordirs; Name: "{localappdata}\AMIGOpy\Segmentator"
