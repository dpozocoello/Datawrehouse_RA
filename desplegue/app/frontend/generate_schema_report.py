from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

tables = [
    'fact_waste_generation',
    'dim_waste_generator',
    'dim_waste_type',
    'dim_dangerous_waste',
    'dim_dangerous_classification',
    'fact_chemical_application',
    'dim_chemical_substance',
    'dim_chemical_storage',
    'fact_project_environmental_impact'
]

with open('d:/DashboardRA/technical_schema_report.md', 'w', encoding='utf-8') as f:
    f.write("# Technical Schema Report: Waste and Chemicals\n\n")
    
    with engine.connect() as conn:
        for t in tables:
            f.write(f"## Table: dw.{t}\n\n")
            f.write("| Column | Type |\n")
            f.write("| :--- | :--- |\n")
            
            query = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = '{t}' ORDER BY ordinal_position")
            res = conn.execute(query)
            for row in res:
                f.write(f"| {row[0]} | {row[1]} |\n")
            f.write("\n")

print("Report generated: d:/DashboardRA/technical_schema_report.md")
