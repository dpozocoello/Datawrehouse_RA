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

echo "Instalaci??n completada."
