@echo off
:: ==============================================================================
:: SISTEMA: Data Warehouse Regularización Ambiental (RA) - Módulo RGD
:: DESCRIPCIÓN: Script de ejecución automatizada para Tareas Programadas Windows
:: VERSIÓN: 2.1.0
:: ==============================================================================

:: 1. Definir variables de entorno y rutas
set "PROJECT_DIR=D:\Datawrehouse_RA"
set "PYTHON_EXEC=python"
set "ETL_SCRIPT=run_full_rgd_etl.py"

:: 2. Configurar el archivo de log para la ejecución Batch
:: Captura año, mes, día, hora y minuto para generar un archivo de log único por corrida
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "LOG_DATE=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%"
set "BATCH_LOG=%PROJECT_DIR%\logs\batch_execution_%LOG_DATE%.log"

:: 3. Ir al directorio del proyecto para evitar problemas de rutas relativas
cd /d "%PROJECT_DIR%"

echo ======================================================= >> "%BATCH_LOG%"
echo INICIO DE EJECUCION ETL RGD - %date% %time% >> "%BATCH_LOG%"
echo ======================================================= >> "%BATCH_LOG%"

:: 4. Ejecutar el proceso y capturar salida
echo Ejecutando orquestador maestro: %ETL_SCRIPT%... >> "%BATCH_LOG%"
%PYTHON_EXEC% "%ETL_SCRIPT%" >> "%BATCH_LOG%" 2>&1

:: 5. Capturar el código de salida (0 = Exito, >0 = Error)
if %ERRORLEVEL% EQU 0 (
    echo [EXITO] El proceso ETL finalizo correctamente. >> "%BATCH_LOG%"
) else (
    echo [ERROR] El proceso ETL finalizo con errores. Codigo: %ERRORLEVEL% >> "%BATCH_LOG%"
)

echo ======================================================= >> "%BATCH_LOG%"
echo FIN DE EJECUCION ETL RGD - %date% %time% >> "%BATCH_LOG%"
echo ======================================================= >> "%BATCH_LOG%"

:: Salir silenciosamente para no interrumpir el Programador de Tareas
exit /B %ERRORLEVEL%
