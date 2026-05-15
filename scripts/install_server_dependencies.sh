#!/bin/bash

# ==============================================================================
# Script de Instalación y Configuración para Servidor DWH (Ubuntu 24.04)
# Componentes: PostgreSQL 16, Java 11 (OpenJDK), Pentaho Data Integration 9.4
# Ejecutar como: root
# ==============================================================================

set -e # Detener la ejecución si hay un error

echo "========================================"
echo "Iniciando configuración del servidor DWH"
echo "========================================"

# 1. Actualizar el sistema
echo "--> Actualizando repositorios y paquetes..."
apt-get update -y
apt-get upgrade -y
apt-get install -y wget curl unzip gnupg2 software-properties-common rsync

# 2. Instalar Java (Requisito estricto para Pentaho)
echo "--> Instalando OpenJDK 11..."
apt-get install -y openjdk-11-jdk
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /etc/environment

# 3. Instalar PostgreSQL 16
echo "--> Instalando PostgreSQL 16..."
apt-get install -y postgresql postgresql-contrib

echo "--> Configurando usuario postgres..."
# Cambiar la contraseña del usuario postgres en la base de datos
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Encontrar la ruta de configuración dinámicamente (ya que se instaló la versión 18 o superior por los repositorios de Postgres)
PG_CONF=$(find /etc/postgresql -name postgresql.conf | head -n 1)
PG_HBA=$(find /etc/postgresql -name pg_hba.conf | head -n 1)

if [ -f "$PG_CONF" ]; then
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" "$PG_CONF"
fi

if [ -f "$PG_HBA" ]; then
    echo "host    all             all             0.0.0.0/0               scram-sha-256" >> "$PG_HBA"
fi

echo "--> Reiniciando PostgreSQL..."
systemctl restart postgresql
systemctl enable postgresql

# 4. Descargar e Instalar Pentaho Data Integration (PDI CE 9.4)
echo "--> Instalando Pentaho Data Integration 9.4..."
mkdir -p /opt/pentaho
cd /opt/pentaho

if [ ! -f "pdi-ce-9.4.0.0-343.zip" ]; then
    echo "Descargando PDI CE 9.4 (Esto puede tomar varios minutos dependiendo del internet)..."
    wget https://privatefilesbucket-community-edition.s3.us-west-2.amazonaws.com/9.4.0.0-343/ce/client-tools/pdi-ce-9.4.0.0-343.zip
fi

echo "Descomprimiendo PDI..."
unzip -q pdi-ce-9.4.0.0-343.zip
rm pdi-ce-9.4.0.0-343.zip

# Dar permisos de ejecución a los scripts de Pentaho
chmod +x /opt/pentaho/data-integration/*.sh

# 5. Crear directorio para el proyecto
echo "--> Creando directorio de despliegue para el ETL..."
mkdir -p /opt/dwh_project
chown -R root:root /opt/dwh_project

echo "=========================================================="
echo "¡Instalación completada con éxito!"
echo "PostgreSQL Puerto: 5432"
echo "Usuario DB: postgres | Clave: postgres"
echo "Directorio Pentaho: /opt/pentaho/data-integration"
echo "Directorio Proyecto: /opt/dwh_project"
echo "=========================================================="
