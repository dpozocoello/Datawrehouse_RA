from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@localhost:5432/dw_reg_v1")

with engine.connect() as conn:
    r = conn.execute(text("""
        SELECT f.origen, COUNT(*) as registros, COUNT(DISTINCT p.codigo_proyecto) as proyectos_unicos,
               MIN(f.fecha_inicio_proceso)::text as min_inicio, MAX(f.fecha_inicio_proceso)::text as max_inicio,
               COUNT(f.fecha_inicio_proceso) as con_fecha, COUNT(*) - COUNT(f.fecha_inicio_proceso) as sin_fecha
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
        GROUP BY f.origen
        ORDER BY proyectos_unicos DESC
    """))
    
    with open("d:/DashboardRA/tmp_results.txt", "w", encoding="utf-8") as out:
        out.write("=== RESUMEN POR ORIGEN ===\n")
        for row in r:
            d = dict(row._mapping)
            out.write(f"  {d['origen']:15s} | proy_unicos={d['proyectos_unicos']:>7} | registros={d['registros']:>7} | con_fecha={d['con_fecha']:>7} | sin_fecha={d['sin_fecha']:>5} | [{d['min_inicio']} to {d['max_inicio']}]\n")

        r2 = conn.execute(text("""
            SELECT p.codigo_proyecto, SUBSTRING(p.nombre_proyecto,1,50) as nombre, f.origen, f.proceso, f.tarea,
                   f.fecha_inicio_proceso::text as fi, f.fecha_fin_proceso::text as ff
            FROM dw.fact_regularizacion f
            JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
            WHERE f.origen = 'RECUPERADO'
            AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
            LIMIT 5
        """))
        out.write("\n=== MUESTRA RECUPERADO ===\n")
        for row in r2:
            d = dict(row._mapping)
            out.write(f"  {d['codigo_proyecto']:35s} | proceso={d['proceso']} | tarea={d['tarea']} | fi={d['fi']} | ff={d['ff']}\n")

        r3 = conn.execute(text("SELECT COUNT(*) as n FROM dw.dim_proyecto WHERE nombre_proyecto = 'Proyecto Recuperado (JBPM)'"))
        d3 = dict(r3.fetchone()._mapping)
        out.write(f"\n=== Proyectos 'Recuperado (JBPM)' en dim_proyecto (EXCLUIDOS del dashboard): {d3['n']} ===\n")

        r4 = conn.execute(text("""
            SELECT COUNT(DISTINCT p.codigo_proyecto) as n
            FROM dw.fact_regularizacion f JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
            WHERE f.origen = 'RECUPERADO' AND p.nombre_proyecto = 'Proyecto Recuperado (JBPM)'
        """))
        d4 = dict(r4.fetchone()._mapping)
        out.write(f"=== RECUPERADO con nombre 'Proyecto Recuperado (JBPM)' (ya excluidos): {d4['n']} ===\n")

print("Done. Results in d:/DashboardRA/tmp_results.txt")
