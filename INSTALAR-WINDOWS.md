# Preparar el instalador de Windows

El instalador empaqueta `MAQUIRRENTHAL -INVENTARIO.py` y su banner. No incluye
`inventario_renta.json`, para evitar distribuir accidentalmente los registros
locales del proyecto. En Windows, los contratos se guardan en:

`%APPDATA%\MAQUIRRETHAL\inventario_renta.json`

Si ya tienes contratos en un `inventario_renta.json` de otra instalación,
cópialo a esa ubicación antes de iniciar la aplicación instalada por primera
vez. El archivo operativo del proyecto no se incorpora al instalador.

## Requisitos para generar el instalador

- Windows de 64 bits.
- Python 3.12 instalado y disponible con el comando `py`.
- Inno Setup 6 instalado para generar el archivo instalador `.exe`.

## Generación

Desde el Explorador de archivos, ejecuta `instalar_windows.bat`. El script crea
un entorno de compilación aislado, instala las dependencias, empaqueta la
aplicación y, si encuentra Inno Setup, genera:

`dist\Instalador-MAQUIRRETHAL-Renta.exe`

Sin Inno Setup, la aplicación empaquetada queda en `dist\MAQUIRRETHAL Renta`.
Tras instalar Inno Setup 6, ejecuta `ISCC.exe instalador.iss` desde esta
carpeta para crear el instalador.

El ejecutable y el instalador de Windows deben generarse en Windows; PyInstaller
no produce ejecutables de Windows al compilar desde Linux.
