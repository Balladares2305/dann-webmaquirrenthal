#define AppName "MAQUIRRETHAL Renta"
#define AppVersion "1.0.0"
#define AppPublisher "MAQUIRRETHAL S.A"
#define AppExeName "MAQUIRRETHAL Renta.exe"

[Setup]
AppId={{DDA277A2-9AB4-4F3D-9D90-8A481D6CB49B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\MAQUIRRETHAL Renta
DefaultGroupName={#AppName}
OutputDir=dist
OutputBaseFilename=Instalador-MAQUIRRETHAL-Renta
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Files]
Source: "dist\MAQUIRRETHAL Renta\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName}"; Flags: nowait postinstall skipifsilent
