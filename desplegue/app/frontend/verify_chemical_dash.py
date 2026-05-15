from sqlalchemy import create_engine, text
import pandas as pd
import sys
import os

# Add the dashboard directory to path if needed (though we'll copy functions or import them)
# For simplicity, I'll redefine the engine and test the queries directly as they are in the dashboard

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def test_load_chemical_import_summary():
    print("Testing load_chemical_import_summary...")
    query = """
    SELECT 
        COALESCE(s.substance_name, 'Desconocida') as substance_name,
        COALESCE(imp.importer_name, 'S/I') as importer_name,
        SUM(f.quantity_authorized) as total_authorized,
        SUM(f.net_weight) as total_net_weight,
        f.source_system
    FROM dw.fact_chemical_import f
    JOIN dw.dim_chemical_substance s ON f.chemical_key = s.chemical_key
    LEFT JOIN dw.dim_chemical_importer imp ON f.importer_key = imp.importer_key
    GROUP BY 1, 2, 5
    ORDER BY total_authorized DESC
    LIMIT 5
    """
    df = pd.read_sql(query, get_engine())
    print(df.to_string())
    print("-" * 20)

def test_load_chemical_movement_summary():
    print("Testing load_chemical_movement_summary...")
    query = """
    SELECT 
        COALESCE(s.substance_name, 'Desconocida') as substance_name,
        SUM(f.quantity_entry) as total_entry,
        SUM(f.quantity_exit) as total_exit,
        (SUM(f.quantity_entry) - SUM(f.quantity_exit)) as balance,
        f.operator_name
    FROM dw.fact_chemical_movement f
    JOIN dw.dim_chemical_substance s ON f.chemical_key = s.chemical_key
    GROUP BY 1, 5
    ORDER BY balance DESC
    LIMIT 5
    """
    df = pd.read_sql(query, get_engine())
    print(df.to_string())
    print("-" * 20)

def test_load_chemical_declaration_summary():
    print("Testing load_chemical_declaration_summary...")
    query = """
    SELECT 
        COALESCE(imp.importer_name, 'S/I') as importer_name,
        SUM(f.initial_quantity) as total_initial,
        SUM(f.final_quantity) as total_final,
        f.declaration_year,
        f.declaration_month
    FROM dw.fact_chemical_declaration f
    LEFT JOIN dw.dim_chemical_importer imp ON f.importer_key = imp.importer_key
    GROUP BY 1, 4, 5
    ORDER BY f.declaration_year DESC, f.declaration_month DESC
    LIMIT 5
    """
    df = pd.read_sql(query, get_engine())
    print(df.to_string())
    print("-" * 20)

if __name__ == "__main__":
    try:
        test_load_chemical_import_summary()
        test_load_chemical_movement_summary()
        test_load_chemical_declaration_summary()
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
