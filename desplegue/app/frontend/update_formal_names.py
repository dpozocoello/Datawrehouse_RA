import os
import re

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Tab 1 mapping
map_dict = """        formal_names = {
            "JBPM_HIDRO": "1. JBPM_HIDRO (Módulo Hidrocarburos)",
            "JBPM_SECTOR": "2. JBPM_SECTOR (A.M. 028)",
            "JBPM_4CAT": "3. JBPM_4CAT (Las 4 Categorías)",
            "COA": "4. COA (SUIA VERDE A.M. 061)",
            "RCOA": "5. RCOA (Reglamento COA)"
        }
"""

old_tab1_kpi = """                st.markdown(f'''
                <div class="kpi-card" style="margin-bottom: 5px; padding: 1.5rem !important;">
                    <div class="kpi-label">{row['origen']}</div>"""

new_tab1_kpi = """                formal_name = {
                    "JBPM_HIDRO": "1. JBPM_HIDRO: Hidrocarburos",
                    "JBPM_SECTOR": "2. JBPM_SECTOR: A.M. 028",
                    "JBPM_4CAT": "3. JBPM_4CAT: 4 Categorías",
                    "COA": "4. COA / SUIA VERDE",
                    "RCOA": "5. RCOA: Reglamento COA"
                }.get(row['origen'], row['origen'])
                st.markdown(f'''
                <div class="kpi-card" style="margin-bottom: 5px; padding: 1.5rem !important;">
                    <div class="kpi-label" style="font-size: 0.95rem;">{formal_name}</div>"""

if old_tab1_kpi in content:
    content = content.replace(old_tab1_kpi, new_tab1_kpi)
    print("SUCCESS TAB 1")
else:
    print("TAB 1 NOT FOUND")

# 2. Update Tab 2 explicit mapping
old_tab2_dict = """        diccionario_origenes = {
            "TODAS LAS BASES (DWH COMPLETO)": "TODOS",
            "Normativa COA": "COA",
            "Normativa RCOA": "RCOA",
            "Normativa 4 CATEGORIAS": "JBPM_4CAT",
            "Normativa SECTOR SUBSECTOR": "JBPM_SECTOR",
            "SIN NORMATIVA": "RECUPERADO",
            "Normativa HIDROCARBUROS": "JBPM_HIDRO"
        }"""

new_tab2_dict = """        diccionario_origenes = {
            "TODAS LAS BASES (DWH COMPLETO)": "TODOS",
            "1. JBPM_HIDRO: Módulo de Hidrocarburos": "JBPM_HIDRO",
            "2. JBPM_SECTOR: Sector/Subsector A.M. 028": "JBPM_SECTOR",
            "3. JBPM_4CAT: Las 4 Categorías": "JBPM_4CAT",
            "4. COA / SUIA VERDE: A.M. 061": "COA",
            "5. RCOA: Reglamento al Código Orgánico Ambiental": "RCOA",
            "SIN NORMATIVA (Proyectos Recuperados)": "RECUPERADO"
        }"""

if old_tab2_dict in content:
    content = content.replace(old_tab2_dict, new_tab2_dict)
    print("SUCCESS TAB 2")
else:
    print("TAB 2 NOT FOUND")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS WRITTEN")
