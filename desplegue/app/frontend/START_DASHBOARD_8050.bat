@echo off
setlocal
cd /d %~dp0
title Dashboard Principal - Puerto 8050

echo ==========================================================
echo   DASHBOARD PRINCIPAL ECO-SIEAA v1.01  ^|  Puerto 8050
echo ==========================================================
echo.

:: Verificar Entorno Virtual
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encuentra python.exe en .venv\Scripts\
    echo Asegurese de haber creado el entorno virtual en D:\DashboardRA\.venv
    pause
    exit /b
)

:: ---- Liberar Puerto 8050 si esta ocupado ----
echo [PRE] Verificando si el puerto 8050 esta en uso...
set FOUND=0
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8050 " ^| findstr "LISTENING"') do (
    echo     -> Proceso encontrado PID %%a. Terminando...
    taskkill /PID %%a /F >nul 2>&1
    set FOUND=1
)
if %FOUND%==0 (
    echo     -> Puerto 8050 libre. OK
)

timeout /t 1 /nobreak >nul
echo.

:: ---- Arrancar Dashboard ----
echo [OK] Iniciando Dashboard Principal en http://localhost:8050
echo      Abriendo navegador automaticamente...
echo.

start "" "http://localhost:8050"
.venv\Scripts\streamlit.exe run Dash_board_RG_v1.01\Dash_board_RG_v1.01.py --server.port 8050 --server.headless false
