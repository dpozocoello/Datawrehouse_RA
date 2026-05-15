"""
Paso 32 del ETL — Enriquecimiento de Coordenadas y Contactos v3.0

Extrae datos de:
  SUIA (179): suia_iii.coordinates (centroides) + vwt_rgd_dashboard (email)
  JBPM (226): public.coordenada + vw_subsect_pro_can_parr (contactos)

Actualiza: stg.consolidado_proyectos → dw.dim_proyecto / dim_proponente
"""
import psycopg2
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONN_DWH_LOCAL
from utils.logger import get_logger

logger = get_logger("ENRIQUECIMIENTO_v3")


def ejecutar_enriquecimiento_contactos_coords():
    """Paso 32: Enriquecimiento de coordenadas y contactos para TODOS los proyectos."""
    logger.info("=" * 60)
    logger.info("ENRIQUECIMIENTO v3.0 — Coordenadas + Contactos (todos)")
    logger.info("=" * 60)

    dsn = f"host={CONN_DWH_LOCAL['host']} port={CONN_DWH_LOCAL['port']} " \
          f"dbname={CONN_DWH_LOCAL['database']} user={CONN_DWH_LOCAL['user']} " \
          f"password={CONN_DWH_LOCAL['password']}"
    conn = psycopg2.connect(dsn)
    conn.autocommit = True

    def _exec(desc, sql):
        try:
            cur = conn.cursor()
            cur.execute(sql)
            cnt = cur.rowcount
            cur.close()
            logger.info(f"  {desc}: {cnt} filas")
            return cnt
        except Exception as e:
            conn.rollback()
            logger.error(f"  {desc}: ERROR — {e}")
            return -1

    # ================================================================
    # 1) COORDENADAS SUIA (MAAE-*) — Server 179
    # ================================================================
    logger.info("\n[1/6] Centroides SUIA (179) — pren → shapes → coordinates")
    _exec("DROP tmp", "DROP TABLE IF EXISTS tmp_coords_suia;")
    _exec("Centroides SUIA", """
        CREATE TEMP TABLE tmp_coords_suia AS
        SELECT * FROM dblink(
            'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
            'SELECT
                pel.pren_code AS codigo_proyecto,
                AVG(co.coor_x) AS coordenada_x,
                AVG(co.coor_y) AS coordenada_y
             FROM suia_iii.projects_environmental_licensing pel
             JOIN suia_iii.project_shapes ps
                ON ps.pren_id = pel.pren_id AND ps.prsh_status = true
             JOIN suia_iii.coordinates co
                ON co.prsh_id = ps.prsh_id AND co.coor_status = true
             WHERE pel.pren_code IS NOT NULL
               AND co.coor_x IS NOT NULL AND co.coor_y IS NOT NULL
               AND co.coor_x > 0 AND co.coor_x < 1000000
               AND co.coor_y > 0 AND co.coor_y < 20000000
             GROUP BY pel.pren_code'
        ) AS t(
            codigo_proyecto TEXT,
            coordenada_x DOUBLE PRECISION,
            coordenada_y DOUBLE PRECISION
        );
    """)

    # ================================================================
    # 2) COORDENADAS JBPM (MAE-RA-*) — Server 226
    # ================================================================
    logger.info("\n[2/6] Coordenadas JBPM (226) — public.coordenada")
    _exec("DROP tmp", "DROP TABLE IF EXISTS tmp_coords_jbpm;")
    _exec("Coords JBPM prod_old", """
        CREATE TEMP TABLE tmp_coords_jbpm AS
        SELECT * FROM dblink(
            'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT
                proyecto_id,
                AVG(coordenadax) AS coordenada_x,
                AVG(coordenaday) AS coordenada_y
             FROM public.coordenada
             WHERE proyecto_id IS NOT NULL
               AND coordenadax IS NOT NULL AND coordenaday IS NOT NULL
               AND coordenadax > 0 AND coordenadax < 1000000
             GROUP BY proyecto_id'
        ) AS t(codigo_proyecto TEXT, coordenada_x DOUBLE PRECISION, coordenada_y DOUBLE PRECISION);
    """)
    _exec("Coords JBPM actual", """
        INSERT INTO tmp_coords_jbpm
        SELECT * FROM dblink(
            'dbname=jbpmdb port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT proyecto_id, AVG(coordenadax), AVG(coordenaday)
             FROM public.coordenada
             WHERE proyecto_id IS NOT NULL AND coordenadax IS NOT NULL
               AND coordenadax > 0 AND coordenadax < 1000000
             GROUP BY proyecto_id'
        ) AS t(codigo_proyecto TEXT, coordenada_x DOUBLE PRECISION, coordenada_y DOUBLE PRECISION)
        ON CONFLICT DO NOTHING;
    """)

    # ================================================================
    # 3) CONTACTOS SUIA — vwt_rgd_dashboard (179)
    # ================================================================
    logger.info("\n[3/6] Contactos SUIA (179) — vwt_rgd_dashboard")
    _exec("DROP tmp", "DROP TABLE IF EXISTS tmp_contacts_suia;")
    _exec("Contactos SUIA", """
        CREATE TEMP TABLE tmp_contacts_suia AS
        SELECT * FROM dblink(
            'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
            'SELECT DISTINCT ON ("CÓDIGO ASOCIADO")
                "CÓDIGO ASOCIADO" AS codigo_proyecto,
                "CORREO ELECTRONICO" AS correo_electronico,
                "CEDULA PROPONENTE" AS cedula,
                "PROPONENTE" AS nombre_proponente
             FROM suia_iii.vwt_rgd_dashboard
             WHERE "CÓDIGO ASOCIADO" IS NOT NULL
               AND "CORREO ELECTRONICO" IS NOT NULL
             ORDER BY "CÓDIGO ASOCIADO", "FECHA DE CREACIÓN" DESC NULLS LAST'
        ) AS t(
            codigo_proyecto TEXT, correo_electronico TEXT,
            cedula TEXT, nombre_proponente TEXT
        );
    """)

    # ================================================================
    # 4) CONTACTOS JBPM (226)
    # ================================================================
    logger.info("\n[4/6] Contactos JBPM (226)")
    _exec("DROP tmp", "DROP TABLE IF EXISTS tmp_contacts_jbpm;")
    _exec("Contactos JBPM", """
        CREATE TEMP TABLE tmp_contacts_jbpm AS
        SELECT * FROM dblink(
            'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT DISTINCT
                "COD_PROYECTO", "EMAIL", COALESCE("TELEFONO","CELULAR")
             FROM public.vw_subsect_pro_can_parr
             WHERE "COD_PROYECTO" IS NOT NULL
               AND ("EMAIL" IS NOT NULL OR "TELEFONO" IS NOT NULL OR "CELULAR" IS NOT NULL)'
        ) AS t(codigo_proyecto TEXT, correo_electronico TEXT, telefono TEXT);
    """)
    _exec("Contactos vw_suia_cat", """
        INSERT INTO tmp_contacts_jbpm
        SELECT * FROM dblink(
            'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT DISTINCT
                cod_proyecto, email, COALESCE(telefono, celular)
             FROM public.vw_suia_categorias_at
             WHERE cod_proyecto IS NOT NULL
               AND (email IS NOT NULL OR telefono IS NOT NULL OR celular IS NOT NULL)'
        ) AS t(codigo_proyecto TEXT, correo_electronico TEXT, telefono TEXT)
        ON CONFLICT DO NOTHING;
    """)

    # ================================================================
    # 5) ACTUALIZAR consolidado_proyectos
    # ================================================================
    logger.info("\n[5/6] Actualizando stg.consolidado_proyectos...")

    _exec("UPDATE coords SUIA", """
        UPDATE stg.consolidado_proyectos cp
        SET coordenada_x = t.coordenada_x, coordenada_y = t.coordenada_y
        FROM tmp_coords_suia t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.coordenada_x IS NULL OR cp.coordenada_x = 0);
    """)
    _exec("UPDATE coords JBPM", """
        UPDATE stg.consolidado_proyectos cp
        SET coordenada_x = t.coordenada_x, coordenada_y = t.coordenada_y
        FROM tmp_coords_jbpm t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.coordenada_x IS NULL OR cp.coordenada_x = 0);
    """)
    _exec("UPDATE contactos SUIA", """
        UPDATE stg.consolidado_proyectos cp
        SET correo_electronico = t.correo_electronico
        FROM tmp_contacts_suia t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.correo_electronico IS NULL OR cp.correo_electronico = '');
    """)
    _exec("UPDATE contactos JBPM", """
        UPDATE stg.consolidado_proyectos cp
        SET correo_electronico = COALESCE(cp.correo_electronico, t.correo_electronico),
            telefono = COALESCE(cp.telefono, t.telefono)
        FROM tmp_contacts_jbpm t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.correo_electronico IS NULL OR cp.telefono IS NULL
               OR cp.correo_electronico = '' OR cp.telefono = '');
    """)

    # ================================================================
    # 6) VALIDACIÓN
    # ================================================================
    logger.info("\n[6/6] Validación...")
    cur = conn.cursor()
    for name, sql in [
        ("consolidado coords",
         "SELECT COUNT(*) FILTER (WHERE coordenada_x IS NOT NULL AND coordenada_x != 0), COUNT(*) FROM stg.consolidado_proyectos"),
        ("consolidado email",
         "SELECT COUNT(*) FILTER (WHERE correo_electronico IS NOT NULL AND correo_electronico != ''), COUNT(*) FROM stg.consolidado_proyectos"),
        ("dim_proyecto coords",
         "SELECT COUNT(*) FILTER (WHERE coordenada_x IS NOT NULL AND coordenada_x != 0), COUNT(*) FROM dw.dim_proyecto"),
        ("dim_proponente email",
         "SELECT COUNT(*) FILTER (WHERE correo_electronico IS NOT NULL AND correo_electronico != ''), COUNT(*) FROM dw.dim_proponente"),
    ]:
        try:
            cur.execute(sql)
            f, t = cur.fetchone()
            logger.info(f"  {name}: {f:,} / {t:,} ({round(f*100/max(t,1),1)}%)")
        except Exception as e:
            conn.rollback()
            logger.error(f"  {name}: ERROR — {e}")
    cur.close()

    # Cleanup
    for t in ['tmp_coords_suia', 'tmp_coords_jbpm', 'tmp_contacts_suia', 'tmp_contacts_jbpm']:
        _exec(f"DROP {t}", f"DROP TABLE IF EXISTS {t};")

    conn.close()
    logger.info("Enriquecimiento v3.0 completado.")
