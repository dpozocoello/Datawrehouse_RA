@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: ==============================================================================
:: run_etl_completo.bat
:: Ejecuta el ETL completo del Data Warehouse dw_reg_v1 (31 pasos)
:: Uso:
::   run_etl_completo.bat              -> ETL completo (pasos 1-31)
::   run_etl_completo.bat --desde 10   -> Desde paso 10 hasta 31
::   run_etl_completo.bat --desde 1 --hasta 16  -> Rango especifico
:: ==============================================================================

:: ------------------------------------------------------------------------------
:: CONFIGURACION
:: ------------------------------------------------------------------------------
SET PROJECT_DIR=D:\Datawrehouse_RA
SET ETL_DIR=%PROJECT_DIR%\ETL_p
SET PYTHON_EXE=C:\Python314\python.exe
SET PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
SET LOG_DIR=%PROJECT_DIR%\logs
SET DB_HOST=localhost
SET DB_PORT=5432
SET DB_USER=postgres
SET DB_NAME=dw_reg_v1
SET PGPASSWORD=postgres
SET PGCLIENTENCODING=UTF8

:: Rango de pasos por defecto
SET PASO_DESDE=1
SET PASO_HASTA=31

:: ------------------------------------------------------------------------------
:: PARSEO DE ARGUMENTOS
:: ------------------------------------------------------------------------------
:PARSE_ARGS
IF "%~1"=="" GOTO END_PARSE
IF /I "%~1"=="--desde" (
    SET PASO_DESDE=%~2
    SHIFT & SHIFT & GOTO PARSE_ARGS
)
IF /I "%~1"=="--hasta" (
    SET PASO_HASTA=%~2
    SHIFT & SHIFT & GOTO PARSE_ARGS
)
SHIFT & GOTO PARSE_ARGS
:END_PARSE

:: ------------------------------------------------------------------------------
:: FECHA Y HORA (robusta, independiente del locale de Windows)
:: ------------------------------------------------------------------------------
FOR /F "tokens=2 delims==" %%I IN ('wmic os get localdatetime /value 2^>nul') DO SET WDATETIME=%%I
SET FECHA=%WDATETIME:~0,4%-%WDATETIME:~4,2%-%WDATETIME:~6,2%
SET HORA=%WDATETIME:~8,2%-%WDATETIME:~10,2%-%WDATETIME:~12,2%
SET TASK_LOG=%LOG_DIR%\etl_completo_%FECHA%_%HORA%.log

IF NOT EXIST "%LOG_DIR%" MKDIR "%LOG_DIR%"

:: ------------------------------------------------------------------------------
:: BANNER INICIAL
:: ------------------------------------------------------------------------------
echo.
echo ================================================================
echo   ETL DATA WAREHOUSE - REGULARIZACION AMBIENTAL
echo   Version: v3.0  ^|  31 pasos
echo   Pasos:   %PASO_DESDE% a %PASO_HASTA%
echo   Fecha:   %FECHA%    Hora: %HORA%
echo   Log:     %TASK_LOG%
echo ================================================================
echo.
echo FASES:
echo   [1-12]  Ingesta    ^| SUIA / JBPM / SNAP / Areas / Geo
echo   [13-22] Transform  ^| Dims / Facts / Area Jerarquia
echo   [23-26] Pagos v3   ^| Historicos / Montos / Puente
echo   [27-28] Residuos   ^| Desechos / Quimicos
echo   [29-31] Intersect  ^| Intersecciones Ambientales
echo ================================================================
echo.

echo [%FECHA% %HORA%] ================================================================ >> "%TASK_LOG%"
echo [%FECHA% %HORA%]   ETL DWH REGULARIZACION AMBIENTAL v3.0 - INICIO             >> "%TASK_LOG%"
echo [%FECHA% %HORA%]   Pasos: %PASO_DESDE% a %PASO_HASTA%                          >> "%TASK_LOG%"
echo [%FECHA% %HORA%] ================================================================ >> "%TASK_LOG%"

:: ------------------------------------------------------------------------------
:: VERIFICACION PREVIA DE DEPENDENCIAS
:: ------------------------------------------------------------------------------
echo [PRE] Verificando dependencias...

IF NOT EXIST "%PYTHON_EXE%" (
    echo [ERROR] Python no encontrado: %PYTHON_EXE%
    echo [ERROR] Python no encontrado: %PYTHON_EXE% >> "%TASK_LOG%"
    GOTO :FIN_ERROR
)

IF NOT EXIST "%ETL_DIR%\etl_main.py" (
    echo [ERROR] etl_main.py no encontrado en: %ETL_DIR%
    echo [ERROR] etl_main.py no encontrado en: %ETL_DIR% >> "%TASK_LOG%"
    GOTO :FIN_ERROR
)

echo         OK - Dependencias verificadas.
echo [%FECHA% %HORA%] PRE: Dependencias OK >> "%TASK_LOG%"
echo.

:: ------------------------------------------------------------------------------
:: EJECUCION ETL PYTHON
:: ------------------------------------------------------------------------------
echo [ETL] Iniciando ETL Python (pasos %PASO_DESDE% a %PASO_HASTA%)...
echo [%FECHA% %HORA%] FASE ETL: Ejecutando etl_main.py --desde %PASO_DESDE% --hasta %PASO_HASTA% >> "%TASK_LOG%"
echo. >> "%TASK_LOG%"

cd /d "%ETL_DIR%"
SET PYTHONUTF8=1
"%PYTHON_EXE%" etl_main.py --desde %PASO_DESDE% --hasta %PASO_HASTA% >> "%TASK_LOG%" 2>&1
SET ETL_EXIT=!ERRORLEVEL!

echo. >> "%TASK_LOG%"
echo [%FECHA% %HORA%] ETL Python finalizo con codigo de salida: !ETL_EXIT! >> "%TASK_LOG%"

IF !ETL_EXIT! NEQ 0 (
    echo.
    echo [ERROR] El ETL Python fallo ^(codigo !ETL_EXIT!^).
    echo         Revisa el log: %TASK_LOG%
    echo.
    GOTO :FIN_ERROR
)

echo         OK - ETL Python completado exitosamente.
echo.

:: ------------------------------------------------------------------------------
:: VALIDACION POST-ETL
:: ------------------------------------------------------------------------------
echo [VAL] Ejecutando validacion de conteos en %DB_NAME%...
echo [%FECHA% %HORA%] FASE VAL: Conteos post-ETL >> "%TASK_LOG%"

%PSQL% -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -v ON_ERROR_STOP=1 -P "footer=off" -c ^
"SELECT esquema_tabla, filas FROM (
  SELECT 'stg.suia_areas_bi'          AS esquema_tabla, COUNT(*) AS filas FROM stg.suia_areas_bi
  UNION ALL SELECT 'stg.suia_areas_types_bi',      COUNT(*) FROM stg.suia_areas_types_bi
  UNION ALL SELECT 'stg.coa_tmp_rcoa_bi',          COUNT(*) FROM stg.coa_tmp_rcoa_bi
  UNION ALL SELECT 'dw.dim_area',                  COUNT(*) FROM dw.dim_area
  UNION ALL SELECT 'dw.bridge_area_jerarquia',      COUNT(*) FROM dw.bridge_area_jerarquia
  UNION ALL SELECT 'dw.dim_proyecto',               COUNT(*) FROM dw.dim_proyecto
  UNION ALL SELECT 'dw.fact_regularizacion',        COUNT(*) FROM dw.fact_regularizacion
  UNION ALL SELECT 'dw.dim_pago',                   COUNT(*) FROM dw.dim_pago
  UNION ALL SELECT 'dw.fact_pago',                  COUNT(*) FROM dw.fact_pago
) t ORDER BY esquema_tabla;" >> "%TASK_LOG%" 2>&1

SET VAL_EXIT=!ERRORLEVEL!

IF !VAL_EXIT! NEQ 0 (
    echo [ADVERTENCIA] Validacion SQL con errores ^(codigo !VAL_EXIT!^). Revisa el log.
    echo [%FECHA% %HORA%] ADVERTENCIA: Validacion con errores >> "%TASK_LOG%"
) ELSE (
    echo         OK - Validacion completada.
)

echo.

:: ------------------------------------------------------------------------------
:: FIN EXITOSO
:: ------------------------------------------------------------------------------
FOR /F "tokens=2 delims==" %%I IN ('wmic os get localdatetime /value 2^>nul') DO SET WEND=%%I
SET HORA_FIN=%WEND:~8,2%:%WEND:~10,2%:%WEND:~12,2%

echo ================================================================
echo   RESULTADO:   EXITOSO
echo   Pasos:       %PASO_DESDE% a %PASO_HASTA%
echo   Inicio:      %HORA%
echo   Fin:         %HORA_FIN%
echo   Log:         %TASK_LOG%
echo ================================================================
echo.
echo [%FECHA% %HORA%] ================================================================ >> "%TASK_LOG%"
echo [%FECHA% %HORA%]   FIN ETL - EXITOSO  ^|  Fin: %HORA_FIN%                      >> "%TASK_LOG%"
echo [%FECHA% %HORA%] ================================================================ >> "%TASK_LOG%"
pause
exit /b 0

:FIN_ERROR
FOR /F "tokens=2 delims==" %%I IN ('wmic os get localdatetime /value 2^>nul') DO SET WEND=%%I
SET HORA_FIN=%WEND:~8,2%:%WEND:~10,2%:%WEND:~12,2%

echo ================================================================
echo   RESULTADO:   FALLO
echo   Fin:         %HORA_FIN%
echo   Log:         %TASK_LOG%
echo ================================================================
echo.
echo [ERROR] ================================================================ >> "%TASK_LOG%"
echo [ERROR]   FIN ETL - FALLO  ^|  Fin: %HORA_FIN%                          >> "%TASK_LOG%"
echo [ERROR] ================================================================ >> "%TASK_LOG%"
pause
exit /b 1