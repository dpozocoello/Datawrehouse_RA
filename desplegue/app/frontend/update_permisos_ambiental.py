import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_func_pattern = r'@st\.cache_data\(ttl=600\)\ndef load_tramites_detail.*?return pd\.read_sql\(query, get_engine\(\), params=\{"origen": origen\}\)'

new_func = """@st.cache_data(ttl=600)
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
    return pd.read_sql(query, get_engine(), params={"origen": origen})"""

if re.search(old_func_pattern, content, flags=re.DOTALL):
    content = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)
    print("SUCCESS FUNCTION")
else:
    print("FUNCTION NOT FOUND")

# Update UI string
old_ui_str = 'st.subheader(f"Cuadro Consolidado de Trámites: {sel_origen}")'
new_ui_str = 'st.subheader(f"Desglose por Tipo de Permiso Ambiental y Estado: {sel_origen}")'

if old_ui_str in content:
    content = content.replace(old_ui_str, new_ui_str)
    print("SUCCESS UI")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS WRITTEN")
