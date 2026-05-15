import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update get_unique_tramites function
old_func = """@st.cache_data(ttl=3600)
def get_unique_tramites():
    try:
        query = "SELECT DISTINCT tipo_permiso_ambiental FROM dw.dim_proyecto WHERE tipo_permiso_ambiental IS NOT NULL AND tipo_permiso_ambiental != '' ORDER BY tipo_permiso_ambiental"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['tipo_permiso_ambiental'].tolist()
    except:
        return ["TODOS"]"""

new_func = """@st.cache_data(ttl=3600)
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
        return ["TODOS"]"""

if old_func in content:
    content = content.replace(old_func, new_func)
    print("SUCCESS FUNC")
else:
    print("FAILED FUNC")


# 2. Update UI call in Tab 2
old_ui = """    with col_f2:
        lista_tramites = get_unique_tramites()"""

new_ui = """    with col_f2:
        lista_tramites = get_unique_tramites(origen_val)"""

if old_ui in content:
    content = content.replace(old_ui, new_ui)
    print("SUCCESS UI")
else:
    print("FAILED UI")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS WRITTEN")
