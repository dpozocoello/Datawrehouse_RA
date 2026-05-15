import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update get_unique_tramites logic to look at tipo_permiso_ambiental
old_get_unique = """@st.cache_data(ttl=3600)
def get_unique_tramites():
    try:
        query = "SELECT DISTINCT proceso FROM dw.fact_regularizacion WHERE proceso IS NOT NULL AND proceso != '' ORDER BY proceso"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['proceso'].tolist()
    except:
        return ["TODOS"]"""

new_get_unique = """@st.cache_data(ttl=3600)
def get_unique_tramites():
    try:
        query = "SELECT DISTINCT tipo_permiso_ambiental FROM dw.dim_proyecto WHERE tipo_permiso_ambiental IS NOT NULL AND tipo_permiso_ambiental != '' ORDER BY tipo_permiso_ambiental"
        df = pd.read_sql(query, get_engine())
        return ["TODOS"] + df['tipo_permiso_ambiental'].tolist()
    except:
        return ["TODOS"]"""

# 2. Update load_projects_advanced_filter to filter on p.tipo_permiso_ambiental
old_adv_filt = """
    if tipo_tramite != "TODOS":
        base_query += " AND f.proceso = %(tipo_tramite)s"
        params["tipo_tramite"] = tipo_tramite
"""

new_adv_filt = """
    if tipo_tramite != "TODOS":
        base_query += " AND p.tipo_permiso_ambiental = %(tipo_tramite)s"
        params["tipo_tramite"] = tipo_tramite
"""

# 3. Remove Discrepancias expander block
discrepancies_pattern = r'st\.markdown\("---"\)\s+with st\.expander\("🛠️ Ver Identificación de Discrepancias \(Staging vs DWH\)"\):.*?st\.success\("Sin discrepancias detectadas para esta fuente\."\)'

if old_get_unique in content:
    content = content.replace(old_get_unique, new_get_unique)
    print("SUCCESS 1: get_unique_tramites updated")
else:
    print("FAILED 1")

if old_adv_filt in content:
    content = content.replace(old_adv_filt, new_adv_filt)
    print("SUCCESS 2: load_projects_advanced_filter updated")
else:
    print("FAILED 2")

if re.search(discrepancies_pattern, content, flags=re.DOTALL):
    content = re.sub(discrepancies_pattern, "", content, flags=re.DOTALL)
    print("SUCCESS 3: Removed discrepancies block")
else:
    print("FAILED 3")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
