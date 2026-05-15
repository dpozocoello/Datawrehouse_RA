@echo off
:: ==============================================================================
:: instalar_tareas.bat
:: Registra las tareas programadas del DWH en el Programador de Windows.
:: REQUIERE: Ejecutar como Administrador
:: ==============================================================================

setlocal
SET SCHEDULER_DIR=%~dp0

echo.
echo  ============================================================
echo   INSTALADOR DE TAREAS PROGRAMADAS - DWH REGULARIZACION
echo  ============================================================
echo.

:: Verificar privilegios de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Permisos insuficientes.
    echo  Haga click derecho sobre este archivo y seleccione
    echo  "Ejecutar como administrador", luego intente de nuevo.
    echo.
    pause
    exit /b 1
)

echo  [1/2] Registrando tarea: DWH_ETL_Diario (02:00 AM)...
schtasks /create /xml "%SCHEDULER_DIR%DWH_ETL_Diario.xml" /tn "DWH_ETL_Diario" /f
if %errorlevel% equ 0 (
    echo        CREADA exitosamente.
) else (
    echo        ERROR al crear la tarea ETL. Verifique el log de eventos.
)

echo.
echo  [2/2] Registrando tarea: DWH_Mantenimiento_Diario (05:00 AM)...
schtasks /create /xml "%SCHEDULER_DIR%DWH_Mantenimiento_Diario.xml" /tn "DWH_Mantenimiento_Diario" /f
if %errorlevel% equ 0 (
    echo        CREADA exitosamente.
) else (
    echo        ERROR al crear la tarea Mantenimiento. Verifique el log de eventos.
)

echo.
echo  ============================================================
echo   VERIFICACION
echo  ============================================================
echo.
schtasks /query /tn "DWH_ETL_Diario" /fo LIST 2>nul
echo.
schtasks /query /tn "DWH_Mantenimiento_Diario" /fo LIST 2>nul

echo.
echo  ============================================================
echo   PROGRAMACION CONFIGURADA:
echo    - ETL          : diario 02:00 AM  (limite 4h, reintento 30min)
echo    - Mantenimiento: diario 05:00 AM  (limite 2h, reintento 15min)
echo    - Logs         : D:\Datawrehouse_RA\logs\
echo    - Usuario      : AMBIENTE\javier.pozo
echo  ============================================================
echo.
pause
endlocal
