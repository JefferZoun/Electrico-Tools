@echo off
setlocal
set "BOOTSTRAP=%~dp0scripts\bootstrap.ps1"
if not exist "%BOOTSTRAP%" (
    echo No se encuentra scripts\bootstrap.ps1. Extrae el ZIP completo antes de ejecutar este archivo.
    pause
    exit /b 1
)
if /I "%~1"=="/verificar" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BOOTSTRAP%" -SoloComprobar
) else (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%BOOTSTRAP%"
)
set "CODIGO=%ERRORLEVEL%"
if not "%CODIGO%"=="0" (
    echo.
    echo No se pudo iniciar Electrico Tools. Lee el error anterior.
    pause
)
exit /b %CODIGO%
