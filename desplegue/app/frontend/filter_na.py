import io

script_path = 'd:/DashboardRA/Dash_board_RG_v1.01/Dash_board_RG_v1.01.py'

with io.open(script_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Tab 1 to 4 queries
code = code.replace(
    "WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'",
    "WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'"
)
code = code.replace(
    "WHERE {where} AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'",
    "WHERE {where} AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'"
)

# Tab layer intersections
code = code.replace(
    "WHERE f.interseccion_snap IS NOT NULL AND f.interseccion_snap != 'NO'",
    "WHERE f.interseccion_snap IS NOT NULL AND f.interseccion_snap != 'NO' AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'"
)

# Tab 5 financial queries
code = code.replace(
    "WHERE {where} AND f.monto_pagado > 0",
    "WHERE {where} AND f.monto_pagado > 0 AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'"
)
code = code.replace(
    "WHERE p.codigo_proyecto = %(cod)s",
    "WHERE p.codigo_proyecto = %(cod)s AND p.codigo_proyecto != 'N/A' AND p.nombre_proyecto != 'N/A'"
)

with io.open(script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Replacement successful")
