from sqlalchemy import create_engine, text

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        for table in ['dim_capa_ambiental', 'bridge_interseccion_ambiental']:
            print(f"\n--- Columns in {table} ---")
            query = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = '{table}'")
            result = conn.execute(query)
            for col in result:
                print(f"Col: {col[0]}, Type: {col[1]}")
                
        print("\n--- Sample data from dim_capa_ambiental ---")
        sample = conn.execute(text("SELECT * FROM dw.dim_capa_ambiental LIMIT 5"))
        for row in sample:
            print(row)

except Exception as e:
    print(f"Error: {e}")
