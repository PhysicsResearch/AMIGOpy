 1 ; Script for AMIGOpy installer (paths are relative for CI)
 2 
 3 #define MyAppName "AMIGOpy"
 4 #define MyAppVersion "0.1"
 5 #define MyAppPublisher "GPF"
 6 #define MyAppURL "https://www.amigo-medphys.com/"
 7 #define MyAppExeName "Launch_ImGUI.exe"
 8 #define MyAppAssocExt ".dcm"
 9 #define MyAppAssocKey StringChange(MyAppName, " ", "") + MyAppAssocExt
10 
11 [Setup]
12 AppId={{E09A3FB0-4DF3-495E-817D-1EAE3753C818}}
13 AppName={#MyAppName}
14 AppVersion={#MyAppVersion}
15 AppPublisher={#MyAppPublisher}
16 AppPublisherURL={#MyAppURL}
17 AppSupportURL={#MyAppURL}
18 AppUpdatesURL={#MyAppURL}
19 DefaultDirName={autopf}\{#MyAppName}
20 DefaultGroupName={#MyAppName}
21 OutputBaseFilename=mysetup
22 Compression=lzma
23 SolidCompression=yes
24 WizardStyle=modern
25 LicenseFile=LINCENSE.txt
26 
27 [Languages]
28 Name: "english"; MessagesFile: "compiler:Default.isl"
29 
30 [Tasks]
31 Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
32 
33 [Files]
34 Source: "dist\Launch_ImGUI\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
35 Source: "dist\Launch_ImGUI\*";               DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
36 Source: "icons\AMBpy.ico";                   DestDir: "{app}"; Flags: ignoreversion
37 
38 [Registry]
39 Root: HKCR; Subkey: "{#MyAppAssocExt}\OpenWithProgids";            ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
40 Root: HKCR; Subkey: "{#MyAppAssocKey}";                            ValueType: string; ValueName: "";                  ValueData: "{#MyAppName}"; Flags: uninsdeletekey
41 Root: HKCR; Subkey: "{#MyAppAssocKey}\DefaultIcon";               ValueType: string; ValueName: "";                  ValueData: """{app}\AMBpy.ico"""
42 Root: HKCR; Subkey: "{#MyAppAssocKey}\shell\open\command";        ValueType: string; ValueName: "";                  ValueData: """{app}\{#MyAppExeName}"" ""%1"""
43 Root: HKCR; Subkey: "Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".dcm";             ValueData: ""
44 Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy";            ValueType: string; ValueName: "";                  ValueData: "Open with AMIGOpy"; Flags: createvalueifdoesntexist
45 Root: HKCR; Subkey: "Directory\shell\OpenWithAMIGOpy\command";    ValueType: string; ValueName: "";                  ValueData: """{app}\{#MyAppExeName}"" ""%1"""
46 
47 [Icons]
48 Name: "{autoprograms}\{#MyAppName}";      Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\AMBpy.ico"
49 Name: "{autodesktop}\{#MyAppName}";       Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\AMBpy.ico"
50 
51 [Run]
52 Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent