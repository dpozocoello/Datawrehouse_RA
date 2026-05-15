#!/bin/bash
# install_ubuntu.sh - Instalador para Ubuntu Server (??ltima estable)
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

echo "Instalaci??n completada."
