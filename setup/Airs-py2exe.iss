[Files]
Source: ..\dist\*.*; DestDir: {app}
Source: ..\gui\*.xrc; DestDir: {app}\gui
Source: ..\gui\images\*.png; DestDir: {app}\gui\images
Source: ..\airs.ico; DestDir: {app}
[Setup]
OutputDir=..\setup
SourceDir=..\dist
OutputBaseFilename=Airs-Setup
VersionInfoVersion=0.9
VersionInfoCompany=ImpossibleSoft
VersionInfoCopyright=(c) Jorgen Bodde
AppCopyright=� Jorgen Bodde
AppName=Airs
AppVerName=Airs
DefaultDirName={pf}\Airs
DefaultGroupName=Airs
UninstallDisplayIcon={app}\airs.ico
[Icons]
Name: "{group}\Airs"; Filename: "{app}\airs.exe"; WorkingDir: {app}
Name: "{group}\Uninstall Airs"; Filename: "{uninstallexe}"

