[Files]
Source: ..\airs.py; DestDir: {app}
Source: ..\airs.pyw; DestDir: {app}
Source: ..\gui\*.xrc; DestDir: {app}\gui
Source: ..\gui\*.py; DestDir: {app}\gui
Source: ..\db\*.py; DestDir: {app}\db
Source: ..\gui\images\*.png; DestDir: {app}\gui\images
Source: ..\gui\images\*.py; DestDir: {app}\gui\images
Source: ..\airs.ico; DestDir: {app}
[Setup]
OutputDir=.\
SourceDir=.\
OutputBaseFilename=Airs-Src
VersionInfoVersion=1.0
VersionInfoCompany=ImpossibleSoft
VersionInfoCopyright=(c) Jorgen Bodde
AppCopyright=© Jorgen Bodde
AppName=Airs
AppVerName=Airs
DefaultDirName={pf}\Airs
DefaultGroupName=Airs
UninstallDisplayIcon={app}\airs.ico
[Icons]
Name: "{group}\Airs"; Filename: "{app}\airs.pyw"; WorkingDir: {app}; IconFilename: "{app}\airs.ico"
Name: "{group}\Uninstall Airs"; Filename: "{uninstallexe}"

