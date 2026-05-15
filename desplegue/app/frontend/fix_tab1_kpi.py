import os

path = r'd:\DashboardRA\Dash_board_RG_v1.01\Dash_board_RG_v1.01.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazo quirúrgico del nombre de columna errado
new_content = content.replace("row['cantidad_proyectos']", "row['total_dwh']")

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
