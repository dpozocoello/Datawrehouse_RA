import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')

def trace_hierarchy():
    print("\n--- HIERARCHY TRACE: dim_area ---")
    df = pd.read_sql("SELECT sk_area, id_area, nombre_area, id_area_padre, zona, provincia FROM dw.dim_area", engine)
    
    # Let's find some nodes that have a parent
    df_with_parent = df[df['id_area_padre'].notnull() & (df['id_area_padre'] != 0)]
    print(f"Nodes with parent: {len(df_with_parent)}")
    print(df_with_parent.head(10).to_string())

    # Let's see some top level nodes
    df_top = df[(df['id_area_padre'].isnull()) | (df['id_area_padre'] == 0)]
    print(f"\nTop level nodes: {len(df_top)}")
    print(df_top.head(10).to_string())

    # Check if 'nombre_area' contains clues like 'DIRECCIÓN ZONAL' or 'OFICINA TÉCNICA'
    print("\n--- SAMPLE names ---")
    print(df['nombre_area'].sample(20).to_string())

if __name__ == "__main__":
    trace_hierarchy()
