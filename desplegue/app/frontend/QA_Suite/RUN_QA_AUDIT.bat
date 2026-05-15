@echo off
setlocal
cd /d %~dp0
cd ..

set REPORT=QA_Suite\ULTIMA_AUDITORIA.txt
echo ========================================================== > %REPORT%
echo    REPORTE DE AUDITORIA QA: DASHBOARD RA V1.01 >> %REPORT%
echo    FECHA: %DATE% %TIME% >> %REPORT%
echo ========================================================== >> %REPORT%
echo. >> %REPORT%

echo [+] Iniciando Auditoria Completa...

echo [1/4] Pruebas de Integridad de Datos (Back-End)...
call .venv\Scripts\activate.bat && pytest QA_Suite\test_data_integrity.py -v --tb=short >> %REPORT% 2>&1

echo [2/4] Auditoria de los 5 Pilares de Calidad (DQ Audit)...
call .venv\Scripts\activate.bat && pytest QA_Suite\test_dq_pillars.py -v --tb=short >> %REPORT% 2>&1

echo [3/4] Auditoria de Sustancias y Desechos (Residuos)...
call .venv\Scripts\activate.bat && pytest QA_Suite\test_waste_data.py -v --tb=short >> %REPORT% 2>&1

echo [4/4] Pruebas de Conectividad UI (Smoke Tests)...
call .venv\Scripts\activate.bat && pytest QA_Suite\test_ui_connectivity.py -v --tb=short >> %REPORT% 2>&1

echo. >> %REPORT%
echo ========================================================== >> %REPORT%
echo  AUDITORIA FINALIZADA. Consulte QA_Suite\INFORME_VALIDACION_QA.md para leer el manual. >> %REPORT%
echo ========================================================== >> %REPORT%

cls
type %REPORT%
echo.
echo ==========================================================
echo  EL REPORTE SE HA GUARDADO EN: %REPORT%
echo ==========================================================
pause
