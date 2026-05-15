path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'class="header-subtitle"' in line and 'style=' in line:
        new_lines.append("            <p class=\"header-subtitle\" style='margin:0; font-size: 1rem;'>Eco-Sistema de Información y Educación Ambiental y del Agua</p>\n")
    elif 'class="header-analyst"' in line and 'style=' in line:
        new_lines.append("            <p class=\"header-analyst\" style='margin-top: 5px; font-size: 0.85rem;'>{user_info['full_name']} | Intel-Environment Analyst</p>\n")
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
