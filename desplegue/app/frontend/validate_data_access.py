from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

tables = [
    'dw.fact_waste_generation',
    'dw.dim_waste_generator',
    'dw.dim_waste_type',
    'dw.dim_dangerous_waste',
    'dw.dim_dangerous_classification',
    'dw.fact_chemical_application',
    'dw.dim_chemical_substance',
    'dw.dim_chemical_storage',
    'dw.fact_project_environmental_impact',
    'dw.dim_geografia'
]

with open('d:/DashboardRA/data_validation_results.txt', 'w', encoding='utf-8') as f:
    f.write("=== CONTEO DE REGISTROS EN TABLAS DE DESECHOS Y QUÍMICOS ===\n")
    with engine.connect() as conn:
        for t in tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                f.write(f"{t:40s} : {count:,} registros\n")
            except Exception as e:
                f.write(f"{t:40s} : ERROR - {e}\n")

        f.write("\n=== VERIFICACIÓN DE JOINS (FACT_WASTE_GENERATION) ===\n")
        # Check if geo_location_key exists in dim_geografia
        q_geo = text("""
            SELECT COUNT(*) 
            FROM dw.fact_waste_generation f
            LEFT JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
            WHERE g.sk_geografia IS NULL
        """)
        null_geo = conn.execute(q_geo).scalar()
        f.write(f"Registros en fact_waste_generation sin match en dim_geografia: {null_geo}\n")

        # Check join with dim_waste_type
        q_type = text("""
            SELECT COUNT(*) 
            FROM dw.fact_waste_generation f
            LEFT JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
            WHERE t.waste_type_key IS NULL
        """)
        null_type = conn.execute(q_type).scalar()
        f.write(f"Registros en fact_waste_generation sin match en dim_waste_type: {null_type}\n")

        f.write("\n=== VERIFICACIÓN DE JOINS (FACT_CHEMICAL_APPLICATION) ===\n")
        q_chem = text("""
            SELECT COUNT(*) 
            FROM dw.fact_chemical_application f
            LEFT JOIN dw.dim_chemical_substance s ON f.chemical_key = s.chemical_key
            WHERE s.chemical_key IS NULL
        """)
        null_chem = conn.execute(q_chem).scalar()
        f.write(f"Registros en fact_chemical_application sin match en dim_chemical_substance: {null_chem}\n")

        f.write("\n=== MUESTRA DE DATOS (fact_waste_generation) ===\n")
        res = conn.execute(text("SELECT * FROM dw.fact_waste_generation LIMIT 5"))
        for row in res:
            f.write(f"{row}\n")

print("Validation complete. Results in d:/DashboardRA/data_validation_results.txt")
