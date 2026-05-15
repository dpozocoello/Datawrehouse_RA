# ==============================================================================
# config.py — Configuración de conexiones y parámetros del ETL
# ==============================================================================
# Este módulo centraliza TODAS las credenciales y parámetros de conexión
# a las bases de datos origen y destino del Data Warehouse.
#
# IMPORTANTE: En un entorno productivo, estas credenciales deberían
# obtenerse de variables de entorno o un gestor de secretos (vault).
# ==============================================================================

import os
import pathlib

# ==============================================================================
# DETECCIÓN DE RUTAS (Path Normalization v1.9.5)
# ==============================================================================
# Detectar la raíz del proyecto (un nivel arriba de /ETL_p)
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()

# Directorio de logs
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

# Rutas de Insumos y Metadatos
GEO_JSON_PATH = os.path.join(PROJECT_ROOT, "area_geo_hierarchy_FIXED.json")
DWH_DDL_PATH = os.path.join(PROJECT_ROOT, "ddl_dwh_completo_v1_9_5.sql")

# ==============================================================================
# CONEXIONES A BASES DE DATOS ORIGEN (Producción)
# ==============================================================================

# Servidor SUIA — Sistema Único de Información Ambiental
CONN_SUIA_ENLISY = {
    "host": os.getenv("SUIA_HOST", "172.16.0.179"),
    "port": int(os.getenv("SUIA_PORT", "5632")),
    "database": "suia_enlisy",
    "user": os.getenv("SUIA_USER", "postgres"),
    "password": os.getenv("SUIA_PASSWORD", "postgres"),
}

# Servidor SUIA BPM — Motor de procesos de negocio
CONN_SUIA_BPMS = {
    "host": os.getenv("SUIA_HOST", "172.16.0.179"),
    "port": int(os.getenv("SUIA_PORT", "5632")),
    "database": "suia_bpms_enlisy_app",
    "user": os.getenv("SUIA_USER", "postgres"),
    "password": os.getenv("SUIA_PASSWORD", "postgres"),
}

# Servidor JBPM — Motor de procesos jBPM (actual)
CONN_JBPM = {
    "host": os.getenv("JBPM_HOST", "172.16.0.226"),
    "port": int(os.getenv("JBPM_PORT", "5432")),
    "database": "jbpmdb",
    "user": os.getenv("JBPM_USER", "postgres"),
    "password": os.getenv("JBPM_PASSWORD", "postgres"),
}

# Servidor JBPM Old — Motor de procesos jBPM (legacy)
CONN_JBPM_OLD = {
    "host": os.getenv("JBPM_HOST", "172.16.0.226"),
    "port": int(os.getenv("JBPM_PORT", "5432")),
    "database": "jbpmdb_prod_old",
    "user": os.getenv("JBPM_USER", "postgres"),
    "password": os.getenv("JBPM_PASSWORD", "postgres"),
}

# ==============================================================================
# CONEXIÓN A BASE DE DATOS DESTINO (Data Warehouse)
# ==============================================================================

# Servidor local — Data Warehouse de Regularización Ambiental
CONN_DWH_LOCAL = {
    "host": os.getenv("DWH_HOST", "localhost"),
    "port": int(os.getenv("DWH_PORT", "5432")),
    "database": os.getenv("DWH_DATABASE", "dw_reg_v1"),
    "user": os.getenv("DWH_USER", "postgres"),
    "password": os.getenv("DWH_PASSWORD", "postgres"),
}

# ==============================================================================
# PARÁMETROS GENERALES DEL ETL
# ==============================================================================

# Tamaño de lote para inserciones masivas
BATCH_SIZE = 1000

# Nivel de logging
LOG_LEVEL = os.getenv("ETL_LOG_LEVEL", "INFO")

# PASOS HABILITADOS
PASOS_HABILITADOS = {
    "SP_ORQUESTAR_EXTRACCION": True,
    "TRX_01_SUIA_RCOA": True,
    "TRX_02_SUIA_COA": True,
    "TRX_03_JBPM_SECTOR": True,
    "TRX_04_JBPM_4CAT": True,
    "TRX_05_JBPM_HIDRO": False,
    "TRX_06_SNAP": True,
    "TRX_07_PAGOS_JBPM": True,
    "TRX_08_PAGOS_SUIA": True,
    "TRX_09_PAGOS_HIST": True,
    "TRX_10_AREAS": True,
    "TRX_10B_AREAS_TYPES": True,
    "TRX_11_GEOGRAFIA": True,
    "SETUP_REFERENCE_DATA": True,
    "SP_CONSOLIDAR_STAGING": True,
    "SP_CARGA_DIMENSIONES": True,
    "SP_CARGA_DIM_AREA": True,
    "SP_JERARQUIA_AREA": True,
    "SP_CARGA_HECHOS": True,
    "SP_CARGA_DIM_PAGO": True,
    "SP_CARGA_FACT_PAGO": True,
    "UPDATE_AREA_RESPONSABLE": True,
    "SP_BRIDGE_PROYECTO_GEO": True,
    "RECALCULO_MONTOS_JBPM": True,
    "SP_SECUENCIA_PAGOS": True,
    "SP_CARGA_PUENTE_AMBIENTAL": True,
    "INGESTA_WASTE_CHEMICAL": True,
    "SP_CARGA_WASTE_CHEMICAL": True,
    "INGESTA_INTERSECTION": True,
    "RECOVER_MISSING_PROJECTS": True,
    "SP_CARGA_DIM_INTERSECTION": True,
}
