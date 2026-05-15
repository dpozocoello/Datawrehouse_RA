import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connections import get_connection
from config import CONN_DWH_LOCAL

with get_connection(CONN_DWH_LOCAL) as conn:
    with conn.cursor() as cur:
        cur.execute("""SELECT schemaname||'.'||tablename as tabla,
                              pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as tamano,
                              pg_total_relation_size(schemaname||'.'||tablename) as bytes
                       FROM pg_tables WHERE schemaname IN ('dw','stg')
                       ORDER BY bytes DESC LIMIT 15""")
        print("TOP 15 TABLAS POR TAMANO:")
        for r in cur.fetchall(): print(f"  {r[0]:<50} {r[1]:>10}")

        cur.execute("SELECT pg_size_pretty(pg_database_size('dw_reg_v1'))")
        print("\nTAMANO TOTAL DWH:", cur.fetchone()[0])

        cur.execute("SELECT origen, COUNT(*) FROM dw.fact_regularizacion GROUP BY origen ORDER BY 2 DESC")
        print("\nFACT_REGULARIZACION POR ORIGEN:")
        for r in cur.fetchall(): print(f"  {r[0]:<25} {r[1]:>10,}")

        cur.execute("SELECT origen, COUNT(*) FROM dw.fact_pago GROUP BY origen ORDER BY 2 DESC")
        print("\nFACT_PAGO POR ORIGEN:")
        for r in cur.fetchall(): print(f"  {r[0]:<25} {r[1]:>10,}")

        cur.execute("SELECT COUNT(DISTINCT sk_proponente) FROM dw.fact_regularizacion WHERE sk_proponente != 0")
        print("\nPROPONENTES UNICOS EN HECHOS:", f"{cur.fetchone()[0]:,}")

        cur.execute("SELECT COUNT(DISTINCT sk_proyecto) FROM dw.fact_regularizacion WHERE sk_proyecto != 0")
        print("PROYECTOS CON HECHOS:", f"{cur.fetchone()[0]:,}")

        cur.execute("SELECT MIN(fecha), MAX(fecha) FROM dw.dim_tiempo WHERE sk_tiempo != 0")
        r = cur.fetchone()
        print(f"RANGO TEMPORAL: {r[0]} a {r[1]}")

        cur.execute("""SELECT COUNT(*) FROM dw.fact_regularizacion fr
                       JOIN dw.fact_proyecto_geografia fpg ON fr.sk_proyecto = fpg.sk_proyecto""")
        print("PROYECTOS CON GEOREFERENCIA:", f"{cur.fetchone()[0]:,}")
