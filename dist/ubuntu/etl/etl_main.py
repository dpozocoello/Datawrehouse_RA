#!/usr/bin/env python3
# ==============================================================================
# etl_main.py — Orquestador principal del ETL Data Warehouse
# ==============================================================================
# Este es el punto de entrada del proceso ETL. Ejecuta secuencialmente
# las 18 etapas del pipeline: 9 ingestas + 9 transformaciones.
#
# Equivale al job maestro de Pentaho:
#   JOB_CARGA_DWH_REGULARIZACION.kjb
#
# Uso:
#   python3 etl_main.py              → Ejecuta todo el ETL
#   python3 etl_main.py --verificar  → Solo ejecuta verificación post-ETL
#   python3 etl_main.py --desde 14   → Ejecuta desde el paso 14 en adelante
#
# Autor: Arquitectura de Datos — DWH Team
# Fecha: 2026-03-05
# ==============================================================================

import sys
import os
import time
import argparse
from datetime import datetime

# Asegurar que el directorio raíz del ETL esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONN_DWH_LOCAL, PASOS_HABILITADOS
from utils import get_logger, verificar_conteos

# Importar módulos de ingesta
from ingesta.ingesta_all import (
    ejecutar_trx_01,
    ejecutar_trx_02,
    ejecutar_trx_03,
    ejecutar_trx_04,
    ejecutar_trx_05,
    ejecutar_trx_06,
    ejecutar_trx_07,
    ejecutar_trx_08,
    ejecutar_trx_09,
    ejecutar_trx_10,
    ejecutar_trx_11,
)

from ingesta.ingesta_waste_chemical import ejecutar_ingesta_waste_chemical
from ingesta.ingesta_intersection import ejecutar_ingesta_intersection_v2
from ingesta.recover_missing_projects_etl import ejecutar_recovery_proyectos

# Importar módulos de transformación
from transformacion.transformacion_all import (
    sp_consolidar_staging,
    sp_carga_dimensiones,
    sp_carga_hechos,
    sp_carga_dim_pago,
    sp_carga_fact_pago,
    sp_carga_dim_area,
    update_area_responsable,
    sp_bridge_proyecto_geo,
    recalculo_montos_jbpm,
    sp_secuencia_pagos,
    sp_orquestar_extraccion_remota,
    sp_carga_puente_ambiental,
    sp_carga_waste_chemical,
    sp_carga_dim_intersection,
)

logger = get_logger("ETL_MAIN")

# ==============================================================================
# DEFINICIÓN DE LA SECUENCIA DE PASOS DEL ETL
# ==============================================================================
# Cada paso es una tupla: (número, clave_config, nombre_descriptivo, función)
#
# La clave_config se usa para verificar si el paso está habilitado
# en config.PASOS_HABILITADOS. Los pasos deshabilitados se saltan
# pero se registran en el log como "SALTADO".
# ==============================================================================

SECUENCIA_ETL = [
    # --- FASE 1: INGESTA (Extracción desde orígenes remotos) ---
    (1,  "SP_ORQUESTAR_EXTRACCION",  "Orquestación Remota v1.4.1",     sp_orquestar_extraccion_remota),
    (2,  "TRX_01_SUIA_RCOA",        "Ingesta SUIA RCOA",              ejecutar_trx_01),
    (3,  "TRX_02_SUIA_COA",         "Ingesta SUIA COA",               ejecutar_trx_02),
    (4,  "TRX_03_JBPM_SECTOR",      "Ingesta JBPM Sector",            ejecutar_trx_03),
    (5,  "TRX_04_JBPM_4CAT",        "Ingesta JBPM 4 Categorías",      ejecutar_trx_04),
    (6,  "TRX_05_JBPM_HIDRO",       "Ingesta JBPM Hidrocarburos",     ejecutar_trx_05),
    (7,  "TRX_06_SNAP",             "Ingesta SNAP Variables",          ejecutar_trx_06),
    (8,  "TRX_07_PAGOS_JBPM",       "Ingesta Pagos JBPM",             ejecutar_trx_07),
    (9,  "TRX_08_PAGOS_SUIA",       "Ingesta Pagos SUIA",             ejecutar_trx_08),
    (10, "TRX_10_AREAS",             "Ingesta Areas SUIA",             ejecutar_trx_10),
    (11, "TRX_11_GEOGRAFIA",        "Ingesta Geografía",              ejecutar_trx_11),

    # --- FASE 2: TRANSFORMACIÓN (Stored Procedures y SQL) ---
    (12, "SP_CONSOLIDAR_STAGING",    "SP Consolidar Staging",          sp_consolidar_staging),
    (13, "SP_CARGA_DIMENSIONES",     "SP Cargar Dimensiones",          sp_carga_dimensiones),
    (14, "SP_CARGA_DIM_AREA",        "SP Cargar Dim Area",             sp_carga_dim_area),
    (15, "SP_CARGA_HECHOS",          "SP Cargar Fact Regularización",  sp_carga_hechos),
    (16, "SP_CARGA_DIM_PAGO",        "SP Cargar Dim Pago",             sp_carga_dim_pago),
    (17, "SP_CARGA_FACT_PAGO",       "SP Cargar Fact Pago",            sp_carga_fact_pago),
    (18, "UPDATE_AREA_RESPONSABLE",  "Update Área Responsable (v2)",   update_area_responsable),
    (19, "SP_BRIDGE_PROYECTO_GEO",   "SP Bridge Proyecto-Geo (v2)",    sp_bridge_proyecto_geo),

    # --- FASE 3: PAGOS HISTÓRICOS (v3) ---
    (20, "TRX_09_PAGOS_HIST",        "Ingesta Pagos Históricos (v3)",  ejecutar_trx_09),
    (21, "RECALCULO_MONTOS_JBPM",    "Recálculo Montos JBPM (v3)",     recalculo_montos_jbpm),
    (22, "SP_SECUENCIA_PAGOS",       "SP Secuencia Pagos (v2/v3)",     sp_secuencia_pagos),
    (23, "SP_CARGA_PUENTE_AMBIENTAL","SP Cargar Puente Ambiental",     sp_carga_puente_ambiental),
    
    # --- FASE 4: DESECHOS Y SUSTANCIAS QUÍMICAS (v1.5) ---
    (24, "INGESTA_WASTE_CHEMICAL",   "Ingesta Desechos/Químicos",      ejecutar_ingesta_waste_chemical),
    (25, "SP_CARGA_WASTE_CHEMICAL",  "SP Carga Desechos/Químicos",     sp_carga_waste_chemical),

    # --- FASE 5: INTERSECCIONES AMBIENTALES (v1.9.1) ---
    (26, "INGESTA_INTERSECTION",      "Ingesta Intersecciones (v1.9)",  ejecutar_ingesta_intersection_v2),
    (27, "RECOVER_MISSING_PROJECTS",  "Recuperar Proyectos Faltantes",  ejecutar_recovery_proyectos),
    (28, "SP_CARGA_DIM_INTERSECTION", "SP Cargar Dim Intersección",     sp_carga_dim_intersection),
]


def ejecutar_etl(paso_desde: int = 1, paso_hasta: int = 21):
    """
    Ejecuta el pipeline ETL completo o un rango de pasos.

    Parámetros:
    -----------
    paso_desde : int
        Número del primer paso a ejecutar (1-21). Default: 1.
    paso_hasta : int
        Número del último paso a ejecutar (1-21). Default: 21.

    Comportamiento:
    ---------------
    - Los pasos deshabilitados en config.PASOS_HABILITADOS se saltan
    - Si un paso falla, el ETL se detiene y registra el error
    - Al finalizar, muestra un resumen con tiempos y estados

    Ejemplo:
    --------
    >>> ejecutar_etl()              # Ejecuta todo
    >>> ejecutar_etl(paso_desde=14) # Solo v2/v3
    """
    inicio_total = time.time()
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║  ETL DATA WAREHOUSE — REGULARIZACIÓN AMBIENTAL          ║")
    logger.info("║  Versión Python — Equivalente a Pentaho Job Maestro     ║")
    logger.info("╠" + "═" * 58 + "╣")
    logger.info(f"║  Inicio: {fecha_ejecucion}                        ║")
    logger.info(f"║  Pasos:  {paso_desde} a {paso_hasta} de 23                              ║")
    logger.info("╚" + "═" * 58 + "╝")

    resultados = []
    pasos_exitosos = 0
    pasos_saltados = 0
    pasos_fallidos = 0

    for num, clave, nombre, funcion in SECUENCIA_ETL:
        # Filtrar por rango solicitado
        if num < paso_desde or num > paso_hasta:
            continue

        # Verificar si el paso está habilitado en la configuración
        if not PASOS_HABILITADOS.get(clave, True):
            logger.warning(f"[Paso {num:02d}] ⊘ SALTADO (deshabilitado): {nombre}")
            resultados.append((num, nombre, "SALTADO", 0))
            pasos_saltados += 1
            continue

        # Ejecutar el paso
        inicio_paso = time.time()
        try:
            resultado = funcion()
            duracion = time.time() - inicio_paso
            resultados.append((num, nombre, "OK", duracion))
            pasos_exitosos += 1
        except Exception as e:
            duracion = time.time() - inicio_paso
            resultados.append((num, nombre, f"ERROR: {e}", duracion))
            pasos_fallidos += 1
            logger.error(f"[Paso {num:02d}] ✗ FALLÓ: {nombre} — {e}")
            logger.error("ETL DETENIDO por error en paso anterior.")
            break

    # ==========================================
    # RESUMEN FINAL
    # ==========================================
    duracion_total = time.time() - inicio_total
    minutos = int(duracion_total // 60)
    segundos = duracion_total % 60

    logger.info("")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║  RESUMEN DE EJECUCIÓN                                   ║")
    logger.info("╠" + "═" * 58 + "╣")

    for num, nombre, estado, duracion in resultados:
        icono = "✓" if estado == "OK" else ("⊘" if estado == "SALTADO" else "✗")
        tiempo_str = f"{duracion:.1f}s" if duracion > 0 else "---"
        logger.info(f"║  {icono} Paso {num:02d}: {nombre:35s} {tiempo_str:>8s}  ║")

    logger.info("╠" + "═" * 58 + "╣")
    logger.info(f"║  Exitosos: {pasos_exitosos}  |  Saltados: {pasos_saltados}  |  Fallidos: {pasos_fallidos}           ║")
    logger.info(f"║  Tiempo total: {minutos}m {segundos:.1f}s                               ║")
    logger.info("╚" + "═" * 58 + "╝")

    return pasos_fallidos == 0


def solo_verificar():
    """
    Ejecuta únicamente las consultas de verificación post-ETL.
    Útil para validar resultados sin re-ejecutar el pipeline.
    """
    logger.info("═" * 50)
    logger.info("VERIFICACIÓN POST-ETL")
    logger.info("═" * 50)
    conteos = verificar_conteos(CONN_DWH_LOCAL)
    logger.info("═" * 50)
    return conteos


# ==============================================================================
# PUNTO DE ENTRADA — CLI
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ETL Data Warehouse Regularización Ambiental (versión Python)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 etl_main.py                    # Ejecuta todo el ETL (pasos 1-21)
  python3 etl_main.py --verificar        # Solo verificación post-ETL
  python3 etl_main.py --desde 14         # Ejecuta desde paso 14 (v2/v3)
  python3 etl_main.py --desde 9 --hasta 13  # Solo SPs base (consolidar a fact_pago)
        """
    )
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="Solo ejecuta verificación post-ETL (conteos de tablas)"
    )
    parser.add_argument(
        "--desde",
        type=int,
        default=1,
        help="Número del paso inicial (1-20). Default: 1"
    )
    parser.add_argument(
        "--hasta",
        type=int,
        default=28,
        help="Número del paso final (1-28). Default: 28"
    )

    args = parser.parse_args()

    if args.verificar:
        solo_verificar()
    else:
        exito = ejecutar_etl(paso_desde=args.desde, paso_hasta=args.hasta)

        # Ejecutar verificación automática al finalizar exitosamente
        if exito:
            logger.info("")
            solo_verificar()

        # Código de salida: 0 = éxito, 1 = error
        sys.exit(0 if exito else 1)
