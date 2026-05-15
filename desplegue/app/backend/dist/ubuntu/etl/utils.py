# ==============================================================================
# utils.py — Utilidades compartidas del ETL (logging, métricas, decoradores)
# ==============================================================================
# Proporciona funciones transversales usadas por todos los módulos del ETL:
# - Configuración centralizada de logging con salida a archivo y consola
# - Decorador para medir tiempo de ejecución de cada paso
# - Funciones de verificación post-ejecución
# ==============================================================================

import os
import sys
import time
import logging
from datetime import datetime
from functools import wraps


def get_logger(name: str) -> logging.Logger:
    """
    Crea y configura un logger con salida dual (consola + archivo).

    El archivo de log se almacena en el directorio 'log/' con el formato:
    etl_YYYYMMDD.log (un archivo por día).

    Parámetros:
    -----------
    name : str
        Nombre del módulo que solicita el logger (típicamente __name__).

    Retorna:
    --------
    logging.Logger
        Logger configurado con handlers para consola y archivo.
    """
    # Importar nivel de log desde config (evita import circular)
    try:
        from config import LOG_LEVEL, LOG_DIR
    except ImportError:
        LOG_LEVEL = "INFO"
        LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")

    # Crear directorio de logs si no existe
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Evitar duplicar handlers si el logger ya fue configurado
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # Formato detallado para archivo
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Formato simplificado para consola
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )

    # Handler: Archivo del día
    log_filename = datetime.now().strftime("etl_%Y%m%d.log")
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, log_filename),
        encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler: Consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def medir_tiempo(paso_nombre: str):
    """
    Decorador que mide y registra el tiempo de ejecución de una función.

    Se usa para envolver cada paso del ETL y generar métricas de rendimiento.

    Parámetros:
    -----------
    paso_nombre : str
        Nombre descriptivo del paso (ej: 'TRX_01_SUIA_RCOA').

    Ejemplo:
    --------
    >>> @medir_tiempo("TRX_01_SUIA_RCOA")
    ... def ejecutar_trx_01():
    ...     # lógica de ingesta
    ...     return 15000
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("METRICAS")
            inicio = time.time()
            logger.info(f"{'='*60}")
            logger.info(f"[{paso_nombre}] [START] INICIANDO...")
            logger.info(f"{'='*60}")

            try:
                resultado = func(*args, **kwargs)
                duracion = time.time() - inicio
                minutos = int(duracion // 60)
                segundos = duracion % 60
                logger.info(f"[{paso_nombre}] [OK] COMPLETADO en {minutos}m {segundos:.1f}s")
                return resultado
            except Exception as e:
                duracion = time.time() - inicio
                logger.error(f"[{paso_nombre}] [ERROR] después de {duracion:.1f}s: {e}")
                raise
        return wrapper
    return decorator


def verificar_conteos(conn_params: dict) -> dict:
    """
    Ejecuta consultas de verificación post-ETL y retorna un resumen
    con los conteos de todas las tablas del DWH.

    Parámetros:
    -----------
    conn_params : dict
        Parámetros de conexión al DWH local.

    Retorna:
    --------
    dict
        Diccionario {nombre_tabla: conteo_filas}.
    """
    from connections import get_connection

    tablas = [
        # Staging
        "stg.suia_rcoa_bi", "stg.suia_coa_bi", "stg.jbpm_sector_bi",
        "stg.jbpm_4cat_bi", "stg.jbpm_hidro_bi", "stg.jbpm_snap_variables",
        "stg.consolidado_proyectos",
        # Dimensiones
        "dw.dim_proyecto", "dw.dim_proponente", "dw.dim_actividad",
        "dw.dim_geografia", "dw.dim_usuario", "dw.dim_estado", "dw.dim_tiempo",
        # Hechos
        "dw.fact_regularizacion", "dw.fact_pago", "dw.fact_proyecto_geografia",
    ]

    logger = get_logger("VERIFICACION")
    conteos = {}

    with get_connection(conn_params) as conn:
        with conn.cursor() as cur:
            for tabla in tablas:
                try:
                    cur.execute(f"SELECT COUNT(1) FROM {tabla}")
                    conteo = cur.fetchone()[0]
                    conteos[tabla] = conteo
                    logger.info(f"  {tabla:45s} → {conteo:>10,} filas")
                except Exception as e:
                    conteos[tabla] = -1
                    logger.warning(f"  {tabla:45s} → ERROR: {e}")

    return conteos
