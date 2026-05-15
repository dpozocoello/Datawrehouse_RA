"""Fix sp_carga_waste_chemical_v2: add DISTINCT ON to avoid duplicate conflict."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from connections import get_connection
from config import CONN_DWH_LOCAL

new_sp = """CREATE OR REPLACE FUNCTION dw.sp_carga_waste_chemical_v2()
 RETURNS boolean
 LANGUAGE plpgsql
AS $func$
BEGIN
    RAISE INFO '[RGD_TRANSFORM] Iniciando transformacion v2.0...';

    -- 1. Actualizar Dimension: dw.dim_tipo_desecho (Con Jerarquia)
    -- DISTINCT ON evita duplicados en cawa_key que causan ON CONFLICT error
    INSERT INTO dw.dim_tipo_desecho (
        codigo_desecho, nombre_desecho, categoria_desecho, grupo_jerarquico, unidad_medida
    )
    SELECT DISTINCT ON (st.cawa_key)
        st.cawa_key,
        st.cawa_name,
        CASE
            WHEN sp.cawp_name ILIKE '%PELIGROSO%' THEN 'PELIGROSO'
            WHEN sp.cawp_name ILIKE '%ESPECIAL%' THEN 'ESPECIAL'
            ELSE 'OTRO'
        END,
        sp.cawp_name,
        'KG'
    FROM stg.stg_waste_type st
    JOIN stg.stg_waste_catalogs_parent sp ON st.cawp_id = sp.cawp_id
    ORDER BY st.cawa_key
    ON CONFLICT (codigo_desecho) DO UPDATE SET
        nombre_desecho = EXCLUDED.nombre_desecho,
        grupo_jerarquico = EXCLUDED.grupo_jerarquico;

    -- 2. Actualizar Dimension: dw.dim_generador_desechos
    INSERT INTO dw.dim_generador_desechos (
        ruc_generador, nombre_generador, codigo_rgd, fuente_sistema
    )
    SELECT DISTINCT ON (ruc)
        ruc,
        COALESCE(registry_number, 'GENERADOR_S_N'),
        registry_number,
        source
    FROM stg.stg_waste_generator
    ORDER BY ruc
    ON CONFLICT (ruc_generador) DO NOTHING;

    RAISE INFO '[RGD_TRANSFORM] Transformacion finalizada OK.';
    RETURN TRUE;
END;
$func$;
"""

with get_connection(CONN_DWH_LOCAL) as conn:
    with conn.cursor() as cur:
        cur.execute(new_sp)
    conn.commit()
    print("SP sp_carga_waste_chemical_v2 updated (DISTINCT ON added).")
