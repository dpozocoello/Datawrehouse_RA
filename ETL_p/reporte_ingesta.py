# ==============================================================================
# reporte_ingesta.py — Reporte post-ejecución con delta entre ejecuciones
# ==============================================================================
# Genera automáticamente al finalizar cada ejecución del ETL:
#
#   1. Snapshot JSON   → logs/snapshot_YYYYMMDD_HHMMSS.json
#      Persiste los conteos de todas las tablas STG y DW de la ejecución actual.
#
#   2. Reporte Markdown → logs/reporte_ingesta_YYYYMMDD_HHMMSS.md
#      Compara la ejecución actual vs el snapshot anterior, calculando:
#        - Registros por sistema origen (FASE de ingesta)
#        - Delta por tabla STG (Δ absoluto y Δ %)
#        - Delta por tabla DW  (Δ absoluto y Δ %)
#        - Indicadores de calidad y alertas automáticas
#
# Uso interno (llamado desde etl_main.py):
#   from reporte_ingesta import generar_reporte_ingesta
#   generar_reporte_ingesta(conteos, metadata, resultados_pasos)
#
# ==============================================================================

import os
import json
import glob
from datetime import datetime
from utils import get_logger

logger = get_logger("REPORTE_INGESTA")

# Directorio donde se almacenan snapshots y reportes
try:
    from config import LOG_DIR
except ImportError:
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")

# ==============================================================================
# MAPEO: Sistema origen → tablas STG que alimenta
# ==============================================================================
MAPA_ORIGEN_STG = {
    "SUIA — RCOA":                  ["stg.suia_rcoa_bi"],
    "SUIA — COA":                   ["stg.suia_coa_bi"],
    "JBPM — Sector":                ["stg.jbpm_sector_bi"],
    "JBPM — 4 Categorías":          ["stg.jbpm_4cat_bi"],
    "JBPM — Hidrocarburos":         ["stg.jbpm_hidro_bi"],
    "SNAP — Variables BPM":         ["stg.jbpm_snap_variables"],
    "JBPM — Pagos Online":          ["stg.online_payments_bi"],
    "SUIA — Transacciones":         ["stg.financial_transaction_bi"],
    "SUIA — Áreas":                 ["stg.suia_areas_bi"],
    "SUIA — Geografía INEC":        ["stg.geographical_locations_bi"],
    "JBPM — Pagos Históricos":      ["stg.online_payments_historical_bi"],
    "SUIA III — Generadores RGD":   ["stg.stg_waste_generator"],
    "SUIA III — Tipos Desechos":    ["stg.stg_waste_catalogs_parent", "stg.stg_waste_type"],
    "SUIA III — Puntos Recuperación": ["stg.stg_rgd_warehouses"],
    "RETCE — Manifiestos":          ["stg.stg_rgd_manifests"],
    "PQA — Importaciones Químicas": [
        "stg.stg_chemical_sustances_records",
        "stg.stg_import_request",
        "stg.stg_chemical_substances_declaration",
        "stg.stg_chemical_substances_movements",
        "stg.stg_project_mapping",
    ],
    "PQA — Plaguicidas": [
        "stg.stg_pesticide_project",
        "stg.stg_products_pqa",
        "stg.stg_detail_pesticide_project",
    ],
    "COA_MAE + SUIA_BPMS — Intersecciones": ["stg.stg_intersection"],
}

# Agrupación DW por tipo de tabla
TABLAS_DW_DIMENSIONES = [
    "dw.dim_proyecto", "dw.dim_proponente", "dw.dim_actividad",
    "dw.dim_geografia", "dw.dim_usuario", "dw.dim_estado", "dw.dim_tiempo",
    "dw.dim_area", "dw.dim_pago", "dw.dim_waste_type",
    "dw.dim_chemical_substance", "dw.dim_intersection",
]

TABLAS_DW_HECHOS = [
    "dw.fact_regularizacion", "dw.fact_pago",
    "dw.fact_proyecto_geografia", "dw.fact_waste_generation",
]


# ==============================================================================
# SNAPSHOT
# ==============================================================================

def guardar_snapshot(conteos: dict, metadata: dict) -> str:
    """
    Persiste los conteos actuales en un archivo JSON para comparación futura.

    Parámetros:
    -----------
    conteos  : dict  — {tabla: filas} resultado de verificar_conteos()
    metadata : dict  — {timestamp, duracion_total, pasos_exitosos, pasos_fallidos, pasos_saltados}

    Retorna:
    --------
    str — Ruta absoluta del archivo snapshot generado.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(LOG_DIR, f"snapshot_{ts}.json")

    payload = {
        "schema_version": "1.0",
        "timestamp": metadata.get("timestamp", ts),
        "metadata": metadata,
        "conteos": conteos,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    logger.info(f"[REPORTE] Snapshot guardado → {os.path.basename(path)}")
    return path


def cargar_snapshot_anterior(excluir_ts: str = None) -> dict | None:
    """
    Carga el snapshot JSON más reciente (excluyendo el de la ejecución actual).

    Parámetros:
    -----------
    excluir_ts : str — Timestamp del snapshot actual a ignorar (formato YYYYMMDD_HHMMSS).

    Retorna:
    --------
    dict | None — Payload del snapshot anterior, o None si no existe.
    """
    patron = os.path.join(LOG_DIR, "snapshot_*.json")
    archivos = sorted(glob.glob(patron), reverse=True)  # Más reciente primero

    for archivo in archivos:
        nombre = os.path.basename(archivo)
        ts_archivo = nombre.replace("snapshot_", "").replace(".json", "")
        if excluir_ts and ts_archivo == excluir_ts:
            continue
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[REPORTE] No se pudo leer snapshot {nombre}: {e}")
            continue

    return None


# ==============================================================================
# CÁLCULO DE DELTA
# ==============================================================================

def calcular_delta(actual: dict, anterior: dict) -> dict:
    """
    Calcula el delta entre dos snapshots de conteos.

    Retorna:
    --------
    dict — {tabla: {"actual": int, "anterior": int, "delta_abs": int, "delta_pct": float}}
    """
    resultado = {}
    todas_tablas = set(actual.keys()) | set(anterior.keys())

    for tabla in todas_tablas:
        v_actual = actual.get(tabla, 0)
        v_anterior = anterior.get(tabla, 0)

        if v_actual < 0:    # Error en conteo actual
            v_actual = 0
        if v_anterior < 0:  # Error en conteo anterior
            v_anterior = 0

        delta_abs = v_actual - v_anterior
        delta_pct = (delta_abs / v_anterior * 100) if v_anterior > 0 else (100.0 if v_actual > 0 else 0.0)

        resultado[tabla] = {
            "actual":    v_actual,
            "anterior":  v_anterior,
            "delta_abs": delta_abs,
            "delta_pct": delta_pct,
            "es_nuevo":  tabla not in anterior,
        }

    return resultado


# ==============================================================================
# GENERADOR DEL REPORTE MARKDOWN
# ==============================================================================

def _icono_delta(delta_abs: int, es_nuevo: bool) -> str:
    if es_nuevo:
        return "★ NUEVO"
    if delta_abs > 0:
        return f"▲ +{delta_abs:,}"
    if delta_abs < 0:
        return f"▼ {delta_abs:,}"
    return "= 0"


def _alerta_tabla(tabla: str, delta: dict) -> str | None:
    """Genera alertas automáticas basadas en umbrales por tipo de tabla."""
    v_actual   = delta["actual"]
    delta_abs  = delta["delta_abs"]
    delta_pct  = abs(delta["delta_pct"])

    # Tablas de hechos — alerta si decrecen
    if tabla in TABLAS_DW_HECHOS and delta_abs < 0:
        return f"ALERTA: {tabla} decreció en {abs(delta_abs):,} registros ({delta_pct:.1f}%)"

    # Tabla de proyectos faltantes — alerta si supera 500
    if tabla == "dw.dim_proyecto" and v_actual > 0 and delta["anterior"] > 0:
        if delta_abs > 500:
            return f"MONITOREAR: dim_proyecto creció {delta_abs:,} filas — verificar proyectos recuperados"

    # Staging core vacío inesperado
    tablas_no_vacias = ["stg.suia_rcoa_bi", "stg.suia_coa_bi", "stg.jbpm_4cat_bi",
                        "stg.online_payments_bi", "stg.online_payments_historical_bi"]
    if tabla in tablas_no_vacias and v_actual == 0:
        return f"CRITICA: {tabla} = 0 filas — verificar conectividad con sistema origen"

    return None


def generar_reporte_ingesta(
    conteos:        dict,
    metadata:       dict,
    resultados_pasos: list,
) -> str:
    """
    Genera el reporte post-ejecución completo en formato Markdown.

    Parámetros:
    -----------
    conteos          : dict  — {tabla: filas} de verificar_conteos()
    metadata         : dict  — {timestamp, duracion_total_s, pasos_exitosos,
                                pasos_fallidos, pasos_saltados}
    resultados_pasos : list  — [(num, nombre, estado, duracion_s), ...]

    Retorna:
    --------
    str — Ruta absoluta del reporte .md generado.
    """
    logger.info("[REPORTE] Generando reporte de ingesta post-ejecución...")

    ts_actual = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Guardar snapshot actual
    path_snap = guardar_snapshot(conteos, metadata)
    ts_snap   = os.path.basename(path_snap).replace("snapshot_", "").replace(".json", "")

    # 2. Cargar snapshot anterior
    snap_anterior = cargar_snapshot_anterior(excluir_ts=ts_snap)
    conteos_ant   = snap_anterior["conteos"] if snap_anterior else {}
    ts_ant_label  = snap_anterior["metadata"].get("timestamp", "N/A") if snap_anterior else "Sin ejecución previa"

    # 3. Calcular deltas
    deltas = calcular_delta(conteos, conteos_ant)

    # 4. Construir reporte
    ahora = metadata.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dur_s = metadata.get("duracion_total_s", 0)
    dur_m = int(dur_s // 60)
    dur_ss = dur_s % 60
    p_ok   = metadata.get("pasos_exitosos", 0)
    p_skip = metadata.get("pasos_saltados", 0)
    p_fail = metadata.get("pasos_fallidos", 0)

    lineas = []

    # ── Encabezado ──────────────────────────────────────────────────────────
    lineas += [
        "# REPORTE DE INGESTA POST-EJECUCIÓN",
        "## ETL Data Warehouse — Regularización Ambiental",
        f"**Ejecución actual:**  {ahora}  ",
        f"**Ejecución anterior:** {ts_ant_label}  ",
        f"**Duración:** {dur_m}m {dur_ss:.1f}s  ",
        f"**Pasos:** {p_ok} exitosos | {p_skip} saltados | {p_fail} fallidos  ",
        "",
        "---",
        "",
    ]

    # ── Sección 1: Pasos ejecutados ──────────────────────────────────────────
    lineas += [
        "## 1. Pasos Ejecutados",
        "",
        "| # | Nombre | Estado | Duración |",
        "|---|---|---|---|",
    ]
    for num, nombre, estado, dur in resultados_pasos:
        icono = "✓" if estado == "OK" else ("⊘" if estado == "SALTADO" else "✗")
        t = f"{int(dur//60)}m {dur%60:.1f}s" if dur > 0 else "---"
        lineas.append(f"| {num:02d} | {nombre} | {icono} {estado} | {t} |")
    lineas += ["", "---", ""]

    # ── Sección 2: Ingesta por sistema origen ────────────────────────────────
    lineas += [
        "## 2. Registros Extraídos por Sistema Origen (STG)",
        "",
        "| Sistema Origen | Tablas STG | Registros Actuales | Registros Anteriores | Δ Neto |",
        "|---|---|---|---|---|",
    ]
    total_stg_actual = 0
    total_stg_ant    = 0

    for origen, tablas in MAPA_ORIGEN_STG.items():
        r_actual = sum(conteos.get(t, 0) for t in tablas if conteos.get(t, 0) >= 0)
        r_ant    = sum(conteos_ant.get(t, 0) for t in tablas if conteos_ant.get(t, 0) >= 0)
        delta    = r_actual - r_ant
        es_nuevo = all(t not in conteos_ant for t in tablas)
        icono    = "★ NUEVO" if es_nuevo else (_icono_delta(delta, False))
        total_stg_actual += r_actual
        total_stg_ant    += r_ant
        nombres_tablas = "<br>".join(t.replace("stg.", "") for t in tablas)
        lineas.append(
            f"| {origen} | {nombres_tablas} | {r_actual:,} | {r_ant:,} | {icono} |"
        )

    delta_total_stg = total_stg_actual - total_stg_ant
    lineas += [
        f"| **TOTAL STG** | | **{total_stg_actual:,}** | **{total_stg_ant:,}** | **{_icono_delta(delta_total_stg, False)}** |",
        "", "---", "",
    ]

    # ── Sección 3: Delta por tabla STG ──────────────────────────────────────
    lineas += [
        "## 3. Delta por Tabla — Capa Staging",
        "",
        "| Tabla STG | Registros Actuales | Registros Anteriores | Δ Absoluto | Δ % |",
        "|---|---|---|---|---|",
    ]
    tablas_stg = [t for origen_tablas in MAPA_ORIGEN_STG.values() for t in origen_tablas]
    tablas_stg_unicas = list(dict.fromkeys(tablas_stg))  # Preservar orden, sin duplicados

    for tabla in tablas_stg_unicas:
        d = deltas.get(tabla, {"actual": 0, "anterior": 0, "delta_abs": 0, "delta_pct": 0.0, "es_nuevo": False})
        icono = _icono_delta(d["delta_abs"], d["es_nuevo"])
        pct   = f"{d['delta_pct']:+.2f}%" if not d["es_nuevo"] else "NUEVO"
        lineas.append(
            f"| `{tabla}` | {d['actual']:,} | {d['anterior']:,} | {icono} | {pct} |"
        )
    lineas += ["", "---", ""]

    # ── Sección 4: Delta por tabla DW ───────────────────────────────────────
    lineas += [
        "## 4. Delta por Tabla — Capa Data Warehouse",
        "",
        "### 4.1 Dimensiones",
        "",
        "| Tabla DW | Registros Actuales | Registros Anteriores | Δ Absoluto | Δ % |",
        "|---|---|---|---|---|",
    ]
    for tabla in TABLAS_DW_DIMENSIONES:
        d = deltas.get(tabla, {"actual": 0, "anterior": 0, "delta_abs": 0, "delta_pct": 0.0, "es_nuevo": False})
        icono = _icono_delta(d["delta_abs"], d["es_nuevo"])
        pct   = f"{d['delta_pct']:+.2f}%" if not d["es_nuevo"] else "NUEVO"
        lineas.append(
            f"| `{tabla}` | {d['actual']:,} | {d['anterior']:,} | {icono} | {pct} |"
        )

    lineas += [
        "",
        "### 4.2 Tablas de Hechos",
        "",
        "| Tabla DW | Registros Actuales | Registros Anteriores | Δ Absoluto | Δ % |",
        "|---|---|---|---|---|",
    ]
    total_fact_actual = 0
    total_fact_ant    = 0
    for tabla in TABLAS_DW_HECHOS:
        d = deltas.get(tabla, {"actual": 0, "anterior": 0, "delta_abs": 0, "delta_pct": 0.0, "es_nuevo": False})
        icono = _icono_delta(d["delta_abs"], d["es_nuevo"])
        pct   = f"{d['delta_pct']:+.2f}%" if not d["es_nuevo"] else "NUEVO"
        total_fact_actual += d["actual"]
        total_fact_ant    += d["anterior"]
        lineas.append(
            f"| `{tabla}` | {d['actual']:,} | {d['anterior']:,} | {icono} | {pct} |"
        )

    delta_total_fact = total_fact_actual - total_fact_ant
    lineas += [
        f"| **TOTAL HECHOS** | **{total_fact_actual:,}** | **{total_fact_ant:,}** | **{_icono_delta(delta_total_fact, False)}** | |",
        "", "---", "",
    ]

    # ── Sección 5: Indicadores de calidad ───────────────────────────────────
    alertas = []
    for tabla, d in deltas.items():
        alerta = _alerta_tabla(tabla, d)
        if alerta:
            alertas.append(alerta)

    tasa_exito = round(p_ok / max(p_ok + p_fail, 1) * 100, 1)
    tablas_vacias_dw = [t for t in TABLAS_DW_HECHOS if conteos.get(t, 0) == 0]

    lineas += [
        "## 5. Indicadores de Calidad",
        "",
        "| Indicador | Valor | Estado |",
        "|---|---|---|",
        f"| Tasa de éxito de pasos | {tasa_exito}% | {'✓ OK' if tasa_exito >= 95 else '⚠ REVISAR'} |",
        f"| Pasos fallidos | {p_fail} | {'✓ OK' if p_fail == 0 else '✗ ERROR'} |",
        f"| Tablas de hechos con 0 filas | {len(tablas_vacias_dw)} | {'✓ OK' if len(tablas_vacias_dw) == 0 else '⚠ INFO'} |",
        f"| Delta total STG | {_icono_delta(delta_total_stg, False)} | {'✓ OK' if delta_total_stg >= 0 else '⚠ REVISAR'} |",
        f"| Delta total HECHOS | {_icono_delta(delta_total_fact, False)} | {'✓ OK' if delta_total_fact >= 0 else '⚠ REVISAR'} |",
        "",
    ]

    if alertas:
        lineas += [
            "### Alertas Automáticas",
            "",
        ]
        for a in alertas:
            prioridad = "CRITICA" if "CRITICA" in a else ("ALERTA" if "ALERTA" in a else "INFO")
            lineas.append(f"- **[{prioridad}]** {a}")
        lineas.append("")
    else:
        lineas += ["### Alertas Automáticas", "", "- Sin alertas detectadas.", ""]

    lineas += ["---", "", "_Reporte generado automáticamente por ETL DWH v1.4 — Clasificación: Uso Interno_"]

    # 5. Escribir archivo
    contenido = "\n".join(lineas)
    nombre_reporte = f"reporte_ingesta_{ts_actual}.md"
    path_reporte   = os.path.join(LOG_DIR, nombre_reporte)

    with open(path_reporte, "w", encoding="utf-8") as f:
        f.write(contenido)

    logger.info(f"[REPORTE] Reporte generado → {nombre_reporte}")
    return path_reporte
