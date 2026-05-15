# ------------------------------------------------------------------------------
# AUTOMATIZACIÓN DE SMOKE TEST - RGD v2.0
# ------------------------------------------------------------------------------
# Este script realiza:
# 1. Respaldo de esquemas dw y stg.
# 2. Limpieza total de datos.
# 3. Ejecución del Job Diario de Pentaho.
# ------------------------------------------------------------------------------

$ErrorActionPreference = "Stop"

# --- Configuración de Entorno ---
$PG_BIN = "C:\Program Files\PostgreSQL\17\bin"
if (Test-Path $PG_BIN) {
    $env:PATH = "$PG_BIN;" + $env:PATH
} else {
    Write-Warning "No se encontró el directorio de binarios de PostgreSQL en $PG_BIN. Asegúrese de que esté en el PATH."
}

# Configuración
$DB_NAME = "dw_reg_v1"
$DB_USER = "postgres"
$BACKUP_DIR = "D:\Datawrehouse_RA\backups"
$BACKUP_FILE = "$BACKUP_DIR\backup_pre_smoke_$(Get-Date -Format 'yyyyMMdd_HHmm').sql"
$CLEAN_SQL = "D:\Datawrehouse_RA\v2\clean_dwh_data.sql"
$MASTER_BAT = "D:\Datawrehouse_RA\Jobs\job_diario_dwh.bat"

# Crear directorio de backup si no existe
if (!(Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR
    Write-Host "Directorio de backups creado: $BACKUP_DIR" -ForegroundColor Cyan
}

# 1. RESPALDO
#Write-Host "--- PASO 1: Generando Backup de dw y stg ---" -ForegroundColor Yellow
#$env:PGPASSWORD = "postgres"
#& pg_dump -h localhost -U $DB_USER -d $DB_NAME -n dw -n stg -f $BACKUP_FILE
#Write-Host "Backup completado: $BACKUP_FILE" -ForegroundColor Green

# 2. LIMPIEZA
Write-Host "--- PASO 2: Limpiando datos (Truncate) ---" -ForegroundColor Yellow
& psql -h localhost -U $DB_USER -d $DB_NAME -f $CLEAN_SQL
Write-Host "Limpieza completada." -ForegroundColor Green

# 3. EJECUCIÓN
Write-Host "--- PASO 3: Iniciando Carga de Datos (Smoke Test) ---" -ForegroundColor Yellow
Set-Location "D:\Datawrehouse_RA\Jobs"
& $MASTER_BAT

Write-Host "--- PROCESO FINALIZADO ---" -ForegroundColor Cyan
