@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Instala Python 3.12 para Windows y habilita el launcher "py".
    pause
    exit /b 1
)

py -3.12 --version >nul 2>nul
if errorlevel 1 (
    echo ERROR: No se encontro Python 3.12. Instala Python 3.12 para Windows.
    pause
    exit /b 1
)

if not exist ".venv-build\Scripts\python.exe" (
    py -3.12 -m venv .venv-build
    if errorlevel 1 goto error
)

call ".venv-build\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto error
python -m pip install -r requirements-windows.txt
if errorlevel 1 goto error
python -m PyInstaller --noconfirm --clean "MAQUIRRETHAL-Renta.spec"
if errorlevel 1 goto error

set "ISCC="
where ISCC.exe >nul 2>nul
if not errorlevel 1 set "ISCC=ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if defined ISCC (
    "%ISCC%" "instalador.iss"
    if errorlevel 1 goto error
    echo.
    echo Instalador generado en la carpeta dist.
) else (
    echo.
    echo Aplicacion generada en dist\MAQUIRRETHAL Renta.
    echo Para generar el instalador, instala Inno Setup 6 y ejecuta:
    echo ISCC.exe instalador.iss
)
exit /b 0

:error
echo.
echo ERROR: No se pudo completar la preparacion. Revisa el mensaje anterior.
pause
exit /b 1
