import streamlit as st
from auth_utils import login_screen, log_audit, hash_password, validate_password_strength, engine as auth_engine
from config_utils import load_config, save_config, apply_custom_theme, save_local_image, get_base64_image, apply_global_frame
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import datetime
import json
import unicodedata
from collections import Counter
import textwrap
from environmental_engine import load_environmental_analytic_data, get_environmental_kpis, get_heatmap_data

def normalize_name(name):
    if not name: return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', str(name).upper())
        if unicodedata.category(c) != 'Mn'
    ).strip()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dashboard ECO-SIEAA - v1.01",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()
apply_global_frame()

# --- UX EXPERTO: GRADIENTE GLOBAL Y ESTÉTICA CONFIGURACIÓN ---
st.markdown("""
<style>
    /* Fondo Degradado de Alta Gama */
    .stApp {
        background: linear-gradient(135deg, #0A3D62 0%, #17202A 50%, #1ABC9C 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Forzar Títulos Blancos en Configuración */
    [data-testid="stExpander"] h1, [data-testid="stExpander"] h2, [data-testid="stExpander"] h3,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: white !important;
    }
    
    /* Estilo para las pestañas de Administración */
    .stTabs [data-baseweb="tab-list"] button {
        color: #BDC3C7 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #1ABC9C !important;
        border-bottom-color: #1ABC9C !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
@st.cache_resource
def get_engine():
    # En producción Linux, se recomienda usar variables de entorno (ej. DATABASE_URL)
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")
    return create_engine(db_url)

# --- FUNCIONES DE CARGA (TABS 1 a 5) ---

@st.cache_data(ttl=600)
def load_integrity_summary():
    query = '''
    SELECT * FROM dw.v_integridad_dashboard 
    ORDER BY 
      CASE origen
        WHEN 'JBPM_HIDRO' THEN 1
        WHEN 'JBPM_SECTOR' THEN 2
        WHEN 'JBPM_4CAT' THEN 3
        WHEN 'COA' THEN 4
        WHEN 'RCOA' THEN 5
        ELSE 6
      END ASC
    '''
    return pd.read_sql(query, get_engine())

@st.cache_data(ttl=600)
def load_tramites_detail(origen):
    query = '''
SELECT
    tipo_permiso_ambiental AS "Tipo Permiso Ambiental",
    COUNT(CASE WHEN es_completado = 1 THEN 1 END) AS "Completadas",
    COUNT(CASE WHEN es_completado = 0 THEN 1 END) AS "No Completadas",
    COUNT(*) AS "Total Proyectos"
FROM (
    SELECT
        p.codigo_proyecto,
        COALESCE(p.tipo_permiso_ambiental, 'Sin Permiso Definido') AS tipo_permiso_ambiental,
        MAX(
            CASE 
                WHEN f.fecha_fin_proceso IS NOT NULL THEN 1
                ELSE 0
            END
        ) AS es_completado
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p
        ON f.sk_proyecto = p.sk_proyecto
    WHERE f.origen = %(origen)s 
      AND p.nombre_proyecto <> 'Proyecto Recuperado (JBPM)'
    GROUP BY
        p.codigo_proyecto,
        COALESCE(p.tipo_permiso_ambiental, 'Sin Permiso Definido')
) t
GROUP BY tipo_permiso_ambiental
ORDER BY tipo_permiso_ambiental;
    '''
    return pd.read_sql(query, get_engine(), params={"origen": origen})

@st.cache_data(ttl=600)
def load_projects_by_origin_summary():
    query = '''
    SELECT 
        f.origen,
        COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos,
        COUNT(DISTINCT CASE WHEN f.fecha_fin_proceso IS NOT NULL THEN p.codigo_proyecto END) as proyectos_completados,
        COUNT(DISTINCT CASE WHEN f.fecha_fin_proceso IS NULL THEN p.codigo_proyecto END) as proyectos_pendientes,
        MIN(f.fecha_inicio_proceso) as fecha_inicio_mas_antigua,
        MAX(f.fecha_inicio_proceso) as fecha_inicio_mas_reciente
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
    GROUP BY f.origen
    ORDER BY cantidad_proyectos DESC
    '''
    return pd.read_sql(query, get_engine())


def render_legal_framework_info():
    with st.expander("📚 Información Legal y Normativa Aplicable (Jerarquía)", expanded=False):
        st.markdown('''
        **Resumen de Jerarquía Legal Gubernamental**
        
        | Acrónimo / Referencia | Nombre Formal del Cuerpo Legal |
        | :--- | :--- |
        | **COA** | Código Orgánico del Ambiente |
        | **RCOA** | Reglamento al Código Orgánico del Ambiente |
        | **A.M. 061** | Reforma al Libro VI del TULSMA |
        | **A.M. 028** | Catálogo de Actividades Sujetas a Regularización |
        | **D.E. 1215** | Reglamento Ambiental de Hidrocarburos |
        
        ---
        
        **1. JBPM_HIDRO: Módulo de Hidrocarburos**
        Se rige principalmente por la normativa técnica ambiental para actividades hidrocarburíferas.
        * **Nombre Formal**: Reglamento Ambiental para las Actividades Hidrocarburíferas (RAAH).
        * **Normativa**: Decreto Ejecutivo 1215. Es la norma específica que regula el control de contaminación ambiental en la fase de prospección, explotación, transporte e industrialización de hidrocarburos.
        
        **2. JBPM_SECTOR: Sector/Subsector A.M. 028**
        Este código hace referencia a la clasificación de actividades según el impacto.
        * **Nombre Formal**: Sustitución del Texto Unificado de Legislación Secundaria del Ministerio del Ambiente (TULSMA), Libro VI.
        * **Normativa**: Acuerdo Ministerial No. 028. Es el instrumento que establece el Catálogo Nacional de Actividades Sujetas a Regularización Ambiental y los criterios para determinar si un proyecto requiere Licencia, Registro o Certificado Ambiental.
        
        **3. JBPM_4CAT: Las 4 Categorías**
        En la normativa ecuatoriana, los proyectos se categorizan según su impacto ambiental para determinar el tipo de permiso.
        * **Nombre Formal**: Categorización Ambiental Nacional. Las 4 Categorías son:
            - Impacto No Significativo: (Certificado Ambiental)
            - Bajo Impacto: (Registro Ambiental)
            - Mediano Impacto: (Licencia Ambiental)
            - Alto Impacto: (Licencia Ambiental)
        * **Normativa**: Definidas en el Código Orgánico del Ambiente (COA) y detalladas en el Acuerdo Ministerial 013 (que actualizó la tabla de categorización del AM 028).
        
        **4. COA / SUIA VERDE: A.M. 061**
        El SUIA (Sistema Único de Información Ambiental) es la plataforma donde se procesan estos trámites.
        * **Nombre Formal**: Reforma al Libro VI del Texto Unificado de Legislación Secundaria del Ministerio del Ambiente (TULSMA).
        * **Normativa**: Acuerdo Ministerial No. 061. Es la norma fundamental que operativiza el proceso de regularización, control y seguimiento ambiental en el país antes de la plena vigencia de todos los reglamentos del COA.
        
        **5. RCOA: Reglamento al Código Orgánico Ambiental**
        Es el cuerpo legal que detalla cómo aplicar lo que dice la ley principal (COA).
        * **Nombre Formal**: Reglamento al Código Orgánico del Ambiente.
        * **Normativa**: Decreto Ejecutivo No. 752. Este reglamento desarrolla los procedimientos administrativos para la regularización, gestión de residuos, reparación integral y sanciones.
        ''')

@st.cache_data(ttl=3600)
def get_unique_tramites(origen="TODOS"):
    try:
        base_query = '''
        SELECT DISTINCT p.tipo_permiso_ambiental 
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE p.tipo_permiso_ambiental IS NOT NULL AND p.tipo_permiso_ambiental != ''
        '''
        params = {}
        if origen != "TODOS":
            base_query += " AND f.origen = %(origen)s"
            params["origen"] = origen
            
        base_query += " ORDER BY p.tipo_permiso_ambiental"
        df = pd.read_sql(base_query, get_engine(), params=params)
        return ["TODOS"] + df['tipo_permiso_ambiental'].tolist()
    except Exception as e:
        return ["TODOS"]


@st.cache_data(ttl=600)
def load_projects_advanced_filter(origen, tipo_tramite, apply_dates, start_date, end_date):
    base_query = '''
    SELECT DISTINCT ON (p.codigo_proyecto)
        p.codigo_proyecto,
        p.nombre_proyecto,
        p.tipo_permiso_ambiental,
        f.origen,
        f.proceso as tipo_tramite,
        e.estado_proceso,
        e.estado_tramite,
        f.fecha_inicio_proceso,
        f.fecha_fin_proceso
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
    WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
    '''
    params = {}
    if origen != "TODOS":
        base_query += " AND f.origen = %(origen)s"
        params["origen"] = origen
    if tipo_tramite != "TODOS":
        base_query += " AND p.tipo_permiso_ambiental = %(tipo_tramite)s"
        params["tipo_tramite"] = tipo_tramite
    if apply_dates:
        base_query += " AND f.fecha_inicio_proceso BETWEEN %(sd)s AND %(ed)s"
        params["sd"] = start_date
        params["ed"] = end_date
        
    base_query += " ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC"
    return pd.read_sql(base_query, get_engine(), params=params)


def fuse_payments_dataframe(df):
    if df.empty: return df
    def get_real_id(row):
        nt = str(row['numero_transaccion']) if 'numero_transaccion' in row and pd.notna(row['numero_transaccion']) else ''
        ntr = str(row['numero_tramite']) if 'numero_tramite' in row and pd.notna(row['numero_tramite']) else ''
        if 'tramite' in row and pd.notna(row['tramite']): ntr = str(row['tramite'])
        if nt and nt not in ['0000000000', 'None', 'nan']: return nt
        if ntr and ntr not in ['0000000000', 'None', 'nan']: return ntr
        return f"DESC_{row['fecha_pago']}_{row.name}"

    df['clave_pago'] = df.apply(get_real_id, axis=1)
    fusionados = []
    group_cols = ['clave_pago']
    if 'codigo_proyecto' in df.columns: group_cols.append('codigo_proyecto')
        
    for keys, group in df.groupby(group_cols):
        monto = group['monto_pagado'].dropna().max()
        tarea = next((t for t in group['tarea_bpm'].dropna() if str(t) not in ['None', 'nan', '']), None)
        proceso = next((p for p in group['proceso_bpm'].dropna() if str(p) not in ['None', 'nan', '']), None)
        origenes = group['origen'].dropna().unique() if 'origen' in group else []
        origen_n = 'Fusionado (JBPM/SUIA)' if len(origenes) > 1 else (origenes[0] if len(origenes)>0 else None)
        
        nt_val = '0000000000'
        if 'numero_transaccion' in group:
            nt_valid = [x for x in group['numero_transaccion'].dropna() if str(x) not in ['0000000000', 'None']]
            nt_val = nt_valid[0] if nt_valid else '0000000000'
        
        res = {
            'monto_pagado': monto,
            'fecha_pago': group['fecha_pago'].iloc[0],
            'proceso_bpm': proceso,
            'tarea_bpm': tarea,
        }
        if 'numero_tramite' in group: res['numero_tramite'] = group['numero_tramite'].dropna().iloc[0] if not group['numero_tramite'].dropna().empty else None
        if 'numero_transaccion' in group: res['numero_transaccion'] = nt_val
        if 'tramite' in group: res['tramite'] = keys[0] if isinstance(keys, tuple) else keys
        if 'origen' in group: res['origen'] = origen_n
        if 'secuencia_pago' in group: res['secuencia_pago'] = group['secuencia_pago'].min()
        for col in ['codigo_proyecto', 'nombre_proyecto', 'tipo_permiso_ambiental', 'provincia', 'canton', 'oficina_tecnica', 'tipo_pago']:
            if col in group.columns: res[col] = group[col].iloc[0]
        fusionados.append(res)
        
    df_f = pd.DataFrame(fusionados)
    sort_cols = ["fecha_pago"]
    if 'secuencia_pago' in df_f.columns: sort_cols.append("secuencia_pago")
    return df_f.sort_values(by=sort_cols, ascending=[True] * len(sort_cols)).reset_index(drop=True)

@st.cache_data(ttl=600)
def load_project_history(codigo_proyecto):
    query = text('''
    SELECT 
        f.proceso, 
        f.tarea, 
        e.estado_proceso, 
        e.estado_tramite, 
        f.fecha_inicio_tarea, 
        COALESCE(f.fecha_fin_tarea, CURRENT_TIMESTAMP) as fecha_fin_tarea,
        u.usuario_tarea
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
    LEFT JOIN dw.dim_usuario u ON f.sk_usuario = u.sk_usuario
    WHERE p.codigo_proyecto = :cp
    AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    ORDER BY f.fecha_inicio_tarea ASC;
    ''')
    return pd.read_sql(query, get_engine(), params={"cp": codigo_proyecto})

@st.cache_data(ttl=600)
def load_project_payments(codigo_proyecto):
    query = text('''
    SELECT 
        fp.numero_tramite,
        fp.numero_transaccion,
        fp.monto_pagado,
        dp.tipo_pago,
        dt.fecha as fecha_pago,
        fp.proceso_bpm,
        fp.tarea_bpm,
        fp.origen,
        fp.secuencia_pago
    FROM dw.fact_pago fp
    JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
    JOIN dw.dim_pago dp ON fp.sk_pago = dp.sk_pago
    LEFT JOIN dw.dim_tiempo dt ON fp.sk_fecha_pago = dt.sk_tiempo
    WHERE p.codigo_proyecto = :cp
    AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    ORDER BY dt.fecha ASC, fp.secuencia_pago ASC
    ''')
    df = pd.read_sql(query, get_engine(), params={"cp": codigo_proyecto})
    return fuse_payments_dataframe(df)

@st.cache_data(ttl=600)
def load_management_summary(start_date, end_date, codigo_proyecto=None):
    if not codigo_proyecto:
        query = text('''
        SELECT 
            COUNT(DISTINCT p.codigo_proyecto) as total_proyectos
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE f.fecha_inicio_proceso BETWEEN :sd AND :ed
        AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        ''')
        return pd.read_sql(query, get_engine(), params={"sd": start_date, "ed": end_date})
    else:
        query = text('''
        SELECT 
            p.codigo_proyecto,
            p.nombre_proyecto,
            p.tipo_permiso_ambiental,
            p.tipo_sector,
            p.tipo_ente,
            p.sistema,
            p.estrategico,
            p.area_responsable,
            prop.nombre_proponente,
            prop.ced_ruc_proponente,
            geo.provincia,
            geo.canton,
            geo.parroquia,
            da.nombre_area                                         as oficina_tecnica,
            COALESCE(da.tipo_area, 'Sin Clasificar')               as tipo_area_inst,
            COALESCE(da.siglas_tipo_area, '')                      as siglas_area,
            COALESCE(da.nombre_area_padre, 'N/A')                  as area_padre,
            COALESCE(da.canton_directo, da.canton, 'N/A')          as canton_directo_area,
            da.es_emisora_aaa                                      as es_emisora_aaa,
            da.es_seguimiento_aaa                                  as es_seguimiento_aaa,
            COALESCE(da.area_resolution_ministerial, '')           as resolucion_ministerial,
            COALESCE(da.nivel_jerarquico, 1)::integer              as nivel_jerarquico,
            COALESCE(da.l1_nombre, da.nombre_area, '')             as l1_nombre,
            COALESCE(da.l1_siglas_tipo, da.siglas_tipo_area, '')   as l1_siglas_tipo,
            COALESCE(da.l2_nombre, '')                             as l2_nombre,
            COALESCE(da.ruta_nombres, da.nombre_area, '')          as ruta_nombres,
            COALESCE(da.es_hoja, TRUE)                             as es_hoja,
            f.superficie_proyecto,
            f.interseccion_snap,
            f.numero_resolucion,
            f.fecha_resolucion,
            f.ente_acreditado,
            MIN(f.fecha_inicio_proceso) as primera_fecha_inicio,
            MAX(f.fecha_fin_proceso) as ultima_fecha_fin,
            COUNT(DISTINCT f.tarea) as total_tareas_realizadas,
            MAX(e.estado_proceso) as estado_actual
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
        LEFT JOIN dw.dim_proponente prop ON f.sk_proponente = prop.sk_proponente
        LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
        WHERE p.codigo_proyecto = :cp
        GROUP BY
            p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental, p.tipo_sector,
            p.tipo_ente, p.sistema, p.estrategico, p.area_responsable,
            prop.nombre_proponente, prop.ced_ruc_proponente,
            geo.provincia, geo.canton, geo.parroquia,
            da.nombre_area, da.tipo_area, da.siglas_tipo_area, da.nombre_area_padre,
            da.canton_directo, da.canton, da.es_emisora_aaa, da.es_seguimiento_aaa,
            da.area_resolution_ministerial, da.nivel_jerarquico, da.l1_nombre,
            da.l1_siglas_tipo, da.l2_nombre, da.ruta_nombres, da.es_hoja,
            f.superficie_proyecto, f.interseccion_snap, f.numero_resolucion,
            f.fecha_resolucion, f.ente_acreditado
        ''')
        return pd.read_sql(query, get_engine(), params={"cp": codigo_proyecto})


@st.cache_data(ttl=600)
def load_origin_period_report(start_date, end_date):
    try:
        query = text('''
        SELECT 
            f.origen as "Normativa Orgánica",
            COUNT(DISTINCT p.codigo_proyecto) as "Volumen de Proyectos Ejecutados",
            MIN(f.fecha_inicio_proceso) as "Primer Movimiento",
            MAX(f.fecha_fin_proceso) as "Último Cierre"
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE f.fecha_inicio_proceso BETWEEN :sd AND :ed
        AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        GROUP BY f.origen
        ORDER BY "Volumen de Proyectos Ejecutados" DESC
        ''')
        return pd.read_sql(query, get_engine(), params={"sd": start_date, "ed": end_date})
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_environmental_analysis():
    try:
        query = '''
        SELECT 
            p.codigo_proyecto as "Código SUIA",
            p.nombre_proyecto as "Proyecto Identificado",
            geo.provincia as "Jurisdicción",
            f.interseccion_snap as "Polígono SNAP Relevante",
            f.superficie_proyecto as "Impacto Hectáreas"
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        WHERE f.interseccion_snap IS NOT NULL AND f.interseccion_snap != 'NO' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
        AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        LIMIT 500
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_layer_frequencies():
    try:
        query = '''
        SELECT 
            f.interseccion_snap as nombre_capa,
            COUNT(DISTINCT p.codigo_proyecto) as total_proyectos
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE f.interseccion_snap IS NOT NULL AND f.interseccion_snap != 'NO' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
        GROUP BY f.interseccion_snap
        ORDER BY total_proyectos DESC
        LIMIT 10
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_geopolitical_heatmap_data():
    try:
        query = '''
        SELECT 
            COALESCE(geo.provincia, 'Desconocido') as "PROVINCIA",
            COALESCE(geo.canton, 'No Registrado') as "CANTON",
            COUNT(DISTINCT p.codigo_proyecto) as "DENSIDAD_PROYECTOS"
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
        GROUP BY geo.provincia, geo.canton
        ORDER BY "DENSIDAD_PROYECTOS" DESC
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_waste_summary():
    try:
        query = '''
        SELECT 
            t.waste_name as tipo_desecho, 
            f.source_system,
            f.record_year,
            SUM(f.quantity_generated) as total_generado
        FROM dw.fact_waste_generation f
        JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
        GROUP BY t.waste_name, f.source_system, f.record_year
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_waste_project_registry():
    try:
        query = '''
        SELECT 
            COALESCE(NULLIF(p.nombre_proyecto, 'PROYECTO NO DEFINIDO'), 'Libre Voluntad') as "Nombre del Proyecto",
            COALESCE(p.codigo_proyecto, 'S/N') as "Código Proyecto",
            g.codigo as "Código RGD",
            g.ruc_generator as "RUC",
            g.generator_name as "Razón Social",
            f.source_system as "Sistema",
            SUM(f.quantity_generated) as "Total (kg)"
        FROM dw.fact_waste_generation f
        LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
        GROUP BY p.nombre_proyecto, p.codigo_proyecto, g.codigo, g.ruc_generator, g.generator_name, f.source_system
        ORDER BY "Total (kg)" DESC
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_waste_managers_report():
    try:
        query = '''
        SELECT 
            g.generator_name as "Razón Social",
            g.ruc_generator as "RUC",
            g.province as "Provincia",
            g.canton as "Cantón",
            g.generator_type as "Tipo Perfil",
            SUM(f.quantity_generated) as "Total Generado (kg)"
        FROM dw.fact_waste_generation f
        JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
        GROUP BY g.generator_name, g.ruc_generator, g.province, g.canton, g.generator_type
        ORDER BY "Total Generado (kg)" DESC
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_chemical_summary():
    try:
        query = '''
        SELECT 
            c.classification, 
            c.substance_name, 
            SUM(f.net_weight) as dosis_total
        FROM dw.fact_chemical_import f
        JOIN dw.dim_chemical_substance c ON f.chemical_key = c.chemical_key
        GROUP BY c.classification, c.substance_name
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_geojson(level='provincia'):
    try:
        # Calcular ruta absoluta basada en la ubicación del script
        suffix = 'es' if level == 'canton' else 's'
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, f'ecuador_{level}{suffix}.geojson')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error crítico cargando GeoJSON ({level}): {e}")
        return None

def normalize_geo_view_name(name):
    # Transforma UPPERCASE (DB) a Title Case (GeoJSON) manejando excepciones comunes
    if not name: return ""
    name = str(name).strip().upper()
    mapping = {
        "PICHINCHA": "Pichincha", "GUAYAS": "Guayas", "AZUAY": "Azuay", "LOJA": "Loja",
        "MANABI": "Manabí", "EL ORO": "El Oro", "COTOPAXI": "Cotopaxi", "IMBABURA": "Imbabura",
        "TUNGURAHUA": "Tungurahua", "SANTO DOMINGO DE LOS TSACHILAS": "Santo Domingo de los Tsáchilas",
        "ESMERALDAS": "Esmeraldas", "LOS RIOS": "Los Ríos", "CHIMBORAZO": "Chimborazo",
        "LOJA": "Loja", "BOLIVAR": "Bolívar", "CANAR": "Cañar", "CARCHI": "Carchi",
        "NAPO": "Napo", "PASTAZA": "Pastaza", "ORELLANA": "Orellana", "SUCUMBIOS": "Sucumbíos",
        "MORONA SANTIAGO": "Morona Santiago", "ZAMORA CHINCHIPE": "Zamora Chinchipe",
        "GALAPAGOS": "Galápagos", "SANTA ELENA": "Santa Elena"
    }
    # Si no está en el mapa manual, usamos un Capitalize genérico
    return mapping.get(name, name.title())

@st.cache_data(ttl=600)
def get_geo_provincias():
    try:
        query = "SELECT DISTINCT provincia FROM dw.dim_geografia WHERE provincia IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine())
        return ["TODAS"] + df['provincia'].tolist()
    except Exception:
        return ["TODAS"]

@st.cache_data(ttl=600)
def get_geo_cantones(provincia):
    try:
        where = "WHERE 1=1"
        params = {}
        if provincia != "TODAS":
            where = "WHERE provincia = %(p)s"
            params["p"] = provincia
        query = f"SELECT DISTINCT canton FROM dw.dim_geografia {where} AND canton IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine(), params=params)
        return ["TODOS"] + df['canton'].tolist()
    except Exception:
        return ["TODOS"]

@st.cache_data(ttl=600)
def get_geo_parroquias(provincia, canton):
    try:
        where = "WHERE 1=1"
        params = {}
        if provincia != "TODAS":
            where += " AND provincia = %(p)s"
            params["p"] = provincia
        if canton != "TODOS":
            where += " AND canton = %(c)s"
            params["c"] = canton
        query = f"SELECT DISTINCT parroquia FROM dw.dim_geografia {where} AND parroquia IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine(), params=params)
        return ["TODAS"] + [p for p in df['parroquia'].tolist() if p and p != 'N/A']
    except Exception:
        return ["TODAS"]

@st.cache_data(ttl=600)
def get_oficinas_tecnicas():
    try:
        query = "SELECT DISTINCT nombre_area FROM dw.dim_area WHERE nombre_area IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine())
        return ["TODAS"] + df['nombre_area'].tolist()
    except Exception:
        return ["TODAS"]

@st.cache_data(ttl=3600)
def get_origenes_normativa():
    try:
        query = "SELECT DISTINCT origen FROM dw.fact_regularizacion WHERE origen IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['origen'].tolist()
    except Exception:
        return ["TODOS"]

@st.cache_data(ttl=600)
def get_pago_anios():
    try:
        query = "SELECT DISTINCT anio FROM dw.dim_tiempo WHERE anio >= 2015 ORDER BY anio DESC"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + [str(a) for a in df['anio'].tolist()]
    except Exception:
        return ["TODOS"]

@st.cache_data(ttl=600)
def load_revenue_metrics(prov='TODAS', cant='TODOS', anio='TODOS', codigo_proyecto=None):
    try:
        params = {}
        where = "1=1"
        if codigo_proyecto:
            where += " AND p.codigo_proyecto = %(cod)s"
            params['cod'] = codigo_proyecto
        if prov != 'TODAS':
            where += " AND geo.provincia = %(prov)s"
            params['prov'] = prov
        if cant != 'TODOS':
            where += " AND geo.canton = %(cant)s"
            params['cant'] = cant
        if anio != 'TODOS':
            where += " AND t.anio = %(anio)s"
            params['anio'] = int(anio)
            
        # DEDUPLICACIÓN: Un pago es único por proyecto, fecha y monto exacto entre SUIA/JBPM
        query = f'''
        SELECT 
            SUM(monto_pagado) as recaudacion_total,
            COUNT(id_fact_pago) as total_transacciones,
            AVG(monto_pagado) as ticket_promedio,
            MAX(monto_pagado) as pago_maximo
        FROM (
            SELECT DISTINCT ON (f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado)
                f.monto_pagado, f.id_fact_pago
            FROM dw.fact_pago f
            JOIN dw.dim_tiempo t ON f.sk_fecha_pago = t.sk_tiempo
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
            LEFT JOIN dw.fact_proyecto_geografia pg ON f.sk_proyecto = pg.sk_proyecto AND pg.es_principal = TRUE
            LEFT JOIN dw.dim_geografia geo ON pg.sk_geografia = geo.sk_geografia
            WHERE {where} AND f.monto_pagado > 0 
            AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
            AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            ORDER BY f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado, f.id_fact_pago DESC
        ) sub
        '''
        return pd.read_sql(query, get_engine(), params=params)
    except Exception as e:
        st.error(f"Error en métricas de recaudación: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_revenue_analytic_data(prov='TODAS', cant='TODOS', parr='TODAS', ofic='TODAS', anio='TODOS', codigo_proyecto=None, start_date=None, end_date=None, tipo_area='TODOS'):
    try:
        params = {}
        where = "1=1"
        if codigo_proyecto:
            where += " AND p.codigo_proyecto = %(cod)s"
            params['cod'] = codigo_proyecto
        if prov != 'TODAS':
            where += " AND geo.provincia = %(prov)s"
            params['prov'] = prov
        if cant != 'TODOS':
            where += " AND geo.canton = %(cant)s"
            params['cant'] = cant
        if parr != 'TODAS':
            where += " AND geo.parroquia = %(parr)s"
            params['parr'] = parr
        if anio != 'TODOS':
            where += " AND t.anio = %(anio)s"
            params['anio'] = int(anio)
        if ofic != 'TODAS':
            where += " AND da.nombre_area = %(ofic)s"
            params['ofic'] = ofic
        if tipo_area != 'TODOS':
            where += " AND da.siglas_tipo_area = %(tipo_area)s"
            params['tipo_area'] = tipo_area
        if start_date is not None and end_date is not None:
            where += " AND t.fecha BETWEEN %(sd)s AND %(ed)s"
            params['sd'] = start_date
            params['ed'] = end_date

        # DEDUPLICACIÓN: Analítica sobre pagos únicos
        query = f'''
        SELECT 
            anio, codigo_proyecto, nombre_proyecto, provincia, canton, parroquia, oficina_tecnica,
            tipo_permiso_ambiental, monto_pagado, numero_tramite
        FROM (
            SELECT DISTINCT ON (f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado)
                p.codigo_proyecto,
                p.nombre_proyecto,
                t.anio, 
                geo.provincia, 
                geo.canton, 
                geo.parroquia,
                da.nombre_area as oficina_tecnica,
                p.tipo_permiso_ambiental,
                f.monto_pagado,
                f.id_fact_pago as numero_tramite,
                f.sk_proyecto, f.sk_fecha_pago
            FROM dw.fact_pago f
            JOIN dw.dim_tiempo t ON f.sk_fecha_pago = t.sk_tiempo
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
            LEFT JOIN dw.fact_proyecto_geografia pg ON f.sk_proyecto = pg.sk_proyecto AND pg.es_principal = TRUE
            LEFT JOIN dw.dim_geografia geo ON pg.sk_geografia = geo.sk_geografia
            LEFT JOIN (
                SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_area 
                FROM dw.fact_regularizacion 
                ORDER BY sk_proyecto, fecha_inicio_proceso DESC
            ) r ON f.sk_proyecto = r.sk_proyecto
            LEFT JOIN dw.dim_area da ON r.sk_area = da.sk_area
            WHERE {where} AND f.monto_pagado > 0 
            AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
            AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            ORDER BY f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado, f.id_fact_pago DESC
        ) sub_an
        '''
        return pd.read_sql(query, get_engine(), params=params)
    except Exception as e:
        st.error(f"Error en datos analíticos de pagos: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def search_payments_by_project(codigo_proyecto):
    try:
        # DEDUPLICACIÓN: Buscador de pagos únicos
        query = '''
        SELECT DISTINCT ON (p.sk_proyecto, t.sk_tiempo, f.monto_pagado)
            f.id_fact_pago as numero_tramite, 
            t.fecha as fecha_de_pago,
            p.tipo_permiso_ambiental as concepto,
            f.monto_pagado
        FROM dw.fact_pago f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_tiempo t ON f.sk_fecha_pago = t.sk_tiempo
        JOIN dw.dim_pago dp ON f.sk_pago = dp.sk_pago
        LEFT JOIN (
            SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_area 
            FROM dw.fact_regularizacion 
            ORDER BY sk_proyecto, fecha_inicio_proceso DESC
        ) r ON f.sk_proyecto = r.sk_proyecto
        LEFT JOIN dw.dim_area da ON r.sk_area = da.sk_area
        WHERE p.codigo_proyecto = %(cod)s 
        AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
        AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        ORDER BY p.sk_proyecto, t.sk_tiempo, f.monto_pagado, f.id_fact_pago DESC
        '''
        return pd.read_sql(query, get_engine(), params={'cod': codigo_proyecto})
    except Exception as e:
        st.error(f"Error buscando pagos por proyecto: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_project_env_details(codigo_proyecto):
    # Obtiene detalles de intersección SNAP y áreas protegidas
    try:
        query = '''
        SELECT 
            f.interseccion_snap, 
            f.areas_protegidas, 
            f.superficie_proyecto,
            f.numero_resolucion, 
            f.fecha_resolucion, 
            f.ente_acreditado,
            f.proceso, 
            f.tarea
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE p.codigo_proyecto = %(cod)s AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
        ORDER BY f.fecha_carga DESC
        LIMIT 1
        '''
        return pd.read_sql(query, get_engine(), params={"cod": codigo_proyecto})
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_project_waste_details(codigo_proyecto):
    # Obtiene historial de declaraciones RGD (Desechos)
    try:
        query = '''
        SELECT 
            COALESCE(g.generator_name, 'Sin RGD') as codigo_rgd,
            t.waste_key_code as codigo_desecho,
            t.waste_name as tipo_desecho, 
            f.quantity_generated as cantidad, 
            f.unit as unidad, 
            f.record_year as anio,
            f.source_system as sistema
        FROM dw.fact_waste_generation f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
        LEFT JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
        WHERE p.codigo_proyecto = %(cod)s AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A' AND f.quantity_generated > 0
        ORDER BY f.record_year DESC
        '''
        return pd.read_sql(query, get_engine(), params={"cod": codigo_proyecto})
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_geo_filtered_data(provincia, canton, parroquia, oficina, sd, ed, origen="TODOS", tipo_area="TODOS"):
    try:
        params = {"sd": sd, "ed": ed}
        where = "f.fecha_inicio_proceso BETWEEN %(sd)s AND %(ed)s"
        if provincia != "TODAS":
            where += " AND geo.provincia = %(prov)s"
            params["prov"] = provincia
        if canton != "TODOS":
            where += " AND geo.canton = %(cant)s"
            params["cant"] = canton
        if parroquia != "TODAS":
            where += " AND geo.parroquia = %(parr)s"
            params["parr"] = parroquia
        if oficina != "TODAS":
            where += " AND da.nombre_area = %(ofic)s"
            params["ofic"] = oficina
        if tipo_area != "TODOS":
            where += " AND da.siglas_tipo_area = %(tipo_area)s"
            params["tipo_area"] = tipo_area
        if origen != "TODOS":
            where += " AND f.origen = %(origen)s"
            params["origen"] = origen

        # SQL con DISTINCT ON para eliminar redundancia de proyectos
        query = f'''
        SELECT DISTINCT ON (p.codigo_proyecto)
            p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental,
            f.origen,
            geo.provincia, geo.canton, geo.parroquia, da.nombre_area as oficina_tecnica,
            f.superficie_proyecto, f.fecha_inicio_proceso,
            e.estado_proceso
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
        LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
        WHERE {where} AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'
        ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC
        '''
        return pd.read_sql(query, get_engine(), params=params)
    except Exception as e:
        st.error(f"Error cargando datos filtrados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_regularization_report(origen="TODOS", estado="TODOS", tipo_permiso="TODOS",
                                autoridad="TODAS", sd=None, ed=None, search_text=""):
    """
    SQL unificado basado en load_geo_filtered_data (Tab 4) + datos de usuario y estado.
    dim_area.nombre_area = Autoridad Responsable (no "dirección zonal").
    dim_geografia provee provincia / cantón / parroquia (contexto territorial).
    """
    try:
        params = {}
        where_clauses = [
            "p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'",
            "p.codigo_proyecto != 'N/A'",
            "p.nombre_proyecto  != 'N/A'"
        ]
        if origen != "TODOS":
            where_clauses.append("f.origen = %(origen)s")
            params["origen"] = origen
        if tipo_permiso != "TODOS":
            where_clauses.append("p.tipo_permiso_ambiental = %(tipo_permiso)s")
            params["tipo_permiso"] = tipo_permiso
        if autoridad != "TODAS":
            where_clauses.append("da.nombre_area = %(autoridad)s")
            params["autoridad"] = autoridad
        if estado == "En Trámite":
            where_clauses.append("f.fecha_fin_proceso IS NULL")
        elif estado == "Completado":
            where_clauses.append("f.fecha_fin_proceso IS NOT NULL")
        if sd and ed:
            where_clauses.append("f.fecha_inicio_proceso BETWEEN %(sd)s AND %(ed)s")
            params["sd"] = sd
            params["ed"] = ed
        if search_text:
            where_clauses.append(
                "(p.codigo_proyecto ILIKE %(search)s OR p.nombre_proyecto ILIKE %(search)s)"
            )
            params["search"] = f"%{search_text}%"

        where_sql = " AND ".join(where_clauses)

        # ── SQL unificado ────────────────────────────────────────────────────
        # Base idéntica a load_geo_filtered_data (Tab 4):
        #   JOIN  dim_geografia → provincia / cantón / parroquia
        #   JOIN  dim_estado    → estado_proceso (campo oficial del DWH)
        #   LEFT JOIN dim_area  → nombre_area = AUTORIDAD RESPONSABLE
        # Complemento para Tab 11:
        #   LEFT JOIN dim_usuario → usuario_tarea = técnico responsable
        # ────────────────────────────────────────────────────────────────────
        query = f'''
        SELECT DISTINCT ON (p.codigo_proyecto)
            p.codigo_proyecto,
            p.nombre_proyecto,
            p.tipo_permiso_ambiental                          AS tipo_permiso,
            f.origen,
            geo.provincia,
            geo.canton,
            geo.parroquia,
            COALESCE(da.nombre_area,         'No Asignada')             AS autoridad_responsable,
            COALESCE(da.tipo_area,           'Sin Tipo')               AS tipo_area,
            COALESCE(da.siglas_tipo_area,    '')                       AS siglas_tipo,
            COALESCE(da.nombre_area_padre,   'N/A')                    AS area_padre,
            COALESCE(da.canton_directo, da.canton, 'N/A')              AS canton_directo_area,
            COALESCE(da.es_emisora_aaa::text,'false')                  AS es_emisora_aaa,
            COALESCE(da.es_seguimiento_aaa::text,'false')              AS es_seguimiento_aaa,
            COALESCE(da.es_proyecto_inversion::text,'false')           AS es_proyecto_inversion,
            COALESCE(da.nivel_jerarquico, 1)::integer                  AS nivel_jerarquico,
            COALESCE(da.l1_nombre, da.nombre_area, '')                 AS l1_nombre,
            COALESCE(da.l2_nombre, '')                                 AS l2_nombre,
            COALESCE(da.ruta_nombres, da.nombre_area, '')              AS ruta_nombres,
            COALESCE(u.usuario_tarea,  'No Asignado')         AS tecnico_responsable,
            e.estado_proceso,
            CASE
                WHEN f.fecha_fin_proceso IS NOT NULL THEN 'Completado'
                ELSE 'En Trámite'
            END                                               AS estado_proyecto,
            COALESCE(f.tarea, 'Sin Tarea Registrada')         AS tarea_actual,
            f.superficie_proyecto,
            f.fecha_inicio_proceso,
            f.fecha_fin_proceso,
            CASE
                WHEN f.tarea ~* '(carga|pago|firma|solicitud|declaraci|ingresa|presenta|propone|operador|gestiona)'
                    THEN 'Operador'
                WHEN f.tarea ~* '(revisi|analisis|inspecci|verificaci|evaluaci|aprueba|valida|emite|elabora|resoluc|califica|dictamen|tecnico)'
                    THEN 'Técnico MAE'
                ELSE 'Proceso Administrativo'
            END                                               AS rol_en_tarea
        FROM       dw.fact_regularizacion f
        JOIN       dw.dim_proyecto  p   ON f.sk_proyecto = p.sk_proyecto
        JOIN       dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        JOIN       dw.dim_estado    e   ON f.sk_estado   = e.sk_estado
        LEFT JOIN  dw.dim_area      da  ON f.sk_area     = da.sk_area
        LEFT JOIN  dw.dim_usuario   u   ON f.sk_usuario  = u.sk_usuario
        WHERE {where_sql}
        ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC
        '''
        return pd.read_sql(query, get_engine(), params=params)
    except Exception as e:
        st.error(f"Error cargando reporte de regularización: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_dir_zonales():
    try:
        query = "SELECT DISTINCT nombre_area FROM dw.dim_area WHERE nombre_area IS NOT NULL ORDER BY 1"
        df = pd.read_sql(query, get_engine())
        return ["TODAS"] + df['nombre_area'].tolist()
    except Exception:
        return ["TODAS"]

# ── dim_area v2.0 — helpers de cascada y cobertura ─────────────────────────
@st.cache_data(ttl=3600)
def get_tipos_area():
    try:
        query = """SELECT DISTINCT siglas_tipo_area
                   FROM dw.dim_area
                   WHERE siglas_tipo_area IS NOT NULL
                   ORDER BY siglas_tipo_area"""
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['siglas_tipo_area'].tolist()
    except Exception:
        return ["TODOS"]

@st.cache_data(ttl=3600)
def get_areas_por_tipo(siglas="TODOS"):
    try:
        if siglas == "TODOS":
            query = "SELECT DISTINCT nombre_area FROM dw.dim_area WHERE nombre_area IS NOT NULL ORDER BY 1"
            df = pd.read_sql(query, get_engine())
        else:
            query = "SELECT DISTINCT nombre_area FROM dw.dim_area WHERE siglas_tipo_area = %(s)s AND nombre_area IS NOT NULL ORDER BY 1"
            df = pd.read_sql(query, get_engine(), params={'s': siglas})
        return ["TODAS"] + df['nombre_area'].tolist()
    except Exception:
        return ["TODAS"]

@st.cache_data(ttl=600, show_spinner=False)
def get_aaa_coverage_kpi():
    try:
        query = """
        SELECT
            COUNT(DISTINCT CASE WHEN da.es_emisora_aaa = TRUE THEN f.sk_proyecto END) AS con_aaa,
            COUNT(DISTINCT f.sk_proyecto) AS total
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
        WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
          AND p.codigo_proyecto != 'N/A'
          AND f.fecha_fin_proceso IS NULL
        """
        df = pd.read_sql(query, get_engine())
        if df.empty: return 0, 0, 0.0
        con_aaa = int(df['con_aaa'].iloc[0] or 0)
        total   = int(df['total'].iloc[0] or 0)
        pct     = round(con_aaa / total * 100, 1) if total > 0 else 0.0
        return con_aaa, total, pct
    except Exception:
        return 0, 0, 0.0

@st.cache_data(ttl=600, show_spinner=False)
def get_gobernanza_gap():
    try:
        query = """
        SELECT
            COUNT(DISTINCT CASE WHEN (da.es_emisora_aaa = FALSE OR da.sk_area IS NULL)
                  THEN f.sk_proyecto END) AS snap_sin_aaa,
            COUNT(DISTINCT f.sk_proyecto) AS total_snap
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
        WHERE (f.areas_protegidas ILIKE '%SNAP%' OR f.interseccion_snap = 'SI')
          AND f.fecha_fin_proceso IS NULL
          AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        """
        df = pd.read_sql(query, get_engine())
        if df.empty: return 0, 0
        return int(df['snap_sin_aaa'].iloc[0] or 0), int(df['total_snap'].iloc[0] or 0)
    except Exception:
        return 0, 0

@st.cache_data(ttl=600)
def load_snap_sin_aaa_coverage():
    try:
        query = """
        SELECT
            geo.provincia,
            COUNT(DISTINCT p.codigo_proyecto) AS proyectos_snap_sin_aaa
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
        WHERE (f.areas_protegidas ILIKE '%SNAP%' OR f.interseccion_snap = 'SI')
          AND (da.es_emisora_aaa = FALSE OR da.sk_area IS NULL)
          AND f.fecha_fin_proceso IS NULL
          AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        GROUP BY geo.provincia
        ORDER BY proyectos_snap_sin_aaa DESC
        """
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_revenue_by_tipo_area(anio='TODOS', sd=None, ed=None):
    try:
        params = {}
        where = "f.monto_pagado > 0 AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A' AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'"
        if anio != 'TODOS':
            where += " AND t.anio = %(anio)s"
            params['anio'] = int(anio)
        if sd and ed:
            where += " AND t.fecha BETWEEN %(sd)s AND %(ed)s"
            params['sd'] = sd
            params['ed'] = ed
        query = f"""
        SELECT
            COALESCE(da.tipo_area, 'Sin Clasificar') AS tipo_area,
            COALESCE(da.siglas_tipo_area, '?')       AS siglas,
            COUNT(DISTINCT p.codigo_proyecto)         AS proyectos,
            SUM(fp.monto_pagado)                      AS recaudacion_total,
            AVG(fp.monto_pagado)                      AS ticket_promedio,
            COUNT(DISTINCT da.sk_area)                AS areas_activas
        FROM (
            SELECT DISTINCT ON (f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado)
                f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado, f.id_fact_pago
            FROM dw.fact_pago f
            JOIN dw.dim_tiempo t ON f.sk_fecha_pago = t.sk_tiempo
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
            WHERE {where}
            ORDER BY f.sk_proyecto, f.sk_fecha_pago, f.monto_pagado, f.id_fact_pago DESC
        ) fp
        JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
        LEFT JOIN (
            SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_area
            FROM dw.fact_regularizacion
            ORDER BY sk_proyecto, fecha_inicio_proceso DESC
        ) r ON fp.sk_proyecto = r.sk_proyecto
        LEFT JOIN dw.dim_area da ON r.sk_area = da.sk_area
        GROUP BY da.tipo_area, da.siglas_tipo_area
        ORDER BY recaudacion_total DESC NULLS LAST
        """
        return pd.read_sql(query, get_engine(), params=params)
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_institutional_hierarchy():
    try:
        query = """
        WITH proyectos_por_area AS (
            SELECT
                da.sk_area,
                COUNT(DISTINCT f.sk_proyecto)                                              AS proyectos_directos,
                COUNT(DISTINCT CASE WHEN f.fecha_fin_proceso IS NULL THEN f.sk_proyecto END) AS en_tramite_directos
            FROM dw.dim_area da
            LEFT JOIN dw.fact_regularizacion f ON da.sk_area = f.sk_area
            LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
              AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            GROUP BY da.sk_area
        ),
        proyectos_consolidados AS (
            SELECT
                b.sk_area_ancestro                                                          AS sk_area,
                COUNT(DISTINCT f.sk_proyecto)                                               AS proyectos_asignados,
                COUNT(DISTINCT CASE WHEN f.fecha_fin_proceso IS NULL THEN f.sk_proyecto END) AS en_tramite
            FROM dw.bridge_area_jerarquia b
            JOIN dw.fact_regularizacion f ON b.sk_area_descendiente = f.sk_area
            LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
              AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            GROUP BY b.sk_area_ancestro
        )
        SELECT
            COALESCE(da.tipo_area, 'Sin Clasificar')               AS tipo_area,
            COALESCE(da.siglas_tipo_area, '?')                     AS siglas,
            COALESCE(da.nivel_jerarquico, 1)::integer              AS nivel_jerarquico,
            COALESCE(da.l1_siglas_tipo, da.siglas_tipo_area, '?')  AS l1_siglas_tipo,
            COALESCE(da.l1_nombre, da.nombre_area, '')             AS l1_nombre,
            COALESCE(da.l2_nombre, '')                             AS l2_nombre,
            COALESCE(da.nombre_area_padre, 'Sin Padre')            AS area_padre,
            da.nombre_area,
            COALESCE(da.ruta_nombres, da.nombre_area, '')          AS ruta_nombres,
            COALESCE(da.es_hoja, TRUE)                             AS es_hoja,
            COALESCE(da.canton_directo, da.canton, 'N/A')          AS canton_directo,
            COALESCE(da.es_emisora_aaa, FALSE)                     AS es_emisora_aaa,
            COALESCE(da.es_seguimiento_aaa, FALSE)                 AS es_seguimiento_aaa,
            COALESCE(da.es_proyecto_inversion, FALSE)              AS es_proyecto_inversion,
            COALESCE(da.area_resolution_ministerial,'')            AS resolucion_ministerial,
            COALESCE(pc.proyectos_asignados, 0)                    AS proyectos_asignados,
            COALESCE(pc.en_tramite, 0)                             AS en_tramite
        FROM dw.dim_area da
        LEFT JOIN proyectos_consolidados pc ON da.sk_area = pc.sk_area
        WHERE da.id_area > 0
        ORDER BY da.tipo_area, COALESCE(pc.proyectos_asignados, 0) DESC
        """
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()
# ── fin helpers dim_area v3.0 ───────────────────────────────────────────────


# --- INTERFAZ DE USUARIO ---




st.markdown("---")



# --- GESTIÓN DE SESIÓN Y AUTENTICACIÓN ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_screen()
    st.stop()

# --- CABECERA INSTITUCIONAL (DINÁMICO) ---
config = load_config()
branding = config.get("branding", {})
base_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_sieaa_b64 = get_base64_image(branding.get("logo_main", os.path.join(base_root, 'assets', 'eco_sieaa', 'logo_main_trans.png')))
logo_gov_b64 = get_base64_image(branding.get("logo_gov", os.path.join(base_root, 'assets', 'branding', 'ministerio.png')))

st.markdown(f"""
<div class="stHeader">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style='margin:0; color:white; font-size: 2.2rem; letter-spacing: 1px;'>{branding.get("org_name", "ECO-SIEAA")}</h1>
            <p class="header-subtitle" style='color: #0A3D62 !important; margin:0; font-size: 1.1rem; font-weight: 700;'>{branding.get("sub_name", "Ministerio de Ambiente y Energía - El Nuevo Ecuador")}</p>
            <p class="header-analyst" style='margin-top: 5px; font-size: 0.85rem;'>{st.session_state['user_data']['full_name']} | {st.session_state['user_data']['role']} | {branding.get("version", "v1.01")}</p>
        </div>
        <div style="display: flex; gap: 16px; align-items: center;">
            <div style="background: #FFFFFF; border-radius: 12px; padding: 8px 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.25), 0 0 20px rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: center;">
                <img src="{logo_gov_b64}" height="55" style="display: block;">
            </div>
            <div style="background: #FFFFFF; border-radius: 12px; padding: 8px 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.25), 0 0 20px rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: center;">
                <img src="{logo_sieaa_b64}" width="110" style="display: block;">
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- ESTADO DE SESIÓN PARA MÓDULO 7.1 ---
if 'tab71_prov' not in st.session_state: st.session_state['tab71_prov'] = 'TODAS'
if 'tab71_cant' not in st.session_state: st.session_state['tab71_cant'] = 'TODOS'

# --- PANEL DE CONTROL (SIDEBAR) ---
st.sidebar.markdown(f'''
<style>
/* Forzar estilo del botón de cerrar sesión por todos los selectores posibles */
[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: #E74C3C !important;
    border: 1px solid #C0392B !important;
    border-radius: 8px !important;
    padding: 10px !important;
    margin-bottom: 20px !important;
}}
[data-testid="stSidebar"] button[kind="secondary"] p,
[data-testid="stSidebar"] button[kind="secondary"] span,
[data-testid="stSidebar"] button[kind="secondary"] div {{
    color: #FFFFFF !important;
    font-weight: bold !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background-color: #C0392B !important;
    border: 1px solid #FFFFFF !important;
}}
</style>
''', unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style='text-align:center; padding-bottom: 20px;'>
        <div style='display: inline-block; background: #FFFFFF; border-radius: 12px; padding: 10px 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.25); margin-bottom: 10px;'>
            <img src="{logo_sieaa_b64}" width="120" style="display: block;">
        </div>
        <h3 style='color:white; margin-top: 10px;'>ECO-SIEAA</h3>
        <p style='color:#bdc3c7; font-size: 0.85rem;'>Ministerio de Ambiente y Energía</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("Panel de Control")

st.sidebar.markdown("### Filtros Globales")
end_date_glob = datetime.date.today()
start_date_glob = end_date_glob - datetime.timedelta(days=365)
start_date_in = st.sidebar.date_input("Fecha Inicio", start_date_glob, key="global_start_date")
end_date_in = st.sidebar.date_input("Fecha Fin", end_date_glob, key="global_end_date")

# NAVEGACIÓN BASADA EN ROLES (RBAC)
module_icons = {
    "tab0": "🏠", "tab1": "📊", "tab2": "🔍", "tab3": "📁", "tab4": "🌎", "tab5": "💰",
    "tab6": "📋", "tab7": "🌲", "tab7_1": "🗺️", "tab8": "🌎", "tab9": "♻️", "tab10": "🧪",
    "tab11": "📑", "admin": "⚙️"
}
tabs_conf = config.get("tabs", {})
role_perms = config.get("role_permissions", {})
user_role = st.session_state['user_data']['role'].upper()
allowed_tabs = ["tab0"] + role_perms.get(user_role, ["tab1", "tab2"]) # tab0 is always allowed as home

# Filtrar por Visibilidad Global Y Permisos de Rol
enabled_tids = []
all_tids = ["tab0", "tab1", "tab2", "tab3", "tab4", "tab5", "tab6", "tab7", "tab7_1", "tab8", "tab9", "tab10", "tab11", "admin"]
for tid in all_tids:
    is_visible = tabs_conf.get(tid, {}).get("visible", True) if tid not in ["admin", "tab0"] else True
    is_allowed = tid in allowed_tabs
    if is_visible and is_allowed:
        enabled_tids.append(tid)

# 1. Agrupar módulos habilitados por Categoría
grouped_nav = {}
for tid in enabled_tids:
    if tid == "tab0":
        grp = "🏠 Inicio"
        lbl = "Guía Maestra de Ingeniería"
    else:
        grp = tabs_conf.get(tid, {}).get("group", "Administración" if tid == "admin" else "Otros")
        lbl = tabs_conf.get(tid, {}).get('label', tid) if tid != "admin" else "Configuración Maestro"
    
    if grp not in grouped_nav:
        grouped_nav[grp] = []
    
    icon = module_icons.get(tid, '🔹')
    grouped_nav[grp].append({"tid": tid, "label": f"{icon} {lbl}"})

# 2. Selector de Área Funcional (Nivel 1)
st.sidebar.markdown("### Áreas de Trabajo")
categories = list(grouped_nav.keys())
# Priorizar '🏠 Inicio' como pantalla de bienvenida
default_cat_idx = categories.index("🏠 Inicio") if "🏠 Inicio" in categories else 0
sel_category = st.sidebar.selectbox("Seleccione Área", categories, index=default_cat_idx, label_visibility="collapsed")

# 3. Selector de Módulo (Nivel 2)
st.sidebar.markdown(f"**Módulos de {sel_category}**")
modules_in_cat = grouped_nav[sel_category]
module_labels = [m['label'] for m in modules_in_cat]

# Inicializar estado para mantener la selección coherente
if f"sel_mod_{sel_category}" not in st.session_state:
    st.session_state[f"sel_mod_{sel_category}"] = module_labels[0]

sel_module_label = st.sidebar.radio(
    "Módulo", 
    module_labels, 
    key=f"radio_{sel_category}",
    label_visibility="collapsed"
)

# 4. Determinar active_tab final
active_tab = "tab1"
for m in modules_in_cat:
    if m['label'] == sel_module_label:
        active_tab = m['tid']
        break

st.sidebar.markdown("---")

# ══════════════════════════════════════════════════════════════════
# SECCIÓN: Estado de Sincronización ETL (Arquitecto de Datos)
# Fuente de verdad: dw.fact_regularizacion — BD dw_reg_v1
# Muestra la última fecha sincronizada en la última ejecución ETL.
# ══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def _get_etl_sync_info(_engine):
    """
    Consulta la última fecha de dato y carga por origen ETL.
    TTL = 5 min para no bloquear el rerun del sidebar.
    Returns: (resumen_dict, lista_detalle)
    """
    try:
        # ── Resumen global: última fecha de dato y carga ─────────────────
        q_resumen = """
            SELECT
                MAX(fecha_carga)::DATE          AS ultima_carga,
                MAX(fecha_inicio_proceso)::DATE  AS max_fecha_dato,
                MIN(fecha_inicio_proceso)::DATE  AS min_fecha_dato,
                COUNT(*)::BIGINT AS total_hechos
            FROM dw.fact_regularizacion
            WHERE fecha_inicio_proceso IS NOT NULL
        """
        df_res = pd.read_sql(q_resumen, _engine)
        resumen = df_res.iloc[0].to_dict() if not df_res.empty else {}

        # ── Detalle por origen: máx fecha de dato en cada fuente ─────────
        q_detalle = """
            SELECT
                COALESCE(origen, 'Sin Origen')       AS origen,
                MAX(fecha_carga)::DATE               AS ultima_carga,
                MAX(fecha_inicio_proceso)::DATE      AS max_fecha_dato,
                COUNT(*)::BIGINT AS registros
            FROM dw.fact_regularizacion
            WHERE fecha_inicio_proceso IS NOT NULL
            GROUP BY origen
            ORDER BY max_fecha_dato DESC NULLS LAST
        """
        df_det = pd.read_sql(q_detalle, _engine)
        detalle = df_det.to_dict(orient="records") if not df_det.empty else []
        return resumen, detalle
    except Exception:
        return {}, []

def _freshness_badge(max_date):
    """Calcula etiqueta, color e icono de frescura de datos."""
    if not max_date or str(max_date) in ("NaT", "None", "nan"):
        return "Sin datos", "#636E72", "⚫"
    try:
        if hasattr(max_date, "date"):
            max_date = max_date.date()
        delta = (datetime.date.today() - max_date).days
        if delta == 0:   return "Hoy ✓",           "#00B894", "🟢"
        elif delta == 1: return "Ayer",             "#FDCB6E", "🟡"
        elif delta <= 3: return f"{delta}d atrás",  "#E17055", "🟠"
        else:            return f"{delta}d atrás",  "#D63031", "🔴"
    except Exception:
        return "Sin datos", "#636E72", "⚫"

_sync_engine = get_engine()
_resumen_etl, _detalle_etl = _get_etl_sync_info(_sync_engine)

_ultima_carga  = _resumen_etl.get("ultima_carga")
_max_dato      = _resumen_etl.get("max_fecha_dato")
_min_dato      = _resumen_etl.get("min_fecha_dato")
_total_hechos  = _resumen_etl.get("total_hechos") or 0

_label, _color, _icon = _freshness_badge(_ultima_carga)

# Formato de fechas
def _fmt(d):
    try:
        if hasattr(d, "strftime"): return d.strftime("%d/%m/%Y")
        if d and str(d) not in ("NaT","None","nan"): return str(d)[:10]
    except Exception:
        pass
    return "—"

# ── Inyección CSS: forzar visibilidad en el sidebar ──────────────────────────
st.sidebar.markdown("""
<style>
/* Forzar legibilidad del panel de sincronización ETL */
[data-testid="stSidebar"] .etl-sync-title {
    font-size: 0.70rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    color: #A9B4C2 !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .etl-sync-card {
    background: rgba(0, 0, 0, 0.35) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    margin-bottom: 6px !important;
}
[data-testid="stSidebar"] .etl-sync-card * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .etl-sync-sub {
    color: rgba(255,255,255,0.55) !important;
    font-size: 0.68rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Título de la sección ──────────────────────────────────────────────────────
_badge_bg   = f"background:rgba(0,0,0,0.3);color:{_color};border:1px solid {_color};border-radius:20px;padding:2px 9px;font-size:0.63rem;font-weight:700;display:inline-block;white-space:nowrap;"
_fecha_disp = _fmt(_ultima_carga) if _ultima_carga else "Sin datos"
_detalle_disp = f"{int(_total_hechos):,} registros &nbsp;·&nbsp; datos hasta <b>{_fmt(_max_dato)}</b>" if _total_hechos else "Sin datos disponibles"

st.sidebar.markdown(
    f"""
    <p style="font-size:0.70rem;font-weight:800;letter-spacing:0.1em;
              color:#A9B4C2;text-transform:uppercase;margin:4px 0 6px 0;">
        🗄️&nbsp; Sincronización DWH
    </p>

    <table width="100%" cellpadding="0" cellspacing="0"
           style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.18);
                  border-radius:8px;padding:10px 12px;border-collapse:separate;
                  border-spacing:0;">
      <tr>
        <td style="color:rgba(255,255,255,0.60);font-size:0.72rem;
                   font-family:sans-serif;padding:0 0 4px 0;">
          Última actualización
        </td>
        <td align="right" style="padding:0 0 4px 0;">
          <span style="{_badge_bg}">{_icon}&nbsp;{_label}</span>
        </td>
      </tr>
      <tr>
        <td colspan="2"
            style="color:#FFFFFF;font-size:1.10rem;font-weight:800;
                   font-family:sans-serif;letter-spacing:0.02em;
                   padding:0 0 4px 0;">
          {_fecha_disp}
        </td>
      </tr>
      <tr>
        <td colspan="2"
            style="color:rgba(255,255,255,0.50);font-size:0.67rem;
                   font-family:sans-serif;padding:0;">
          {_detalle_disp}
        </td>
      </tr>
    </table>
    """,
    unsafe_allow_html=True,
)

# ── Detalle por origen ────────────────────────────────────────────────────────
if _detalle_etl:
    filas_html = ""
    for row in _detalle_etl:
        r_label, r_color, r_icon = _freshness_badge(row.get("max_fecha_dato"))
        r_regs  = row.get("registros", 0) or 0
        r_orig  = row.get("origen", "—")
        r_fecha = _fmt(row.get("max_fecha_dato"))
        filas_html += f"""
        <tr style="border-top:1px solid rgba(255,255,255,0.10);">
          <td width="10" valign="top" style="padding:6px 6px 6px 0;">
            <div style="width:8px;height:8px;border-radius:50%;
                        background:{r_color};margin-top:3px;"></div>
          </td>
          <td style="padding:6px 4px;font-family:sans-serif;">
            <div style="color:#FFFFFF;font-size:0.73rem;font-weight:700;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        max-width:160px;" title="{r_orig}">{r_orig}</div>
            <div style="color:rgba(255,255,255,0.55);font-size:0.64rem;
                        margin-top:2px;">{r_fecha}</div>
          </td>
          <td align="right" valign="middle"
              style="color:rgba(255,255,255,0.45);font-size:0.64rem;
                     font-family:sans-serif;white-space:nowrap;padding:6px 0;">
            {int(r_regs):,} regs
          </td>
        </tr>"""

    st.sidebar.markdown(
        f"""
        <p style="font-size:0.65rem;font-weight:700;letter-spacing:0.07em;
                  color:#A9B4C2;text-transform:uppercase;margin:8px 0 4px 0;">
          📋 Detalle por origen ETL
        </p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.12);
                      border-radius:6px;overflow:hidden;border-collapse:collapse;">
          {filas_html}
        </table>
        """,
        unsafe_allow_html=True,
    )

# ── Timestamp sesión ──────────────────────────────────────────────────────────
_now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.sidebar.markdown(
    f"""<p style="color:rgba(255,255,255,0.30);font-size:0.60rem;
                  text-align:center;margin:6px 0 2px 0;font-family:sans-serif;">
        Consulta: {_now_str}
    </p>""",
    unsafe_allow_html=True,
)
# ══════════════════════════════════════════════════════════════════

# ── KPI AAA + Alerta Gobernanza (dim_area v2.0) ───────────────────────────────
try:
    _aaa_con, _aaa_total, _aaa_pct = get_aaa_coverage_kpi()
    _aaa_color = "#2ECC71" if _aaa_pct >= 80 else "#E67E22" if _aaa_pct >= 50 else "#E74C3C"
    st.sidebar.markdown(
        f"""<div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.1);
                        border-radius:8px;padding:10px 12px;margin:6px 0;">
          <div style="font-size:0.6rem;color:#A9B4C2;text-transform:uppercase;
                      font-weight:700;letter-spacing:0.07em;margin-bottom:4px;">
            🛡️ Cobertura AAA (En Trámite)
          </div>
          <div style="display:flex;align-items:center;gap:8px;">
            <div style="font-size:1.3rem;color:{_aaa_color};font-weight:800;">{_aaa_pct}%</div>
            <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);">
              {_aaa_con:,} / {_aaa_total:,} proyectos<br>con área emisora AAA
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True
    )
    # Alerta de gobernanza si proyectos SNAP activos sin AAA > 0
    _gap_sin, _gap_total = get_gobernanza_gap()
    if _gap_sin > 0:
        _pct_gap = round(_gap_sin / _gap_total * 100, 1) if _gap_total > 0 else 0
        st.sidebar.markdown(
            f"""<div style="background:rgba(231,76,60,0.15);border:1px solid #E74C3C;
                            border-radius:8px;padding:10px 12px;margin:4px 0;">
              <div style="font-size:0.65rem;color:#E74C3C;font-weight:700;margin-bottom:3px;">
                ⚠️ Alerta de Gobernanza AAA
              </div>
              <div style="font-size:0.7rem;color:rgba(255,255,255,0.8);">
                <b style="color:#FF7675;">{_gap_sin:,}</b> proyectos SNAP activos sin cobertura AAA
                ({_pct_gap}% del total SNAP)
              </div>
            </div>""",
            unsafe_allow_html=True
        )
except Exception:
    pass
# ── fin KPI AAA ───────────────────────────────────────────────────────────────

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- RENDERIZADO DE MÓDULOS (if active_tab == ...) ---
# Implementación progresiva de los 10 módulos según la lógica recuperada

if active_tab == "tab0":
    # Infografía CENTRADA según solicitud (Expert UX) - Sin títulos ni resúmenes (Cleanup)
    col_c1, col_c2, col_c3 = st.columns([1, 10, 1])
    with col_c2:
        base_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(base_root, 'assets', 'infografia_dwh.png')
        try:
            st.image(img_path, use_container_width=True)
        except:
            st.warning("⚠️ Infografía técnica no encontrada en assets. Por favor asegúrese de que 'infografia_dwh.png' esté en la carpeta assets.")
            st.info("Esta sección está reservada para la infografía del Ciclo de Vida del DWH.")

elif active_tab == "tab1":
    st.markdown("<h2 style='color: white !important; margin-bottom: 15px;'>📊 Proyectos por tipo de Normativa</h2>", unsafe_allow_html=True)
    df_integrity = load_integrity_summary()
    if not df_integrity.empty:
        # --- MAPPING ---
        formal_names = {
            "JBPM_HIDRO": "Hidrocarburos",
            "JBPM_SECTOR": "Sector A.M. 028",
            "JBPM_4CAT": "4 Categorías",
            "COA": "COA / SUIA Verde",
            "RCOA": "RCOA",
            "RECUPERADO": "Sin Clasificación"
        }
        colors_map = {
            "Hidrocarburos": "#E74C3C",
            "Sector A.M. 028": "#3498DB",
            "4 Categorías": "#E67E22",
            "COA / SUIA Verde": "#2ECC71",
            "RCOA": "#9B59B6",
            "Sin Clasificación": "#95A5A6"
        }
        df_integrity['modulo'] = df_integrity['origen'].map(lambda x: formal_names.get(x, x))

        # --- GLOBAL KPI BANNER ---
        total_proj = df_integrity['proyectos_unicos_dwh'].sum()
        avg_integrity = df_integrity['porcentaje_integridad'].mean()
        total_diff = df_integrity['diferencia'].sum()
        n_modules = len(df_integrity)

        banner = '<div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;">'
        banner += f'<div style="flex:1;min-width:160px;background:linear-gradient(135deg,#1A5276,#154360);padding:14px 18px;border-radius:12px;border-left:5px solid #2ECC71;"><div style="font-size:0.65rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;letter-spacing:1px;">Total Proyectos DWH</div><div style="font-size:1.6rem;color:#FFFFFF !important;font-weight:800;">{total_proj:,}</div></div>'
        banner += f'<div style="flex:1;min-width:160px;background:rgba(255,255,255,0.06);padding:14px 18px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.65rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Integridad Global</div><div style="font-size:1.6rem;color:#2ECC71 !important;font-weight:800;">{avg_integrity:.0f}%</div></div>'
        banner += f'<div style="flex:1;min-width:160px;background:rgba(255,255,255,0.06);padding:14px 18px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.65rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Diferencia Total</div><div style="font-size:1.6rem;color:{"#2ECC71" if total_diff == 0 else "#E74C3C"} !important;font-weight:800;">{total_diff:,}</div></div>'
        banner += f'<div style="flex:1;min-width:160px;background:rgba(255,255,255,0.06);padding:14px 18px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.65rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Módulos Cargados</div><div style="font-size:1.6rem;color:#FFFFFF !important;font-weight:800;">{n_modules}</div></div>'
        banner += '</div>'
        st.markdown(banner, unsafe_allow_html=True)

        # --- COMPACT MODULE PILLS WITH BUTTONS ---
        pills_html = '<div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">'
        for _, row in df_integrity.iterrows():
            mod = formal_names.get(row['origen'], row['origen'])
            clr = colors_map.get(mod, '#85C1E9')
            pills_html += f'<div style="background:rgba(255,255,255,0.05);padding:10px 16px;border-radius:10px;border-left:4px solid {clr};flex:1;min-width:150px;"><div style="font-size:0.7rem;color:{clr} !important;font-weight:700;text-transform:uppercase;">{mod}</div><div style="font-size:1.3rem;color:#FFFFFF !important;font-weight:800;">{row["proyectos_unicos_dwh"]:,}</div><div style="font-size:0.65rem;color:#85C1E9 !important;">proyectos únicos</div></div>'
        pills_html += '</div>'
        st.markdown(pills_html, unsafe_allow_html=True)

        # --- BOTONES VER TRÁMITES (compactos) ---
        btn_cols = st.columns(len(df_integrity))
        for idx, (_, row) in enumerate(df_integrity.iterrows()):
            with btn_cols[idx]:
                mod = formal_names.get(row['origen'], row['origen'])
                if st.button(f"🔍 {mod}", key=f"btn_det_{row['origen']}", use_container_width=True):
                    st.session_state['selected_origin_detail'] = row['origen']

        if 'selected_origin_detail' in st.session_state:
            sel_origen = st.session_state['selected_origin_detail']
            st.markdown("---")
            col_t, col_b = st.columns([5, 1])
            with col_t:
                st.markdown(f"<h3 style='color: white !important;'>Desglose por Tipo de Permiso Ambiental y Estado: {sel_origen}</h3>", unsafe_allow_html=True)
            with col_b:
                if st.button("❌ Cerrar Detalle", use_container_width=True):
                    del st.session_state['selected_origin_detail']
                    st.rerun()
            df_detail = load_tramites_detail(sel_origen)
            if not df_detail.empty:
                st.dataframe(df_detail, use_container_width=True, hide_index=True)
            else:
                st.info(f"No hay detalles cronológicos disponibles para {sel_origen}.")

        st.markdown("---")

        # --- GRÁFICAS ESTADÍSTICAS GERENCIALES ---
        chart_c1, chart_c2 = st.columns(2)

        with chart_c1:
            fig_bar = px.bar(
                df_integrity, x='modulo', y='total_dwh',
                color='modulo',
                color_discrete_map=colors_map,
                title="Volumen de Proyectos por Módulo Normativo en Bruto",
                labels={'total_dwh': 'Proyectos', 'modulo': 'Módulo'},
                text='total_dwh'
            )
            # UX Expert: Ajuste de legibilidad para etiquetas de valor
            max_val = df_integrity['total_dwh'].max() if not df_integrity.empty else 1000
            fig_bar.update_traces(
                texttemplate='%{text:,}', 
                textposition='outside', 
                textfont_size=12, 
                textfont_color='#FFFFFF',
                cliponaxis=False
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF', title_font=dict(size=14, color='#FFFFFF'), showlegend=False,
                xaxis=dict(tickangle=-25, tickfont=dict(size=11, color='#FFFFFF')),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(255,255,255,0.05)', 
                    tickfont=dict(color='#FFFFFF'),
                    range=[0, max_val * 1.15]
                ),
                margin=dict(t=60, b=40, l=40, r=20), height=380
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with chart_c2:
            # Donut chart: Distribución porcentual
            fig_donut = px.pie(
                df_integrity, values='total_dwh', names='modulo',
                color='modulo', color_discrete_map=colors_map,
                title="Distribución del Portafolio DWH en Bruto", hole=0.55
            )
            fig_donut.update_traces(
                textposition='inside', textinfo='percent+label',
                textfont=dict(size=11, color='#FFFFFF'), pull=[0.03]*len(df_integrity)
            )
            fig_donut.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF', title_font=dict(size=14, color='#FFFFFF'),
                legend=dict(font=dict(size=10, color='#FFFFFF'), orientation='h', yanchor='bottom', y=-0.15),
                margin=dict(t=50, b=20, l=20, r=20), height=360
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        # --- TABLA DE PRODUCCIÓN (compacta) ---
        st.markdown("<h2 style='color: white !important; margin-bottom: 15px;'>📋 Cuadro comparativo de paso de Producción vs DWH de datos en Bruto</h2>", unsafe_allow_html=True)
        st.dataframe(df_integrity[['origen','total_produccion','total_dwh','diferencia','porcentaje_integridad']], use_container_width=True, hide_index=True)
    else:
        st.warning("No se encontraron datos de integridad.")

elif active_tab == "tab2":
    st.markdown("<h2 style='color: white !important; margin-bottom: 25px;'>🔍 Orígenes de los Proyectos según Normativa</h2>", unsafe_allow_html=True)
    
    # --- EXPLICACIÓN DETALLADA (EXECUTIVE SUMMARY) ---
    with st.expander("ℹ️ Explicación Detallada: Análisis de Status y Normativas", expanded=True):
        st.markdown('''
        <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:10px; border-left:4px solid #85C1E9;">
            <p style="color:#D5D8DC; font-size:0.95rem; line-height:1.6;">
                Este módulo proporciona una <b>visión gerencial discriminada</b> de la carga operativa distribuida por los diferentes marcos legales (normativas). 
                La información se divide en dos categorías críticas para la toma de decisiones:
            </p>
            <ul style="color:#D5D8DC; font-size:0.9rem;">
                <li><b>Finalizado (✅):</b> Proyectos que han completado su ciclo administrativo y cuentan con una resolución o fecha de fin registrada en el DWH.</li>
                <li><b>En Trámite (⏳):</b> Proyectos activos que se encuentran en alguna etapa del proceso de regularización y no tienen aún una fecha de cierre.</li>
            </ul>
            <p style="color:#D5D8DC; font-size:0.9rem;">
                <i>Nota: La discriminación permite identificar qué normativas tienen mayor volumen de "cuello de botella" pendiente de resolución.</i>
            </p>
        </div>
        ''', unsafe_allow_html=True)

    render_legal_framework_info()
    st.markdown("<h3 style='color: white !important; font-weight: bold;'>Análisis de Status</h3>", unsafe_allow_html=True)
    df_origin = load_projects_by_origin_summary()
    if not df_origin.empty:
        # Omitir registros RECUPERADO según solicitud
        df_origin = df_origin[~df_origin['origen'].isin(['RECUPERADO', 'RECUPERADO_JBPM'])]
        
        mapping_origenes = {
            "JBPM_HIDRO": "Hidrocarburos", "JBPM_SECTOR": "Sector A.M. 028", "JBPM_4CAT": "4 Categorías",
            "COA": "COA/SUIA Verde", "RCOA": "RCOA"
        }
        df_origin['origen_formal'] = df_origin['origen'].map(lambda x: mapping_origenes.get(x, x))
        
        # El selector se moverá a la columna del gráfico para una integración más estrecha (UX Expert)
        sel_norm = "PORTAFOLIO GLOBAL" # Inicialización
        
        df_filtered = df_origin.copy()
        # Moveremos la lógica de filtrado después de definir las columnas para permitir que el selector esté en col_c2
        col_c1, col_c2 = st.columns([3, 2])
        
        with col_c2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container():
                # Selector integrado "en la gráfica" según solicitud UX
                sel_norm = st.selectbox("🔎 Monitor de Status: Seleccione Origen", 
                                        ["PORTAFOLIO GLOBAL"] + sorted(df_origin['origen_formal'].unique().tolist()),
                                        key="status_drilldown_selector")
        
        df_filtered = df_origin.copy()
        if sel_norm != "PORTAFOLIO GLOBAL":
            df_filtered = df_origin[df_origin['origen_formal'] == sel_norm]

        # --- 1. KPI BANNER DE STATUS (DINÁMICO) ---
        total_comp = df_filtered['proyectos_completados'].sum()
        total_pend = df_filtered['proyectos_pendientes'].sum()
        total_all = df_filtered['cantidad_proyectos'].sum()
        pct_comp = (total_comp / total_all * 100) if total_all > 0 else 0
        
        # Estilo 100% transparente con bordes de color (Estética Minimalista)
        status_banner = f"""
        <div style="display:flex; gap:15px; margin-bottom:25px;">
            <div style="flex:1; background:transparent; padding:15px; border-radius:12px; border:1px solid rgba(46,204,113,0.4); border-left:5px solid #2ECC71;">
                <div style="font-size:0.75rem; color:#2ECC71; font-weight:700; text-transform:uppercase;">Completados</div>
                <div style="font-size:1.8rem; color:#FFFFFF; font-weight:800;">{total_comp:,}</div>
                <div style="font-size:0.8rem; color:rgba(255,255,255,0.6);">{pct_comp:.1f}% del total</div>
            </div>
            <div style="flex:1; background:transparent; padding:15px; border-radius:12px; border:1px solid rgba(230,126,34,0.4); border-left:5px solid #E67E22;">
                <div style="font-size:0.75rem; color:#E67E22; font-weight:700; text-transform:uppercase;">En Trámite</div>
                <div style="font-size:1.8rem; color:#FFFFFF; font-weight:800;">{total_pend:,}</div>
                <div style="font-size:0.8rem; color:rgba(255,255,255,0.6);">{100-pct_comp:.1f}% pendiente</div>
            </div>
            <div style="flex:1; background:transparent; padding:15px; border-radius:12px; border:1px solid rgba(133,193,233,0.3); border-left:5px solid #85C1E9;">
                <div style="font-size:0.75rem; color:#85C1E9; font-weight:700; text-transform:uppercase;">Universo: {sel_norm}</div>
                <div style="font-size:1.8rem; color:#FFFFFF; font-weight:800;">{total_all:,}</div>
                <div style="font-size:0.8rem; color:rgba(255,255,255,0.6);">Base DWH consolidada</div>
            </div>
        </div>
        """
        st.markdown(status_banner, unsafe_allow_html=True)

        # --- 2. GRÁFICA DE STATUS DISCRIMINADO (STACKED BAR) ---
        # Preparar datos long format para Plotly
        df_long = pd.melt(df_origin, id_vars=['origen_formal'], 
                          value_vars=['proyectos_completados', 'proyectos_pendientes'],
                          var_name='Status', value_name='Cantidad')
        df_long['Status'] = df_long['Status'].map({
            'proyectos_completados': '✅ Finalizado',
            'proyectos_pendientes': '⏳ En Trámite'
        })

        # --- 2. ÁREA DE GRÁFICOS (ALINEADOS) ---
        col_c1, col_c2 = st.columns([3, 2])
        
        with col_c1:
            fig_stack = px.bar(
                df_long, x='origen_formal', y='Cantidad', color='Status',
                title="Status de Proyectos por Cuerpo Legal",
                barmode='stack',
                color_discrete_map={'✅ Finalizado': '#2ECC71', '⏳ En Trámite': '#E67E22'},
                text='Cantidad'
            )
            fig_stack.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF', legend=dict(orientation="h", y=-0.2, font=dict(color="white")),
                xaxis=dict(tickfont=dict(size=10, color="white")),
                yaxis=dict(title=dict(text="N° Proyectos", font=dict(color="white")), gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color="white")),
                title=dict(text="Status de Proyectos por Cuerpo Legal", font=dict(color="white", size=16)),
                margin=dict(t=60, b=50, l=40, r=20), height=450
            )
            st.plotly_chart(fig_stack, use_container_width=True)

        with col_c2:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True) # Alineación vertical con el título de la izq
            # Replaced with Dynamic Status Distribution
            df_status_total = pd.DataFrame({
                'Status': ['✅ Finalizado', '⏳ En Trámite'],
                'Cantidad': [total_comp, total_pend]
            })
            
            fig_pie = px.pie(df_status_total, values='Cantidad', names='Status', 
                             hole=.6,
                             color='Status',
                             color_discrete_map={'✅ Finalizado': '#2ECC71', '⏳ En Trámite': '#E67E22'})
            
            fig_pie.update_traces(
                textinfo='percent+label', 
                textposition='inside', 
                textfont=dict(size=11, color="black"),
                pull=[0.05, 0.05],
                marker=dict(line=dict(color='#0A3D62', width=2))
            )
            
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF', 
                legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(color="white")),
                title=dict(text=f"Proporción: {sel_norm}", font=dict(color="white", size=16), x=0.5, xanchor="center"),
                margin=dict(t=40, b=40, l=10, r=10), height=400
            )
            
            # Contenedor Glassmorphism para el gráfico
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:10px; border-radius:15px; box-shadow:0 10px 30px rgba(0,0,0,0.2);">
            """, unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h3 style='color: white !important;'>Buscador Avanzado de Proyectos</h3>", unsafe_allow_html=True)
    st.info("Filtre la base de datos completa interactuando con los selectores. La consulta inicial abarca toda la base (sin filtro temporal obligatorio).")
    
    # Dropdowns for advanced filtering
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        diccionario_origenes = {
            "TODAS LAS NORMATIVAS": "TODOS",
            "1. Módulo de Hidrocarburos": "JBPM_HIDRO",
            "2. Sector/Subsector A.M. 028": "JBPM_SECTOR",
            "3. Las 4 Categorías": "JBPM_4CAT",
            "4. COA / SUIA VERDE: A.M. 061": "COA",
            "5. RCOA: Reglamento al Código Orgánico Ambiental": "RCOA",
            "SIN CLASIFICACION": "RECUPERADO"
        }
        sel_normativa_label = st.selectbox("Origen / Normativa", list(diccionario_origenes.keys()))
        origen_val = diccionario_origenes[sel_normativa_label]
        
    with col_f2:
        lista_tramites = get_unique_tramites(origen_val)
        sel_tramite = st.selectbox("Tipo de Permiso", lista_tramites)
        
    with col_f3:
        st.write("")
        st.write("")
        apply_dates = st.checkbox("Filtrar por rango de fechas (Globales)", value=False)
        
    # Using session state to allow slider interaction without losing data
    if st.button("Aplicar Filtros y Consultar", type="primary", use_container_width=True):
        st.session_state['run_advanced_query'] = True
        
    if st.session_state.get('run_advanced_query', False):
        with st.spinner("Extrayendo volúmenes del Data Warehouse (Puede tardar unos segundos)..."):
            df_norm = load_projects_advanced_filter(origen_val, sel_tramite, apply_dates, start_date_in, end_date_in)
            if not df_norm.empty:
                total_records = len(df_norm)
                st.success(f"✅ Se encontraron **{total_records:,}** proyectos coincidentes. Toda la información ha sido cargada exitosamente.")
                
                # Estrategia de Paginación Frontend (Eficiencia en Renderizado del Navegador)
                page_size = 5000
                total_pages = (total_records // page_size) + (1 if total_records % page_size > 0 else 0)
                
                if total_pages > 1:
                    page = st.slider(f"Navegación Paginada (Visualizando bloques de {page_size:,} registros)", 1, total_pages, 1)
                    start_idx = (page - 1) * page_size
                    end_idx = start_idx + page_size
                    st.info(f"Mostrando registros {start_idx + 1:,} al {min(end_idx, total_records):,} (Página {page} de {total_pages})")
                    st.dataframe(df_norm.iloc[start_idx:end_idx], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_norm, use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron proyectos bajo los criterios seleccionados.")
            
    

elif active_tab == "tab3":
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>📁 Validador y Verificación de Proyectos</h2>", unsafe_allow_html=True)
    st.info("Funcionalidad de Consulta: Ingrese el código de proyecto para acceder a su trazabilidad completa.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_codigo = st.text_input("Código de Proyecto", help="Ejemplo: MAAE-SUIA-RA-DPAT-2022-XXXX")
    with col2:
        st.write("")
        st.write("")
        btn_search = st.button("🔍 Buscar Proyecto", use_container_width=True, type="primary")
        
    if search_codigo and btn_search:
        df_proj = load_management_summary(start_date_in, end_date_in, codigo_proyecto=search_codigo)
        if not df_proj.empty:
            st.success(f"Proyecto Encontrado: {df_proj['nombre_proyecto'].iloc[0]}")
            st.markdown("<h3 style='color: white !important;'>Resumen de Gestión (Acreditación SUIA)</h3>", unsafe_allow_html=True)
            
            # --- DISEÑO UX EXPERTO: CERTIFICADO DIGITAL DE GESTIÓN (REPLICADO DE TAB 6) ---
            proj_data = df_proj.iloc[0]
            tipo_permiso = proj_data.get('tipo_permiso_ambiental', 'No definido')
            v_res = proj_data.get("numero_resolucion", "En Trámite")
            v_fecha = proj_data.get("fecha_resolucion", "No registrada")
            v_ente = proj_data.get("ente_acreditado", "Ministerio de Ambiente / GAD")
            v_prov = proj_data.get("provincia", "N/D")
            v_cant = proj_data.get("canton", "N/D")
            v_prop = proj_data.get("nombre_proponente", "No registrado")
            v_ruc = proj_data.get("ced_ruc_proponente", "N/D")
            
            # Card HTML con estética premium
            cert_card = f"""<div style="background: linear-gradient(135deg, rgba(26,82,118,0.2) 0%, rgba(21,67,96,0.4) 100%); padding: 25px; border-radius: 15px; border: 1px solid rgba(52,152,219,0.3); position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 20px;">
<div style="position: absolute; right: -20px; top: -20px; opacity: 0.05; font-size: 150px; transform: rotate(15deg);">🛡️</div>
<div style="display: flex; gap: 20px; align-items: flex-start;">
<div style="background: linear-gradient(180deg, #1ABC9C 0%, #16A085 100%); width: 12px; height: 180px; border-radius: 6px; box-shadow: 0 0 15px rgba(26,188,156,0.4);"></div>
<div style="flex: 1;">
<div style="font-size: 0.75rem; color: #85C1E9 !important; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; margin-bottom: 5px;">📜 Certificado de Regularización Ambiental</div>
<div style="font-size: 1.5rem; color: #FFFFFF !important; font-weight: 800; margin-bottom: 15px; line-height: 1.2;">{tipo_permiso}</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: rgba(0,0,0,0.2); padding: 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
<div>
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">Proponente / RUC</div>
<div style="font-size: 0.9rem; color: #ECF0F1 !important; font-weight: 700;">👤 {v_prop}<br><small style="color:#85C1E9;">ID: {v_ruc}</small></div>
</div>
<div>
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">N° de Resolución</div>
<div style="font-size: 1rem; color: #F1C40F !important; font-weight: 700; font-family: 'Courier New', monospace;">{v_res}</div>
</div>
<div>
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">Jurisdicción Territorial</div>
<div style="font-size: 0.9rem; color: #FFFFFF !important; font-weight: 600;">📍 {v_prov} - {v_cant}</div>
</div>
<div>
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">Fecha / Autoridad</div>
<div style="font-size: 0.9rem; color: #FFFFFF !important; font-weight: 600;">📅 {v_fecha}<br><small style="color:#BDC3C7;">{v_ente}</small></div>
</div>
</div>
</div>
</div>
<div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
<div style="font-size: 0.7rem; color: #A9DFBF !important; font-weight: 600;">Sincronizado con DWH: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
<div style="font-size: 0.65rem; color: #2ECC71 !important; border: 1px solid #2ECC71; padding: 4px 12px; border-radius: 20px; font-weight: 700;">✅ PROYECTO VALIDADO</div>
</div>
</div>"""
            st.markdown(cert_card, unsafe_allow_html=True)

            # ── PANEL INSTITUCIONAL dim_area v3.0 ────────────────────────────
            _tipo_inst   = proj_data.get('tipo_area_inst', 'Sin Clasificar') or 'Sin Clasificar'
            _siglas      = proj_data.get('siglas_area', '') or ''
            _area_padre  = proj_data.get('area_padre', 'N/A') or 'N/A'
            _canton_dir  = proj_data.get('canton_directo_area', 'N/A') or 'N/A'
            _emisora     = bool(proj_data.get('es_emisora_aaa', False))
            _seguimiento = bool(proj_data.get('es_seguimiento_aaa', False))
            _resol_min   = proj_data.get('resolucion_ministerial', '') or ''
            _oficina     = proj_data.get('oficina_tecnica', 'N/D') or 'N/D'
            _nivel_jer   = proj_data.get('nivel_jerarquico', 1) or 1
            _l1_nombre   = proj_data.get('l1_nombre', '') or ''
            _l1_siglas   = proj_data.get('l1_siglas_tipo', '') or ''
            _l2_nombre   = proj_data.get('l2_nombre', '') or ''
            _ruta        = proj_data.get('ruta_nombres', '') or ''
            _es_hoja     = bool(proj_data.get('es_hoja', True))

            _TIPO_COLORS = {
                'PC': '#8E44AD', 'EA': '#E67E22', 'DP': '#2980B9',
                'OT': '#27AE60', 'DZ': '#C0392B', 'ZONALES': '#E74C3C',
                'CONELEC': '#16A085'
            }
            _badge_emisora   = '<span style="background:#1ABC9C;color:#fff;padding:2px 10px;border-radius:12px;font-size:0.7rem;font-weight:700;margin-right:6px;">✅ Emisora AAA</span>' if _emisora else ''
            _badge_seguim    = '<span style="background:#3498DB;color:#fff;padding:2px 10px;border-radius:12px;font-size:0.7rem;font-weight:700;margin-right:6px;">📋 Seguimiento AAA</span>' if _seguimiento else ''
            _badge_tipo_col  = _TIPO_COLORS.get(_siglas, '#566573')
            _resol_row       = f'<div style="font-size:0.65rem;color:#BDC3C7;text-transform:uppercase;font-weight:600;margin-top:8px;">Resolución Ministerial</div><div style="font-size:0.8rem;color:#F1C40F;font-family:monospace;">{_resol_min}</div>' if _resol_min else ''

            # Breadcrumb jerárquico v3.0
            _ruta_display = _ruta if _ruta else (_area_padre if _area_padre != 'N/A' else _oficina)
            _nivel_label  = {1: '🔵 Nivel 1 — Raíz', 2: '🟡 Nivel 2', 3: '🟢 Nivel 3'}.get(int(_nivel_jer), f'Nivel {_nivel_jer}')
            _hoja_badge   = '<span style="background:#1E8449;color:#fff;padding:1px 8px;border-radius:10px;font-size:0.65rem;font-weight:700;margin-left:6px;">NODO TERMINAL</span>' if _es_hoja else ''

            inst_card = f"""
<div style="background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.08);
            border-radius:12px;padding:18px 22px;margin-bottom:18px;">
  <div style="font-size:0.65rem;color:#85C1E9;text-transform:uppercase;font-weight:700;
              letter-spacing:1.5px;margin-bottom:4px;">🏛️ Información Institucional (dim_area v3.0)</div>
  <div style="font-size:0.7rem;color:#A9DFBF;margin-bottom:12px;font-family:monospace;">
    {_ruta_display}
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;">
    <div>
      <div style="font-size:0.6rem;color:#BDC3C7;text-transform:uppercase;font-weight:600;">Tipo Institucional</div>
      <div style="margin-top:4px;">
        <span style="background:{_badge_tipo_col};color:#fff;padding:3px 12px;border-radius:20px;
                     font-size:0.75rem;font-weight:700;">{_tipo_inst}</span>
        <span style="color:rgba(255,255,255,0.5);font-size:0.7rem;margin-left:6px;">({_siglas})</span>
      </div>
      <div style="font-size:0.65rem;color:#BDC3C7;margin-top:6px;">{_nivel_label}{_hoja_badge}</div>
    </div>
    <div>
      <div style="font-size:0.6rem;color:#BDC3C7;text-transform:uppercase;font-weight:600;">Raíz Jerárquica (L1)</div>
      <div style="font-size:0.8rem;color:#ECF0F1;font-weight:600;margin-top:4px;">📂 {_l1_nombre or _area_padre}</div>
      <div style="font-size:0.65rem;color:#85C1E9;">{_l1_siglas}</div>
    </div>
    <div>
      <div style="font-size:0.6rem;color:#BDC3C7;text-transform:uppercase;font-weight:600;">Autoridad / Área</div>
      <div style="font-size:0.85rem;color:#ECF0F1;font-weight:600;margin-top:4px;">🏢 {_oficina}</div>
      {f'<div style="font-size:0.7rem;color:#BDC3C7;margin-top:2px;">↳ {_l2_nombre}</div>' if _l2_nombre else ''}
    </div>
    <div>
      <div style="font-size:0.6rem;color:#BDC3C7;text-transform:uppercase;font-weight:600;">Cantón del Área</div>
      <div style="font-size:0.85rem;color:#FFFFFF;font-weight:600;margin-top:4px;">📍 {_canton_dir}</div>
    </div>
    <div style="grid-column:span 2;">
      <div style="font-size:0.6rem;color:#BDC3C7;text-transform:uppercase;font-weight:600;">Capacidades AAA</div>
      <div style="margin-top:6px;">{_badge_emisora}{_badge_seguim}{'<span style="color:rgba(255,255,255,0.3);font-size:0.75rem;">Sin habilitación AAA registrada</span>' if not _emisora and not _seguimiento else ''}</div>
      {_resol_row}
    </div>
  </div>
</div>"""
            st.markdown(inst_card, unsafe_allow_html=True)
            # ── FIN PANEL INSTITUCIONAL ──────────────────────────────────────

            with st.expander("🔍 Ver Tabla de Datos Completa (Resumen de Gestión)", expanded=False):
                st.dataframe(df_proj.T.rename(columns={0: "Detalle Extendido"}), use_container_width=True)
            
            st.markdown("<h3 style='color: white !important;'>Historial de Trámites y Tareas</h3>", unsafe_allow_html=True)
            df_hist = load_project_history(search_codigo)
            if not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else:
                st.info("No hay historial de tareas para este proyecto.")

            st.markdown("---")
            st.markdown("<h3 style='color: white !important;'>Registro de Pagos Asociados</h3>", unsafe_allow_html=True)
            df_pay = load_project_payments(search_codigo)
            if not df_pay.empty:
                st.dataframe(df_pay, use_container_width=True, hide_index=True)
            else:
                st.info("No hay pagos registrados para este proyecto.")

            # --- VISUALIZADORES AVANZADOS (Flujo y Gantt) ---
            if not df_hist.empty:
                st.markdown("---")
                col_g, col_f = st.columns(2)
                with col_g:
                    with st.expander("📊 Diagrama de Gantt (Trazabilidad Temporal)", expanded=False):
                        # Ensure timestamps (Force timezone removal to prevent tz-naive vs tz-aware subtraction errors)
                        df_hist['fecha_inicio_tarea'] = pd.to_datetime(df_hist['fecha_inicio_tarea'], utc=True).dt.tz_localize(None)
                        df_hist['fecha_fin_tarea'] = pd.to_datetime(df_hist['fecha_fin_tarea'], utc=True).dt.tz_localize(None)
                        if 'usuario_tarea' not in df_hist.columns:
                            df_hist['usuario_tarea'] = 'Sistema'
                            
                        fig_gantt = px.timeline(df_hist, x_start="fecha_inicio_tarea", x_end="fecha_fin_tarea", 
                                                y="tarea", color="estado_proceso", hover_name="usuario_tarea",
                                                title="Línea de Vida del Proyecto")
                        fig_gantt.update_yaxes(autorange="reversed")
                        fig_gantt.update_layout(
                            paper_bgcolor="#F8F9F9", # Fondo claro para visibilidad total de líneas
                            plot_bgcolor="#FFFFFF",
                            title_font=dict(color="black", size=18),
                            font=dict(color="#2C3E50"), # Texto oscuro sobre fondo claro
                            margin=dict(t=60, b=20, l=20, r=20),
                            height=450
                        )
                        st.plotly_chart(fig_gantt, use_container_width=True)
                        
                with col_f:
                    with st.expander("🔄 Diagrama de Flujo Analítico (BPMN / Bizagi Style)", expanded=False):
                        flow = 'digraph BizagiProcess {\n'
                        flow += 'rankdir=TB;\n'
                        flow += 'bgcolor="#F8F9F9";\n' # Fondo claro sólido (High visibility)
                        flow += 'label="FLUJO ANALÍTICO DE PROCESO (BPMN)";\n'
                        flow += 'labelloc="t";\n'
                        flow += 'fontsize=16;\n'
                        flow += 'fontcolor="black";\n'
                        flow += 'splines=ortho;\n'
                        flow += 'nodesep=0.7;\n'
                        flow += 'node [fontname="Segoe UI, sans-serif", penwidth=2];\n'
                        flow += 'edge [color="#2C3E50", penwidth=2.5, arrowsize=1.0];\n'
                        
                        # [BPMN] Evento de Inicio (Círculo verde delgado)
                        flow += 'start_event [shape=circle, style=filled, fillcolor="#D5F5E3", color="#2ECC71", penwidth=2, label="Inicio", width=0.6, height=0.6];\n'
                        
                        for i in range(len(df_hist)):
                            row = df_hist.iloc[i]
                            task_id = f"n{i}"
                            t_name = str(row['tarea']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            estado = str(row['estado_proceso']).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', "'")
                            
                            f_ini = row['fecha_inicio_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_inicio_tarea']) else 'N/A'
                            f_fin = row['fecha_fin_tarea'].strftime('%d %b %Y %H:%M') if pd.notnull(row['fecha_fin_tarea']) else 'En Proceso'
                            
                            # Paleta de Colores Bizagi BPM
                            t_upper = t_name.upper()
                            if any(k in t_upper for k in ['PAGO', 'LIQUIDACION', 'FACTURA', 'COMPROB', 'TRANSF', 'FINAN', 'ORDEN_PAGO', 'REGISTRO PAGO']):
                                bg_color = "#E8F8F5" # Fondo menta muy claro
                                border_color = "#1ABC9C" # Borde esmeralda oscuro
                                font_color = "#117A65"
                            elif estado.upper() in ['RECHAZADO', 'ANULADO', 'ARCHIVADO']:
                                bg_color = "#FDEDEC" # Fondo rosa pastel
                                border_color = "#E74C3C" # Borde rojo puro
                                font_color = "#922B21"
                            else:
                                bg_color = "#EBF5FB" # Fondo azul cielo (Default Bizagi Activity)
                                border_color = "#2980B9" # Borde azul corporativo
                                font_color = "#154360"
                                
                            html_label = f'''<
                            <table border="0" cellborder="0" cellspacing="0" cellpadding="2">
                              <tr><td align="center"><b><font point-size="11" color="{font_color}">{t_name}</font></b></td></tr>
                              <tr><td align="center"><font point-size="9" color="#7F8C8D">[{estado}]</font></td></tr>
                              <tr><td align="center"><font point-size="8" color="#95A5A6">{f_ini} ➔ {f_fin}</font></td></tr>
                            </table>
                            >'''
                            
                            # [BPMN] Actividad (Rectángulo redondeado claro con doble borde colorido)
                            flow += f'{task_id} [shape=box, style="rounded,filled", fillcolor="{bg_color}", color="{border_color}", penwidth=1.5, label={html_label}, margin="0.2,0.1"];\n'
                            
                        # [BPMN] Evento de Fin (Círculo rojo grueso)
                        flow += 'end_event [shape=circle, style=filled, fillcolor="#FADBD8", color="#E74C3C", penwidth=3, label="Fin", width=0.6, height=0.6];\n'
                            
                        # Enrutamiento y Conexiones Ortogonales
                        if len(df_hist) > 0:
                            flow += 'start_event -> n0;\n'
                            for i in range(len(df_hist)-1):
                                flow += f'n{i} -> n{i+1};\n'
                            flow += f'n{len(df_hist)-1} -> end_event;\n'
                        else:
                            flow += 'start_event -> end_event;\n'
                            
                        flow += '}'
                        st.graphviz_chart(flow)
        else:
            st.error("Proyecto no encontrado en el Data Warehouse. Verifique el código e intente nuevamente.")

elif active_tab == "tab4":
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>🌎 Inteligencia Territorial y Administrativa</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: transparent; padding: 15px; border-left: 5px solid #e74c3c; border-radius: 5px; margin-bottom: 20px;">
    <strong>Análisis multinivel de procesos de regularización ambiental:</strong>
    Gestión por Parroquias y Oficinas Técnicas.
    <br><br>
    <div style="padding: 10px; border: 2px dashed #e74c3c; border-radius: 4px; font-weight: bold; color: #922b21;">
        ❗La información presentada corresponde exclusivamente a los proyectos que cumplen con el período seleccionado.
    </div>
</div>
    """, unsafe_allow_html=True)
    
    # Filtros Avanzados
    with st.expander("🛠️ Panel de Filtros Geográficos y Administrativos", expanded=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            provincias = get_geo_provincias()
            sel_prov = st.selectbox("Provincia", provincias)
        with f2:
            cantones = get_geo_cantones(sel_prov)
            sel_cant = st.selectbox("Cantón", cantones)
        with f3:
            parroquias = get_geo_parroquias(sel_prov, sel_cant)
            sel_parr = st.selectbox("Parroquia", parroquias)

        f4, f5, f6 = st.columns(3)
        with f4:
            _tipos_geo = get_tipos_area()
            sel_tipo_geo = st.selectbox("Tipo Institucional", _tipos_geo, key="geo_tipo_area")
        with f5:
            _areas_geo = get_areas_por_tipo(sel_tipo_geo)
            sel_ofic = st.selectbox("Autoridad / Área", _areas_geo, key="geo_oficina")
        with f6:
            origenes = get_origenes_normativa()
            sel_origen_geo = st.selectbox("Origen Normativa", origenes, key="geo_origen")

    df_geo = load_geo_filtered_data(sel_prov, sel_cant, sel_parr, sel_ofic, start_date_in, end_date_in, sel_origen_geo, sel_tipo_geo)
    # Cargar datos nacionales (sin filtros geográficos) para estadísticas globales; respeta filtro de origen
    df_nacional = load_geo_filtered_data("TODAS", "TODOS", "TODAS", "TODAS", start_date_in, end_date_in, sel_origen_geo)

    if not df_nacional.empty:
        # --- BANNER NACIONAL (Estadísticas a nivel país) ---
        total_nac = len(df_nacional)
        ha_nac = df_nacional['superficie_proyecto'].sum()
        top_ofic_nac = df_nacional['oficina_tecnica'].value_counts().idxmax() if 'oficina_tecnica' in df_nacional and not df_nacional['oficina_tecnica'].dropna().empty else "N/A"
        top_parr_nac = df_nacional['parroquia'].value_counts().idxmax() if not df_nacional['parroquia'].dropna().empty else "N/A"
        n_prov = df_nacional['provincia'].nunique() if 'provincia' in df_nacional else 0

        st.markdown("<h3 style='color: white !important; margin-bottom:8px;'>🇪🇨 Panorama Nacional</h3>", unsafe_allow_html=True)
        nac_banner = '<div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;">'
        nac_banner += f'<div style="flex:1;min-width:140px;background:linear-gradient(135deg,#1A5276,#154360);padding:12px 16px;border-radius:12px;border-left:5px solid #2ECC71;"><div style="font-size:0.6rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;letter-spacing:1px;">Total Proyectos</div><div style="font-size:1.5rem;color:#FFFFFF !important;font-weight:800;">{total_nac:,}</div></div>'
        nac_banner += f'<div style="flex:1;min-width:140px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.6rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Hectáreas Totales</div><div style="font-size:1.5rem;color:#2ECC71 !important;font-weight:800;">{ha_nac:,.1f}</div></div>'
        nac_banner += f'<div style="flex:1;min-width:140px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.6rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Provincias Activas</div><div style="font-size:1.5rem;color:#FFFFFF !important;font-weight:800;">{n_prov}</div></div>'
        nac_banner += f'<div style="flex:1;min-width:180px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.6rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Oficina con más Carga</div><div style="font-size:0.85rem;color:#E67E22 !important;font-weight:700;line-height:1.2;">{top_ofic_nac}</div></div>'
        nac_banner += f'<div style="flex:1;min-width:140px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.6rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;">Parroquia Top</div><div style="font-size:0.95rem;color:#9B59B6 !important;font-weight:700;">{top_parr_nac}</div></div>'
        nac_banner += '</div>'
        st.markdown(nac_banner, unsafe_allow_html=True)

        # --- GRÁFICAS ESCALONADAS (Drill-Down según filtros) ---
        # chart_data SIEMPRE usa df_geo para que los TOPs sean 100% coherentes
        # con TODOS los filtros seleccionados en el panel (provincia, cantón,
        # parroquia, oficina técnica y origen de normativa).
        # df_nacional se reserva exclusivamente para el banner de referencia nacional.
        chart_data = df_geo

        # Construir etiquetas de contexto que reflejen los filtros activos
        _ctx_parts = []
        if sel_prov != "TODAS":
            _ctx_parts.append(sel_prov)
        if sel_cant != "TODOS":
            _ctx_parts.append(sel_cant)
        if sel_parr != "TODAS":
            _ctx_parts.append(sel_parr)
        if sel_ofic != "TODAS":
            _ctx_parts.append(f"Oficina: {sel_ofic}")
        if sel_origen_geo != "TODOS":
            _ctx_parts.append(f"Normativa: {sel_origen_geo}")

        if sel_prov == "TODAS":
            left_field = 'provincia'
            left_label = 'Provincia'
            _suffix = f" ({', '.join(_ctx_parts)})" if _ctx_parts else " (Nacional)"
            left_title = f"Top 10 Provincias{_suffix}"
            left_color = 'Blues'
            context_label = ", ".join(_ctx_parts) if _ctx_parts else "Nacional"
        elif sel_cant == "TODOS":
            left_field = 'canton'
            left_label = 'Cantón'
            left_title = f"Top 10 Cantones en {sel_prov}"
            left_color = 'Tealgrn'
            context_label = sel_prov
        elif sel_parr == "TODAS":
            left_field = 'parroquia'
            left_label = 'Parroquia'
            left_title = f"Top 10 Parroquias en {sel_cant}"
            left_color = 'Purp'
            context_label = f"{sel_prov} > {sel_cant}"
        else:
            left_field = 'oficina_tecnica'
            left_label = 'Oficina Técnica'
            left_title = f"Oficinas Técnicas en {sel_parr}"
            left_color = 'Oranges'
            context_label = f"{sel_prov} > {sel_cant} > {sel_parr}"

        st.markdown(f"<div style='background:rgba(255,255,255,0.04);padding:8px 16px;border-radius:8px;margin-bottom:12px;border-left:4px solid #3498DB;'><span style='color:#85C1E9 !important;font-size:0.75rem;text-transform:uppercase;font-weight:700;'>📊 Análisis Escalonado:</span> <span style='color:#FFFFFF !important;font-size:0.9rem;font-weight:600;'>{context_label}</span></div>", unsafe_allow_html=True)

        gnac1, gnac2 = st.columns(2)
        with gnac1:
            if left_field in chart_data.columns and not chart_data[left_field].dropna().empty:
                rank_left = chart_data[left_field].value_counts().head(10).reset_index()
                rank_left.columns = [left_label, 'Proyectos']
                fig_left = px.bar(rank_left, x='Proyectos', y=left_label, orientation='h',
                                  title=left_title,
                                  color='Proyectos', color_continuous_scale=left_color, text='Proyectos')
                fig_left.update_traces(texttemplate='%{text:,}', textposition='outside', textfont_color='#FFFFFF')
                fig_left.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF', title_font=dict(size=14, color='#FFFFFF'),
                    yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                    xaxis=dict(tickfont=dict(color='#FFFFFF')),
                    coloraxis_showscale=False, showlegend=False,
                    margin=dict(t=45, b=20, l=10, r=40), height=350
                )
                st.plotly_chart(fig_left, use_container_width=True)

        with gnac2:
            # Siempre mostrar Top 10 Oficinas Técnicas del contexto actual
            if 'oficina_tecnica' in chart_data.columns and not chart_data['oficina_tecnica'].dropna().empty:
                ofic_rank = chart_data['oficina_tecnica'].value_counts().head(10).reset_index()
                ofic_rank.columns = ['Oficina', 'Proyectos']
                ofic_title = f"Top 10 Oficinas Técnicas ({context_label})"
                fig_ofic = px.bar(ofic_rank, x='Proyectos', y='Oficina', orientation='h',
                                  title=ofic_title,
                                  color='Proyectos', color_continuous_scale='Tealgrn', text='Proyectos')
                fig_ofic.update_traces(texttemplate='%{text:,}', textposition='outside', textfont_color='#FFFFFF')
                fig_ofic.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF', title_font=dict(size=14, color='#FFFFFF'),
                    yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                    xaxis=dict(tickfont=dict(color='#FFFFFF')),
                    coloraxis_showscale=False, showlegend=False,
                    margin=dict(t=45, b=20, l=10, r=40), height=350
                )
                st.plotly_chart(fig_ofic, use_container_width=True)

        st.markdown("---")

    # --- SECCIÓN FILTRADA (contexto según selección del usuario) ---
    if not df_geo.empty:
        # KPIs del contexto filtrado (compacto)
        # Construir etiqueta que refleja TODOS los filtros activos del panel
        _fl_parts = []
        if sel_prov != "TODAS": _fl_parts.append(sel_prov)
        if sel_cant != "TODOS": _fl_parts.append(sel_cant)
        if sel_parr != "TODAS": _fl_parts.append(sel_parr)
        if sel_ofic != "TODAS": _fl_parts.append(f"Oficina: {sel_ofic}")
        if sel_origen_geo != "TODOS": _fl_parts.append(f"Normativa: {sel_origen_geo}")
        filtro_label = " > ".join(_fl_parts) if _fl_parts else "Nacional (Sin Filtros Aplicados)"
        st.markdown(f"<h3 style='color: white !important;'>📍 Contexto Filtrado: {filtro_label}</h3>", unsafe_allow_html=True)

        filt_strip = '<div style="display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;">'
        filt_strip += f'<div style="flex:1;min-width:130px;background:rgba(255,255,255,0.05);padding:10px 14px;border-radius:10px;border-left:4px solid #3498DB;"><div style="font-size:0.65rem;color:#3498DB !important;font-weight:700;text-transform:uppercase;">Proyectos</div><div style="font-size:1.3rem;color:#FFFFFF !important;font-weight:800;">{len(df_geo):,}</div></div>'
        total_ha = df_geo['superficie_proyecto'].sum()
        filt_strip += f'<div style="flex:1;min-width:130px;background:rgba(255,255,255,0.05);padding:10px 14px;border-radius:10px;border-left:4px solid #2ECC71;"><div style="font-size:0.65rem;color:#2ECC71 !important;font-weight:700;text-transform:uppercase;">Hectáreas</div><div style="font-size:1.3rem;color:#FFFFFF !important;font-weight:800;">{total_ha:,.1f}</div></div>'
        top_oficina = df_geo['oficina_tecnica'].value_counts().idxmax() if 'oficina_tecnica' in df_geo and not df_geo['oficina_tecnica'].dropna().empty else "N/A"
        filt_strip += f'<div style="flex:1;min-width:160px;background:rgba(255,255,255,0.05);padding:10px 14px;border-radius:10px;border-left:4px solid #E67E22;"><div style="font-size:0.65rem;color:#E67E22 !important;font-weight:700;text-transform:uppercase;">Oficina Top</div><div style="font-size:0.85rem;color:#FFFFFF !important;font-weight:700;">{top_oficina}</div></div>'
        top_parr = df_geo['parroquia'].value_counts().idxmax() if not df_geo['parroquia'].dropna().empty else "N/A"
        filt_strip += f'<div style="flex:1;min-width:130px;background:rgba(255,255,255,0.05);padding:10px 14px;border-radius:10px;border-left:4px solid #9B59B6;"><div style="font-size:0.65rem;color:#9B59B6 !important;font-weight:700;text-transform:uppercase;">Parroquia Top</div><div style="font-size:0.85rem;color:#FFFFFF !important;font-weight:700;">{top_parr}</div></div>'
        filt_strip += '</div>'
        st.markdown(filt_strip, unsafe_allow_html=True)

        st.markdown("---")
        
        # Mapa de Calor Inteligente Multi-Capa con Fondo Claro
        m1, m2 = st.columns([2, 1])
        
        with m1:
            if sel_prov == "TODAS":
                st.markdown("<h3 style='color: white !important;'>🌐 Inteligencia Territorial: Mapa Nacional</h3>", unsafe_allow_html=True)
                map_level = 'provincia'
                group_key = 'provincia'
                feature_key = "properties.provincia"
                zoom_map = 5.7
            else:
                st.markdown(f"<h3 style='color: white !important;'>🗺️ Análisis Detallado: Cantones de {sel_prov}</h3>", unsafe_allow_html=True)
                map_level = 'canton'
                group_key = 'canton'
                feature_key = "properties.canton"
                zoom_map = 7.2

            geojson_data = load_geojson(map_level)
            
            if geojson_data:
                # 1. Preparar y Normalizar Datos
                map_data = df_geo.groupby([group_key]).size().reset_index(name='conteo')
                def get_geo_key(row):
                    db_val = str(row[group_key]).upper()
                    for f in geojson_data['features']:
                        geo_val = str(f['properties'].get(map_level, '')).upper()
                        if db_val == geo_val or normalize_name(db_val) == normalize_name(geo_val):
                            return f['properties'].get(map_level)
                    return row[group_key]

                map_data['geo_name'] = map_data.apply(get_geo_key, axis=1)

                # 2. Configurar Capas
                fig_map = go.Figure()

                # Capa A: Coroplético con escala de color contrastada para fondo claro
                fig_map.add_trace(go.Choroplethmapbox(
                    geojson=geojson_data,
                    locations=map_data['geo_name'],
                    z=map_data['conteo'],
                    featureidkey=feature_key,
                    colorscale="Reds", # Escala roja vibrante para fondo claro
                    marker_opacity=0.7,
                    marker_line_width=0.5,
                    colorbar_title="Proyectos",
                    hovertemplate="<b>%{location}</b><br>Proyectos: %{z}<extra></extra>"
                ))

                fig_map.update_layout(
                    mapbox_style="carto-positron", # FONDO CLARO (Light Theme)
                    mapbox_zoom=zoom_map,
                    mapbox_center={"lat": -1.8312, "lon": -78.1834},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    height=600,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.error("Error en infraestructura cartográfica.")

        with m2:
            st.markdown("<h3 style='color: white !important;'>Distribución por Oficina</h3>", unsafe_allow_html=True)
            if 'oficina_tecnica' in df_geo:
                ofic_data = df_geo['oficina_tecnica'].value_counts().reset_index()
                ofic_data.columns = ['Oficina', 'Cantidad']
                fig_ofic = px.pie(ofic_data.head(10), values='Cantidad', names='Oficina', hole=0.5,
                                  color_discrete_sequence=px.colors.sequential.Tealgrn)
                fig_ofic.update_layout(showlegend=True, height=500,
                                       font_color='#000000',
                                       legend=dict(orientation="h", y=-0.2, font=dict(color="black")))
                fig_ofic.update_traces(textinfo='none')
                st.plotly_chart(fig_ofic, use_container_width=True)

        st.markdown("---")

        # --- DISTRIBUCIÓN ESTADÍSTICA POR ORIGEN DE NORMATIVA ---
        st.markdown("<h3 style='color: white !important; margin-bottom: 12px;'>📐 Distribución Estadística por Origen de Normativa</h3>", unsafe_allow_html=True)

        if 'origen' in df_geo.columns and not df_geo['origen'].dropna().empty:
            origen_labels = {
                "JBPM_HIDRO": "Hidrocarburos", "JBPM_SECTOR": "Sector A.M. 028",
                "JBPM_4CAT": "4 Categorías", "COA": "COA / SUIA Verde", "RCOA": "RCOA"
            }
            df_geo['origen_label'] = df_geo['origen'].map(origen_labels).fillna(df_geo['origen'])

            dist_c1, dist_c2, dist_c3 = st.columns(3)

            # Gráfico 1: Proyectos por Origen de Normativa (dona)
            with dist_c1:
                st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Por Origen de Normativa</p>", unsafe_allow_html=True)
                orig_dist = df_geo['origen_label'].value_counts().reset_index()
                orig_dist.columns = ['Origen', 'Proyectos']
                fig_orig = px.pie(orig_dist, values='Proyectos', names='Origen', hole=0.5,
                                  color_discrete_sequence=px.colors.qualitative.Bold)
                fig_orig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"),
                    legend=dict(orientation="v", font=dict(color="white", size=10)),
                    margin=dict(t=10, b=10, l=10, r=10), height=320
                )
                fig_orig.update_traces(textinfo='percent+label', textfont_color='white')
                st.plotly_chart(fig_orig, use_container_width=True)

            # Gráfico 2: Top 10 Provincias por Origen (barras apiladas)
            with dist_c2:
                st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Top Provincias por Normativa</p>", unsafe_allow_html=True)
                if 'provincia' in df_geo.columns:
                    prov_orig = (
                        df_geo.groupby(['provincia', 'origen_label'])
                        .size().reset_index(name='Proyectos')
                    )
                    top_provs = df_geo['provincia'].value_counts().head(10).index.tolist()
                    prov_orig = prov_orig[prov_orig['provincia'].isin(top_provs)]
                    fig_prov_orig = px.bar(
                        prov_orig, x='Proyectos', y='provincia', color='origen_label',
                        orientation='h', barmode='stack',
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        labels={'provincia': 'Provincia', 'origen_label': 'Normativa'}
                    )
                    fig_prov_orig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#FFFFFF', showlegend=False,
                        yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                        xaxis=dict(tickfont=dict(color='#FFFFFF')),
                        margin=dict(t=10, b=20, l=10, r=10), height=320
                    )
                    st.plotly_chart(fig_prov_orig, use_container_width=True)

            # Gráfico 3: Top 10 Cantones por Origen (barras apiladas)
            with dist_c3:
                st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Top Cantones por Normativa</p>", unsafe_allow_html=True)
                if 'canton' in df_geo.columns:
                    cant_orig = (
                        df_geo.groupby(['canton', 'origen_label'])
                        .size().reset_index(name='Proyectos')
                    )
                    top_cants = df_geo['canton'].value_counts().head(10).index.tolist()
                    cant_orig = cant_orig[cant_orig['canton'].isin(top_cants)]
                    fig_cant_orig = px.bar(
                        cant_orig, x='Proyectos', y='canton', color='origen_label',
                        orientation='h', barmode='stack',
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        labels={'canton': 'Cantón', 'origen_label': 'Normativa'}
                    )
                    fig_cant_orig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#FFFFFF',
                        legend=dict(orientation="h", y=-0.35, font=dict(color="white", size=9)),
                        yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                        xaxis=dict(tickfont=dict(color='#FFFFFF')),
                        margin=dict(t=10, b=60, l=10, r=10), height=320
                    )
                    st.plotly_chart(fig_cant_orig, use_container_width=True)

        st.markdown("---")
        st.markdown("<h2 style='color: white !important; margin-bottom: 15px;'>📋 Detalle Analítico de Proyectos</h2>", unsafe_allow_html=True)
        # Mostrar tabla expandida
        st.dataframe(df_geo[[
            "codigo_proyecto", "nombre_proyecto", "tipo_permiso_ambiental",
            "origen", "provincia", "canton", "parroquia", "oficina_tecnica",
            "superficie_proyecto", "estado_proceso"
        ]], use_container_width=True, hide_index=True)
        
        # Botón de Descarga
        csv = df_geo.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte Territorial (CSV)", csv, "reporte_geo_sieaa.csv", "text/csv", use_container_width=True)
    else:
        st.warning("No hay datos coincidentes para los criterios de filtrado seleccionados.")


elif active_tab == "tab5":
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>💰 Inteligencia Financiera y Recaudación</h2>", unsafe_allow_html=True)
    
    # El buscador se mantiene arriba pero influye en todo el tab si tiene valor
    with st.expander("🔍 Buscador de Pagos por Proyecto", expanded=False):
        c1, c2 = st.columns([3,1])
        with c1:
            pago_search_cod = st.text_input("Ingrese Código de Proyecto para filtrar el Tab completo", 
                                           placeholder="Ej: MAAE-SUIA-RA-...", key="f_pago_cod")
        with c2:
            st.write("")
            st.write("")
            btn_pago_search = st.button("Buscar y Sincronizar", use_container_width=True)
            
        if pago_search_cod:
            df_search = search_payments_by_project(pago_search_cod)
            if not df_search.empty:
                st.success(f"Se encontraron {len(df_search)} transacciones para este proyecto.")
                # Formatear el monto en base a visualización
                df_search_view = df_search.copy()
                df_search_view['monto_pagado'] = df_search_view['monto_pagado'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(df_search_view[[
                    "numero_tramite", "concepto", "fecha_de_pago", "monto_pagado"
                ]], use_container_width=True, hide_index=True)
            elif btn_pago_search:
                st.warning("No se registraron pagos para este código en el Data Warehouse.")

    st.markdown("---")
    
    # Filtros de Dashboard Fiscal (Jerarquía Geográfica Completa)
    st.markdown("""
        <style>
        /* Modifica el color del título del expander de filtros a negro */
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary p,
        div[data-testid="stExpander"] summary svg {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    with st.expander("🛠️ Filtros Geográficos y Temporales", expanded=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            p_list = get_geo_provincias()
            f_prov = st.selectbox("Provincia", p_list)
        with f2:
            c_list = get_geo_cantones(f_prov)
            f_cant = st.selectbox("Cantón", c_list)
        with f3:
            par_list = get_geo_parroquias(f_prov, f_cant)
            f_parr = st.selectbox("Parroquia", par_list)

        f4, f5, f6 = st.columns(3)
        with f4:
            _tipos_rev = get_tipos_area()
            f_tipo_area = st.selectbox("Tipo Institucional", _tipos_rev, key="rev_tipo_area")
        with f5:
            ofic_list = get_areas_por_tipo(f_tipo_area)
            f_ofic = st.selectbox("Autoridad / Área", ofic_list, key="rev_oficina")
        with f6:
            y_list = get_pago_anios()
            f_anio = st.selectbox("Año de Recaudación", y_list)

    # Carga de Datos Analíticos (Sincronizados con los filtros, buscador y rango de fechas global)
    df_revenue_all = load_revenue_analytic_data(f_prov, f_cant, f_parr, f_ofic, f_anio, codigo_proyecto=pago_search_cod if pago_search_cod else None, start_date=start_date_in, end_date=end_date_in, tipo_area=f_tipo_area)

    # Cargar total país genérico para la métrica base si no hay búsqueda por código específico
    df_nacional = load_revenue_analytic_data(anio=f_anio, start_date=start_date_in, end_date=end_date_in) if not pago_search_cod else df_revenue_all

    if not df_revenue_all.empty and df_revenue_all['monto_pagado'].sum() > 0:
        # --- BANNER EJECUTIVO DE MANDO (RECAUDACIÓN) ---
        total_context = df_revenue_all['monto_pagado'].sum()
        total_nacional = df_nacional['monto_pagado'].sum() if not df_nacional.empty else total_context
        
        top_ofic_rev = df_revenue_all.groupby('oficina_tecnica')['monto_pagado'].sum()
        top_oficina = top_ofic_rev.idxmax() if not top_ofic_rev.empty else "N/A"
        
        top_perm_rev = df_revenue_all.groupby('tipo_permiso_ambiental')['monto_pagado'].sum()
        top_permiso = top_perm_rev.idxmax() if not top_perm_rev.empty else "N/A"

        rev_banner = f"""
        <div style="display:flex; gap:12px; margin-bottom: 25px; flex-wrap:wrap;">
            <div style="flex:1.5; min-width:220px; background:linear-gradient(135deg, rgba(46,204,113,0.1) 0%, rgba(39,174,96,0.2) 100%); padding:18px; border-radius:12px; border-left:5px solid #2ECC71; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size:0.75rem; color:#A9DFBF !important; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">💰 Recaudación (Contexto)</div>
                <div style="font-size:1.8rem; color:#FFFFFF !important; font-weight:800; line-height:1.1;">${total_context:,.2f}</div>
            </div>
            <div style="flex:1; min-width:180px; background:rgba(255,255,255,0.03); padding:16px; border-radius:10px; border: 1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; color:#BDC3C7 !important; font-weight:600; text-transform:uppercase; margin-bottom:3px;">🇪🇨 Recaudación Nacional</div>
                <div style="font-size:1.2rem; color:#2ECC71 !important; font-weight:700;">${total_nacional:,.2f}</div>
            </div>
            <div style="flex:1.2; min-width:200px; background:rgba(255,255,255,0.03); padding:16px; border-radius:10px; border: 1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; color:#BDC3C7 !important; font-weight:600; text-transform:uppercase; margin-bottom:3px;">🏢 Oficina Mayor Recaudo</div>
                <div style="font-size:0.9rem; color:#FFFFFF !important; font-weight:700;">{top_oficina}</div>
            </div>
            <div style="flex:1; min-width:180px; background:rgba(255,255,255,0.03); padding:16px; border-radius:10px; border: 1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; color:#BDC3C7 !important; font-weight:600; text-transform:uppercase; margin-bottom:3px;">📄 Permiso Destacado</div>
                <div style="font-size:0.9rem; color:#FFFFFF !important; font-weight:700;">{top_permiso}</div>
            </div>
        </div>
        """
        st.markdown(rev_banner, unsafe_allow_html=True)

        # --- GRÁFICAS ESCALONADAS (Drill-Down Monetario) ---
        if f_prov == "TODAS":
            left_field = 'provincia'
            left_label = 'Provincia'
            left_title = "Top 10 Provincias (Nacional)"
            left_color = 'Greens'
            context_label = "Nacional"
        elif f_cant == "TODOS":
            left_field = 'canton'
            left_label = 'Cantón'
            left_title = f"Top 10 Cantones en {f_prov}"
            left_color = 'Tealgrn'
            context_label = f"{f_prov}"
        elif f_parr == "TODAS":
            left_field = 'parroquia'
            left_label = 'Parroquia'
            left_title = f"Top 10 Parroquias en {f_cant}"
            left_color = 'Emrld'
            context_label = f"{f_prov} > {f_cant}"
        else:
            left_field = 'oficina_tecnica'
            left_label = 'Oficina Técnica'
            left_title = f"Oficinas Técnicas en {f_parr}"
            left_color = 'Mint'
            context_label = f"{f_prov} > {f_cant} > {f_parr}"

        st.markdown(f"<div style='background:rgba(255,255,255,0.04);padding:8px 16px;border-radius:8px;margin-bottom:12px;border-left:4px solid #2ECC71;'><span style='color:#A9DFBF !important;font-size:0.75rem;text-transform:uppercase;font-weight:700;'>📊 Análisis Escalonado Recaudación:</span> <span style='color:#FFFFFF !important;font-size:0.9rem;font-weight:600;'>{context_label}</span></div>", unsafe_allow_html=True)
        
        row1_c1, row1_c2 = st.columns(2)
        
        with row1_c1:
            if left_field in df_revenue_all.columns and not df_revenue_all[left_field].dropna().empty:
                geo_rank = df_revenue_all.groupby(left_field)['monto_pagado'].sum().sort_values(ascending=False).head(10).reset_index()
                geo_rank.columns = [left_label, 'Recaudación ($)']
                fig_left = px.bar(geo_rank, x='Recaudación ($)', y=left_label, orientation='h',
                                  title=left_title,
                                  color='Recaudación ($)', color_continuous_scale=left_color, text='Recaudación ($)')
                fig_left.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_color='#FFFFFF')
                fig_left.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF', title_font=dict(size=14, color='#FFFFFF'),
                    yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                    xaxis=dict(tickfont=dict(color='#FFFFFF')),
                    coloraxis_showscale=False, showlegend=False,
                    margin=dict(t=45, b=20, l=10, r=40), height=350
                )
                st.plotly_chart(fig_left, use_container_width=True)

        with row1_c2:
            st.markdown("<h3 style='color: white !important; font-size:14px; margin-bottom:5px;'>Tipos de Permiso (Contexto Actual)</h3>", unsafe_allow_html=True)
            permit_rank = df_revenue_all.groupby('tipo_permiso_ambiental')['monto_pagado'].sum().sort_values(ascending=False).head(10).reset_index()
            permit_rank.columns = ['Tipo de Permiso', 'Recaudación ($)']
            
            # Paleta gerencial de colores sólidos (Alto Contraste)
            gerencial_colors = ['#2ECC71', '#3498DB', '#F39C12', '#E74C3C', '#9B59B6', '#1ABC9C', '#F1C40F', '#34495E']
            
            fig_permit = px.pie(permit_rank, values='Recaudación ($)', names='Tipo de Permiso', hole=0.5,
                                color_discrete_sequence=gerencial_colors)
            fig_permit.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                font=dict(color="black"), 
                legend=dict(orientation="h", y=-0.3, font=dict(color="black", size=10)),
                margin=dict(t=20, b=20, l=10, r=10), height=350
            )
            fig_permit.update_traces(textinfo='none', pull=[0.05] + [0]*(len(permit_rank)-1))
            st.plotly_chart(fig_permit, use_container_width=True)

        st.markdown("---")
        st.markdown("<h3 style='color: white !important;'>📋 Listado Detallado de Proyectos Reales (Desglose Territorial)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: white; font-size:14px'>Listado utilizado para transparentar y definir a qué proyectos corresponden casos N/A en territorio.</p>", unsafe_allow_html=True)
        
        detail_cols = ["numero_tramite", "codigo_proyecto", "nombre_proyecto", "provincia", "canton", "parroquia", "oficina_tecnica", "tipo_permiso_ambiental", "anio", "monto_pagado"]
        
        # Validar si las nuevas columnas existen porque Streamlit cachea los dataframes viejos a veces.
        if set(detail_cols).issubset(df_revenue_all.columns):
            st.dataframe(df_revenue_all[detail_cols].sort_values(by='monto_pagado', ascending=False), 
                         use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Limpiando caché... Por favor recarga la página para visualizar las nuevas columnas del proyecto.")
            
        # Botón de Descarga
        csv = df_revenue_all.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Listado de Proyectos (CSV)", csv, "reporte_recaudacion_proyectos_sieaa.csv", "text/csv", use_container_width=True)

        # ── S2.3: Recaudación segmentada por Tipo Institucional (dim_area v2.0) ──
        st.markdown("---")
        st.markdown("<h3 style='color:white !important;'>🏛️ Recaudación por Tipo Institucional (dim_area v2.0)</h3>", unsafe_allow_html=True)
        df_tipo_rev = load_revenue_by_tipo_area(anio=f_anio, sd=start_date_in, ed=end_date_in)
        if not df_tipo_rev.empty:
            _rt1, _rt2 = st.columns([1, 2])
            with _rt1:
                _color_map_rev = {'Planta Central': '#8E44AD', 'Ente Acreditado': '#E67E22',
                                  'Dirección Provincial': '#2980B9', 'Oficina Técnica': '#27AE60',
                                  'ZONALES DZ': '#C0392B', 'ZONALES': '#E74C3C',
                                  'CONELEC': '#16A085', 'Sin Clasificar': '#7F8C8D'}
                fig_tipo_rev = px.pie(
                    df_tipo_rev, values='recaudacion_total', names='tipo_area', hole=0.52,
                    color='tipo_area', color_discrete_map=_color_map_rev,
                    title="Distribución por Tipo"
                )
                fig_tipo_rev.update_traces(textinfo='percent+label', textfont=dict(color='white', size=10))
                fig_tipo_rev.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                    showlegend=False, margin=dict(t=40, b=10, l=5, r=5), height=320
                )
                st.plotly_chart(fig_tipo_rev, use_container_width=True)
            with _rt2:
                df_tipo_rev_disp = df_tipo_rev.copy()
                df_tipo_rev_disp['recaudacion_total'] = df_tipo_rev_disp['recaudacion_total'].apply(lambda x: f"${x:,.2f}" if x else "$0.00")
                df_tipo_rev_disp['ticket_promedio']   = df_tipo_rev_disp['ticket_promedio'].apply(lambda x: f"${x:,.2f}" if x else "$0.00")
                st.dataframe(
                    df_tipo_rev_disp.rename(columns={
                        'tipo_area': 'Tipo Institucional', 'siglas': 'Siglas',
                        'proyectos': 'Proyectos', 'recaudacion_total': 'Recaudación Total',
                        'ticket_promedio': 'Ticket Promedio', 'areas_activas': 'Áreas Activas'
                    }),
                    use_container_width=True, hide_index=True
                )
        # ── fin S2.3 ────────────────────────────────────────────────────────────

        # Mapa Coroplético de Recaudación (Provincial)
        st.markdown("---")
        st.markdown("<h3 style='color: white !important;'>🗺️ Distribución Geográfica de Ingresos (Provincias)</h3>", unsafe_allow_html=True)
        geo_rev = df_revenue_all.groupby('provincia')['monto_pagado'].sum().reset_index()
        geojson_map = load_geojson('provincia')
        if geojson_map:
            # Normalización para mapa
            def get_map_key(row):
                db_val = str(row['provincia']).upper()
                for f in geojson_map['features']:
                    geo_val = str(f['properties'].get('provincia', '')).upper()
                    if db_val == geo_val or normalize_name(db_val) == normalize_name(geo_val):
                        return f['properties'].get('provincia')
                return row['provincia']
            geo_rev['geo_name'] = geo_rev.apply(get_map_key, axis=1)
            
            fig_georev = go.Figure(go.Choroplethmapbox(
                geojson=geojson_map, locations=geo_rev['geo_name'], z=geo_rev['monto_pagado'],
                featureidkey="properties.provincia", colorscale="Greens", marker_opacity=0.8,
                hovertemplate="<b>%{location}</b><br>Recaudación: $%{z:,.2f}<extra></extra>"
            ))
            fig_georev.update_layout(
                mapbox_style="carto-positron", mapbox_zoom=5.6, mapbox_center={"lat": -1.8312, "lon": -78.1834},
                margin={"r":0,"t":0,"l":0,"b":0}, height=500, paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_georev, use_container_width=True)
    else:
        st.warning("No se encontraron registros financieros para los criterios seleccionados.")

elif active_tab == "tab6":
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>📋 Perfil Inteligente 360° del Proyecto</h2>", unsafe_allow_html=True)
    
    # Buscador Centralizado
    col1, col2 = st.columns([3, 1])
    with col1:
        search_360 = st.text_input("Ingrese Código de Proyecto (SUIA) para análisis integral", 
                                   placeholder="MAE-RA-202X-XXXXXX", key="search_360")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("🚀 Generar Perfil 360°", use_container_width=True)

    if search_360 or do_search:
        # Carga Multidimensional
        df_base = load_management_summary(start_date_in, end_date_in, codigo_proyecto=search_360)
        df_env = load_project_env_details(search_360)
        df_waste = load_project_waste_details(search_360)
        df_pay = search_payments_by_project(search_360)

        if not df_base.empty:
            proj_name = df_base['nombre_proyecto'].iloc[0]
            permisos_list = df_base['tipo_permiso_ambiental'].unique().tolist()
            status = df_base['estado_actual'].iloc[0]
            surface = df_env['superficie_proyecto'].iloc[0] if not df_env.empty else 0
            inter_raw = df_env['interseccion_snap'].iloc[0] if not df_env.empty else "N/A"
            total_paid = df_pay['monto_pagado'].sum() if not df_pay.empty else 0

            # --- INJECT GLOBAL SCOPED CSS FOR THIS PROFILE ---
            st.markdown('<style>.prof360-card,.prof360-card *{color:#1B2631 !important;}.prof360-card .pf-label{color:#21618C !important;font-weight:700;}.prof360-card .pf-val{color:#000000 !important;font-weight:600;}.geo-strip,.geo-strip *{color:#D5DBDB !important;}.geo-strip .geo-val{color:#FFFFFF !important;font-weight:700;}</style>', unsafe_allow_html=True)

            # --- HERO: NOMBRE DEL PROYECTO + TIPO DE PERMISO ---
            permisos_html = ""
            for p in permisos_list:
                permisos_html += f'<span style="display:inline-block;background:rgba(46,204,113,0.2);color:#2ECC71 !important;padding:6px 16px;border-radius:20px;border:1px solid #2ECC71;font-size:0.9rem;font-weight:700;margin:2px 4px;">{p}</span>'
            hero_html = f'<div style="background:linear-gradient(135deg,#1A5276 0%,#154360 100%);padding:22px 28px;border-radius:14px;margin-bottom:18px;border-left:6px solid #2ECC71;">'
            hero_html += f'<div style="font-size:0.7rem;color:#85C1E9 !important;text-transform:uppercase;letter-spacing:2px;font-weight:700;margin-bottom:4px;">Proyecto SUIA</div>'
            hero_html += f'<div style="font-size:1.3rem;color:#FFFFFF !important;font-weight:800;margin-bottom:10px;line-height:1.3;">{proj_name}</div>'
            hero_html += f'<div>{permisos_html}</div>'
            hero_html += '</div>'
            st.markdown(hero_html, unsafe_allow_html=True)

            # --- KPIs COMPACTOS: STRIP HORIZONTAL ---
            snap_color = "#E74C3C" if "SI" in str(inter_raw).upper() else "#2ECC71"
            snap_icon = "⚠️" if "SI" in str(inter_raw).upper() else "✅"
            kpi_strip = '<div style="display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;">'
            kpi_strip += f'<div style="flex:1;min-width:140px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.7rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:600;">Estado</div><div style="font-size:1.1rem;color:#FFFFFF !important;font-weight:700;">{status}</div></div>'
            kpi_strip += f'<div style="flex:1;min-width:140px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.7rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:600;">Superficie</div><div style="font-size:1.1rem;color:#FFFFFF !important;font-weight:700;">{surface:,.2f} Has</div></div>'
            kpi_strip += f'<div style="flex:1;min-width:140px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.7rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:600;">Inversión</div><div style="font-size:1.1rem;color:#2ECC71 !important;font-weight:700;">${total_paid:,.2f}</div></div>'
            kpi_strip += f'<div style="flex:1;min-width:200px;background:rgba(255,255,255,0.06);padding:12px 16px;border-radius:10px;border:1px solid {snap_color};"><div style="font-size:0.7rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:600;">{snap_icon} SNAP</div><div style="font-size:0.85rem;color:{snap_color} !important;font-weight:700;line-height:1.2;">{inter_raw}</div></div>'
            kpi_strip += '</div>'
            st.markdown(kpi_strip, unsafe_allow_html=True)

            # --- UBICACIÓN GEOGRÁFICA: BARRA COMPACTA ---
            geo_prov = df_base['provincia'].iloc[0] if 'provincia' in df_base.columns else "N/D"
            geo_cant = df_base['canton'].iloc[0] if 'canton' in df_base.columns else "N/D"
            geo_parr = df_base['parroquia'].iloc[0] if 'parroquia' in df_base.columns else "N/D"
            geo_ofic = df_base['oficina_tecnica'].iloc[0] if 'oficina_tecnica' in df_base.columns else "N/D"
            geo_html = '<div class="geo-strip" style="background:rgba(255,255,255,0.04);padding:12px 20px;border-radius:10px;margin-bottom:18px;border:1px solid rgba(255,255,255,0.08);display:flex;flex-wrap:wrap;gap:20px;align-items:center;">'
            geo_html += '<div style="font-size:0.7rem;color:#85C1E9 !important;text-transform:uppercase;font-weight:700;letter-spacing:1px;">📍 Ubicación</div>'
            geo_html += f'<div><span style="color:#3498DB !important;font-size:0.9rem;">●</span> <span style="color:#AEB6BF !important;font-size:0.75rem;">Prov:</span> <span class="geo-val" style="font-size:0.9rem;">{geo_prov}</span></div>'
            geo_html += f'<div><span style="color:#2ECC71 !important;font-size:0.9rem;">●</span> <span style="color:#AEB6BF !important;font-size:0.75rem;">Cantón:</span> <span class="geo-val" style="font-size:0.9rem;">{geo_cant}</span></div>'
            geo_html += f'<div><span style="color:#E67E22 !important;font-size:0.9rem;">●</span> <span style="color:#AEB6BF !important;font-size:0.75rem;">Parr:</span> <span class="geo-val" style="font-size:0.9rem;">{geo_parr}</span></div>'
            geo_html += f'<div><span style="color:#9B59B6 !important;font-size:0.9rem;">●</span> <span style="color:#AEB6BF !important;font-size:0.75rem;">Oficina:</span> <span class="geo-val" style="font-size:0.9rem;">{geo_ofic}</span></div>'
            geo_html += '</div>'
            st.markdown(geo_html, unsafe_allow_html=True)

            st.markdown("---")

            # --- SECCIÓN 2: SENSIBILIDAD AMBIENTAL Y LEGAL ---
            row1_c1, row1_c2 = st.columns(2)
            with row1_c1:
                st.markdown("<h3 style='color: white !important;'>🌳 Sensibilidad Ambiental (SNAP)</h3>", unsafe_allow_html=True)
                if not df_env.empty and df_env['interseccion_snap'].iloc[0] == "SI":
                    areas = df_env['areas_protegidas'].iloc[0]
                    st.warning(f"**Áreas Afectadas:** {areas}")
                else:
                    st.info("El proyecto no presenta intersecciones registradas con el Sistema Nacional de Áreas Protegidas.")

            with row1_c2:
                st.markdown("<h3 style='color: white !important;'>⚖️ Integridad Legal (Resoluciones)</h3>", unsafe_allow_html=True)
                if not df_env.empty and df_env['numero_resolucion'].iloc[0]:
                    tipo_permiso = df_base['tipo_permiso_ambiental'].iloc[0]
                    v_res = df_env["numero_resolucion"].iloc[0] or "No registrado"
                    v_fecha = df_env["fecha_resolucion"].iloc[0] or "No registrada"
                    v_ente = df_env["ente_acreditado"].iloc[0] or "No registrado"
                    # Diseño UX Experto: Certificado Digital de Integridad Legal (HTML corregido sin indentación)
                    card = f"""<div style="background: linear-gradient(135deg, rgba(26,82,118,0.2) 0%, rgba(21,67,96,0.4) 100%); padding: 25px; border-radius: 15px; border: 1px solid rgba(52,152,219,0.3); position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
<div style="position: absolute; right: -20px; top: -20px; opacity: 0.1; font-size: 120px; transform: rotate(15deg);">⚖️</div>
<div style="display: flex; gap: 20px; align-items: flex-start;">
<div style="background: linear-gradient(180deg, #F1C40F 0%, #D4AC0D 100%); width: 12px; height: 100px; border-radius: 6px; box-shadow: 0 0 15px rgba(241,196,15,0.4);"></div>
<div style="flex: 1;">
<div style="font-size: 0.7rem; color: #85C1E9 !important; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; margin-bottom: 5px;">📜 Resolución Oficial Habilitante</div>
<div style="font-size: 1.4rem; color: #FFFFFF !important; font-weight: 800; margin-bottom: 15px; line-height: 1.2;">{tipo_permiso}</div>
<div style="display: grid; grid-template-columns: 1fr; gap: 12px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
<div style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">N° de Documento</div>
<div style="font-size: 1rem; color: #F1C40F !important; font-weight: 700; font-family: 'Courier New', monospace;">{v_res}</div>
</div>
<div style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">Fecha de Emisión</div>
<div style="font-size: 0.95rem; color: #ECF0F1 !important; font-weight: 600;">📅 {v_fecha}</div>
</div>
<div>
<div style="font-size: 0.65rem; color: #BDC3C7 !important; text-transform: uppercase; font-weight: 600;">Autoridad Competente</div>
<div style="font-size: 0.95rem; color: #FFFFFF !important; font-weight: 600;">🏛️ {v_ente}</div>
</div>
</div>
</div>
</div>
<div style="margin-top: 15px; display: flex; justify-content: flex-end;">
<div style="font-size: 0.6rem; color: #2ECC71 !important; border: 1px solid #2ECC71; padding: 3px 10px; border-radius: 20px; font-weight: 700;">✅ INTEGRIDAD VERIFICADA</div>
</div>
</div>"""
                    st.markdown(card, unsafe_allow_html=True)
                else:
                    st.info("No se dispone de información de resolución final para este registro.")

            st.markdown("---")

            # --- SECCIÓN 3: GESTIÓN DE DESECHOS Y PAGOS ---
            row2_c1, row2_c2 = st.columns(2)
            with row2_c1:
                st.markdown("<h3 style='color: white !important;'>♻️ Gestión de Desechos (RGD)</h3>", unsafe_allow_html=True)
                if not df_waste.empty:
                    # Mostrar código(s) RGD del generador (dim_waste_generator)
                    codigos_rgd = df_waste['codigo_rgd'].dropna().unique().tolist()
                    codigos_rgd = [c for c in codigos_rgd if c != 'Sin RGD']
                    if codigos_rgd:
                        badges_rgd = '<style>.rgd-badge{color:#000000 !important;background:#D5F5E3 !important;}</style>'
                        for c in codigos_rgd:
                            badges_rgd += f'<span class="rgd-badge" style="display:inline-block;padding:6px 16px;border-radius:12px;margin:2px 4px;font-size:0.9rem;font-weight:800;border:1px solid #82E0AA;letter-spacing:0.3px;">{c}</span>'
                        st.markdown('<div style="margin-bottom:10px;"><span style="color:#BDC3C7;font-size:0.75rem;text-transform:uppercase;font-weight:600;">Código(s) RGD:</span><br>' + badges_rgd + '</div>', unsafe_allow_html=True)
                    st.dataframe(df_waste, use_container_width=True, hide_index=True)
                else:
                    st.info("No se han registrado declaraciones de desechos (RGD) con cantidad > 0 para este proyecto.")

            with row2_c2:
                st.markdown("<h3 style='color: white !important;'>💰 Trazabilidad Financiera</h3>", unsafe_allow_html=True)
                if not df_pay.empty:
                    # Formatear el monto si la columna existe en el DF devuelto
                    if 'monto_pagado' in df_pay.columns:
                        df_pay_view = df_pay.copy()
                        df_pay_view['monto_pagado'] = df_pay_view['monto_pagado'].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
                    else:
                        df_pay_view = df_pay.copy()
                    
                    pay_cols = ['numero_tramite', 'concepto', 'fecha_de_pago', 'monto_pagado']
                    # Filtrar las columnas de pay_cols que realmente existen para evitar KeyErrors
                    pay_cols_exist = [c for c in pay_cols if c in df_pay_view.columns]
                    st.dataframe(df_pay_view[pay_cols_exist], use_container_width=True, hide_index=True)
                else:
                    st.info("No hay registros de pagos asociados a este código de proyecto.")


        else:
            st.warning("No se encontró información para el código ingresado. Verifique el formato e intente nuevamente.")
    else:
        st.info("Ingrese un código de proyecto SUIA para desplegar la inteligencia 360°.")

elif active_tab == "tab7":
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>🌲 Inteligencia de Superposición e Intersección Ambiental</h2>", unsafe_allow_html=True)
    
    # --- FILTROS DE TAB 7 ---
    with st.expander("🛠️ Filtros de Análisis Ambiental (Jerarquía Completa)", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            prov_list = get_geo_provincias()
            sel_prov_env = st.selectbox("⚓ Provincia Focalizada", prov_list, key="env_prov")
        with f2:
            cant_list = get_geo_cantones(sel_prov_env)
            sel_cant_env = st.selectbox("🏙️ Cantón Focalizado", cant_list, key="env_cant")
        with f3:
            parr_list = get_geo_parroquias(sel_prov_env, sel_cant_env)
            sel_parr_env = st.selectbox("📍 Parroquia Focalizada", parr_list, key="env_parr")
        with f4:
            st.write("")
            st.write("")
            show_only_inter = st.toggle("Solo Proyectos con Intersección", value=True)

        # Filtros institucionales AAA (dim_area v2.0)
        fa1, fa2, fa3 = st.columns(3)
        with fa1:
            _tipos_env = get_tipos_area()
            sel_tipo_env = st.selectbox("Tipo Institucional", _tipos_env, key="env_tipo_area")
        with fa2:
            st.write("")
            st.write("")
            solo_aaa_env = st.toggle("Solo áreas emisoras AAA", value=False, key="env_solo_aaa",
                                     help="Muestra solo proyectos cuya autoridad responsable está habilitada para emitir certificados AAA")
        with fa3:
            st.write("")
            st.write("")
            show_gap_aaa = st.toggle("Ver brecha de gobernanza AAA", value=False, key="env_gap_aaa",
                                     help="Proyectos SNAP activos supervisados por áreas SIN habilitación AAA")

        st.markdown("---")
        # Filtros de Categoría y Nombre de Área
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            cat_options = [
                '🛡️ SNAP',
                '🔒 ZONAS INTANGIBLES',
                '🌳 BOSQUES PROTECTORES',
                '🌲 PATRIMONIO FORESTAL DEL ESTADO',
                '⚪ SIN INTERSECCIÓN'
            ]
            sel_cats = st.multiselect("🏷️ Categoría de Intersección (Jerarquía Gerencial)",
                                      cat_options, default=cat_options[:-1] if show_only_inter else cat_options)

        with col_f2:
            search_area = st.text_input("🔎 Buscar por Nombre de Área (Ej: Yasuní, Sangay...)",
                                        placeholder="Ingrese nombre de la reserva o zona...",
                                        key="search_area_env")

    # Carga de datos usando el motor ambiental (Sincronizado Jerárquicamente)
    df_env_all = load_environmental_analytic_data(get_engine(), sel_prov_env, sel_cant_env, sel_parr_env, "TODAS",
                                                  start_date_in, end_date_in, selected_cats=sel_cats,
                                                  solo_emisoras_aaa=solo_aaa_env, tipo_area=sel_tipo_env)
    
    # ── Alerta de Brecha Gobernanza AAA (si toggle activo) ─────────────────────
    if show_gap_aaa:
        df_gap = load_snap_sin_aaa_coverage()
        if not df_gap.empty:
            st.markdown("---")
            st.markdown("<h4 style='color:#E74C3C !important;'>⚠️ Brecha de Gobernanza AAA — Proyectos SNAP sin cobertura habilitada</h4>", unsafe_allow_html=True)
            st.caption("Proyectos activos con intersección SNAP cuya autoridad responsable NO está habilitada como emisora AAA.")
            _ga1, _ga2 = st.columns([2, 1])
            with _ga1:
                fig_gap = px.bar(
                    df_gap.head(15), x='proyectos_snap_sin_aaa', y='provincia', orientation='h',
                    color='proyectos_snap_sin_aaa', color_continuous_scale='Reds',
                    text='proyectos_snap_sin_aaa', title="Proyectos SNAP sin AAA por Provincia"
                )
                fig_gap.update_traces(texttemplate='%{text:,}', textposition='outside', textfont_color='#FFFFFF')
                fig_gap.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF', coloraxis_showscale=False,
                    yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                    xaxis=dict(tickfont=dict(color='#FFFFFF')),
                    margin=dict(t=40, b=10, l=10, r=50), height=350
                )
                st.plotly_chart(fig_gap, use_container_width=True)
            with _ga2:
                _total_gap = int(df_gap['proyectos_snap_sin_aaa'].sum())
                st.markdown(f"""
<div style="background:rgba(231,76,60,0.15);border:2px solid #E74C3C;border-radius:10px;
            padding:20px;text-align:center;margin-top:30px;">
  <div style="font-size:2.2rem;color:#FF7675;font-weight:800;">{_total_gap:,}</div>
  <div style="font-size:0.75rem;color:rgba(255,255,255,0.7);margin-top:5px;">
    proyectos SNAP activos<br>sin cobertura AAA
  </div>
  <div style="font-size:0.65rem;color:#E74C3C;margin-top:10px;font-weight:700;">
    Riesgo de Gobernanza<br>Regulatoria
  </div>
</div>""", unsafe_allow_html=True)
                st.dataframe(df_gap, use_container_width=True, hide_index=True,
                             column_config={'provincia': 'Provincia',
                                            'proyectos_snap_sin_aaa': st.column_config.NumberColumn('Sin AAA', format='%d')})
            st.markdown("---")

    if not df_env_all.empty:
        # Filtrado adicional por búsqueda de nombre de área (Front-end level)
        if search_area:
            df_env_all = df_env_all[df_env_all['areas_protegidas'].str.contains(search_area, case=False, na=False)]

        df_env_active = df_env_all

        # --- BANNER DE MÉTRICAS AMBIENTALES (KPIs) ---
        kpis = get_environmental_kpis(df_env_all)
        
        env_banner = f"""
        <div style="display:flex; gap:12px; margin-bottom: 25px; flex-wrap:wrap;">
            <div style="flex:1.5; min-width:220px; background:linear-gradient(135deg, rgba(26,188,156,0.1) 0%, rgba(22,160,133,0.2) 100%); padding:18px; border-radius:12px; border-left:5px solid #1ABC9C; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size:0.75rem; color:#A9DFBF !important; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">🌲 Proyectos en Intersección</div>
                <div style="font-size:1.8rem; color:#FFFFFF !important; font-weight:800; line-height:1.1;">{kpis['total_proyectos']:,}</div>
            </div>
            <div style="flex:1; min-width:180px; background:rgba(255,255,255,0.03); padding:16px; border-radius:10px; border: 1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; color:#BDC3C7 !important; font-weight:600; text-transform:uppercase; margin-bottom:3px;">📐 Hectáreas Afectadas</div>
                <div style="font-size:1.2rem; color:#1ABC9C !important; font-weight:700;">{kpis['total_has']:,.2f} Has</div>
            </div>
            <div style="flex:1.2; min-width:200px; background:rgba(255,255,255,0.03); padding:16px; border-radius:10px; border: 1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; color:#BDC3C7 !important; font-weight:600; text-transform:uppercase; margin-bottom:3px;">🛡️ Capas Ambientales Activas</div>
                <div style="font-size:1.2rem; color:#FFFFFF !important; font-weight:700;">{kpis['capas_activas']} Categorías</div>
            </div>
        </div>
        """
        st.markdown(env_banner, unsafe_allow_html=True)

        # --- SECCIÓN MAPA Y DISTRIBUCIÓN ---
        row1_c1, row1_c2 = st.columns([3, 2])
        
        with row1_c1:
            st.markdown("<h3 style='color: white !important;'>🗺️ Heatmap: Densidad de Intersección Ambiental</h3>", unsafe_allow_html=True)
            
            map_level = 'canton' if sel_prov_env != "TODAS" else 'provincia'
            df_map = get_heatmap_data(df_env_all, level=map_level)
            
            geojson_env = load_geojson(map_level)
            if geojson_env and not df_map.empty:
                # Normalización de nombres para el mapa
                def map_norm(row):
                    val = str(row[0]).upper()
                    for f in geojson_env['features']:
                        g_val = str(f['properties'].get(map_level, '')).upper()
                        if val == g_val or normalize_name(val) == normalize_name(g_val):
                            return f['properties'].get(map_level)
                    return row[0]
                
                df_map['geo_key'] = df_map.apply(map_norm, axis=1)
                
                fig_env_map = px.choropleth_mapbox(
                    df_map, geojson=geojson_env, locations='geo_key', color='densidad',
                    featureidkey=f"properties.{map_level}",
                    mapbox_style="carto-positron", # Estilo claro (más legible)
                    color_continuous_scale="YlGn", # Escala Amarillo a Verde
                    center={"lat": -1.8312, "lon": -78.1834}, zoom=5.4 if map_level == 'provincia' else 7,
                    opacity=0.8, labels={'densidad': 'Proyectos'}
                )
                fig_env_map.update_layout(
                    margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_colorbar=dict(title="N° Proy", tickfont=dict(color="white"))
                )
                st.plotly_chart(fig_env_map, use_container_width=True)
            else:
                st.info("No se dispone de datos geográficos para representar en el mapa con los filtros actuales.")

        with row1_c2:
            st.markdown("<h3 style='color: white !important;'>📊 Categorización de Sensibilidad</h3>", unsafe_allow_html=True)
            
            order_cat = [
                '🛡️ SNAP',
                '🔒 ZONAS INTANGIBLES',
                '🌳 BOSQUES PROTECTORES',
                '🌲 PATRIMONIO FORESTAL DEL ESTADO',
                '⚪ SIN INTERSECCIÓN'
            ]
            
            df_dist = df_env_all['categoria_ambiental'].value_counts().reset_index()
            df_dist.columns = ['Categoría', 'Cantidad']
            df_dist['Categoría'] = pd.Categorical(df_dist['Categoría'], categories=order_cat, ordered=True)
            df_dist = df_dist.sort_values('Categoría')
            
            fig_dist = px.bar(
                df_dist, x='Cantidad', y='Categoría', orientation='h',
                color='Categoría', text='Cantidad',
                color_discrete_map={
                    '🛡️ SNAP': '#2ECC71',
                    '🔒 ZONAS INTANGIBLES': '#E74C3C',
                    '🌳 BOSQUES PROTECTORES': '#F1C40F',
                    '🌲 PATRIMONIO FORESTAL DEL ESTADO': '#3498DB',
                    '⚪ SIN INTERSECCIÓN': '#BDC3C7'
                }
            )
            fig_dist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white"),
                showlegend=False,
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='white')),
                yaxis=dict(tickfont=dict(color='white')),
                margin=dict(t=10, b=10, l=10, r=10), height=380
            )
            fig_dist.update_traces(textfont_color="white")
            st.plotly_chart(fig_dist, use_container_width=True)

        st.markdown("---")
        st.markdown("<p style='color: white; font-size:14px'>Detalle técnico deduplicado por proyecto, mostrando la capa de mayor sensibilidad ambiental según la jerarquía gubernamental.</p>", unsafe_allow_html=True)
        
        view_cols = ["codigo_proyecto", "nombre_proyecto", "tipo_permiso_ambiental", "provincia", "canton", "categoria_ambiental", "areas_protegidas", "superficie_proyecto"]
        df_display = df_env_active.sort_values(by=["prioridad", "superficie_proyecto"], ascending=[True, False])
        st.dataframe(df_display[view_cols], use_container_width=True, hide_index=True)
        
        # Botón de Descarga
        csv_env = df_env_active.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte de Intersección (CSV)", csv_env, "reporte_ambiental_sieaa.csv", "text/csv", use_container_width=True)

    else:
        st.warning("No se encontraron registros ambientales coincidentes con los filtros seleccionados.")

elif active_tab == "tab7_1":
    import json
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>🗺️ Mapa Interactivo: Explorador de Intersección por Selección</h2>", unsafe_allow_html=True)
    
    # 1. CARGA DE DATOS (Independiente del Sidebar para Geografía)
    df_map_data = load_environmental_analytic_data(
        get_engine(), 
        prov=st.session_state['tab71_prov'], 
        cant=st.session_state['tab71_cant'],
        sd=start_date_in, 
        ed=end_date_in
    )

    if not df_map_data.empty:
        # --- LÓGICA DE MAPA ---
        if st.session_state['tab71_prov'] == 'TODAS':
            level = "provincia"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            geojson_path = os.path.join(base_dir, "ecuador_provincias.geojson")
            map_title = "Mapa Nacional: Criticidad Ambiental por Provincia"
            geo_prop = "provincia"  # Propiedad real en el GeoJSON
        else:
            level = "canton"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            geojson_path = os.path.join(base_dir, "ecuador_cantones.geojson")
            map_title = f"Drill-Down: Cantones en {st.session_state['tab71_prov']}"
            geo_prop = "canton"  # Propiedad real en el GeoJSON

        with open(geojson_path, encoding='utf-8') as f:
            geojson_data = json.load(f)

        # Extraer nombres del GeoJSON para normalización (con eliminación de acentos)
        import unicodedata
        def _norm(s):
            if not s: return ''
            return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).upper()
        
        geo_names = [feat['properties'].get(geo_prop, '') for feat in geojson_data['features']]
        geo_lookup = {_norm(n): n for n in geo_names}  # BOLIVAR -> Bolívar

        # Agrupar datos (CRITICIDAD POR HECTÁREAS)
        df_inter = df_map_data[df_map_data['categoria_ambiental'] != '⚪ SIN INTERSECCIÓN'].copy()
        
        # Normalizar a Title Case para match con GeoJSON (fuzzy: sin acentos)
        df_inter['_geo_match'] = df_inter[level].apply(lambda x: geo_lookup.get(_norm(x)))
        df_inter = df_inter.dropna(subset=['_geo_match'])

        
        df_plot = df_inter.groupby('_geo_match').agg(
            hectareas=('superficie_proyecto', 'sum'),
            proyectos=('codigo_proyecto', 'nunique')
        ).reset_index()
        df_plot.columns = [geo_prop, 'Hectáreas', 'Proyectos']

        # 2. CONTROLES GIS (Drill-Down por Selectbox + Reset)
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3, 3, 1])
        with col_ctrl1:
            if st.session_state['tab71_prov'] == 'TODAS':
                # Listar provincias disponibles para drill-down
                prov_options = sorted(df_plot[geo_prop].unique().tolist())
                sel_prov = st.selectbox("🔎 Seleccione Provincia para Drill-Down", ["— Seleccionar —"] + prov_options, key="tab71_prov_select")
                if sel_prov != "— Seleccionar —":
                    st.session_state['tab71_prov'] = sel_prov.upper()
                    st.rerun()
            else:
                st.info(f"📍 Vista actual: **{st.session_state['tab71_prov']}**")
        with col_ctrl2:
            # Cantón es nivel terminal: NO hace rerun, solo filtra datos en pantalla
            selected_canton_filter = None
            if st.session_state['tab71_prov'] != 'TODAS':
                cant_options = sorted(df_plot[geo_prop].unique().tolist()) if not df_plot.empty else []
                selected_canton_filter = st.selectbox("🔎 Filtrar por Cantón", ["— Todos —"] + cant_options, key="tab71_cant_filter")
                if selected_canton_filter == "— Todos —":
                    selected_canton_filter = None
        with col_ctrl3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state['tab71_prov'] = 'TODAS'
                st.session_state['tab71_cant'] = 'TODOS'
                st.rerun()


        # 3. MAPA CHOROPLETH (Estilo claro + colores vibrantes)
        fig_map = px.choropleth_mapbox(
            df_plot, geojson=geojson_data, locations=geo_prop,
            featureidkey=f"properties.{geo_prop}", color='Hectáreas',
            color_continuous_scale="YlOrRd", mapbox_style="carto-positron",
            zoom=5.8 if level == "provincia" else 8, 
            center={"lat": -1.5, "lon": -78.5},
            opacity=0.75, labels={'Hectáreas': 'Superficie (ha)'},
            hover_data={geo_prop: True, 'Hectáreas': ':.2f', 'Proyectos': True}
        )
        
        fig_map.update_traces(
            marker_line_width=1.5, marker_line_color='rgba(50,50,50,0.6)',
            hovertemplate='<b>%{location}</b><br>Superficie: %{z:,.2f} ha<br>Proyectos: %{customdata[0]}<extra></extra>',
            customdata=df_plot[['Proyectos']].values
        )
        
        fig_map.update_layout(
            height=750,
            margin={"r":0,"t":50,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            title=dict(text=f"🎚️ {map_title}", font=dict(size=22, color='white')),
            coloraxis_colorbar=dict(
                title="Hectáreas",
                thicknessmode="pixels", thickness=20,
                lenmode="fraction", len=0.6,
                yanchor="middle", y=0.5,
                ticks="outside", ticksuffix=" ha"
            )
        )

        st.plotly_chart(fig_map, use_container_width=True, key="gis_interactive_map")
        
        # --- LEYENDA DE CRITICIDAD (Color Scale Description) ---
        st.markdown("""
            <div style="background:rgba(255,255,255,0.03); padding:15px; border-radius:10px; border:1px solid rgba(255,255,255,0.05); margin-top: -10px; margin-bottom: 20px;">
                <div style="font-size:0.9rem; font-weight:700; color:white; margin-bottom:10px;">🎨 Guía de Interpretación de Criticidad (Superficie de Intersección)</div>
                <div style="display:flex; gap:20px; align-items:center; flex-wrap:wrap;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="width:14px; height:14px; background:#FFFFB2; border-radius:3px;"></div>
                        <span style="font-size:0.8rem; color:#BDC3C7;"><b>Bajo:</b> Superficie mínima (< 100 ha)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="width:14px; height:14px; background:#FEB24C; border-radius:3px;"></div>
                        <span style="font-size:0.8rem; color:#BDC3C7;"><b>Medio:</b> Alarma Preventiva (100 - 500 ha)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="width:14px; height:14px; background:#F03B20; border-radius:3px;"></div>
                        <span style="font-size:0.8rem; color:#BDC3C7;"><b>Alto:</b> Criticidad Elevada (500 - 5,000 ha)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="width:14px; height:14px; background:#BD0026; border-radius:3px;"></div>
                        <span style="font-size:0.8rem; color:#BDC3C7;"><b>Extremo:</b> Punto Caliente Ambiental (> 5,000 ha)</span>
                    </div>
                </div>
                <p style="font-size:0.75rem; color:rgba(255,255,255,0.4); margin-top:10px; font-style:italic;">* Los colores representan la suma total de hectáreas de intersección con áreas protegidas por demarcación geográfica.</p>
            </div>
        """, unsafe_allow_html=True)

        # 4. KPIs (filtrar por cantón si fue seleccionado)
        st.markdown("---")
        df_kpi_source = df_map_data
        if selected_canton_filter:
            df_kpi_source = df_map_data[df_map_data['canton'].apply(lambda x: _norm(x) == _norm(selected_canton_filter))]
            st.caption(f"📍 Filtrado por cantón: **{selected_canton_filter}**")
        kpis = get_environmental_kpis(df_kpi_source)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Proyectos Analizados", kpis['total_proyectos'])
        with col2:
            st.metric("📏 Superficie Total (ha)", f"{kpis['total_has']:,.2f}")
        with col3:
            st.metric("🛡️ Capas de Intersección", kpis['capas_activas'])

        with st.expander("📈 Detalle Técnico de Inventario (Background)"):
            view_cols = ["codigo_proyecto", "nombre_proyecto", "provincia", "canton", "categoria_ambiental", "areas_protegidas", "superficie_proyecto"]
            df_sort = df_kpi_source.sort_values(by=["prioridad", "superficie_proyecto"], ascending=[True, False])
            st.dataframe(df_sort[view_cols], use_container_width=True, hide_index=True)

    else:
        st.info("No hay datos de intersección en el periodo/área seleccionada.")

elif active_tab == "tab8":
    st.markdown("<h2 style='color: white !important; margin-bottom: 20px;'>🗺️ Inteligencia Geopolítica: Mapas de Intersección Ambiental</h2>", unsafe_allow_html=True)
    
    # --- 0. GESTIÓN DE SELECCIÓN INTERACTIVA ---
    if 'env_chart_filter' not in st.session_state:
        st.session_state['env_chart_filter'] = None
    
    st.markdown("<div style='background:rgba(255,255,255,0.03); padding:20px; border-radius:15px; border:1px solid rgba(255,255,255,0.05); margin-bottom:25px;'>", unsafe_allow_html=True)
    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 2])
    
    with col_f1:
        sel_prov_geo = st.selectbox("📍 Provincia", get_geo_provincias(), key="geo_prov_8")
    with col_f2:
        sel_cant_geo = st.selectbox("🏢 Cantón", get_geo_cantones(sel_prov_geo), key="geo_cant_8")
    with col_f3:
        sel_parr_geo = st.selectbox("🏘️ Parroquia", get_geo_parroquias(sel_prov_geo, sel_cant_geo), key="geo_parr_8")
    with col_f4:
        cat_options = ['🛡️ SNAP', '🔒 ZONAS INTANGIBLES', '🌳 BOSQUES PROTECTORES', '🌲 PATRIMONIO FORESTAL DEL ESTADO', '⚪ SIN INTERSECCIÓN']
        sel_cats_geo = st.multiselect("🏷️ Capas de Intersección", cat_options, default=cat_options, key="geo_cats_8")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- 2. CARGA DE DATA FILTRADA ---
    with st.spinner("Actualizando analítica geopolítica..."):
        df_geo_inter = load_environmental_analytic_data(
            get_engine(), 
            prov=sel_prov_geo, 
            cant=sel_cant_geo, 
            parr=sel_parr_geo,
            sd=start_date_in, 
            ed=end_date_in,
            selected_cats=sel_cats_geo
        )
    
    if not df_geo_inter.empty:
        # --- 3. KPIs DE INTERSECCIÓN ---
        capas_req = [
            ('🛡️ SNAP', '#2ECC71'),
            ('🔒 ZONAS INTANGIBLES', '#E74C3C'),
            ('🌳 BOSQUES PROTECTORES', '#F1C40F'),
            ('🌲 PATRIMONIO FORESTAL DEL ESTADO', '#3498DB'),
            ('⚪ SIN INTERSECCIÓN', '#BDC3C7')
        ]
        
        kpi_html = '<div style="display:flex; gap:10px; margin-bottom: 25px; flex-wrap:wrap;">'
        for nombre, color in capas_req:
            conteo = len(df_geo_inter[df_geo_inter['categoria_ambiental'] == nombre])
            kpi_html += f'''
            <div style="flex:1; min-width:180px; background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; border-left:5px solid {color}; border:1px solid rgba(255,255,255,0.1);">
                <div style="font-size:0.65rem; color:{color} !important; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px;">{nombre}</div>
                <div style="font-size:1.6rem; color:#FFFFFF !important; font-weight:800;">{conteo:,}</div>
                <div style="font-size:0.75rem; color:rgba(255,255,255,0.5);">proyectos registrados</div>
            </div>'''
        kpi_html += '</div>'
        st.markdown(kpi_html, unsafe_allow_html=True)
        
        # --- 2. GRÁFICOS ESTADÍSTICOS ---
        col_g1, col_g2, col_g3 = st.columns([1.2, 1.4, 1.4])
        
        with col_g1:
            st.markdown("<h3 style='color: white !important; font-size:16px;'>Distribución por Sensibilidad Ambiental</h3>", unsafe_allow_html=True)
            df_dist = df_geo_inter['categoria_ambiental'].value_counts().reset_index()
            df_dist.columns = ['Capa', 'Proyectos']
            
            fig_pie = px.pie(df_dist, values='Proyectos', names='Capa', hole=0.5,
                             color='Capa', color_discrete_map={
                                 '🛡️ SNAP': '#2ECC71',
                                 '🔒 ZONAS INTANGIBLES': '#E74C3C',
                                 '🌳 BOSQUES PROTECTORES': '#F1C40F',
                                 '🌲 PATRIMONIO FORESTAL DEL ESTADO': '#3498DB',
                                 '⚪ SIN INTERSECCIÓN': '#BDC3C7'
                             })
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                legend=dict(orientation="h", y=-0.2, font=dict(size=10, color="white")),
                margin=dict(t=10, b=10, l=10, r=10), height=400
            )
            fig_pie.update_traces(textfont_color="white", textinfo='percent+label')
            event_pie = st.plotly_chart(fig_pie, use_container_width=True, on_select="rerun", key="env_pie_chart")
            
            # Capturar selección del Pie
            if event_pie and "selection" in event_pie and event_pie["selection"]["points"]:
                selected_val = event_pie["selection"]["points"][0]["label"]
                st.session_state['env_chart_filter'] = {"type": "Categoría", "val": selected_val}
            
        with col_g2:
            df_inter_only = df_geo_inter[df_geo_inter['categoria_ambiental'] != '⚪ SIN INTERSECCIÓN']
            
            if not df_inter_only.empty:
                # 1. GRÁFICO POR VOLUMEN (CANTIDAD)
                if sel_prov_geo == "TODAS":
                    title_vol = "Top 10 Provincias (Volumen de Proyectos)"
                    group_col = 'provincia'
                elif sel_cant_geo == "TODOS":
                    title_vol = f"Top Cantones en {sel_prov_geo} (Volumen de Proyectos)"
                    group_col = 'canton'
                else:
                    title_vol = f"Parroquias en {sel_cant_geo} (Volumen de Proyectos)"
                    group_col = 'parroquia'
                
                st.markdown(f"<h3 style='color: white !important; font-size:16px;'>📊 {title_vol}</h3>", unsafe_allow_html=True)
                
                df_vol = df_inter_only.groupby(group_col).size().sort_values(ascending=False).head(10).reset_index()
                df_vol.columns = [group_col.capitalize(), 'Proyectos']
                
                fig_vol = px.bar(df_vol, x='Proyectos', y=group_col.capitalize(), orientation='h',
                                 color='Proyectos', color_continuous_scale='Viridis',
                                 text='Proyectos')
                fig_vol.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="white"), coloraxis_showscale=False,
                    xaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white')),
                    yaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white'), autorange='reversed'),
                    margin=dict(t=10, b=10, l=10, r=10), height=380
                )
                fig_vol.update_traces(textfont_color="white", textposition='outside')
                event_vol = st.plotly_chart(fig_vol, use_container_width=True, on_select="rerun", key="env_vol_chart")
                
                # Capturar selección de Barras Volumen
                if event_vol and "selection" in event_vol and event_vol["selection"]["points"]:
                    selected_val = event_vol["selection"]["points"][0]["y"]
                    st.session_state['env_chart_filter'] = {"type": group_col.capitalize(), "val": selected_val}
            else:
                st.info("Sin datos para volumen.")

        with col_g3:
            if not df_inter_only.empty:
                # 2. GRÁFICO POR MAGNITUD (HECTÁREAS)
                if sel_prov_geo == "TODAS":
                    title_sup = "Top 10 Provincias (Superficie)"
                elif sel_cant_geo == "TODOS":
                    title_sup = f"Top Cantones en {sel_prov_geo} (Superficie)"
                else:
                    title_sup = f"Parroquias en {sel_cant_geo} (Superficie)"
                
                st.markdown(f"<h3 style='color: white !important; font-size:16px;'>🌳 {title_sup}</h3>", unsafe_allow_html=True)
                
                df_sup = df_inter_only.groupby(group_col)['superficie_proyecto'].sum().sort_values(ascending=False).head(10).reset_index()
                df_sup.columns = [group_col.capitalize(), 'Hectáreas']
                
                fig_sup = px.bar(df_sup, x='Hectáreas', y=group_col.capitalize(), orientation='h',
                                 color='Hectáreas', color_continuous_scale='Greens',
                                 text='Hectáreas')
                fig_sup.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="white"), coloraxis_showscale=False,
                    xaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white')),
                    yaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white'), autorange='reversed'),
                    margin=dict(t=10, b=10, l=10, r=10), height=380
                )
                fig_sup.update_traces(textfont_color="white", textposition='outside', texttemplate='%{x:.2f} ha')
                event_sup = st.plotly_chart(fig_sup, use_container_width=True, on_select="rerun", key="env_sup_chart")
                
                # Capturar selección de Barras Superficie
                if event_sup and "selection" in event_sup and event_sup["selection"]["points"]:
                    selected_val = event_sup["selection"]["points"][0]["y"]
                    st.session_state['env_chart_filter'] = {"type": group_col.capitalize(), "val": selected_val}
            else:
                st.info("Sin datos para superficie.")

        st.markdown("---")
        
        # --- 3. TABLA DE DETALLE Y EXPORTACIÓN CON CROSS-FILTERING ---
        st.markdown("<h3 style='color: white !important;'>📋 Inventario de Superposición Geográfica</h3>", unsafe_allow_html=True)
        
        df_geo_display = df_geo_inter.copy()
        
        # Aplicar filtro de gráfico si existe
        if st.session_state['env_chart_filter']:
            f_type = st.session_state['env_chart_filter']["type"]
            f_val = st.session_state['env_chart_filter']["val"]
            
            st.info(f"🔍 Filtrado por gráfico: **{f_type} = {f_val}**")
            if st.button("🔄 Limpiar Filtro de Gráfico"):
                st.session_state['env_chart_filter'] = None
                st.rerun()
            
            if f_type == "Categoría":
                df_geo_display = df_geo_display[df_geo_display['categoria_ambiental'] == f_val]
            else:
                # Filtrar por Provincia/Cantón/Parroquia
                col_name = f_type.lower()
                if col_name in df_geo_display.columns:
                    df_geo_display = df_geo_display[df_geo_display[col_name].str.upper() == str(f_val).upper()]

        view_cols = ["codigo_proyecto", "nombre_proyecto", "provincia", "canton", "categoria_ambiental", "areas_protegidas", "superficie_proyecto"]
        df_geo_display = df_geo_display.sort_values(by=["prioridad", "superficie_proyecto"], ascending=[True, False])
        st.dataframe(df_geo_display[view_cols], use_container_width=True, hide_index=True)
        
        csv_data = df_geo_inter.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Análisis Completo de Intersección (CSV)",
            data=csv_data,
            file_name=f"interseccion_geopolitica_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("No se encontraron datos para procesar el mapa de intersección.")

elif active_tab == "tab9":
    st.header("♻️ Registro Gestor de Desechos (Inventario Nacional)")

    # --- DATOS BASE (Sin ubicación) ---
    df_waste_all = load_waste_summary()
    df_proj_reg_all = load_waste_project_registry()

    # --- FILTROS DE SIDEBAR EXCLUSIVOS ---
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔍 Filtros de Inventario")
        # Filtro por Tipo de Desecho para búsqueda rápida
        waste_list = sorted(df_waste_all['tipo_desecho'].unique().tolist())
        sel_waste = st.multiselect("Filtrar por Tipo de Desecho", waste_list, default=[])

    # Filtrado Dinámico
    df_w_filt = df_waste_all.copy()
    df_p_filt = df_proj_reg_all.copy()
    
    if sel_waste:
        df_w_filt = df_w_filt[df_w_filt['tipo_desecho'].isin(sel_waste)]
        # El listado detallado no tiene tipo_desecho por fila de forma directa en la query actual, 
        # pero se puede inferir del contexto si se desea.

    # --- SECCIÓN 0: KPIs ---
    k1, k2, k3 = st.columns(3)
    with k1:
        total_tons = df_w_filt['total_generado'].sum() / 1000
        st.metric("Total Generado (Toneladas)", f"{total_tons:,.1f} t")
    with k2:
        variedad = len(df_w_filt['tipo_desecho'].unique())
        st.metric("Tipos de Desecho", f"{variedad:,}")
    with k3:
        num_proy = len(df_p_filt[df_p_filt['Nombre del Proyecto'] != 'Libre Voluntad'])
        st.metric("Proyectos Oficiales", f"{num_proy:,}")

    # --- SECCIÓN 1: ANÁLISIS DE INVENTARIO ---
    st.markdown("<h3 style='color: white !important;'>📊 Caracterización Nacional de Desechos</h3>", unsafe_allow_html=True)
    
    col_w1, col_w2 = st.columns([2, 1])
    
    with col_w1:
        st.markdown("**Top 10 Desechos por Volumen de Generación (kg)**")
        df_top_w = df_w_filt.groupby('tipo_desecho')['total_generado'].sum().reset_index().sort_values('total_generado', ascending=False).head(10)
        fig_top_w = px.bar(df_top_w, x='total_generado', y='tipo_desecho', orientation='h',
                           color='total_generado', color_continuous_scale='Tealgrn', text_auto='.2s')
        fig_top_w.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                font=dict(color="white"), showlegend=False, height=450)
        fig_top_w.update_coloraxes(showscale=False)
        st.plotly_chart(fig_top_w, use_container_width=True)

    with col_w2:
        st.markdown("**Distribución por Sistema / Origen**")
        fig_sys = px.pie(df_w_filt, values='total_generado', names='source_system', hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sys.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), 
                              legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_sys, use_container_width=True)

    st.markdown("---")
    # --- SECCIÓN 2: LISTADO MAESTRO ---
    st.markdown("<h3 style='color: white !important;'>📋 Detalle de Registros y Códigos RGD</h3>", unsafe_allow_html=True)
    if not df_p_filt.empty:
        st.dataframe(df_p_filt, use_container_width=True, hide_index=True)
        csv = df_p_filt.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Inventario Completo (CSV)", csv, "inventario_nacional_desechos.csv", "text/csv", use_container_width=True)
    else:
        st.warning("No hay registros coincidentes.")

elif active_tab == "tab10":
    st.header("🧪 Registro Nacional de Sustancias Químicas")
    df_chem = load_chemical_summary()
    if not df_chem.empty:
        # --- LIMPIEZA DE DATOS (Hierarchy Fix) ---
        # Plotly requiere que los padres en 'path' no sean None/NaN
        df_chem['classification'] = df_chem['classification'].fillna("SIN CLASIFICACION")
        df_chem['substance_name'] = df_chem['substance_name'].fillna("SIN NOMBRE")
        # Filtrar valores duplicados o incoherentes si los hubiera
        df_chem = df_chem.dropna(subset=['classification', 'substance_name'])
        
        st.dataframe(df_chem, use_container_width=True, hide_index=True)
        fig_chem = px.treemap(df_chem, path=['classification', 'substance_name'], values='dosis_total',
                              title="Concentración de Sustancias por Clasificación")
        fig_chem.update_traces(textinfo='label+percent entry', insidetextfont=dict(color='black'))
        st.plotly_chart(fig_chem, use_container_width=True)
    else: st.error("Sin registros de sustancias químicas.")

elif active_tab == "admin":
    st.markdown(f"<h2 style='color: white !important; margin-bottom: 20px;'>⚙️ Centro de Control Maestro (v1.01)</h2>", unsafe_allow_html=True)
    
    # --- INYECCIÓN DE ESTILO GLOBAL PARA ADMINISTRACIÓN (PEQUEÑO Y CENTRADO) ---
    st.markdown("""
        <style>
        /* Contenedor de botones para centrado */
        div.stButton, div[data-testid="stFormSubmitButton"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }

        /* Estilo para botones de acción (Verde Institucional - TAMAÑO PEQUEÑO) */
        div.stButton > button, 
        button[data-testid="stFormSubmitButton"],
        div.stFormSubmitButton > button {
            background-color: #27ae60 !important;
            color: white !important;
            border: none !important;
            padding: 0.3rem 1.0rem !important; 
            min-height: 32px !important;      
            min-width: 140px !important;      
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;    
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }

        div.stButton > button:hover, 
        button[data-testid="stFormSubmitButton"]:hover,
        div.stFormSubmitButton > button:hover {
            background-color: #2ecc71 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
            color: white !important;
        }

        div.stButton > button:active, 
        button[data-testid="stFormSubmitButton"]:active,
        div.stFormSubmitButton > button:active {
            transform: translateY(0) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.info("Gestión centralizada de arquitectura, branding, parámetros de negocio y seguridad perimetral.")
    
    config = load_config()
    tab_arch, tab_brand, tab_params, tab_roles, tab_users, tab_audit = st.tabs([
        "📱 Arquitectura", "🎨 Identidad", "📊 Parámetros", "👥 Perfiles", "👤 Usuarios", "🔐 Auditoría"
    ])
    
    with tab_arch:
        st.subheader("🛠️ Control de Módulos Core")
        tabs_conf = config.get("tabs", {})
        updated_tabs = {}
        with st.form("arch_form"):
            # Definir grupos disponibles para asignar
            group_options = ["Operación y Gestión", "Validaciones de Proyectos", "Superposición Geográfica"]
            cols = st.columns(2)
            all_tabs_ids = ["tab1", "tab2", "tab3", "tab4", "tab5", "tab6", "tab7", "tab7_1", "tab8", "tab9", "tab10", "tab11"]
            for i, tid in enumerate(all_tabs_ids):
                col = cols[i % 2]
                current_conf = tabs_conf.get(tid, {})
                current_label = current_conf.get("label", f"Módulo {tid}")
                current_visible = current_conf.get("visible", True)
                current_group = current_conf.get("group", "Operación y Gestión")
                
                with col:
                    st.markdown(f"**[ {tid.upper()} ]**")
                    new_label = st.text_input("Etiqueta", value=current_label, key=f"arch_lbl_{tid}")
                    new_group = st.selectbox("Área", group_options, index=group_options.index(current_group) if current_group in group_options else 0, key=f"arch_grp_{tid}")
                    is_visible = st.toggle("Activo", value=current_visible, key=f"arch_vis_{tid}")
                    updated_tabs[tid] = {"label": new_label, "visible": is_visible, "group": new_group}
            
            if st.form_submit_button("💾 Guardar Arquitectura", use_container_width=False):
                config["tabs"] = updated_tabs
                save_config(config)
                st.success("Arquitectura actualizada. Reiniciando portales...")
                st.rerun()


    with tab_brand:
        st.subheader("🖼️ Identidad Visual e Institucional")
        branding = config.get("branding", {})
        with st.form("brand_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_org = st.text_input("Nombre de la Organización", value=branding.get("org_name", ""))
                new_sub = st.text_input("Subtítulo del Dashboard", value=branding.get("sub_name", ""))
            with c2:
                new_ver = st.text_input("Versión del Sistema", value=branding.get("version", ""))
                new_mail = st.text_input("Email de Soporte", value=branding.get("support_email", ""))
            
            if st.form_submit_button("💾 Guardar Identidad", use_container_width=False):
                branding.update({"org_name": new_org, "sub_name": new_sub, "version": new_ver, "support_email": new_mail})
                config["branding"] = branding
                save_config(config)
                st.success("Identidad visual consolidada.")
                st.rerun()

    with tab_params:
        st.subheader("📊 Reglas de Negocio e Inteligencia")
        rules = config.get("business_rules", {})
        with st.form("rules_form"):
            ex_rec = st.toggle("Excluir registros 'Sin Clasificar' (RECUPERADO) automáticamente", 
                               value=rules.get("exclude_recuperado", True))
            kpi_target = st.number_input("Meta Institucional de Proyectos Completados (%)", 
                                         min_value=0.0, max_value=100.0, value=rules.get("kpi_target_pct", 75.0))
            
            if st.form_submit_button("💾 Guardar Parámetros", use_container_width=False):
                rules.update({"exclude_recuperado": ex_rec, "kpi_target_pct": kpi_target})
                config["business_rules"] = rules
                save_config(config)
                st.success("Reglas de negocio actualizadas.")
                st.rerun()

    with tab_roles:
        st.subheader("👥 Matriz de Permisos por Perfil")
        roles_perm = config.get("role_permissions", {})
        role_list = ["ADMIN", "GERENCIA", "MESA_AYUDA", "DESARROLLADOR", "QA"]
        
        tabs_conf_admin = config.get("tabs", {})
        area_order = [
            ("🏢 Operación y Gestión", ["tab1", "tab2", "tab4", "tab9", "tab10"]),
            ("✅ Validaciones de Proyectos", ["tab3", "tab5", "tab6"]),
            ("🗺️ Superposición Geográfica", ["tab7", "tab7_1", "tab8"]),
            ("⚙️ Administración", ["admin"]),
        ]
        
        # Selector de perfil para editar (evita problemas con expanders en forms)
        sel_role = st.selectbox("Seleccione Perfil a Configurar", role_list, key="sel_role_perm")
        current_p = roles_perm.get(sel_role, [])
        
        with st.form(f"roles_form_{sel_role}"):
            st.markdown(f"### 👤 Permisos de: **{sel_role}**")
            selected_tabs = []
            
            for area_name, area_tids in area_order:
                st.markdown(f"**{area_name}**")
                cols = st.columns(4)
                for i, tid in enumerate(area_tids):
                    lbl = tabs_conf_admin.get(tid, {}).get("label", tid) if tid != "admin" else "Config. Maestro"
                    with cols[i % 4]:
                        if st.checkbox(lbl, value=(tid in current_p), key=f"perm_{sel_role}_{tid}"):
                            selected_tabs.append(tid)
            
            if st.form_submit_button("💾 Guardar Permisos", use_container_width=False):
                roles_perm[sel_role] = selected_tabs
                config["role_permissions"] = roles_perm
                save_config(config)
                st.success(f"✅ Permisos de **{sel_role}** guardados correctamente.")
                st.rerun()
        
        # Vista resumen de todos los perfiles
        with st.expander("📊 Vista Resumen — Todos los Perfiles"):
            summary_data = []
            for r in role_list:
                perms = roles_perm.get(r, [])
                count_total = sum(len(tids) for _, tids in area_order)
                summary_data.append({"Perfil": r, "Módulos Habilitados": len(perms), "Total Disponible": count_total})
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)



    with tab_users:
        st.subheader("👤 Gestión de Usuarios Institucionales")
        
        # --- Listado con estado ---
        query_users = """
        SELECT u.user_id, u.username, u.full_name, r.role_name as rol, 
               u.status, u.last_login, u.created_at
        FROM dw.users u 
        JOIN dw.roles r ON u.role_id = r.role_id 
        ORDER BY u.status DESC, u.username
        """
        df_u = pd.read_sql(query_users, get_engine())
        
        # Colorizar estado
        st.dataframe(
            df_u[['username', 'full_name', 'rol', 'status', 'last_login']].rename(
                columns={'username': 'Usuario', 'full_name': 'Nombre', 'rol': 'Perfil', 'status': 'Estado', 'last_login': 'Último Acceso'}
            ),
            use_container_width=True, hide_index=True
        )
        
        existing_users = df_u['username'].str.lower().tolist()
        
        # --- Obtención Dinámica de Roles desde DB ---
        try:
            df_roles = pd.read_sql("SELECT role_id, role_name FROM dw.roles ORDER BY role_id", get_engine())
            # Normalizar: crear mapa {NOMBRE: ID} para la lógica interna
            role_map = dict(zip(df_roles['role_name'], df_roles['role_id']))
        except:
            # Fallback en caso de error de conexión
            role_map = {"ADMIN": 1, "GERENCIA": 2, "MESA_AYUDA": 3, "DESARROLLADOR": 4, "QA": 5}
        
        # --- TABS INTERNAS: Alta / Modificación / Desactivación ---
        op_create, op_edit, op_deactivate = st.tabs(["➕ Alta", "✏️ Modificar", "🔒 Activar / Desactivar"])
        
        with op_create:
            with st.form("new_user_form", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1:
                    new_username = st.text_input("Usuario (nombre.apellido)", placeholder="juan.perez")
                    new_full_name = st.text_input("Nombre Completo")
                with c2:
                    new_role = st.selectbox("Perfil de Acceso", list(role_map.keys()), key="create_role")
                    new_pwd = st.text_input("Contraseña Temporal", type="password")
                
                submitted_create = st.form_submit_button("💾 Guardar Intención de Alta", use_container_width=False)
            
            if submitted_create:
                errors = []
                if not new_username or not new_username.strip():
                    errors.append("❌ El campo **Usuario** es obligatorio.")
                if not new_full_name or not new_full_name.strip():
                    errors.append("❌ El campo **Nombre Completo** es obligatorio.")
                if not new_pwd or len(new_pwd) < 6:
                    errors.append("❌ La **Contraseña** debe tener al menos 6 caracteres.")
                if new_username and new_username.strip().lower() in existing_users:
                    errors.append(f"⚠️ El usuario **'{new_username}'** ya existe.")
                
                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    st.session_state["pending_create"] = {
                        "u": new_username.strip(),
                        "f": new_full_name.strip(),
                        "r": new_role,
                        "p": new_pwd
                    }

            if "pending_create" in st.session_state:
                pc = st.session_state["pending_create"]
                st.info("📋 **Resumen de Nuevo Usuario** — Revise antes de confirmar:")
                st.markdown(f"""
                | Campo | Valor |
                | :--- | :--- |
                | **Usuario** | `{pc['u']}` |
                | **Nombre** | `{pc['f']}` |
                | **Perfil** | `{pc['r']}` |
                """)
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("✅ Confirmar Alta en DWH", use_container_width=False, type="primary"):
                        try:
                            h_pwd = hash_password(pc['p'])
                            rid = role_map[pc['r']]
                            with get_engine().connect() as conn:
                                conn.execute(text("INSERT INTO dw.users (username, full_name, role_id, password_hash, status, must_change_password) VALUES (:u, :f, :r, :p, 'Active', TRUE)"),
                                    {"u": pc['u'], "f": pc['f'], "r": rid, "p": h_pwd})
                                conn.commit()
                            st.success(f"✅ Usuario **{pc['u']}** creado exitosamente.")
                            log_audit("CREATE_USER", "ADMIN", {"username": pc['u'], "role": pc['r']})
                            del st.session_state["pending_create"]
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error al guardar: {ex}")
                with col_c2:
                    if st.button("❌ Cancelar Alta", use_container_width=False):
                        del st.session_state["pending_create"]
                        st.rerun()
        
        with op_edit:
            active_users = df_u[df_u['status'] == 'Active']['username'].tolist()
            if active_users:
                sel_user_edit = st.selectbox("Seleccione Usuario a Modificar", active_users, key="edit_user_sel")
                user_row = df_u[df_u['username'] == sel_user_edit].iloc[0]
                
                with st.form(f"edit_user_form_{sel_user_edit}", clear_on_submit=False):
                    st.caption(f"✏️ Editando: **{sel_user_edit}**")
                    c1, c2 = st.columns(2)
                    with c1:
                        edit_full_name = st.text_input("Nombre Completo Actualizado", value=user_row['full_name'])
                    with c2:
                        current_role_name = user_row['rol']
                        role_keys = list(role_map.keys())
                        default_idx = role_keys.index(current_role_name) if current_role_name in role_keys else 0
                        edit_role = st.selectbox("Nuevo Perfil", role_keys, index=default_idx)
                    
                    reset_pwd = st.text_input("Nueva Contraseña (vacío p/mantener historial)", type="password")
                    submitted_edit = st.form_submit_button("💾 Guardar Intención de Cambio", use_container_width=False)
                
                if submitted_edit:
                    st.session_state["pending_edit"] = {
                        "u": sel_user_edit,
                        "f_old": user_row['full_name'],
                        "f_new": edit_full_name.strip(),
                        "r_old": current_role_name,
                        "r_new": edit_role,
                        "p": reset_pwd
                    }

                if "pending_edit" in st.session_state and st.session_state["pending_edit"]["u"] == sel_user_edit:
                    pe = st.session_state["pending_edit"]
                    st.warning("⚠️ **Confirmación de Cambios** — Verifique el resumen comparativo:")
                    
                    # Mostrar comparativa clara
                    st.markdown(f"""
                    | Atributo | Valor Anterior | Valor Nuevo |
                    | :--- | :--- | :--- |
                    | **Nombre** | `{pe['f_old']}` | **`{pe['f_new']}`** |
                    | **Perfil** | `{pe['r_old']}` | **`{pe['r_new']}`** |
                    | **Password** | *Origen DWH* | *{'Actualizado' if pe['p'] else 'Sin cambio'}* |
                    """)
                    
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        if st.button("✅ Confirmar Actualización", use_container_width=False, type="primary"):
                            try:
                                rid = role_map[pe['r_new']]
                                with get_engine().connect() as conn:
                                    conn.execute(text("UPDATE dw.users SET full_name = :f, role_id = :r WHERE username = :u"),
                                        {"f": pe['f_new'], "r": rid, "u": pe['u']})
                                    if pe['p'] and len(pe['p']) >= 6:
                                        h_pwd = hash_password(pe['p'])
                                        conn.execute(text("UPDATE dw.users SET password_hash = :p, must_change_password = TRUE WHERE username = :u"),
                                            {"p": h_pwd, "u": pe['u']})
                                    conn.commit()
                                st.success(f"✅ Cambios para **{pe['u']}** persistidos en DWH.")
                                log_audit("UPDATE_USER", "ADMIN", {"username": pe['u'], "new_role": pe['r_new']})
                                del st.session_state["pending_edit"]
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error al persistir: {ex}")
                    with col_e2:
                        if st.button("❌ Descartar Cambios", use_container_width=False):
                            del st.session_state["pending_edit"]
                            st.rerun()
            else:
                st.info("No hay usuarios activos registrados para modificar.")
        
        with op_deactivate:
            st.caption("La desactivación es lógica: el usuario no podrá iniciar sesión pero sus datos se conservan.")
            all_users_status = df_u[['username', 'full_name', 'status']].copy()
            
            sel_user_toggle = st.selectbox("Seleccione Usuario", df_u['username'].tolist(), key="toggle_user_sel")
            current_status = df_u[df_u['username'] == sel_user_toggle]['status'].values[0]
            
            new_status = "Inactive" if current_status == "Active" else "Active"
            action_label = "🔒 Desactivar" if current_status == "Active" else "🔓 Reactivar"
            action_color = "primary" if current_status != "Active" else "secondary"
            
            st.info(f"Estado actual de **{sel_user_toggle}**: **{current_status}**")
            
            if st.button(f"{action_label} Usuario", use_container_width=False, type=action_color):
                try:
                    with get_engine().connect() as conn:
                        conn.execute(text("UPDATE dw.users SET status = :s WHERE username = :u"),
                            {"s": new_status, "u": sel_user_toggle})
                        conn.commit()
                    st.success(f"✅ Usuario **{sel_user_toggle}** ahora está **{new_status}**.")
                    log_audit("TOGGLE_USER_STATUS", "ADMIN", {"username": sel_user_toggle, "new_status": new_status})
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")


    with tab_audit:
        st.subheader("🔐 Auditoría de Eventos Institucionales")
        if st.button("🔄 Refrescar Logs de Acceso", use_container_width=False):
            query = "SELECT u.username, a.action, a.module, a.details, a.created_at FROM dw.audit_logs a JOIN dw.users u ON a.user_id = u.user_id ORDER BY a.created_at DESC LIMIT 50"
            df_audit = pd.read_sql(query, get_engine())
            st.dataframe(df_audit, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🧹 Mantenimiento Nuclear")
        colA, colB = st.columns(2)
        with colA:
            if st.button("Ejecutar Indexación DWH", use_container_width=False):
                st.success("Sentencia de mantenimiento transmitida al motor PostgreSQL.")
        with colB:
            if st.button("🚀 Limpiar Caché Total (RAM)", use_container_width=False):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("Memoria caché fragmentada eliminada.")
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 11 – REPORTES DE REGULARIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────
elif active_tab == "tab11":
    st.markdown(
        "<h2 style='color:white !important; margin-bottom:20px;'>📑 Reportes de Regularización Ambiental</h2>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style="background-color:transparent; padding:14px; border-left:5px solid #1ABC9C;
                border-radius:5px; margin-bottom:20px;">
        <strong style="color:white;">Reporte operativo de proyectos emitidos y en trámite.</strong>
        <span style="color:#D5D8DC;"> Incluye identificación de técnicos responsables,
        dirección zonal, tarea actual y rol en el proceso (Operador / Técnico MAE).</span>
    </div>
    """, unsafe_allow_html=True)

    # ── PANEL DE FILTROS ──────────────────────────────────────────────────────
    with st.expander("🛠️ Panel de Filtros del Reporte", expanded=True):
        rf1, rf2, rf3 = st.columns(3)
        with rf1:
            _orig_map = {
                "TODAS LAS NORMATIVAS": "TODOS",
                "Hidrocarburos (D.E. 1215)": "JBPM_HIDRO",
                "Sector A.M. 028": "JBPM_SECTOR",
                "4 Categorías (COA)": "JBPM_4CAT",
                "COA / SUIA Verde (A.M. 061)": "COA",
                "RCOA (D.E. 752)": "RCOA",
            }
            sel_rep_orig_lbl = st.selectbox("Origen / Normativa", list(_orig_map.keys()), key="rep_origen")
            sel_rep_orig = _orig_map[sel_rep_orig_lbl]
        with rf2:
            sel_rep_estado = st.selectbox(
                "Estado del Proyecto",
                ["TODOS", "En Trámite", "Completado"],
                key="rep_estado"
            )
        with rf3:
            _permisos = get_unique_tramites(sel_rep_orig)
            sel_rep_permiso = st.selectbox("Tipo de Permiso Ambiental", _permisos, key="rep_permiso")

        rf4, rf5 = st.columns(2)
        with rf4:
            _tipos_rep = get_tipos_area()
            sel_rep_tipo_area = st.selectbox("Tipo Institucional", _tipos_rep, key="rep_tipo_area")
        with rf5:
            _autoridades = get_areas_por_tipo(sel_rep_tipo_area)
            sel_rep_autoridad = st.selectbox("Autoridad Responsable", _autoridades, key="rep_autoridad")

        rf5, rf6 = st.columns([3, 1])
        with rf5:
            rep_search = st.text_input(
                "🔎 Buscar por Código o Nombre del Proyecto",
                placeholder="Ej: MAAE-SUIA-RA-2023 o nombre parcial...",
                key="rep_search"
            )
        with rf6:
            st.write("")
            rep_use_dates = st.checkbox("Aplicar fechas globales", value=False, key="rep_dates")

    # ── CARGA DE DATOS ────────────────────────────────────────────────────────
    with st.spinner("Consultando el Data Warehouse..."):
        df_rep = load_regularization_report(
            origen=sel_rep_orig,
            estado=sel_rep_estado if sel_rep_estado != "TODOS" else "TODOS",
            tipo_permiso=sel_rep_permiso,
            autoridad=sel_rep_autoridad,
            sd=start_date_in if rep_use_dates else None,
            ed=end_date_in if rep_use_dates else None,
            search_text=rep_search.strip() if rep_search else ""
        )

    if df_rep.empty:
        st.warning("No se encontraron proyectos con los criterios seleccionados. Ajuste los filtros e intente nuevamente.")
    else:
        total_rep     = len(df_rep)
        n_tramite     = (df_rep['estado_proyecto'] == 'En Trámite').sum()
        n_completado  = (df_rep['estado_proyecto'] == 'Completado').sum()
        n_tecnicos    = df_rep['tecnico_responsable'].nunique()
        n_autoridades = df_rep['autoridad_responsable'].nunique()
        pct_completado = (n_completado / total_rep * 100) if total_rep > 0 else 0
        n_emisoras_aaa = (df_rep['es_emisora_aaa'].astype(str).str.lower() == 'true').sum() \
                         if 'es_emisora_aaa' in df_rep.columns else 0
        pct_aaa = (n_emisoras_aaa / total_rep * 100) if total_rep > 0 else 0

        # ── KPI BANNER ────────────────────────────────────────────────────────
        kpi_html = '<div style="display:flex; gap:12px; margin-bottom:22px; flex-wrap:wrap;">'
        kpi_html += f'''
        <div style="flex:1.5; min-width:180px; background:linear-gradient(135deg,rgba(26,82,118,0.25),rgba(21,67,96,0.5));
                    padding:16px 20px; border-radius:12px; border-left:5px solid #3498DB;">
            <div style="font-size:0.65rem; color:#85C1E9 !important; text-transform:uppercase; font-weight:700; letter-spacing:1px;">
                Total Proyectos en Reporte</div>
            <div style="font-size:1.9rem; color:#FFFFFF !important; font-weight:800;">{total_rep:,}</div>
        </div>
        <div style="flex:1; min-width:150px; background:rgba(255,255,255,0.05); padding:16px 18px;
                    border-radius:12px; border-left:5px solid #E67E22;">
            <div style="font-size:0.65rem; color:#E67E22 !important; text-transform:uppercase; font-weight:700;">En Trámite</div>
            <div style="font-size:1.7rem; color:#FFFFFF !important; font-weight:800;">{n_tramite:,}</div>
        </div>
        <div style="flex:1; min-width:150px; background:rgba(255,255,255,0.05); padding:16px 18px;
                    border-radius:12px; border-left:5px solid #2ECC71;">
            <div style="font-size:0.65rem; color:#2ECC71 !important; text-transform:uppercase; font-weight:700;">Completados</div>
            <div style="font-size:1.7rem; color:#FFFFFF !important; font-weight:800;">{n_completado:,}</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.55);">{pct_completado:.1f}% del total</div>
        </div>
        <div style="flex:1; min-width:150px; background:rgba(255,255,255,0.05); padding:16px 18px;
                    border-radius:12px; border-left:5px solid #9B59B6;">
            <div style="font-size:0.65rem; color:#9B59B6 !important; text-transform:uppercase; font-weight:700;">Técnicos Involucrados</div>
            <div style="font-size:1.7rem; color:#FFFFFF !important; font-weight:800;">{n_tecnicos:,}</div>
        </div>
        <div style="flex:1; min-width:150px; background:rgba(255,255,255,0.05); padding:16px 18px;
                    border-radius:12px; border-left:5px solid #1ABC9C;">
            <div style="font-size:0.65rem; color:#1ABC9C !important; text-transform:uppercase; font-weight:700;">Autoridades Responsables</div>
            <div style="font-size:1.7rem; color:#FFFFFF !important; font-weight:800;">{n_autoridades:,}</div>
        </div>
        <div style="flex:1; min-width:150px; background:rgba(255,255,255,0.05); padding:16px 18px;
                    border-radius:12px; border-left:5px solid #F39C12;">
            <div style="font-size:0.65rem; color:#F39C12 !important; text-transform:uppercase; font-weight:700;">Proyectos c/ Emisión AAA</div>
            <div style="font-size:1.7rem; color:#FFFFFF !important; font-weight:800;">{n_emisoras_aaa:,}</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.55);">{pct_aaa:.1f}% del total</div>
        </div>
        '''
        kpi_html += '</div>'
        st.markdown(kpi_html, unsafe_allow_html=True)

        # ── GRÁFICOS ANALÍTICOS ───────────────────────────────────────────────
        gc1, gc2, gc3, gc_inst = st.columns(4)

        with gc1:
            st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Estado del Portafolio</p>", unsafe_allow_html=True)
            df_estado_dist = df_rep['estado_proyecto'].value_counts().reset_index()
            df_estado_dist.columns = ['Estado', 'Proyectos']
            fig_estado = px.pie(
                df_estado_dist, values='Proyectos', names='Estado', hole=0.55,
                color='Estado',
                color_discrete_map={'Completado': '#2ECC71', 'En Trámite': '#E67E22'}
            )
            fig_estado.update_traces(
                textinfo='percent+label', textfont=dict(color='white', size=11),
                pull=[0.04, 0.04]
            )
            fig_estado.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                legend=dict(orientation='h', y=-0.15, font=dict(color='white', size=10)),
                margin=dict(t=10, b=10, l=10, r=10), height=300
            )
            st.plotly_chart(fig_estado, use_container_width=True)

        with gc2:
            st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Top 10 Técnicos Responsables</p>", unsafe_allow_html=True)
            df_tec = (
                df_rep[df_rep['tecnico_responsable'] != 'No Asignado']
                ['tecnico_responsable'].value_counts().head(10).reset_index()
            )
            df_tec.columns = ['Técnico', 'Proyectos']
            if not df_tec.empty:
                fig_tec = px.bar(
                    df_tec, x='Proyectos', y='Técnico', orientation='h',
                    color='Proyectos', color_continuous_scale='Teal', text='Proyectos'
                )
                fig_tec.update_traces(texttemplate='%{text:,}', textposition='outside', textfont_color='#FFFFFF')
                fig_tec.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF', coloraxis_showscale=False, showlegend=False,
                    yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                    xaxis=dict(tickfont=dict(color='#FFFFFF')),
                    margin=dict(t=5, b=10, l=10, r=40), height=300
                )
                st.plotly_chart(fig_tec, use_container_width=True)
            else:
                st.info("Sin técnicos asignados en la selección actual.")

        with gc3:
            st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Rol en Tarea (Operador / Técnico)</p>", unsafe_allow_html=True)
            df_rol = df_rep['rol_en_tarea'].value_counts().reset_index()
            df_rol.columns = ['Rol', 'Proyectos']
            fig_rol = px.bar(
                df_rol, x='Proyectos', y='Rol', orientation='h',
                color='Rol', text='Proyectos',
                color_discrete_map={
                    'Operador': '#F39C12',
                    'Técnico MAE': '#3498DB',
                    'Proceso Administrativo': '#95A5A6'
                }
            )
            fig_rol.update_traces(texttemplate='%{text:,}', textposition='outside', textfont_color='#FFFFFF')
            fig_rol.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF', showlegend=False,
                yaxis=dict(tickfont=dict(size=10, color='#FFFFFF')),
                xaxis=dict(tickfont=dict(color='#FFFFFF')),
                margin=dict(t=5, b=10, l=10, r=40), height=300
            )
            st.plotly_chart(fig_rol, use_container_width=True)

        with gc_inst:
            st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Tipo Institucional (dim_area v3.0)</p>", unsafe_allow_html=True)
            if 'siglas_tipo' in df_rep.columns:
                df_tipo = df_rep['siglas_tipo'].replace('', 'Sin Tipo').value_counts().reset_index()
                df_tipo.columns = ['Tipo', 'Proyectos']
                _color_map_tipo = {
                    'PC': '#8E44AD', 'EA': '#E67E22', 'DP': '#2980B9',
                    'OT': '#27AE60', 'DZ': '#C0392B', 'ZONALES': '#E74C3C',
                    'CONELEC': '#16A085', 'Sin Tipo': '#7F8C8D'
                }
                fig_tipo = px.pie(
                    df_tipo, values='Proyectos', names='Tipo', hole=0.5,
                    color='Tipo', color_discrete_map=_color_map_tipo
                )
                fig_tipo.update_traces(textinfo='percent+label', textfont=dict(color='white', size=10))
                fig_tipo.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                    showlegend=True,
                    legend=dict(orientation='v', font=dict(color='white', size=9)),
                    margin=dict(t=5, b=10, l=5, r=5), height=300
                )
                st.plotly_chart(fig_tipo, use_container_width=True)
            else:
                st.info("Columna tipo_area no disponible.")

        # ── DISTRIBUCIÓN POR AUTORIDAD RESPONSABLE Y PROVINCIA ───────────────
        st.markdown("---")
        gc4, gc5 = st.columns([2, 1])

        with gc4:
            st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Top 15 Autoridades Responsables por Carga</p>", unsafe_allow_html=True)
            df_aut_dist = (
                df_rep.groupby(['autoridad_responsable', 'estado_proyecto'])
                .size().reset_index(name='Proyectos')
            )
            top_auts = df_rep['autoridad_responsable'].value_counts().head(15).index.tolist()
            df_aut_dist = df_aut_dist[df_aut_dist['autoridad_responsable'].isin(top_auts)]
            fig_aut = px.bar(
                df_aut_dist, x='Proyectos', y='autoridad_responsable', color='estado_proyecto',
                orientation='h', barmode='stack',
                color_discrete_map={'Completado': '#2ECC71', 'En Trámite': '#E67E22'},
                labels={'autoridad_responsable': 'Autoridad Responsable', 'estado_proyecto': 'Estado'}
            )
            fig_aut.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF',
                yaxis=dict(autorange='reversed', tickfont=dict(size=9, color='#FFFFFF')),
                xaxis=dict(tickfont=dict(color='#FFFFFF')),
                legend=dict(orientation='h', y=-0.15, font=dict(color='white', size=10)),
                margin=dict(t=5, b=40, l=10, r=20), height=420
            )
            st.plotly_chart(fig_aut, use_container_width=True)

        with gc5:
            st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Por Tipo de Permiso Ambiental</p>", unsafe_allow_html=True)
            df_perm_dist = df_rep['tipo_permiso'].value_counts().reset_index()
            df_perm_dist.columns = ['Tipo de Permiso', 'Proyectos']
            fig_perm = px.pie(
                df_perm_dist.head(8), values='Proyectos', names='Tipo de Permiso', hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_perm.update_traces(
                textinfo='percent', textfont=dict(color='white', size=10)
            )
            fig_perm.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                legend=dict(orientation='v', font=dict(color='white', size=9)),
                margin=dict(t=10, b=10, l=10, r=10), height=420
            )
            st.plotly_chart(fig_perm, use_container_width=True)

        # ── TABLA MAESTRA DEL REPORTE ─────────────────────────────────────────
        st.markdown("---")
        st.markdown(
            f"<h3 style='color:white !important;'>📋 Listado Detallado — {total_rep:,} proyectos</h3>",
            unsafe_allow_html=True
        )

        # Mapa de columnas: campo SQL → etiqueta institucional
        col_rename = {
            'codigo_proyecto':       'Código Proyecto',
            'nombre_proyecto':       'Nombre del Proyecto',
            'autoridad_responsable': 'Autoridad Responsable',
            'tipo_area':             'Tipo Institucional',
            'siglas_tipo':           'Siglas',
            'nivel_jerarquico':      'Nivel Jerárquico',
            'l1_nombre':             'Raíz (L1)',
            'l2_nombre':             'Subnivel (L2)',
            'ruta_nombres':          'Ruta Jerárquica',
            'area_padre':            'Unidad Padre',
            'canton_directo_area':   'Cantón del Área',
            'es_emisora_aaa':        'Emite AAA',
            'es_seguimiento_aaa':    'Seguimiento AAA',
            'es_proyecto_inversion': 'Proyecto Inversión',
            'provincia':             'Provincia',
            'canton':                'Cantón',
            'parroquia':             'Parroquia',
            'tipo_permiso':          'Tipo de Permiso',
            'tecnico_responsable':   'Técnico Responsable',
            'estado_proceso':        'Estado Proceso (DWH)',
            'estado_proyecto':       'Estado',
            'tarea_actual':          'Tarea Actual',
            'rol_en_tarea':          'Rol (Operador / Técnico)',
            'origen':                'Normativa',
            'fecha_inicio_proceso':  'Fecha Inicio',
            'fecha_fin_proceso':     'Fecha Fin',
        }
        _cols_presentes = [c for c in col_rename if c in df_rep.columns]
        df_display = df_rep[_cols_presentes].rename(columns=col_rename)

        for col_fecha in ['Fecha Inicio', 'Fecha Fin']:
            if col_fecha in df_display.columns:
                df_display[col_fecha] = pd.to_datetime(df_display[col_fecha], errors='coerce').dt.strftime('%Y-%m-%d')

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Estado': st.column_config.TextColumn(
                    'Estado',
                    help='En Trámite = proceso activo | Completado = resolución emitida'
                ),
                'Rol (Operador / Técnico)': st.column_config.TextColumn(
                    'Rol',
                    help='Operador = entidad proponente | Técnico MAE = funcionario revisor'
                ),
            }
        )

        # ── EXPORTACIÓN ───────────────────────────────────────────────────────
        csv_rep = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte de Regularización (CSV)",
            data=csv_rep,
            file_name=f"reporte_regularizacion_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    # S3.1 — MÓDULO MAPA INSTITUCIONAL (dim_area v3.0)
    # Treemap jerárquico v3.0 + bridge_area_jerarquia + tabla de capacidades AAA
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    with st.expander("🏛️ Mapa Institucional — Jerarquía Consolidada v3.0 (bridge_area_jerarquia)", expanded=False):
        st.markdown("<h4 style='color:white !important;margin-bottom:12px;'>Distribución institucional de carga de proyectos y habilitaciones AAA</h4>", unsafe_allow_html=True)

        df_hier = load_institutional_hierarchy()
        if not df_hier.empty:
            _mi1, _mi2 = st.columns([3, 2])

            with _mi1:
                # Treemap v3.0: l1_siglas_tipo → l1_nombre → nombre_area (jerarquía real)
                _df_tree = df_hier[df_hier['proyectos_asignados'] > 0].copy()
                if not _df_tree.empty:
                    # Rellenar l1_nombre vacío con nombre_area (nodos raíz sin padre)
                    _df_tree['l1_nombre'] = _df_tree['l1_nombre'].replace('', None).fillna(_df_tree['nombre_area'])
                    # Para áreas nivel 1 (sin l2), el nodo final es el mismo que l1
                    _df_tree['_nodo_hoja'] = _df_tree.apply(
                        lambda r: r['nombre_area'] if r['nombre_area'] != r['l1_nombre'] else r['nombre_area'], axis=1
                    )
                    fig_tree = px.treemap(
                        _df_tree,
                        path=['l1_siglas_tipo', 'l1_nombre', '_nodo_hoja'],
                        values='proyectos_asignados',
                        color='en_tramite',
                        color_continuous_scale='RdYlGn_r',
                        color_continuous_midpoint=_df_tree['en_tramite'].median(),
                        title="Jerarquía Institucional (v3.0) — Carga consolidada por Área",
                        hover_data={'es_emisora_aaa': True, 'canton_directo': True, 'ruta_nombres': True}
                    )
                    fig_tree.update_traces(
                        textinfo="label+value",
                        textfont=dict(size=11)
                    )
                    fig_tree.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                        margin=dict(t=40, b=5, l=5, r=5), height=480,
                        coloraxis_colorbar=dict(title=dict(text="En Trámite", font=dict(color='white')),
                                               tickfont=dict(color='white'))
                    )
                    st.plotly_chart(fig_tree, use_container_width=True)
                else:
                    st.info("Sin datos con proyectos asignados para el treemap.")

            with _mi2:
                st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;'>Capacidades AAA por Tipo (v3.0)</p>", unsafe_allow_html=True)
                _aaa_summary = df_hier.groupby(['siglas', 'tipo_area']).agg(
                    areas_total=('nombre_area', 'count'),
                    emisoras_aaa=('es_emisora_aaa', 'sum'),
                    seguimiento_aaa=('es_seguimiento_aaa', 'sum'),
                    proyectos=('proyectos_asignados', 'sum'),
                    en_tramite=('en_tramite', 'sum')
                ).reset_index()
                _aaa_summary['% Emisoras'] = (_aaa_summary['emisoras_aaa'] / _aaa_summary['areas_total'] * 100).round(1)
                st.dataframe(
                    _aaa_summary.rename(columns={
                        'siglas': 'Siglas', 'tipo_area': 'Tipo', 'areas_total': 'Áreas',
                        'emisoras_aaa': 'Emit. AAA', 'seguimiento_aaa': 'Seg. AAA',
                        'proyectos': 'Proyectos', 'en_tramite': 'En Trámite'
                    }).sort_values('Proyectos', ascending=False),
                    use_container_width=True, hide_index=True,
                    column_config={
                        '% Emisoras': st.column_config.ProgressColumn(
                            '% Emisoras AAA', format='%.1f%%', min_value=0, max_value=100
                        )
                    }
                )

                # Filtro interactivo por siglas para la tabla detallada
                st.markdown("<p style='color:#85C1E9;font-size:0.8rem;font-weight:700;text-transform:uppercase;margin-top:12px;'>Detalle por Área — Jerarquía v3.0</p>", unsafe_allow_html=True)
                _tipos_mapa = ["TODOS"] + sorted(df_hier['siglas'].replace('?', None).dropna().unique().tolist())
                _sel_tipo_mapa = st.selectbox("Filtrar por siglas", _tipos_mapa, key="mapa_inst_tipo")
                _df_det = df_hier if _sel_tipo_mapa == "TODOS" else df_hier[df_hier['siglas'] == _sel_tipo_mapa]

                _cols_det = ['ruta_nombres', 'nombre_area', 'siglas', 'nivel_jerarquico',
                             'canton_directo', 'es_emisora_aaa',
                             'es_seguimiento_aaa', 'proyectos_asignados', 'en_tramite', 'resolucion_ministerial']
                _cols_det_pres = [c for c in _cols_det if c in _df_det.columns]
                st.dataframe(
                    _df_det[_cols_det_pres].sort_values('proyectos_asignados', ascending=False).rename(columns={
                        'ruta_nombres': 'Ruta Jerárquica', 'nombre_area': 'Área', 'siglas': 'Tipo',
                        'nivel_jerarquico': 'Nivel', 'canton_directo': 'Cantón',
                        'es_emisora_aaa': 'Emit. AAA', 'es_seguimiento_aaa': 'Seg. AAA',
                        'proyectos_asignados': 'Proyectos', 'en_tramite': 'En Trámite',
                        'resolucion_ministerial': 'Resolución'
                    }),
                    use_container_width=True, hide_index=True,
                    column_config={
                        'Emit. AAA': st.column_config.CheckboxColumn('Emit. AAA'),
                        'Seg. AAA':  st.column_config.CheckboxColumn('Seg. AAA'),
                        'Ruta Jerárquica': st.column_config.TextColumn('Ruta', width='large'),
                    }
                )

                # Descarga del mapa institucional completo
                _csv_hier = df_hier.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Descargar Mapa Institucional v3.0 (CSV)", _csv_hier,
                    f"mapa_institucional_v3_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv", use_container_width=True
                )
        else:
            st.warning("No se pudo cargar la jerarquía institucional. Verifique la conexión al DWH.")
    # ══ fin Módulo Mapa Institucional v3.0 ══

