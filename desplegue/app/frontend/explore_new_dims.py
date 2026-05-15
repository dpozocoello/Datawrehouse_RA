from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

print("=== BÚSQUEDA DE TABLAS RELACIONADAS A DESECHOS, RESIDUOS Y SUSTANCIAS QUÍMICAS ===")
with engine.connect() as conn:
    # Buscar tablas en esquema dw que contengan palabras clave
    query = text("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'dw' 
        AND (table_name ILIKE '%desecho%' OR table_name ILIKE '%residuo%' OR table_name ILIKE '%quimic%' OR table_name ILIKE '%sustancia%' OR table_name ILIKE '%gen%')
    """)
    res = conn.execute(query)
    tables = [row[1] for row in res]
    
    if not tables:
        print("No se encontraron tablas con esos nombres exactos en dw. Listando todas las tablas en dw:")
        res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw'"))
        for row in res:
            print(f" - {row[0]}")
    else:
        for t in tables:
            print(f"\n--- Estructura de la tabla: dw.{t} ---")
            cols = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = '{t}'"))
            for col in cols:
                print(f"  {col[0]} ({col[1]})")
                
    # Voy a ver si en dim_proyecto o fact_regularizacion hay nuevos campos
    print("\n--- Campos nuevos en dw.dim_proyecto ---")
    cols = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'dim_proyecto'"))
    for col in cols:
        if any(x in col[0] for x in ['desecho', 'residuo', 'quimic', 'sustancia', 'generador']):
            print(f"  {col[0]} ({col[1]})")

    print("\n--- Campos nuevos en dw.fact_regularizacion ---")
    cols = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'dw' AND table_name = 'fact_regularizacion'"))
    for col in cols:
        if any(x in col[0] for x in ['desecho', 'residuo', 'quimic', 'sustancia', 'generador']):
            print(f"  {col[0]} ({col[1]})")
