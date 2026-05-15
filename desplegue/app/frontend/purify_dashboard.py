import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Detectar y eliminar el fragmento huérfano de st.tabs
    if '"1. Integridad"' in line and '"2. Orígenes"' in line:
        # Saltar esta línea y la siguiente que cierra el corchete
        continue
    if '])' in line and i > 580 and i < 600:
        continue
    if '"6. Gestión"' in line and '"7. Superposición"' in line:
        continue
        
    # Eliminar títulos duplicados o redundantes de la versión anterior
    if 'st.title("🖥️ Dashboard RG v1.01' in line:
        continue
    if 'st.sidebar.title("Panel de Control v1.01")' in line:
        continue
        
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
