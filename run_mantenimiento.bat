@echo off
:: ==============================================================================
:: run_mantenimiento.bat — Ejecutor de Mantenimiento Preventivo DWH
:: Programado: 05:00 AM diario (Windows Task Scheduler)
:: Se ejecuta DESPUES del ETL para evitar conflictos de recursos
:: ==============================================================================

SET PROJECT_DIR=D:\Datawrehouse_RA
SET ETL_DIR=%PROJECT_DIR%\ETL_p
SET PYTHON_EXE=C:\Python314\python.exe
SET LOG_DIR=%PROJECT_DIR%\logs
SET FECHA=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%
SET TASK_LOG=%LOG_DIR%\scheduler_maint_%FECHA%.log

:: Crear directorio de logs si no existe
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%DATE% %TIME%] ===== INICIO MANTENIMIENTO PROGRAMADO ===== >> "%TASK_LOG%"
echo [%DATE% %TIME%] Directorio: %ETL_DIR% >> "%TASK_LOG%"

:: Cambiar al directorio del ETL
cd /d "%ETL_DIR%"

:: Ejecutar mantenimiento completo
echo [%DATE% %TIME%] Lanzando mantenimiento_db.py... >> "%TASK_LOG%"
"%PYTHON_EXE%" mantenimiento_db.py >> "%TASK_LOG%" 2>&1

SET EXIT_CODE=%ERRORLEVEL%

echo [%DATE% %TIME%] Mantenimiento finalizado con codigo: %EXIT_CODE% >> "%TASK_LOG%"

if %EXIT_CODE% EQU 0 (
    echo [%DATE% %TIME%] RESULTADO: EXITO >> "%TASK_LOG%"
) else (
    echo [%DATE% %TIME%] RESULTADO: FALLO - Revisar logs para detalles >> "%TASK_LOG%"
)

echo [%DATE% %TIME%] ===== FIN MANTENIMIENTO PROGRAMADO ===== >> "%TASK_LOG%"
exit /b %EXIT_CODE%
