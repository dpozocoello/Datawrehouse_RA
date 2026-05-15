import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    # Detectar el bloque redundante en las líneas exactas (582-586 originales en el view_file)
    # Pero usaremos contenido para seguridad
    if 'st.sidebar.markdown("Filtros Globales")' in line and i < 600:
        skip = True
        continue
    
    if skip:
        if 'end_date_in = st.sidebar.date_input("Fecha Fin"' in line:
            skip = False
        continue
    
    # Agregar keys únicas al bloque principal (634-635 aprox)
    if 'start_date_in = st.sidebar.date_input("Fecha Inicio"' in line and i > 600:
        line = line.replace('start_date_glob)', 'start_date_glob, key="global_start_date")')
    if 'end_date_in = st.sidebar.date_input("Fecha Fin"' in line and i > 600:
        line = line.replace('end_date_glob)', 'end_date_glob, key="global_end_date")')
        
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
