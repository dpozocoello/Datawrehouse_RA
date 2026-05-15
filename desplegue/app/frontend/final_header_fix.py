import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_mode = False
for i, line in enumerate(lines):
    # Encontrar el inicio de set_page_config
    if 'st.set_page_config(' in line:
        new_lines.append("st.set_page_config(\n")
        new_lines.append('    page_title="Dashboard ECO-SIEAA - v1.01",\n')
        new_lines.append('    page_icon="📊",\n')
        new_lines.append('    layout="wide",\n')
        new_lines.append('    initial_sidebar_state="expanded"\n')
        new_lines.append(")\n\n")
        new_lines.append("# --- ECO-SIEAA DESIGN SYSTEM ---\n")
        new_lines.append("apply_custom_theme()\n")
        new_lines.append("apply_global_frame()\n")
        
        # Saltar hasta que termine el bloque antiguo malformado
        skip_mode = True
        continue
    
    if skip_mode:
        if 'initial_sidebar_state="expanded"' in line or ')' in line and i < 40:
             # Seguir saltando hasta que encontremos el final del bloque o una línea conocida
             if ')' in line:
                 skip_mode = False
             continue
        continue

    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
