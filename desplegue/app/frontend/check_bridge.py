from sqlalchemy import create_engine, text

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/dw_reg_v1')
    with engine.connect() as conn:
        print("--- Bridge table columns ---")
        q = text("SELECT column_name FROM information_schema.columns WHERE table_schema='dw' AND table_name='bridge_interseccion_ambiental'")
        res = conn.execute(q)
        for r in res:
            print(r[0])
except Exception as e:
    print(f"Error: {e}")
