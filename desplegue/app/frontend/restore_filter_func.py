import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

missing_func = """
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
        
    base_query += " ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC LIMIT 5000"
    return pd.read_sql(base_query, get_engine(), params=params)

# --- INTERFAZ DE USUARIO ---
"""

if "def load_projects_advanced_filter" not in content:
    content = content.replace("# --- INTERFAZ DE USUARIO ---", missing_func)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("FUNCTION ALREADY EXISTS")
