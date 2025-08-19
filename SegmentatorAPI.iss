; SegmentatorAPI.iss — Inno Setup script for the bundled Segmentator API

[Setup]
AppId={{76C6B1B7-5F7C-4E3D-9B95-1E43B0C2B9D9}
AppName=AMIGOpy Segmentator API
AppVersion=1.0.0
AppPublisher=AMIGO
DefaultDirName={pf}\AMIGOpy\SegmentatorAPI
DefaultGroupName=AMIGOpy
OutputDir=Output
OutputBaseFilename=SegmentatorAPI-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
DisableDirPage=no
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Install the PyInstaller OneDir output (must exist at build time)
; e.g., dist\segmentator_api\segmentator_api.exe and its files
Source: "dist\segmentator_api\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Segmentator API (console)"; Filename: "{app}\segmentator_api.exe"
Name: "{userdesktop}\Segmentator API"; Filename: "{app}\segmentator_api.exe"; Tasks: desktopicon

[Registry]
; AMIGOpy looks up this HKLM key (your code already supports it)
Root: HKLM; Subkey: "SOFTWARE\AMIGOpy\Segmentator"; ValueType: string; ValueName: "InstalledPath"; ValueData: "{app}\segmentator_api.exe"; Flags: uninsdeletevalue

; Optional: write a per-user env var (AMIGOpy also checks this)
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "AMIGO_API_EXE"; ValueData: "{app}\segmentator_api.exe"; Flags: preservestringtype

; (Optional) set TOTALSEG_HOME if you ship models with the installer
; Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "TOTALSEG_HOME"; ValueData: "{app}\models\TotalSegmentator"; Flags: preservestringtype

[Run]
; Make sure the current user session sees the new env var immediately
Filename: "{cmd}"; Parameters: "/C setx AMIGO_API_EXE ""{app}\segmentator_api.exe"""; Flags: runhidden

; Notify running processes (including AMIGOpy) that environment variables changed
Filename: "{cmd}"; Parameters: "/C powershell -NoProfile -Command ""$sig = '[DllImport(\"user32.dll\", SetLastError=true)]public static extern int SendMessageTimeout(IntPtr hWnd, int Msg, IntPtr wParam, string lParam, int fuFlags, int uTimeout, out IntPtr lpdwResult);'; Add-Type -MemberDefinition $sig -Name X -Namespace Y; [Y.X]::SendMessageTimeout([IntPtr]0xffff, 0x1A, [IntPtr]0, 'Environment', 2, 1000, [ref]([IntPtr]::Zero))"""; Flags: runhidden

; (Optional) Launch API after install
; Filename: "{app}\segmentator_api.exe"; Description: "Start Segmentator API"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Clean up per-user env var on uninstall
Filename: "{cmd}"; Parameters: "/C reg delete HKCU\Environment /v AMIGO_API_EXE /f"; Flags: runhidden
