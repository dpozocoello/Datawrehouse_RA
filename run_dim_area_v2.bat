@echo off
chcp 65001 > nul

SET PROJECT_DIR=D:\Datawrehouse_RA
SET ETL_DIR=%PROJECT_DIR%\ETL_p
SET PYTHON_EXE=C:\Python314\python.exe
SET PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
SET LOG_DIR=%PROJECT_DIR%\logs
SET DB_HOST=localhost
SET DB_USER=postgres
SET DB_NAME=dw_reg_v1
SET PGPASSWORD=postgres
SET PGCLIENTENCODING=UTF8

:: Fecha/hora robusta independiente del locale
FOR /F "tokens=2 delims==" %%I IN ('wmic os get localdatetime /value 2^>nul') DO SET WDATETIME=%%I
SET FECHA=%WDATETIME:~0,4%-%WDATETIME:~4,2%-%WDATETIME:~6,2%
SET HORA=%WDATETIME:~8,2%-%WDATETIME:~10,2%-%WDATETIME:~12,2%
SET TASK_LOG=%LOG_DIR%\dim_area_v3_%FECHA%_%HORA%.log

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo ================================================================
echo   ETL DWH - Recarga dim_area v3.0
echo   Pasos: 10 (Areas) ^> 11 (Tipos) ^> 12 (Geo)
echo          13 (Consolidar) ^> 14 (Dims) ^> 15 (dim_area)
echo          16 (Jerarquia recursiva + bridge table)
echo   Fecha: %FECHA%  Hora: %HORA%
echo   Log : %TASK_LOG%
echo ================================================================
echo.

echo [%FECHA% %HORA%] ===== INICIO RUN_DIM_AREA_V3 ===== >> "%TASK_LOG%"

:: FASE 1: ETL Python pasos 10 a 16
echo [%FECHA% %HORA%] [FASE 1] Iniciando ETL Python pasos 10-16... >> "%TASK_LOG%"
echo [1/2] Ejecutando ETL Python (pasos 10 a 16)...

cd /d "%ETL_DIR%"
SET PYTHONUTF8=1
"%PYTHON_EXE%" etl_main.py --desde 10 --hasta 16 >> "%TASK_LOG%" 2>&1
SET ETL_EXIT=%ERRORLEVEL%

echo [%FECHA% %HORA%] ETL Python finalizo con codigo: %ETL_EXIT% >> "%TASK_LOG%"

if %ETL_EXIT% NEQ 0 (
    echo.
    echo [ERROR] El ETL Python fallo en pasos 10-16.
    echo         Revisa el log: %TASK_LOG%
    echo.
    echo [%FECHA% %HORA%] RESULTADO: FALLO ETL - Abortando. >> "%TASK_LOG%"
    goto :FIN_ERROR
)

echo         OK - ETL Python completado.
echo.

:: FASE 2: Validacion SQL
echo [%FECHA% %HORA%] [FASE 2] Ejecutando validacion SQL... >> "%TASK_LOG%"
echo [2/2] Ejecutando validacion en %DB_NAME%...

%PSQL% -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -v ON_ERROR_STOP=1 -c "SELECT 'stg.suia_areas_bi' AS tabla, COUNT(*) AS filas FROM stg.suia_areas_bi UNION ALL SELECT 'stg.suia_areas_types_bi', COUNT(*) FROM stg.suia_areas_types_bi UNION ALL SELECT 'dw.dim_area', COUNT(*) FROM dw.dim_area UNION ALL SELECT 'dw.bridge_area_jerarquia', COUNT(*) FROM dw.bridge_area_jerarquia;" >> "%TASK_LOG%" 2>&1

SET SQL_EXIT=%ERRORLEVEL%

if %SQL_EXIT% NEQ 0 (
    echo [ADVERTENCIA] La validacion SQL retorno errores. Revisa el log: %TASK_LOG%
    echo [%FECHA% %HORA%] ADVERTENCIA: Validacion SQL con errores (codigo %SQL_EXIT%) >> "%TASK_LOG%"
) else (
    echo         OK - Validacion completada.
)

echo.
echo ================================================================
echo   RESULTADO: EXITOSO
echo   Log completo: %TASK_LOG%
echo ================================================================
echo [%FECHA% %HORA%] ===== FIN RUN_DIM_AREA_V3 - EXITOSO ===== >> "%TASK_LOG%"
goto :FIN_OK

:FIN_ERROR
echo.
echo ================================================================
echo   RESULTADO: FALLO
echo   Log completo: %TASK_LOG%
echo ================================================================
echo [%FECHA% %HORA%] ===== FIN RUN_DIM_AREA_V3 - FALLO ===== >> "%TASK_LOG%"
exit /b 1

:FIN_OK
pause
exit /b 0