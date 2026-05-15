@echo off
:: ==============================================================================
:: JOB DIARIO - DATA WAREHOUSE DWH_REG_V1 (Incluye v2, v3 e Intersecciones v1.9)
:: Este script ejecuta las transformaciones globales del DWH, incluyendo el 
:: cálculo histórico de pagos (v3) que recalcula dinámicamente el valor
:: transaccional exacto basándose en el saldo remanente para tódos los proyectos,
:: y la carga de certificados de intersección ambiental (v1.9.1).
:: ==============================================================================

set PGPASSWORD=postgres
set PGCLIENTENCODING=UTF8
set PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
set DB_HOST=localhost
set DB_USER=postgres
set DB_NAME=dw_reg_v1

echo [INFO] Iniciando Job Diario DWH...
echo [INFO] ----------------------------------------------------

echo [1/4] Ejecutando Carga Base ETL Original...
%PSQL% -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "d:\Datawrehouse_RA\etl_carga_datos.sql"
echo [INFO] Carga Base completada.

echo [2/4] Ejecutando Transformaciones Globales v2 (Bridge Table, Area Responsable, Secuencias)...
%PSQL% -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "d:\Datawrehouse_RA\v2\etl_carga_datos_v2.sql"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falló la ejecución de ETL v2.
    exit /b %ERRORLEVEL%
)

echo [3/4] Ejecutando Transformaciones Globales v3 (Pagos JBPM Históricos para todos los proyectos)...
%PSQL% -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "d:\Datawrehouse_RA\v3\etl_carga_datos_v3.sql"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falló la ejecución de ETL v3.
    exit /b %ERRORLEVEL%
)

echo [4/4] Ejecutando Carga de Intersecciones Ambientales v1.9.1...
%PSQL% -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -f "d:\Datawrehouse_RA\etl_intersection_load.sql"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falló la ejecución de Intersecciones v1.9.
    exit /b %ERRORLEVEL%
)

echo [INFO] ----------------------------------------------------
echo [INFO] Job completado exitosamente con cálculo global e intersecciones aplicados.
