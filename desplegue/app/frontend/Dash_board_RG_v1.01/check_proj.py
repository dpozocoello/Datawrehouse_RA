from sqlalchemy import create_engine, text

def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1?client_encoding=utf8")

def check_specific_project(cp):
    engine = get_engine()
    with engine.connect() as conn:
        print(f"Checking project: {cp}")
        query = text("""
        SELECT p.codigo_proyecto, f.interseccion_snap,
               EXISTS (SELECT 1 FROM dw.bridge_interseccion_ambiental b WHERE b.sk_proyecto = p.sk_proyecto) as bridge_exists,
               (SELECT string_agg(c.nombre_capa, ', ') 
                FROM dw.bridge_interseccion_ambiental b 
                JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa 
                WHERE b.sk_proyecto = p.sk_proyecto) as bridge_layers
        FROM dw.dim_proyecto p
        JOIN dw.fact_regularizacion f ON p.sk_proyecto = f.sk_proyecto
        WHERE p.codigo_proyecto = :cp
        ORDER BY f.fecha_inicio_proceso DESC
        LIMIT 1
        """)
        res = conn.execute(query, {"cp": cp}).fetchone()
        if res:
            print(f"interseccion_snap: |{res[1]}|")
            print(f"bridge_exists: {res[2]}")
            print(f"bridge_layers: {res[3]}")
        else:
            print("Project not found.")

if __name__ == "__main__":
    check_specific_project("MAAE-RA-2020-368524")
