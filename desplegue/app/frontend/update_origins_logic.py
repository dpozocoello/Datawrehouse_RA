import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update load_integrity_summary and load_tramites_detail
old_funcs_pattern = r'@st\.cache_data\(ttl=600\)\ndef load_integrity_summary\(\):.*?return pd\.read_sql\(query, get_engine\(\), params=\{"origen": origen\}\)'

new_funcs = """@st.cache_data(ttl=600)
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
        f.proceso as tipo_de_tramite,
        COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos
    FROM dw.fact_regularizacion f
    JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
    WHERE f.origen = %(origen)s 
      AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
      AND f.proceso IS NOT NULL
      AND f.proceso != ''
    GROUP BY 1
    ORDER BY 2 DESC
    '''
    return pd.read_sql(query, get_engine(), params={"origen": origen})"""

if re.search(old_funcs_pattern, content, flags=re.DOTALL):
    content = re.sub(old_funcs_pattern, new_funcs, content, flags=re.DOTALL)
    print("SUCCESS FUNCTIONS")
else:
    print("FUNCTIONS NOT FOUND")
    
# Update UI string
old_ui_str = 'st.subheader(f"Desglose Cronológico de Trámites: {sel_origen}")'
new_ui_str = 'st.subheader(f"Cuadro Consolidado de Trámites: {sel_origen}")'

content = content.replace(old_ui_str, new_ui_str)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS WRITTEN")
