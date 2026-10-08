param([switch]$SoloComprobar)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root '.venv'
$VenvPython = Join-Path $Venv 'Scripts/python.exe'
$Requirements = Join-Path $Root 'requirements.txt'
$Main = Join-Path $Root 'main.py'
$PythonVersion = '3.13.16'
$PythonSha256 = 'FB4F9F5D438B2396DA0086DC70B935C530CB578E37ADC6D354F7AD2037FEE83B'
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"

function Test-Python([string]$Executable) {
    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) { return $false }
    try {
        & $Executable -I -c "import sys, struct, tkinter, pip, venv; assert (3, 10) <= sys.version_info[:2] < (3, 15) and struct.calcsize('P') == 8" 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Test-Pygame([string]$Executable) {
    if (-not (Test-Python $Executable)) { return $false }
    try {
        & $Executable -I -c "import importlib.metadata as m; import pygame; assert m.version('pygame-ce') == '2.5.8'" 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Find-Python {
    foreach ($minor in 14, 13, 12, 11, 10) {
        $candidate = Join-Path $env:LOCALAPPDATA ("Programs/Python/Python3$minor/python.exe")
        if (Test-Python $candidate) { return $candidate }
    }
    foreach ($command in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
        $candidate = $command.Source
        if ($candidate -notlike '*WindowsApps*' -and (Test-Python $candidate)) {
            return $candidate
        }
    }
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        foreach ($minor in 14, 13, 12, 11, 10) {
            try {
                $candidate = & $launcher.Source "-3.$minor" -c 'import sys; print(sys.executable)' 2>$null
                if ($LASTEXITCODE -eq 0 -and (Test-Python $candidate)) { return $candidate }
            } catch { }
        }
    }
    return $null
}

function Install-Python {
    $folder = Join-Path $env:TEMP 'ElectricoTools'
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    $installer = Join-Path $folder "python-$PythonVersion-amd64.exe"
    if (Test-Path -LiteralPath $installer) {
        if ((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash -ne $PythonSha256) {
            Remove-Item -LiteralPath $installer -Force
        }
    }
    if (-not (Test-Path -LiteralPath $installer)) {
        Write-Host "Descargando Python $PythonVersion desde python.org..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing -Uri $PythonUrl -OutFile $installer
    }
    if ((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash -ne $PythonSha256) {
        throw 'La descarga de Python no coincide con la suma SHA-256 oficial. No se instalara.'
    }
    Write-Host 'Instalando Python solo para este usuario (con Tkinter y pip)...'
    $options = @('/quiet','InstallAllUsers=0','Include_launcher=0','Include_pip=1',
                 'Include_tcltk=1','Include_test=0','PrependPath=0','Shortcuts=0')
    $process = Start-Process -FilePath $installer -ArgumentList $options -Wait -PassThru -WindowStyle Hidden
    if ($process.ExitCode -notin @(0,3010)) {
        throw "La instalacion de Python termino con el codigo $($process.ExitCode)."
    }
    $python = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python313/python.exe'
    if (-not (Test-Python $python)) {
        throw 'Python se instalo, pero no se pudo verificar Tkinter, pip y la version. Revisa la instalacion.'
    }
    Remove-Item -LiteralPath $installer -Force -ErrorAction SilentlyContinue
    return $python
}

try {
    if (-not [Environment]::Is64BitOperatingSystem) {
        throw 'Este lanzador necesita Windows de 64 bits.'
    }
    if (-not (Test-Path -LiteralPath $Requirements -PathType Leaf) -or
        -not (Test-Path -LiteralPath $Main -PathType Leaf)) {
        throw 'Faltan archivos del proyecto. Extrae el ZIP completo en una carpeta.'
    }
    Set-Location -LiteralPath $Root
    Write-Host 'Electrico Tools: comprobando el entorno...'
    if ($SoloComprobar) {
        if (-not (Test-Pygame $VenvPython)) {
            throw 'Aun falta preparar el entorno. Ejecuta Iniciar_Electrico_Tools.bat sin /verificar.'
        }
        Write-Host 'Entorno listo: Python, Tkinter y pygame-ce 2.5.8.'
        exit 0
    }
    if (-not (Test-Pygame $VenvPython)) {
        $python = Find-Python
        if (-not $python) { $python = Install-Python }
        Write-Host "Preparando el entorno virtual con $python ..."
        & $python -m venv --clear $Venv
        if ($LASTEXITCODE -ne 0 -or -not (Test-Python $VenvPython)) {
            throw 'No se pudo crear el entorno virtual de Python.'
        }
        Write-Host 'Instalando las dependencias del juego...'
        & $VenvPython -m pip install --only-binary=:all: -r $Requirements
        if ($LASTEXITCODE -ne 0 -or -not (Test-Pygame $VenvPython)) {
            throw 'No se pudo instalar o verificar pygame-ce. Comprueba la conexion a Internet.'
        }
    }
    Write-Host 'Abriendo el escritorio de Electrico Tools...'
    & $VenvPython $Main
    if ($LASTEXITCODE -ne 0) { throw 'El programa se ha cerrado con un error.' }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
