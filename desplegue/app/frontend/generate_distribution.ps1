# generate_distribution.ps1
# Script para generar el paquete de distribución del Dashboard ECO-SIEAA
# Compatible con Windows (Generador) y Linux (Target)

$ErrorActionPreference = "Stop"

$projectName = "DashboardRA"
$distDir = "distribucion"
$zipFile = "DashboardRA_Distribution_$(Get-Date -Format 'yyyyMMdd_HHmm').zip"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GENERADOR DE DISTRIBUCIÓN ECO-SIEAA v1.01" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Limpiar/Crear carpeta de distribución
if (Test-Path $distDir) {
    Write-Host "[1/6] Limpiando carpeta de distribución existente..."
    Remove-Item -Path $distDir -Recurse -Force
}
New-Item -ItemType Directory -Path "$distDir/app" -Force | Out-Null
New-Item -ItemType Directory -Path "$distDir/scripts" -Force | Out-Null
New-Item -ItemType Directory -Path "$distDir/sql" -Force | Out-Null
New-Item -ItemType Directory -Path "$distDir/assets" -Force | Out-Null

# 2. Copiar archivos de la aplicación
Write-Host "[2/6] Copiando archivos de la aplicación..."
$appFiles = @(
    "Dash_board_RG_v1.01/Dash_board_RG_v1.01.py",
    "Dash_board_RG_v1.01/auth_utils.py",
    "Dash_board_RG_v1.01/config_utils.py",
    "Dash_board_RG_v1.01/environmental_engine.py",
    "Dash_board_RG_v1.01/dashboard_config.json",
    "Dash_board_RG_v1.01/ecuador_cantones.geojson",
    "Dash_board_RG_v1.01/ecuador_provincias.geojson",
    "requirements.txt"
)

foreach ($file in $appFiles) {
    $src = $file
    $dest = "$distDir/app/$(Split-Path $file -Leaf)"
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dest
    } else {
        Write-Warning "Archivo no encontrado: $src"
    }
}

# Copiar assets
if (Test-Path "assets") {
    Copy-Item -Path "assets" -Destination "$distDir/app/assets" -Recurse
}

# 3. Copiar scripts SQL
Write-Host "[3/6] Copiando scripts de base de datos..."
$sqlFiles = @(
    "Scripts_obtencion_data.sql",
    "Dash_board_RG_v1.01/setup_roles_v2.sql",
    "Dash_board_RG_v1.01/setup_security_schema.sql"
)
foreach ($sql in $sqlFiles) {
    if (Test-Path $sql) {
        Copy-Item -Path $sql -Destination "$distDir/sql/$(Split-Path $sql -Leaf)"
    }
}

# 4. Generar Scripts de Instalación para Linux
Write-Host "[4/6] Generando scripts de instalación para Rocky Linux y Ubuntu..."

$rockyScript = @"
#!/bin/bash
# install_rocky.sh - Instalador para Rocky Linux 10
set -e

echo "Instalando dependencias del sistema en Rocky Linux 10..."
sudo dnf update -y
sudo dnf install -y python3.12 python3.12-devel postgresql-devel gcc git

echo "Configurando entorno virtual..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r app/requirements.txt

echo "Configurando permisos..."
chmod +x start_dashboard.sh

echo "Instalación completada."
"@

$ubuntuScript = @"
#!/bin/bash
# install_ubuntu.sh - Instalador para Ubuntu Server (Última estable)
set -e

echo "Instalando dependencias del sistema en Ubuntu..."
sudo apt update
sudo apt install -y python3-venv python3-pip libpq-dev gcc git

echo "Configurando entorno virtual..."
python3 -m venv .venv
source .venv/bin/activate

echo "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r app/requirements.txt

echo "Configurando permisos..."
chmod +x start_dashboard.sh

echo "Instalación completada."
"@

$startScript = @"
#!/bin/bash
# start_dashboard.sh - Lanzador para Linux
source .venv/bin/activate
streamlit run app/Dash_board_RG_v1.01.py --server.port 8050 --server.headless true
"@

$readme = @"
# Dashboard ECO-SIEAA v1.01 - Distribución

Este paquete contiene todo lo necesario para instalar el Dashboard en servidores Linux.

## Estructura
- /app: Código fuente y GeoJSON.
- /scripts: Instaladores para Rocky Linux y Ubuntu.
- /sql: Scripts de inicialización de Base de Datos.

## Instalación

1. Copiar esta carpeta al servidor (ej. /opt/dashboard).
2. Ejecutar el script correspondiente a su distribución:
   - Rocky Linux 10: `bash scripts/install_rocky.sh`
   - Ubuntu Server: `bash scripts/install_ubuntu.sh`
3. Configurar la base de datos PostgreSQL utilizando los scripts en /sql.
4. Ejecutar el dashboard: `./start_dashboard.sh`

## Nota sobre PostgreSQL
Asegúrese de que el servidor tenga acceso a una base de datos PostgreSQL y que las credenciales en `app/Dash_board_RG_v1.01.py` o variables de entorno sean correctas.
"@

$rockyScript | Out-File -FilePath "$distDir/scripts/install_rocky.sh" -Encoding ascii
$ubuntuScript | Out-File -FilePath "$distDir/scripts/install_ubuntu.sh" -Encoding ascii
$startScript | Out-File -FilePath "$distDir/start_dashboard.sh" -Encoding ascii
$readme | Out-File -FilePath "$distDir/README_INSTALL.md" -Encoding utf8

# 5. Comprimir paquete
Write-Host "[5/6] Comprimiendo paquete de distribución..."
if (Test-Path $zipFile) { Remove-Item $zipFile }
Compress-Archive -Path "$distDir/*" -DestinationPath $zipFile

# 6. Finalizar
Write-Host "[6/6] Proceso completado con éxito." -ForegroundColor Green
Write-Host "Archivo generado: $zipFile" -ForegroundColor Yellow
Write-Host "Carpeta de origen: $distDir" -ForegroundColor Yellow
