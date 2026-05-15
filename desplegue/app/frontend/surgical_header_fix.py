import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Detectar el inicio del bloque corrupto
    if 'st.set_page_config(' in line and i < 20:
        new_lines.append("st.set_page_config(\n")
        new_lines.append('    page_title="Dashboard ECO-SIEAA - v1.01",\n')
        new_lines.append('    page_icon="📊",\n')
        new_lines.append('    layout="wide",\n')
        new_lines.append('    initial_sidebar_state="expanded"\n')
        new_lines.append(")\n\n")
        new_lines.append("# --- ECO-SIEAA DESIGN SYSTEM ---\n")
        new_lines.append("apply_custom_theme()\n")
        new_lines.append("apply_global_frame()\n")
        skip = True
        continue
    
    # Detener el salto cuando lleguemos a la conexión de base de datos
    if skip and '# --- CONEXIÓN A BASE DE DATOS ---' in line:
        skip = False
        new_lines.append("\n")
        new_lines.append(line)
        continue
        
    if skip:
        continue
        
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
