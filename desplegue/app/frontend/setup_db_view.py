import psycopg2
import sys

def create_view():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "dw_reg_v1",
        "user": "postgres",
        "password": "postgres" # Ajustar si es diferente
    }
    
    sql = """
    CREATE VIEW dw.v_integridad_dashboard AS
    WITH cte_stg AS (
        SELECT 'RCOA'        AS origen, COUNT(*) AS registros_stg FROM stg.suia_rcoa_bi
        UNION ALL
        SELECT 'COA',                   COUNT(*)                   FROM stg.suia_coa_bi
        UNION ALL
        SELECT 'JBPM_SECTOR',           COUNT(*)                   FROM stg.jbpm_sector_bi
        UNION ALL
        SELECT 'JBPM_4CAT',             COUNT(*)                   FROM stg.jbpm_4cat_bi
        UNION ALL
        SELECT 'JBPM_HIDRO',            COUNT(*)                   FROM stg.jbpm_hidro_bi
    ),
    cte_fact AS (
        SELECT
            f.origen,
            COUNT(*)                      AS registros_dw,
            COUNT(DISTINCT CASE
                WHEN p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
                THEN f.sk_proyecto
            END)                          AS proyectos_unicos_dw
        FROM dw.fact_regularizacion f
        JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
        GROUP BY f.origen
    )
    SELECT
        s.origen,
        s.registros_stg                                     AS total_produccion,
        COALESCE(f.registros_dw, 0)                         AS total_dwh,
        COALESCE(f.proyectos_unicos_dw, 0)                  AS proyectos_unicos_dwh,
        (s.registros_stg - COALESCE(f.registros_dw, 0))     AS diferencia,
        CASE
            WHEN s.registros_stg = 0 THEN 100
            ELSE ROUND(
                COALESCE(f.registros_dw, 0)::numeric
                / s.registros_stg::numeric * 100,
                2
            )
        END AS porcentaje_integridad
    FROM cte_stg s
    LEFT JOIN cte_fact f ON s.origen = f.origen;

    COMMENT ON VIEW dw.v_integridad_dashboard IS
        'Contrasta registros entre Staging (Produccion) y DWH. '
        'total_dwh = filas cargadas (validacion ETL). '
        'proyectos_unicos_dwh = proyectos distintos sin recuperados (KPIs dashboard).';
    """
    
    try:
        print(f"Conectando a la base de datos {conn_params['database']}...")
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cur = conn.cursor()
        print("Eliminando vista anterior dw.v_integridad_dashboard...")
        cur.execute("DROP VIEW IF EXISTS dw.v_integridad_dashboard;")
        print("Creando vista dw.v_integridad_dashboard...")
        cur.execute(sql)
        print("¡Vista creada exitosamente!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_view()
