import os

# 1. FIX DASHBOARD SYNTAX
path_dash = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path_dash, 'r', encoding='utf-8') as f:
    lines = f.readlines()

final_lines = []
skip = False
for i, line in enumerate(lines):
    if '# Mapa de Iconos por Módulo' in line:
        final_lines.append("# Mapa de Iconos Institucionales (UX Audit Standard)\n")
        final_lines.append("module_icons = {\n")
        final_lines.append('    "tab1": "📊", "tab2": "🔍", "tab3": "📁", "tab4": "🌎", "tab5": "💰",\n')
        final_lines.append('    "tab6": "📋", "tab7": "🌲", "tab8": "🗺️", "tab9": "♻️", "tab10": "🧪"\n')
        final_lines.append("}\n")
        skip = True
        continue
    if skip:
        if '}' in line and i < len(lines)-1 and 'nav_options' in lines[i+1]:
            skip = False
            continue
        elif '}' in line: # Sigue saltando hasta el final del bloque malformado
            if i + 1 < len(lines) and 'nav_options' in lines[i+1]:
                skip = False
            continue
        continue
    final_lines.append(line)

with open(path_dash, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

# 2. FIX CONFIG BACKGROUND
path_conf = r'd:\DashboardRA\Dash_board_RG_v1.01\config_utils.py'
with open(path_conf, 'r', encoding='utf-8') as f:
    conf_content = f.read()

# Forzando el fondo con un selector más genérico para Streamlit
new_style = """
        /* CONTENEDOR PRINCIPAL (#F4F6F7) - AGGRESSIVE OVERRIDE */
        .stMain, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        [data-testid="stMain"] > div:first-child {
            background-color: #F4F6F7 !important;
            border-radius: 20px 0 0 0;
            padding: 2rem !important;
        }
        .main .block-container {
             background-color: #F4F6F7 !important;
        }
"""
if '[data-testid="stMain"] {' in conf_content:
    import re
    conf_content = re.sub(r'\[data-testid="stMain"\] \{.*?\}', new_style, conf_content, flags=re.DOTALL)

with open(path_conf, 'w', encoding='utf-8') as f:
    f.write(conf_content)
