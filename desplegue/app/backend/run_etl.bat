@echo off
:: ==============================================================================
:: run_etl.bat — Ejecutor del Pipeline ETL DWH Regularizacion Ambiental
:: Programado: 02:00 AM diario (Windows Task Scheduler)
:: ==============================================================================

SET PROJECT_DIR=D:\Datawrehouse_RA
SET ETL_DIR=%PROJECT_DIR%\ETL_p
SET PYTHON_EXE=C:\Python314\python.exe
SET LOG_DIR=%PROJECT_DIR%\logs
SET FECHA=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%
SET TASK_LOG=%LOG_DIR%\scheduler_etl_%FECHA%.log

:: Crear directorio de logs si no existe
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%DATE% %TIME%] ===== INICIO ETL PROGRAMADO ===== >> "%TASK_LOG%"
echo [%DATE% %TIME%] Directorio: %ETL_DIR% >> "%TASK_LOG%"
echo [%DATE% %TIME%] Python: %PYTHON_EXE% >> "%TASK_LOG%"

:: Cambiar al directorio del ETL
cd /d "%ETL_DIR%"

:: Ejecutar el pipeline ETL completo
echo [%DATE% %TIME%] Lanzando etl_main.py... >> "%TASK_LOG%"
"%PYTHON_EXE%" etl_main.py >> "%TASK_LOG%" 2>&1

SET EXIT_CODE=%ERRORLEVEL%

echo [%DATE% %TIME%] ETL finalizado con codigo: %EXIT_CODE% >> "%TASK_LOG%"

if %EXIT_CODE% EQU 0 (
    echo [%DATE% %TIME%] RESULTADO: EXITO >> "%TASK_LOG%"
) else (
    echo [%DATE% %TIME%] RESULTADO: FALLO - Revisar log ETL para detalles >> "%TASK_LOG%"
)

echo [%DATE% %TIME%] ===== FIN ETL PROGRAMADO ===== >> "%TASK_LOG%"
exit /b %EXIT_CODE%
