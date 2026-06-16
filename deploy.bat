@echo off
setlocal enabledelayedexpansion

REM Subir código al NAO
echo Subiendo codigo al NAO...
pscp -r -pw nao * nao@169.254.92.177:naoqi_competition
if errorlevel 1 (
    echo Error en la copia de archivos
    exit /b 1
)

REM Conectar al NAO y ejecutar main.py
echo Conectando al NAO y ejecutando main.py...
plink -pw nao nao@169.254.92.177 "cd naoqi_competition && python main.py"
if errorlevel 1 (
    echo Error al ejecutar main.py
    exit /b 1
)

echo Deployment completado exitosamente
pause