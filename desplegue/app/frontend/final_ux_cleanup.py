import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_mode = False
for line in lines:
    # 1. Eliminar Estilos CSS antiguos (líneas 34-39 aprox)
    if '# --- ESTILOS CSS ---' in line:
        skip_mode = True
        continue
    if skip_mode and '""", unsafe_allow_html=True)' in line:
        skip_mode = False
        continue
    if skip_mode:
        continue

    # 2. Actualizar Iconos Institucionales
    if '"tab1": "📊", "tab2": "📁"' in line:
        new_lines.append("""# Mapa de Iconos Institucionales (UX Audit Standard)
module_icons = {
    "tab1": "📊", "tab2": "🔍", "tab3": "📁", "tab4": "🌎", "tab5": "💰",
    "tab6": "📋", "tab7": "🌲", "tab8": "🗺️", "tab9": "♻️", "tab10": "🧪"
}
""")
        continue
    
    # Evitar duplicar si ya se reemplazó
    if 'module_icons = {' in line and 'tab1' in line and '📊' in line and '#' not in line:
        # Ya procesamos esto
        continue
        
    # 3. Aplicar clase stImage a imágenes existentes si no la tienen (opcional via CSS global es mejor)
    # Sin embargo, forzaremos el centrado en el renderizado específico si lo encontramos
    
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
