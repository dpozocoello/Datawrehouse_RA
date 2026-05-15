from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

core_tables = [
    'dw.fact_regularizacion',
    'dw.dim_proyecto',
    'dw.dim_geografia',
    'dw.fact_pago',
    'dw.v_integridad_dashboard'
]

with open('d:/DashboardRA/core_data_validation.txt', 'w', encoding='utf-8') as f:
    f.write("=== CONTEO DE REGISTROS EN TABLAS CORE ===\n")
    with engine.connect() as conn:
        for t in core_tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                f.write(f"{t:40s} : {count:,} registros\n")
            except Exception as e:
                f.write(f"{t:40s} : ERROR - {e}\n")

        f.write("\n=== PRUEBA DE QUERY RESUMEN INTEGRIDAD ===\n")
        try:
            res = conn.execute(text("SELECT * FROM dw.v_integridad_dashboard LIMIT 3"))
            for row in res:
                f.write(f"{row}\n")
        except Exception as e:
            f.write(f"Error en v_integridad_dashboard: {e}\n")

print("Core validation complete. Results in d:/DashboardRA/core_data_validation.txt")
