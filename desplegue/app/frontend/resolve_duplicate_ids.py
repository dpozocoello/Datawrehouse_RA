import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Detectar el bloque legado redundante (ahora sabemos exactamente las líneas)
    if 'st.sidebar.title("Panel de Control v1.01")' in line:
        skip = True
        continue
    
    if skip:
        if 'st.sidebar.date_input("Fecha Fin"' in line:
            skip = False
        continue
    
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
