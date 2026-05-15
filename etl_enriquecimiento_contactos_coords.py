"""
ETL de Enriquecimiento v3.0 — Extracción de coordenadas y contactos
desde SUIA (179) y JBPM (226) para TODOS los proyectos.

Cadenas de extracción:
  COORDENADAS SUIA (MAAE-*):
    projects_environmental_licensing.pren_code
    → project_shapes.pren_id (prsh_status=true)
    → coordinates.prsh_id (coor_x, coor_y)
    → AVG() por proyecto = centroide

  COORDENADAS JBPM (MAE-RA-*):
    coordenada.proyecto_id → AVG(coordenadax, coordenaday)

  CONTACTOS SUIA:
    vwt_rgd_dashboard → CORREO ELECTRONICO por CÓDIGO ASOCIADO

  CONTACTOS JBPM:
    vw_subsect_pro_can_parr → COD_PROYECTO, EMAIL, TELEFONO
    vw_suia_categorias_at → cod_proyecto, email, telefono

Integrado como Paso 32 del ETL.
"""
import psycopg2
import sys
import os
from datetime import datetime

LOG_DIR = r"D:\Datawrehouse_RA\logs"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"enriquecimiento_v3_{TIMESTAMP}.log")
os.makedirs(LOG_DIR, exist_ok=True)

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

DWH_LOCAL = {
    "host": "localhost", "port": 5432,
    "dbname": "dw_reg_v1", "user": "postgres", "password": "postgres"
}

def _exec(conn, desc, sql):
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cnt = cur.rowcount
        cur.close()
        log(f"  {desc}: {cnt} filas")
        return cnt
    except Exception as e:
        conn.rollback()
        log(f"  {desc}: ERROR — {e}")
        return -1

def main():
    log("=" * 70)
    log(f"ENRIQUECIMIENTO ETL v3.0 — TODOS LOS PROYECTOS")
    log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 70)

    conn = psycopg2.connect(**DWH_LOCAL)
    conn.autocommit = True

    # ==================================================================
    # FASE 1: COORDENADAS SUIA (MAAE-*) — Server 179
    # Cadena: pren_code → project_shapes → coordinates → AVG centroide
    # ==================================================================
    log("\n[1/8] Extrayendo centroides SUIA (179) — proyectos MAAE...")
    _exec(conn, "DROP tmp", "DROP TABLE IF EXISTS tmp_coords_suia;")
    cnt = _exec(conn, "Centroides SUIA", """
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

    if cnt >= 0:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tmp_coords_suia;")
        log(f"  → Proyectos SUIA con centroide: {cur.fetchone()[0]}")
        cur.execute("SELECT * FROM tmp_coords_suia LIMIT 3;")
        for r in cur.fetchall():
            log(f"    {r}")
        cur.close()

    # ==================================================================
    # FASE 2: COORDENADAS COA (coa_mae) — Server 179
    # Para proyectos COA que NO están en suia_iii
    # ==================================================================
    log("\n[2/8] Extrayendo centroides COA (179) — coa_mae...")
    _exec(conn, "DROP tmp", "DROP TABLE IF EXISTS tmp_coords_coa;")
    cnt = _exec(conn, "Centroides COA", """
        CREATE TEMP TABLE tmp_coords_coa AS
        SELECT * FROM dblink(
            'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
            'SELECT
                plc.prco_name AS nombre_proyecto,
                plc.prco_id,
                AVG(cplc.coor_x) AS coordenada_x,
                AVG(cplc.coor_y) AS coordenada_y
             FROM coa_mae.project_licencing_coa plc
             JOIN coa_mae.project_licencing_coa_shapes plcs 
                ON plcs.prco_id = plc.prco_id AND plcs.prsh_status = true
             JOIN coa_mae.coordinates_project_licencing_coa cplc 
                ON cplc.prsh_id = plcs.prsh_id AND cplc.coor_status = true
             WHERE cplc.coor_x IS NOT NULL AND cplc.coor_y IS NOT NULL
               AND cplc.coor_x > 0 AND cplc.coor_x < 1000000
               AND cplc.coor_y > 0 AND cplc.coor_y < 20000000
             GROUP BY plc.prco_name, plc.prco_id'
        ) AS t(
            nombre_proyecto TEXT,
            prco_id INTEGER,
            coordenada_x DOUBLE PRECISION,
            coordenada_y DOUBLE PRECISION
        );
    """)

    if cnt >= 0:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tmp_coords_coa;")
        log(f"  → Proyectos COA con centroide: {cur.fetchone()[0]}")
        cur.execute("SELECT * FROM tmp_coords_coa LIMIT 3;")
        for r in cur.fetchall():
            log(f"    {r}")
        cur.close()

    # ==================================================================
    # FASE 3: COORDENADAS JBPM (MAE-RA-*) — Server 226
    # ==================================================================
    log("\n[3/8] Extrayendo coordenadas JBPM (226) — proyectos MAE-RA...")
    _exec(conn, "DROP tmp", "DROP TABLE IF EXISTS tmp_coords_jbpm;")
    _exec(conn, "Coords JBPM prod_old", """
        CREATE TEMP TABLE tmp_coords_jbpm AS
        SELECT * FROM dblink(
            'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT
                proyecto_id AS codigo_proyecto,
                AVG(coordenadax) AS coordenada_x,
                AVG(coordenaday) AS coordenada_y
             FROM public.coordenada
             WHERE proyecto_id IS NOT NULL
               AND coordenadax IS NOT NULL AND coordenaday IS NOT NULL
               AND coordenadax > 0 AND coordenadax < 1000000
             GROUP BY proyecto_id'
        ) AS t(
            codigo_proyecto TEXT,
            coordenada_x DOUBLE PRECISION,
            coordenada_y DOUBLE PRECISION
        );
    """)

    # Complementar con jbpmdb actual
    _exec(conn, "Coords JBPM actual", """
        INSERT INTO tmp_coords_jbpm
        SELECT * FROM dblink(
            'dbname=jbpmdb port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT
                proyecto_id AS codigo_proyecto,
                AVG(coordenadax) AS coordenada_x,
                AVG(coordenaday) AS coordenada_y
             FROM public.coordenada
             WHERE proyecto_id IS NOT NULL
               AND coordenadax IS NOT NULL AND coordenaday IS NOT NULL
               AND coordenadax > 0 AND coordenadax < 1000000
             GROUP BY proyecto_id'
        ) AS t(
            codigo_proyecto TEXT,
            coordenada_x DOUBLE PRECISION,
            coordenada_y DOUBLE PRECISION
        )
        ON CONFLICT DO NOTHING;
    """)

    # ==================================================================
    # FASE 4: CONTACTOS SUIA — vwt_rgd_dashboard (179)
    # ==================================================================
    log("\n[4/8] Extrayendo contactos SUIA (179) — vwt_rgd_dashboard...")
    _exec(conn, "DROP tmp", "DROP TABLE IF EXISTS tmp_contacts_suia;")
    _exec(conn, "Contactos SUIA", """
        CREATE TEMP TABLE tmp_contacts_suia AS
        SELECT * FROM dblink(
            'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
            'SELECT DISTINCT
                "CÓDIGO ASOCIADO" AS codigo_proyecto,
                "CORREO ELECTRONICO" AS correo_electronico,
                "CEDULA PROPONENTE" AS cedula,
                "PROPONENTE" AS nombre_proponente
             FROM suia_iii.vwt_rgd_dashboard
             WHERE "CÓDIGO ASOCIADO" IS NOT NULL
               AND "CORREO ELECTRONICO" IS NOT NULL'
        ) AS t(
            codigo_proyecto TEXT,
            correo_electronico TEXT,
            cedula TEXT,
            nombre_proponente TEXT
        );
    """)

    if cnt >= 0:
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(DISTINCT codigo_proyecto) FROM tmp_contacts_suia;")
            log(f"  → Proyectos SUIA con contacto: {cur.fetchone()[0]}")
        except:
            conn.rollback()
        cur.close()

    # ==================================================================
    # FASE 5: CONTACTOS JBPM (226)
    # ==================================================================
    log("\n[5/8] Extrayendo contactos JBPM (226)...")
    _exec(conn, "DROP tmp", "DROP TABLE IF EXISTS tmp_contacts_jbpm;")
    _exec(conn, "Contactos JBPM", """
        CREATE TEMP TABLE tmp_contacts_jbpm AS
        SELECT * FROM dblink(
            'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT DISTINCT
                "COD_PROYECTO" AS codigo_proyecto,
                "EMAIL" AS correo_electronico,
                COALESCE("TELEFONO", "CELULAR") AS telefono
             FROM public.vw_subsect_pro_can_parr
             WHERE "COD_PROYECTO" IS NOT NULL
               AND ("EMAIL" IS NOT NULL OR "TELEFONO" IS NOT NULL OR "CELULAR" IS NOT NULL)'
        ) AS t(
            codigo_proyecto TEXT,
            correo_electronico TEXT,
            telefono TEXT
        );
    """)

    # Complementar con vw_suia_categorias_at
    _exec(conn, "Contactos vw_suia_cat", """
        INSERT INTO tmp_contacts_jbpm
        SELECT * FROM dblink(
            'dbname=jbpmdb_prod_old port=5432 host=172.16.0.226 user=postgres password=postgres',
            'SELECT DISTINCT
                cod_proyecto AS codigo_proyecto,
                email AS correo_electronico,
                COALESCE(telefono, celular) AS telefono
             FROM public.vw_suia_categorias_at
             WHERE cod_proyecto IS NOT NULL
               AND (email IS NOT NULL OR telefono IS NOT NULL OR celular IS NOT NULL)'
        ) AS t(
            codigo_proyecto TEXT,
            correo_electronico TEXT,
            telefono TEXT
        )
        ON CONFLICT DO NOTHING;
    """)

    # ==================================================================
    # FASE 6: ACTUALIZAR consolidado_proyectos
    # ==================================================================
    log("\n[6/8] Actualizando stg.consolidado_proyectos...")

    # 6a: Coords SUIA (MAAE)
    _exec(conn, "UPDATE coords SUIA", """
        UPDATE stg.consolidado_proyectos cp
        SET coordenada_x = t.coordenada_x,
            coordenada_y = t.coordenada_y
        FROM tmp_coords_suia t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.coordenada_x IS NULL OR cp.coordenada_x = 0);
    """)

    # 6b: Coords JBPM (MAE-RA)
    _exec(conn, "UPDATE coords JBPM", """
        UPDATE stg.consolidado_proyectos cp
        SET coordenada_x = t.coordenada_x,
            coordenada_y = t.coordenada_y
        FROM tmp_coords_jbpm t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.coordenada_x IS NULL OR cp.coordenada_x = 0);
    """)

    # 6c: Contactos SUIA
    _exec(conn, "UPDATE contactos SUIA", """
        UPDATE stg.consolidado_proyectos cp
        SET correo_electronico = t.correo_electronico
        FROM tmp_contacts_suia t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.correo_electronico IS NULL OR cp.correo_electronico = '');
    """)

    # 6d: Contactos JBPM
    _exec(conn, "UPDATE contactos JBPM", """
        UPDATE stg.consolidado_proyectos cp
        SET correo_electronico = COALESCE(cp.correo_electronico, t.correo_electronico),
            telefono = COALESCE(cp.telefono, t.telefono)
        FROM tmp_contacts_jbpm t
        WHERE cp.codigo_proyecto = t.codigo_proyecto
          AND (cp.correo_electronico IS NULL OR cp.telefono IS NULL
               OR cp.correo_electronico = '' OR cp.telefono = '');
    """)

    # ==================================================================
    # FASE 7: REFRESCAR DIMENSIONES
    # ==================================================================
    log("\n[7/8] Refrescando dimensiones...")
    _exec(conn, "sp_carga_dimensiones()", "SELECT dw.sp_carga_dimensiones();")

    # ==================================================================
    # FASE 8: VALIDACIÓN
    # ==================================================================
    log("\n[8/8] Validación post-enriquecimiento...")
    cur = conn.cursor()

    validaciones = [
        ("Consolidado con coordenadas",
         "SELECT COUNT(*) FILTER (WHERE coordenada_x IS NOT NULL AND coordenada_x != 0), COUNT(*) FROM stg.consolidado_proyectos"),
        ("Consolidado con email",
         "SELECT COUNT(*) FILTER (WHERE correo_electronico IS NOT NULL AND correo_electronico != ''), COUNT(*) FROM stg.consolidado_proyectos"),
        ("Consolidado con teléfono",
         "SELECT COUNT(*) FILTER (WHERE telefono IS NOT NULL AND telefono != ''), COUNT(*) FROM stg.consolidado_proyectos"),
        ("dim_proyecto con coordenadas",
         "SELECT COUNT(*) FILTER (WHERE coordenada_x IS NOT NULL AND coordenada_x != 0), COUNT(*) FROM dw.dim_proyecto"),
        ("dim_proponente con email",
         "SELECT COUNT(*) FILTER (WHERE correo_electronico IS NOT NULL AND correo_electronico != ''), COUNT(*) FROM dw.dim_proponente"),
    ]

    for name, sql in validaciones:
        try:
            cur.execute(sql)
            filled, total = cur.fetchone()
            pct = round(filled * 100 / max(total, 1), 1)
            log(f"  {name}: {filled:,} / {total:,} ({pct}%)")
        except Exception as e:
            conn.rollback()
            log(f"  {name}: ERROR — {e}")

    cur.close()

    # Cleanup
    for t in ['tmp_coords_suia', 'tmp_coords_coa', 'tmp_coords_jbpm',
              'tmp_contacts_suia', 'tmp_contacts_jbpm']:
        _exec(conn, f"DROP {t}", f"DROP TABLE IF EXISTS {t};")

    conn.close()

    log(f"\n{'='*70}")
    log(f"ENRIQUECIMIENTO v3.0 COMPLETADO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"{'='*70}")

    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    print(f"\n>>> Log: {LOG_FILE}")

if __name__ == "__main__":
    main()
