#!/usr/bin/env python3
# ==============================================================================
# mantenimiento_db.py — Mantenimiento Preventivo del DWH (PostgreSQL 17)
# ==============================================================================
# Ejecuta las tareas de mantenimiento diario del Data Warehouse local:
#   1. Verificación de espacio en disco
#   2. VACUUM ANALYZE sobre tablas con dead tuples acumulados
#   3. REINDEX CONCURRENTLY sobre índices con bloat
#   4. Actualización de estadísticas del planificador (ANALYZE)
#   5. Limpieza de archivos de log antiguos (> 7 días)
#   6. Informe de salud del servidor (tamaños, conexiones, bloat)
#   7. Alerta si espacio disponible < umbral crítico
#
# Uso:
#   python mantenimiento_db.py              → Ejecución completa
#   python mantenimiento_db.py --reindex    → Solo reindexación
#   python mantenimiento_db.py --informe    → Solo informe de salud
#
# Programación recomendada: 05:00 AM diario (post ETL)
# ==============================================================================

import os
import sys
import time
import glob
import shutil
import argparse
import psycopg2
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CONN_DWH_LOCAL, LOG_DIR
from utils import get_logger

logger = get_logger("MANTENIMIENTO")

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
DISCO_UMBRAL_GB       = 5.0       # Alerta si disco libre < 5 GB
LOG_RETENCION_DIAS    = 7         # Días de retención de logs ETL
DEAD_TUPLES_UMBRAL    = 10_000    # VACUUM si dead_tuples > este valor
TABLAS_PRIORITARIAS   = [         # Siempre vacuumizan independiente de dead tuples
    "dw.fact_regularizacion",
    "dw.fact_pago",
    "dw.fact_proyecto_geografia",
    "dw.dim_proyecto",
    "stg.consolidado_proyectos",
]

# ==============================================================================
# PASO 1: VERIFICACIÓN DE ESPACIO EN DISCO
# ==============================================================================
def verificar_espacio_disco() -> dict:
    """Verifica el espacio libre en disco. Lanza alerta si < umbral."""
    logger.info("=" * 60)
    logger.info("[DISCO] Verificando espacio disponible...")

    total, usado, libre = shutil.disk_usage("d:/")
    libre_gb   = libre  / (1024 ** 3)
    usado_gb   = usado  / (1024 ** 3)
    total_gb   = total  / (1024 ** 3)
    porcentaje = (usado / total) * 100

    logger.info(f"[DISCO] Total : {total_gb:.1f} GB")
    logger.info(f"[DISCO] Usado : {usado_gb:.1f} GB  ({porcentaje:.1f}%)")
    logger.info(f"[DISCO] Libre : {libre_gb:.1f} GB")

    if libre_gb < DISCO_UMBRAL_GB:
        logger.warning(f"[DISCO] *** ALERTA *** Espacio libre crítico: {libre_gb:.1f} GB < umbral {DISCO_UMBRAL_GB} GB")
        logger.warning("[DISCO] Considerar VACUUM FULL en tablas grandes o liberar espacio manualmente.")
    else:
        logger.info(f"[DISCO] Estado: OK (libre > {DISCO_UMBRAL_GB} GB)")

    return {"total_gb": total_gb, "usado_gb": usado_gb, "libre_gb": libre_gb, "pct_uso": porcentaje}


# ==============================================================================
# PASO 2: VACUUM ANALYZE SELECTIVO
# ==============================================================================
def ejecutar_vacuum(conn_params: dict) -> int:
    """
    Ejecuta VACUUM ANALYZE sobre:
    - Tablas prioritarias (siempre)
    - Tablas con dead_tuples > DEAD_TUPLES_UMBRAL
    Retorna número de tablas vacuumiadas.
    """
    logger.info("=" * 60)
    logger.info("[VACUUM] Iniciando VACUUM ANALYZE selectivo...")

    # Obtener tablas con dead tuples elevados
    conn_info = psycopg2.connect(**conn_params)
    conn_info.autocommit = True
    cur_info = conn_info.cursor()

    cur_info.execute("""
        SELECT schemaname || '.' || relname AS tabla,
               n_dead_tup,
               n_live_tup,
               pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS size
        FROM pg_stat_user_tables
        WHERE schemaname IN ('dw', 'stg')
          AND n_dead_tup > %s
        ORDER BY n_dead_tup DESC
    """, (DEAD_TUPLES_UMBRAL,))

    tablas_con_bloat = [(r[0], r[1], r[2], r[3]) for r in cur_info.fetchall()]

    # Unir con prioritarias (evitando duplicados)
    tablas_a_vacuumizar = list(dict.fromkeys(
        TABLAS_PRIORITARIAS + [t[0] for t in tablas_con_bloat]
    ))

    logger.info(f"[VACUUM] Tablas prioritarias     : {len(TABLAS_PRIORITARIAS)}")
    logger.info(f"[VACUUM] Tablas con bloat > {DEAD_TUPLES_UMBRAL:,}: {len(tablas_con_bloat)}")
    logger.info(f"[VACUUM] Total a vacuumizar      : {len(tablas_a_vacuumizar)}")

    vacuumiadas = 0
    for tabla in tablas_a_vacuumizar:
        inicio = time.time()
        try:
            logger.info(f"[VACUUM] Procesando: {tabla}...")
            cur_info.execute(f"VACUUM ANALYZE {tabla}")
            duracion = time.time() - inicio
            logger.info(f"[VACUUM] OK: {tabla} ({duracion:.1f}s)")
            vacuumiadas += 1
        except Exception as e:
            logger.warning(f"[VACUUM] ERROR en {tabla}: {e}")

    cur_info.close()
    conn_info.close()

    logger.info(f"[VACUUM] Completado: {vacuumiadas}/{len(tablas_a_vacuumizar)} tablas procesadas")
    return vacuumiadas


# ==============================================================================
# PASO 3: ANALYZE GLOBAL (estadísticas del planificador)
# ==============================================================================
def ejecutar_analyze(conn_params: dict):
    """Actualiza las estadísticas del planificador de consultas."""
    logger.info("=" * 60)
    logger.info("[ANALYZE] Actualizando estadísticas del planificador...")

    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    tablas_criticas = [
        "stg.consolidado_proyectos",
        "dw.fact_regularizacion",
        "dw.fact_pago",
        "dw.dim_proyecto",
        "dw.dim_proponente",
        "dw.dim_intersection",
    ]

    for tabla in tablas_criticas:
        try:
            cur.execute(f"ANALYZE {tabla}")
            logger.info(f"[ANALYZE] OK: {tabla}")
        except Exception as e:
            logger.warning(f"[ANALYZE] ERROR en {tabla}: {e}")

    cur.close()
    conn.close()
    logger.info("[ANALYZE] Estadísticas actualizadas.")


# ==============================================================================
# PASO 4: LIMPIEZA DE LOGS ANTIGUOS
# ==============================================================================
def limpiar_logs_antiguos() -> int:
    """Elimina archivos de log ETL con más de LOG_RETENCION_DIAS días."""
    logger.info("=" * 60)
    logger.info(f"[LOGS] Limpiando logs con más de {LOG_RETENCION_DIAS} días...")

    eliminados = 0
    umbral_fecha = datetime.now() - timedelta(days=LOG_RETENCION_DIAS)

    patron = os.path.join(LOG_DIR, "etl_*.log")
    archivos = glob.glob(patron)

    for archivo in archivos:
        try:
            fecha_mod = datetime.fromtimestamp(os.path.getmtime(archivo))
            if fecha_mod < umbral_fecha:
                nombre = os.path.basename(archivo)
                os.remove(archivo)
                logger.info(f"[LOGS] Eliminado: {nombre} (mod: {fecha_mod.strftime('%Y-%m-%d')})")
                eliminados += 1
        except Exception as e:
            logger.warning(f"[LOGS] No se pudo eliminar {archivo}: {e}")

    logger.info(f"[LOGS] Archivos eliminados: {eliminados} | Retenidos: {len(archivos) - eliminados}")
    return eliminados


# ==============================================================================
# PASO 5: INFORME DE SALUD DEL SERVIDOR
# ==============================================================================
def informe_salud(conn_params: dict) -> dict:
    """Genera un informe completo del estado del DWH."""
    logger.info("=" * 60)
    logger.info("[SALUD] Generando informe de salud del servidor...")

    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    informe = {}

    # Tamaño de la base de datos
    cur.execute("SELECT pg_size_pretty(pg_database_size('dw_reg_v1')), pg_database_size('dw_reg_v1')")
    r = cur.fetchone()
    informe["db_size_pretty"] = r[0]
    informe["db_size_bytes"]  = r[1]
    logger.info(f"[SALUD] Tamaño DB             : {r[0]}")

    # Conexiones activas
    cur.execute("SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'dw_reg_v1'")
    informe["conexiones_activas"] = cur.fetchone()[0]
    logger.info(f"[SALUD] Conexiones activas    : {informe['conexiones_activas']}")

    # Consultas de larga duración (> 5 minutos)
    cur.execute("""
        SELECT pid, now() - pg_stat_activity.query_start AS duracion, query
        FROM pg_stat_activity
        WHERE datname = 'dw_reg_v1'
          AND state = 'active'
          AND (now() - pg_stat_activity.query_start) > interval '5 minutes'
    """)
    queries_lentas = cur.fetchall()
    informe["queries_lentas"] = len(queries_lentas)
    if queries_lentas:
        logger.warning(f"[SALUD] *** Consultas > 5 min : {len(queries_lentas)} ***")
        for q in queries_lentas:
            logger.warning(f"[SALUD]   PID {q[0]} | {str(q[1])[:15]} | {q[2][:80]}...")
    else:
        logger.info("[SALUD] Consultas largas      : ninguna")

    # Top 10 tablas por tamaño
    cur.execute("""
        SELECT schemaname || '.' || relname AS tabla,
               pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS size,
               pg_total_relation_size(schemaname||'.'||relname) AS bytes
        FROM pg_stat_user_tables
        WHERE schemaname IN ('dw', 'stg')
        ORDER BY bytes DESC
        LIMIT 10
    """)
    logger.info("[SALUD] Top 10 tablas por tamaño:")
    tablas = []
    for r in cur.fetchall():
        logger.info(f"[SALUD]   {r[0]:<50} {r[1]:>10}")
        tablas.append({"tabla": r[0], "size": r[1]})
    informe["top_tablas"] = tablas

    # Conteos de hechos principales
    cur.execute("SELECT COUNT(*) FROM dw.fact_regularizacion")
    informe["fact_regularizacion"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dw.fact_pago")
    informe["fact_pago"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dw.fact_proyecto_geografia")
    informe["fact_proyecto_geografia"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dw.dim_proyecto")
    informe["dim_proyecto"] = cur.fetchone()[0]

    logger.info(f"[SALUD] fact_regularizacion   : {informe['fact_regularizacion']:>12,}")
    logger.info(f"[SALUD] fact_pago             : {informe['fact_pago']:>12,}")
    logger.info(f"[SALUD] fact_proyecto_geo     : {informe['fact_proyecto_geografia']:>12,}")
    logger.info(f"[SALUD] dim_proyecto          : {informe['dim_proyecto']:>12,}")

    # Tablespace usage
    cur.execute("SELECT pg_size_pretty(pg_tablespace_size('pg_default'))")
    informe["tablespace_size"] = cur.fetchone()[0]
    logger.info(f"[SALUD] Tablespace pg_default  : {informe['tablespace_size']}")

    # Últimas fechas de vacuum por tabla clave
    cur.execute("""
        SELECT schemaname || '.' || relname,
               last_vacuum, last_autovacuum, last_analyze
        FROM pg_stat_user_tables
        WHERE schemaname || '.' || relname = ANY(%s)
        ORDER BY relname
    """, (TABLAS_PRIORITARIAS,))
    logger.info("[SALUD] Estado de VACUUM en tablas clave:")
    for r in cur.fetchall():
        last_vac = str(r[1])[:19] if r[1] else (str(r[2])[:19] if r[2] else "NUNCA")
        logger.info(f"[SALUD]   {r[0]:<50} último VACUUM: {last_vac}")

    cur.close()
    conn.close()

    logger.info("[SALUD] Informe completado.")
    return informe


# ==============================================================================
# ORQUESTADOR PRINCIPAL
# ==============================================================================
def ejecutar_mantenimiento(solo_reindex: bool = False, solo_informe: bool = False):
    """Ejecuta el ciclo completo de mantenimiento preventivo."""
    inicio_total = time.time()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("")
    logger.info("=" * 62)
    logger.info("  MANTENIMIENTO PREVENTIVO DWH - REGULARIZACION AMBIENTAL")
    logger.info("=" * 62)
    logger.info(f"  Inicio : {fecha}")

    resultados = {}

    if solo_informe:
        resultados["salud"] = informe_salud(CONN_DWH_LOCAL)
    elif solo_reindex:
        logger.info("[MAINT] Modo: solo reindexación (no implementada en esta versión)")
    else:
        # Ejecución completa
        resultados["disco"]      = verificar_espacio_disco()
        resultados["vacuum"]     = ejecutar_vacuum(CONN_DWH_LOCAL)
        resultados["analyze"]    = ejecutar_analyze(CONN_DWH_LOCAL)
        resultados["logs"]       = limpiar_logs_antiguos()
        resultados["salud"]      = informe_salud(CONN_DWH_LOCAL)

    duracion = time.time() - inicio_total
    minutos  = int(duracion // 60)
    segundos = duracion % 60

    logger.info("")
    logger.info("=" * 62)
    logger.info("  MANTENIMIENTO COMPLETADO")
    logger.info(f"  Duracion : {minutos}m {segundos:.1f}s")
    logger.info("=" * 62)

    return resultados


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mantenimiento preventivo del DWH PostgreSQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python mantenimiento_db.py              # Mantenimiento completo
  python mantenimiento_db.py --informe    # Solo informe de salud
  python mantenimiento_db.py --reindex    # Solo reindexación
        """
    )
    parser.add_argument("--reindex",  action="store_true", help="Solo reindexación")
    parser.add_argument("--informe",  action="store_true", help="Solo informe de salud")
    args = parser.parse_args()

    resultado = ejecutar_mantenimiento(
        solo_reindex=args.reindex,
        solo_informe=args.informe
    )
    sys.exit(0)
