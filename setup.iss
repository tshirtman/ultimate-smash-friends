; NOTE: This file generates a Windows executible (32bin only for now). 
; It is still neccessary to have Python and PyGame installed.

; Be sure to change paths to correspond to the ones on your machine before running.

; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{2960F315-EA73-4EFF-B16D-F82C319CDC88}
AppName=Ultimate Smash Friends
AppVerName=Ultimate Smash Friends 0.1.0-1
AppPublisher=USF Team
AppPublisherURL=http://usf.tuxfamily.org
AppSupportURL=http://usf.tuxfamily.org
AppUpdatesURL=http://usf.tuxfamily.org
DefaultDirName={pf}\Ultimate Smash Friends
DisableDirPage=yes
DefaultGroupName=Ultimate Smash Friends
LicenseFile=\\Vboxsvr\ultimate-smash-friends\COPYING.txt
OutputBaseFilename=ultimate-smash-friends-0.1.0-setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "\\Vboxsvr\ultimate-smash-friends\ultimate-smash-friends.pyw"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\README.fr.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\CREDITS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\system.cfg"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\TODO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\viewer.pyw"; DestDir: "{app}"; Flags: ignoreversion
Source: "\\Vboxsvr\ultimate-smash-friends\contrib\*"; DestDir: "{app}\contrib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "\\Vboxsvr\ultimate-smash-friends\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "\\Vboxsvr\ultimate-smash-friends\doc\*"; DestDir: "{app}\doc"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "\\Vboxsvr\ultimate-smash-friends\utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "\\Vboxsvr\ultimate-smash-friends\usf\*"; DestDir: "{sd}\Python26\Lib\site-packages\usf"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Ultimate Smash Friends"; Filename: "{app}\ultimate-smash-friends.pyw"
Name: "{commondesktop}\Ultimate Smash Friends"; Filename: "{app}\ultimate-smash-friends.pyw"; Tasks: desktopicon
Name: "{group}\{cm:UninstallProgram,My Program}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\ultimate-smash-friends.pyw"; Description: "{cm:LaunchProgram,Ultimate Smash Friends}"; Flags: shellexec postinstall skipifsilent








