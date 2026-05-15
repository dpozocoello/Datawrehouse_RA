
import psycopg2

def debug_etl():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, user="postgres", password="postgres", database="dw_reg_v1"
        )
        cur = conn.cursor()
        
        print("--- Step 1: Mapping ---")
        cur.execute("DROP TABLE IF EXISTS tmp_map;")
        cur.execute("""
            CREATE TEMP TABLE tmp_map AS
            WITH base AS (
                SELECT r.chsr_id, COALESCE(m.prco_cua, 'N/A') as direct_cua, r.chsr_identification_rep_legal as ruc, r.chsr_code
                FROM stg.stg_chemical_sustances_records r
                LEFT JOIN stg.stg_project_mapping m ON m.prco_id = r.prco_id
            )
            SELECT b.chsr_id,
                COALESCE(
                    (SELECT dp1.sk_proyecto FROM dw.dim_proyecto dp1 WHERE RIGHT(dp1.codigo_proyecto, 11) = RIGHT(b.direct_cua, 11) ORDER BY 1 DESC LIMIT 1),
                    (SELECT fr.sk_proyecto FROM dw.fact_regularizacion fr JOIN dw.dim_proponente dp2 ON fr.sk_proponente = dp2.sk_proponente WHERE dp2.ced_ruc_proponente = b.ruc ORDER BY 1 DESC LIMIT 1),
                    (SELECT dp3.sk_proyecto FROM dw.dim_proyecto dp3 WHERE dp3.codigo_proyecto = COALESCE(b.chsr_code, 'REG-CHSR-' || b.chsr_id) LIMIT 1),
                    0
                ) as sk_proyecto
            FROM base b;
        """)
        print("Mapping done.")

        print("--- Step 2: Movements Aggregation ---")
        cur.execute("""
            SELECT count(*) FROM (
                SELECT sk_proyecto, chemical_key, importer_key, 0 as sk_tiempo, COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id) as invoice
                FROM stg.stg_chemical_substances_movements m
                JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
                LEFT JOIN tmp_map tpm ON d.chsr_id = tpm.chsr_id
                LEFT JOIN dw.dim_chemical_substance ds ON ds.chemical_id = m.achs_id
                LEFT JOIN dw.dim_chemical_importer di ON di.importer_id = d.chsr_id
                GROUP BY 1, 2, 3, 4, 5
                HAVING count(*) > 1
            ) s;
        """)
        dupes = cur.fetchone()[0]
        print(f"Duplicates in aggregated set: {dupes}")

        if dupes == 0:
            print("--- Step 3: Attempting Insert ---")
            cur.execute("""
                INSERT INTO dw.fact_chemical_movement (sk_proyecto, chemical_key, importer_key, sk_tiempo, quantity_entry, quantity_exit, invoice_number)
                SELECT sk_proyecto, chemical_key, importer_key, 0, SUM(m.chsm_entry), SUM(m.chsm_exit), COALESCE(m.chsm_invoice, 'MOV-' || m.chsm_id)
                FROM stg.stg_chemical_substances_movements m
                JOIN stg.stg_chemical_substances_declaration d ON m.chsd_id = d.chsd_id
                LEFT JOIN tmp_map tpm ON d.chsr_id = tpm.chsr_id
                LEFT JOIN dw.dim_chemical_substance ds ON ds.chemical_id = m.achs_id
                LEFT JOIN dw.dim_chemical_importer di ON di.importer_id = d.chsr_id
                GROUP BY 1, 2, 3, 4, 7
                ON CONFLICT (sk_proyecto, chemical_key, importer_key, sk_tiempo, invoice_number) DO NOTHING;
            """)
            print(f"Inserted: {cur.rowcount}")
            conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_etl()
