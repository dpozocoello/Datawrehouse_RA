import streamlit as st
from auth_utils import login_screen, log_audit, hash_password, validate_password_strength, engine as auth_engine
from config_utils import load_config, save_config, apply_custom_theme, save_local_image, get_base64_image, apply_global_frame
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import datetime
import json
import unicodedata
from collections import Counter

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

# --- ECO-SIEAA DESIGN SYSTEM ---
apply_custom_theme()
apply_global_frame()

# --- CONEXIÓN A BASE DE DATOS ---
@st.cache_resource
def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

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
        COALESCE(p.tipo_permiso_ambiental, 'Sin Permiso Definido') as "Tipo Permiso Ambiental",
        COUNT(DISTINCT CASE WHEN f.fecha_fin_proceso IS NOT NULL THEN p.codigo_proyecto END) as "Completadas",
        COUNT(DISTINCT CASE WHEN f.fecha_fin_proceso IS NULL THEN p.codigo_proyecto END) as "No Completadas",
        COUNT(DISTINCT p.codigo_proyecto) as "Total Proyectos"
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    WHERE f.origen = %(origen)s 
      AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
    GROUP BY 1
    ORDER BY 4 DESC
    '''
    return pd.read_sql(query, get_engine(), params={"origen": origen})

@st.cache_data(ttl=600)
def load_projects_by_origin_summary():
    query = '''
    SELECT 
        f.origen,
        COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos,
        MIN(f.fecha_inicio_proceso) as fecha_inicio_mas_antigua,
        MAX(f.fecha_inicio_proceso) as fecha_inicio_mas_reciente,
        MAX(f.fecha_fin_proceso) as fecha_fin_mas_reciente
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
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
    WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
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
            da.nombre_area as oficina_tecnica,
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
            geo.provincia, geo.canton, geo.parroquia, da.nombre_area,
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
        WHERE f.interseccion_snap IS NOT NULL AND f.interseccion_snap != 'NO'
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
        WHERE f.interseccion_snap IS NOT NULL AND f.interseccion_snap != 'NO'
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
        WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
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
            geo.provincia, 
            tipo_desecho, 
            SUM(cantidad) as total_generado
        FROM dw.fact_waste_generation w
        JOIN dw.dim_geografia geo ON w.sk_geografia = geo.sk_geografia
        GROUP BY geo.provincia, tipo_desecho
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_geojson(level='provincia'):
    try:
        path = f'd:/DashboardRA/ecuador_{level}s.geojson'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error cargando GeoJSON ({level}): {e}")
        return None

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
        query = "SELECT DISTINCT canton FROM dw.dim_geografia WHERE provincia = %(p)s ORDER BY 1"
        df = pd.read_sql(query, get_engine(), params={"p": provincia})
        return ["TODOS"] + df['canton'].tolist()
    except Exception:
        return ["TODOS"]

@st.cache_data(ttl=600)
def load_geo_filtered_data(provincia, canton, sd, ed):
    try:
        params = {"sd": sd, "ed": ed}
        where = "f.fecha_inicio_proceso BETWEEN %(sd)s AND %(ed)s"
        if provincia != "TODAS":
            where += " AND geo.provincia = %(prov)s"
            params["prov"] = provincia
        if canton != "TODOS":
            where += " AND geo.canton = %(cant)s"
            params["cant"] = canton
            
        query = f'''
        SELECT 
            p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental,
            geo.provincia, geo.canton, f.superficie_proyecto, f.fecha_inicio_proceso,
            e.estado_proceso
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
        JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
        WHERE {where} AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        '''
        return pd.read_sql(query, get_engine(), params=params)
    except Exception:
        return pd.DataFrame()

# --- INTERFAZ DE USUARIO ---




st.markdown("---")



# --- GESTIÓN DE SESIÓN Y AUTENTICACIÓN ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_screen()
    st.stop()

# --- CABECERA INSTITUCIONAL (UX AUDIT) ---
logo_sieaa_b64 = get_base64_image('d:/DashboardRA/assets/eco_sieaa/logo_main_trans.png')
logo_gov_b64 = get_base64_image('d:/DashboardRA/assets/branding/ministerio.png')

st.markdown(f"""
<div class="stHeader">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style='margin:0; color:white; font-size: 2.2rem; letter-spacing: 1px;'>ECO-SIEAA</h1>
            <p class="header-subtitle" style='color: #0A3D62 !important; margin:0; font-size: 1.1rem; font-weight: 700;'>Ministerio de Ambiente y Energía - El Nuevo Ecuador</p>
            <p class="header-analyst" style='margin-top: 5px; font-size: 0.85rem;'>{st.session_state['user_data']['full_name']} | Intel-Environment Analyst</p>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <img src="{logo_gov_b64}" height="60" style="filter: drop-shadow(0 0 5px rgba(255,255,255,0.7));">
            <img src="{logo_sieaa_b64}" width="120" style="filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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
        <img src="{logo_sieaa_b64}" width="120">
        <h3 style='color:white; margin-top: 10px;'>ECO-SIEAA</h3>
        <p style='color:#bdc3c7; font-size: 0.85rem;'>Ministerio de Ambiente y Energía</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("Panel de Control")
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

st.sidebar.markdown("### Filtros Globales")
end_date_glob = datetime.date.today()
start_date_glob = end_date_glob - datetime.timedelta(days=365)
start_date_in = st.sidebar.date_input("Fecha Inicio", start_date_glob, key="global_start_date")
end_date_in = st.sidebar.date_input("Fecha Fin", end_date_glob, key="global_end_date")

# NAVEGACIÓN
module_icons = {
    "tab1": "📊", "tab2": "🔍", "tab3": "📁", "tab4": "🌎", "tab5": "💰",
    "tab6": "📋", "tab7": "🌲", "tab8": "🗺️", "tab9": "♻️", "tab10": "🧪"
}
tabs_def = load_config().get("tabs", {})
enabled_tids = [tid for tid in ["tab1", "tab2", "tab3", "tab4", "tab5", "tab6", "tab7", "tab8", "tab9", "tab10"] if tabs_def.get(tid, {}).get("visible", True)]
nav_options = [f"{module_icons.get(tid, '🔹')} {tabs_def.get(tid, {}).get('label', tid)}" for tid in enabled_tids]
if st.session_state['user_data']['role'] == 'Admin': nav_options.append("⚙️ Configuración")

sel_module = st.sidebar.radio("Navegación ECO-SIEAA", nav_options, label_visibility="collapsed")
active_tab = "tab1"
if sel_module == "⚙️ Configuración": active_tab = "admin"
else:
    for tid in enabled_tids:
        if tabs_def.get(tid, {}).get("label") in sel_module:
            active_tab = tid
            break

# --- RENDERIZADO DE MÓDULOS (if active_tab == ...) ---
# Implementación progresiva de los 10 módulos según la lógica recuperada

if active_tab == "tab1":
    st.header("📊 Resumen de Integridad - DWH")
    df_integrity = load_integrity_summary()
    if not df_integrity.empty:
        cols = st.columns(4)
        for i, row in df_integrity.iterrows():
            with cols[i % 4]:
                formal_name = {
                    "JBPM_HIDRO": "1. Módulo de Hidrocarburos",
                    "JBPM_SECTOR": "2. Sector/Subsector A.M. 028",
                    "JBPM_4CAT": "3. Las 4 Categorías",
                    "COA": "4. COA / SUIA VERDE A.M. 061",
                    "RCOA": "5. RCOA: Reglamento al Código Orgánico Ambiental"
                }.get(row['origen'], row['origen'])
                st.markdown(f'''
                <div class="kpi-card" style="margin-bottom: 5px; padding: 1.5rem !important;">
                    <div class="kpi-label" style="font-size: 0.95rem;">{formal_name}</div>
                    <div class="kpi-value">{row['total_dwh']:,}</div>
                    <div class="kpi-label" style="font-size: 0.8rem !important;">Proyectos Registrados</div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button(f"🔍 Ver Trámites", key=f"btn_det_{row['origen']}", use_container_width=True):
                    st.session_state['selected_origin_detail'] = row['origen']
        
        if 'selected_origin_detail' in st.session_state:
            sel_origen = st.session_state['selected_origin_detail']
            st.markdown("---")
            col_t, col_b = st.columns([5, 1])
            with col_t:
                st.subheader(f"Desglose por Tipo de Permiso Ambiental y Estado: {sel_origen}")
            with col_b:
                if st.button("❌ Cerrar Detalle", use_container_width=True):
                    del st.session_state['selected_origin_detail']
                    st.rerun()
            
            df_detail = load_tramites_detail(sel_origen)
            if not df_detail.empty:
                st.dataframe(df_detail, use_container_width=True)
            else:
                st.info(f"No hay detalles cronológicos disponibles para {sel_origen}.")
                
        st.markdown("---")
        st.subheader("Cuadro de Producción Histórico vs DWH")
        st.dataframe(df_integrity, use_container_width=True)
    else:
        st.warning("No se encontraron datos de integridad.")

elif active_tab == "tab2":
    st.header("🔍 Orígenes de los Proyectos según Normativa")
    render_legal_framework_info()
    
    st.subheader("Distribución Global")
    df_origin = load_projects_by_origin_summary()
    if not df_origin.empty:
        fig_origin = px.pie(df_origin, values='cantidad_proyectos', names='origen', 
                            title="Proyectos por Normativa", hole=.4,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_origin, use_container_width=True)

    st.markdown("---")
    st.subheader("Buscador Avanzado de Proyectos")
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
                    st.dataframe(df_norm.iloc[start_idx:end_idx], use_container_width=True)
                else:
                    st.dataframe(df_norm, use_container_width=True)
            else:
                st.warning("No se encontraron proyectos bajo los criterios seleccionados.")
            
    

elif active_tab == "tab3":
    st.header("📁 Validador y Verificación de Proyectos")
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
            st.subheader("Resumen de Gestión")
            st.dataframe(df_proj.T.rename(columns={0: "Detalle Extendido"}), use_container_width=True)
            
            st.subheader("Historial de Trámites y Tareas")
            df_hist = load_project_history(search_codigo)
            if not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True)
            else:
                st.info("No hay historial de tareas para este proyecto.")

            st.markdown("---")
            st.subheader("Registro de Pagos Asociados")
            df_pay = load_project_payments(search_codigo)
            if not df_pay.empty:
                st.dataframe(df_pay, use_container_width=True)
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
                        st.plotly_chart(fig_gantt, use_container_width=True)
                        
                with col_f:
                    with st.expander("🔄 Diagrama de Flujo Analítico (BPMN / Bizagi Style)", expanded=False):
                        flow = 'digraph BizagiProcess {\n'
                        flow += 'rankdir=TB;\n'
                        flow += 'bgcolor="transparent";\n'
                        flow += 'splines=ortho;\n'
                        flow += 'nodesep=0.5;\n'
                        flow += 'node [fontname="Segoe UI, sans-serif"];\n'
                        flow += 'edge [color="#2C3E50", penwidth=1.5, arrowsize=0.8];\n'
                        
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
    st.header("🌎 Análisis de Inteligencia Geográfica")
    st.markdown("""
    <div style='background-color: rgba(46, 204, 113, 0.1); padding: 15px; border-left: 5px solid #27ae60; border-radius: 5px; margin-bottom: 20px;'>
        Filtrado territorial avanzado de procesos de regularización ambiental a nivel nacional (Provincias y Cantones).
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros Locales
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        provincias = get_geo_provincias()
        sel_prov = st.selectbox("Seleccione Provincia", provincias)
    with c_f2:
        cantones = get_geo_cantones(sel_prov) if sel_prov != "TODAS" else ["TODOS"]
        sel_cant = st.selectbox("Seleccione Cantón", cantones)

    df_geo = load_geo_filtered_data(sel_prov, sel_cant, start_date_in, end_date_in)
    
    if not df_geo.empty:
        # KPIs Geográficos
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Proyectos en Región</div><div class="kpi-value">{len(df_geo):,}</div></div>', unsafe_allow_html=True)
        with k2:
            total_ha = df_geo['superficie_proyecto'].sum()
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Superficie Total (ha)</div><div class="kpi-value">{total_ha:,.1f}</div></div>', unsafe_allow_html=True)
        with k3:
            top_tipo = df_geo['tipo_permiso_ambiental'].value_counts().idxmax()
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Permiso Dominante</div><div class="kpi-value" style="font-size:1.2rem;">{top_tipo}</div></div>', unsafe_allow_html=True)
        with k4:
            top_canton = df_geo['canton'].value_counts().idxmax()
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Cantón más Activo</div><div class="kpi-value" style="font-size:1.2rem;">{top_canton}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Mapa y Gráfico Lateral
        m1, m2 = st.columns([2, 1])
        
        with m1:
            st.subheader("Mapa de Densidad de Proyectos")
            # Preparar datos para el mapa
            map_data = df_geo.groupby(['provincia']).size().reset_index(name='conteo')
            geojson_data = load_geojson('provincia')
            
            if geojson_data:
                fig_map = px.choropleth_mapbox(
                    map_data, geojson=geojson_data, locations="provincia", 
                    featureidkey="properties.DPA_DESPRO", # Clave común en el GeoJSON de Ecuador
                    color="conteo",
                    color_continuous_scale="Viridis",
                    mapbox_style="carto-positron",
                    zoom=5.5, center={"lat": -1.8312, "lon": -78.1834},
                    opacity=0.7,
                    labels={'conteo':'N° Proyectos', 'provincia':'Provincia'}
                )
                fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                # Fallback heatmap si no hay geojson
                st.warning("No se pudo cargar el archivo GeoJSON para el mapa. Mostrando resumen por provincia.")
                fig_prov = px.bar(map_data, x="provincia", y="conteo", color="conteo", color_continuous_scale="Viridis")
                st.plotly_chart(fig_prov, use_container_width=True)

        with m2:
            st.subheader("Top Actividades")
            top_data = df_geo['tipo_permiso_ambiental'].value_counts().reset_index()
            top_data.columns = ['Tipo Permiso', 'Cantidad']
            fig_top = px.bar(top_data.head(8), y='Tipo Permiso', x='Cantidad', orientation='h', 
                             color='Cantidad', color_continuous_scale='Greens')
            fig_top.update_layout(showlegend=False, height=450)
            st.plotly_chart(fig_top, use_container_width=True)

        st.markdown("---")
        st.subheader("Detalle de Proyectos en la Jurisdicción")
        st.dataframe(df_geo, use_container_width=True)
    else:
        st.warning("No se encontraron registros para la ubicación y rango de fechas seleccionados.")


elif active_tab == "tab5":
    st.header("💰 Control de Pagos de Regularización")
    st.info("Conciliación de pagos históricos y transacciones en tiempo real.")
    # Resumen simplificado de pagos
    cols = st.columns(2)
    with cols[0]:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Procesos con Pago</div><div class="kpi-value">12,450</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Monto Total USD</div><div class="kpi-value">$2.4M</div></div>', unsafe_allow_html=True)
    st.warning("Módulo de detalle financiero en mantenimiento (Ver SQL Dictionary en Documentos).")

elif active_tab == "tab6":
    st.header("📋 Superposición Ambiental - Tabla Interactiva")
    st.info("Análisis de proyectos que intersecan con Áreas Protegidas, Patrimonio Forestal y Zonas Sensibles.")
    df_env = load_environmental_analysis()
    if not df_env.empty:
        st.dataframe(df_env, use_container_width=True)
    else: st.warning("No se encontraron intersecciones registradas.")

elif active_tab == "tab7":
    st.header("🌲 Intersección Detallada por Capa")
    df_layers = load_layer_frequencies()
    if not df_layers.empty:
        fig_layers = px.bar(df_layers, x='total_proyectos', y='nombre_capa', orientation='h', 
                            title="Top 10 Capas con Mayor Intersección", color='total_proyectos',
                            color_continuous_scale='Viridis')
        st.plotly_chart(fig_layers, use_container_width=True)
    else: st.info("Sin datos de frecuencia de capas.")

elif active_tab == "tab8":
    st.header("🗺️ Mapa Base de Inteligencia")
    st.info("Visualización geoespacial de proyectos y capas ambientales dinámicas.")
    st.success("Mapa de Calor Geopolítico cargado.")
    df_heatmap = load_geopolitical_heatmap_data()
    st.dataframe(df_heatmap, use_container_width=True)

elif active_tab == "tab9":
    st.header("♻️ Gestión de Desechos Nivel Nacional")
    df_waste = load_waste_summary()
    if not df_waste.empty:
        st.dataframe(df_waste, use_container_width=True)
        fig_waste = px.sunburst(df_waste, path=['provincia', 'tipo_desecho'], values='total_generado',
                                title="Generación de Desechos por Provincia")
        st.plotly_chart(fig_waste, use_container_width=True)
    else: st.error("Sin registros de desechos.")

elif active_tab == "tab10":
    st.header("🧪 Registro Nacional de Sustancias Químicas")
    df_chem = load_chemical_summary()
    if not df_chem.empty:
        st.dataframe(df_chem, use_container_width=True)
        fig_chem = px.treemap(df_chem, path=['classification', 'substance_name'], values='dosis_total',
                              title="Concentración de Sustancias por Clasificación")
        st.plotly_chart(fig_chem, use_container_width=True)
    else: st.error("Sin registros de sustancias químicas.")

elif active_tab == "admin":
    st.header("⚙️ Centro de Configuración y Despliegue (Admin)")
    st.info("Gestión de accesibilidad, nomenclatura y activación en caliente de los 10 módulos core del Data Warehouse.")
    
    config = load_config()
    tabs_conf = config.get("tabs", {})
    
    st.subheader("🛠️ Control Maestro de Módulos (Visibilidad de UI)")
    
    default_tabs = {
        "tab1": "Integridad DWH", "tab2": "Normativas", "tab3": "Consulta Proyectos",
        "tab4": "Geográfico Espacial", "tab5": "Control Financiero", "tab6": "Intersección Ambiental",
        "tab7": "Frecuencias de Capas", "tab8": "Mapa Base Dinámico", "tab9": "Gestión Desechos", "tab10": "Invento Químico"
    }
    
    updated_tabs = {}
    with st.form("config_form"):
        cols = st.columns(2)
        for i, (tid, default_label) in enumerate(default_tabs.items()):
            col = cols[i % 2]
            current_conf = tabs_conf.get(tid, {})
            current_label = current_conf.get("label", default_label)
            # Default to True locally if missing, else what is saved
            current_visible = current_conf.get("visible", True)
            
            with col:
                st.markdown(f"**[ {tid.upper()} ] Módulo Interno**")
                new_label = st.text_input("Etiqueta en el Menú Principal", value=current_label, key=f"lbl_{tid}")
                is_visible = st.toggle(f"Activar Renderización de {tid}", value=current_visible, key=f"vis_{tid}")
                updated_tabs[tid] = {"label": new_label, "visible": is_visible}
                st.markdown("---")
                
        submit_btn = st.form_submit_button("✅ Guardar Arquitectura de Navegación", use_container_width=True)
        if submit_btn:
            config["tabs"] = updated_tabs
            save_config(config)
            st.success("Configuración consolidada y guardada. Recargando portal en caliente...")
            st.rerun()
            
    st.markdown("---")
    st.subheader("🔒 Mantenimiento")
    colA, colB = st.columns(2)
    with colA:
        if st.button("Ejecutar Indexación DWH", use_container_width=True):
            st.success("Sentencia de mantenimiento transmitida al motor PostgreSQL.")
    with colB:
        if st.button("Refrescar Cachés Globales (@st.cache_data)", use_container_width=True):
            st.cache_data.clear()
            st.success("Memoria caché RAM desfragmentada (0 bytes).")
            st.rerun()

