import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

missing_func = """@st.cache_data(ttl=600)
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

# --- INTERFAZ DE USUARIO ---"""

if "def load_projects_by_origin_summary():" not in content:
    content = content.replace("# --- INTERFAZ DE USUARIO ---", missing_func)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("FUNCTION ALREADY EXISTS")
