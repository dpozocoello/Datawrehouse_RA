@echo off
setlocal
cd /d %~dp0
title DashboardRA - Iniciador de Servicios

echo ==========================================================
echo    INICIADOR DE SERVICIOS: REGULARIZACION AMBIENTAL
echo ==========================================================
echo.

:: Verificar Entorno Virtual
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encuentra python.exe en .venv\Scripts\
    echo Asegurese de haber creado el entorno virtual en D:\DashboardRA\.venv
    pause
    exit /b
)

:: ---- Liberar Puerto 8103 si esta ocupado ----
echo [PRE] Verificando puerto 8103...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8103 " ^| findstr "LISTENING"') do (
    echo     Terminando proceso PID %%a en puerto 8103...
    taskkill /PID %%a /F >nul 2>&1
)

:: ---- Liberar Puerto 8050 si esta ocupado ----
echo [PRE] Verificando puerto 8050...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8050 " ^| findstr "LISTENING"') do (
    echo     Terminando proceso PID %%a en puerto 8050...
    taskkill /PID %%a /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo [1/2] Iniciando Portal de Integridad (Puerto 8103)...
start "Portal RA 8103" /min cmd /c ".venv\Scripts\streamlit.exe run dashboard_ra.py --server.port 8103 --server.headless true"

timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Dashboard Principal v1.01 (Puerto 8050)...
start "Dashboard RA 8050" /min cmd /c ".venv\Scripts\streamlit.exe run Dash_board_RG_v1.01\Dash_board_RG_v1.01.py --server.port 8050 --server.headless true"

echo.
echo ==========================================================
echo  SERVICIOS LANZADOS EXITOSAMENTE
echo ==========================================================
echo  Portal:    http://localhost:8103
echo  Dashboard: http://localhost:8050
echo ==========================================================
echo.
echo Esta ventana puede cerrarse. Los servicios continuaran
echo ejecutandose en segundo plano (minimizados).
echo.
pause
