import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_func = """
@st.cache_data(ttl=600)
def load_tramites_detail(origen):
    query = '''
    SELECT 
        TO_CHAR(f.fecha_inicio_proceso, 'YYYY-MM') as periodo_cronologico,
        f.proceso as tipo_de_tramite,
        COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    WHERE f.origen = %(origen)s 
      AND f.fecha_inicio_proceso IS NOT NULL 
      AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
      AND f.proceso IS NOT NULL
      AND f.proceso != ''
    GROUP BY 1, 2
    ORDER BY 1 ASC, 3 DESC
    '''
    return pd.read_sql(query, get_engine(), params={"origen": origen})

# --- INTERFAZ DE USUARIO ---
"""

# Replace the marker securely
if "# --- INTERFAZ DE USUARIO ---" in content and "def load_tramites_detail" not in content:
    content = content.replace("# --- INTERFAZ DE USUARIO ---", new_func)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
elif "def load_tramites_detail" in content:
    print("FUNCTION ALREADY EXISTS")
else:
    print("MARKER NOT FOUND")
