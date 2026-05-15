import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

missing_functions = """
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

@st.cache_data(ttl=600)
def load_chemical_summary():
    try:
        query = '''
        SELECT 
            c.classification, 
            c.substance_name, 
            SUM(f.cantidad_total) as dosis_total
        FROM dw.fact_chemical_import f
        JOIN dw.dim_chemical c ON f.sk_chemical = c.sk_chemical
        GROUP BY c.classification, c.substance_name
        '''
        return pd.read_sql(query, get_engine())
    except Exception:
        return pd.DataFrame()

# --- INTERFAZ DE USUARIO ---"""

if "def load_origin_period_report" not in content:
    content = content.replace("# --- INTERFAZ DE USUARIO ---", missing_functions)
    print("SUCCESS: Functions Resurrected.")
else:
    print("FUNCTIONS ALREADY PRESENT.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
