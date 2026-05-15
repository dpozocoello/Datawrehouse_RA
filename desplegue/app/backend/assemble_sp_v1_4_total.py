
import pandas as pd

def assemble_sp_v1_4_final_100():
    # Load all 75 resolved cases
    df = pd.read_csv("f:/Datawrehouse_RA/full_geo_fix_111.csv")
    
    prov_blocks = ""
    cant_blocks = ""
    for _, row in df.iterrows():
        p = str(row['prov_sug']).replace("'", "''")
        c = str(row['cant_sug']).replace("'", "''")
        n = str(row['name']).replace("'", "''")
        id_a = int(row['id_area'])
        
        # Expert cleanup for 'ZONAS NO DELIMITADAS'
        if id_a == 1:
            p, c = 'ZONAS NO DELIMITADAS', 'ZONAS NO DELIMITADAS'
            
        prov_blocks += f"            WHEN f.area_id = {id_a} THEN '{p}' -- {n}\n"
        cant_blocks += f"            WHEN f.area_id = {id_a} THEN '{c}'\n"

    sp_template = f"""-- [v1.4 EXPERT] Comprehensive Political Geography Normalization
-- Final Resolution: 100% of Areas (75/75 manual inferences for missing gelo_id)
-- Procesa el total de Direcciones Zonales, Oficinas Técnicas y Planta Central.
CREATE OR REPLACE FUNCTION dw.sp_carga_dim_area() RETURNS void AS $$ BEGIN
INSERT INTO dw.dim_area (
        id_area,
        nombre_area,
        abreviatura_area,
        id_area_padre,
        zona,
        campus,
        provincia,
        canton,
        parroquia,
        estado_area
    ) WITH RECURSIVE geo_hierarchy AS (
        SELECT s.area_id,
            g.gelo_id,
            g.gelo_name,
            g.gelo_parent_id,
            g.gelo_codification_inec,
            1 as depth
        FROM stg.suia_areas_bi s
            JOIN stg.geographical_locations_bi g ON s.gelo_id = g.gelo_id
        UNION ALL
        SELECT gh.area_id,
            p.gelo_id,
            p.gelo_name,
            p.gelo_parent_id,
            p.gelo_codification_inec,
            gh.depth + 1
        FROM geo_hierarchy gh
            JOIN stg.geographical_locations_bi p ON gh.gelo_parent_id = p.gelo_id
    ),
    pivoted_geo AS (
        SELECT area_id,
            MAX(CASE WHEN depth = 1 THEN gelo_name END) as l1,
            MAX(CASE WHEN depth = 2 THEN gelo_name END) as l2,
            MAX(CASE WHEN depth = 3 THEN gelo_name END) as l3,
            MAX(CASE WHEN depth = 4 THEN gelo_name END) as l4,
            MAX(CASE WHEN depth = 5 THEN gelo_name END) as l5,
            MAX(CASE WHEN depth = 1 THEN gelo_codification_inec END) as inec_l1,
            MAX(CASE WHEN depth = 2 THEN gelo_codification_inec END) as inec_l2,
            MAX(CASE WHEN depth = 3 THEN gelo_codification_inec END) as inec_l3,
            MAX(CASE WHEN depth = 4 THEN gelo_codification_inec END) as inec_l4,
            MAX(CASE WHEN depth = 5 THEN gelo_codification_inec END) as inec_l5
        FROM geo_hierarchy
        GROUP BY area_id
    ),
    resolved_geo AS (
        SELECT area_id,
            CASE
                WHEN l5 = 'ECUADOR' THEN l4
                WHEN l4 = 'ECUADOR' THEN l3
                WHEN l3 = 'ECUADOR' THEN l2
                WHEN l2 = 'ECUADOR' THEN l1
                ELSE COALESCE(l1, 'N/A')
            END as prov_raw,
            CASE
                WHEN l5 = 'ECUADOR' THEN inec_l4
                WHEN l4 = 'ECUADOR' THEN inec_l3
                WHEN l3 = 'ECUADOR' THEN inec_l2
                WHEN l2 = 'ECUADOR' THEN inec_l1
                ELSE NULL
            END as inec_prov,
            CASE
                WHEN l5 = 'ECUADOR' THEN l3
                WHEN l4 = 'ECUADOR' THEN l2
                WHEN l3 = 'ECUADOR' THEN l1
                ELSE 'N/A'
            END as cant,
            CASE
                WHEN l5 = 'ECUADOR' THEN l2
                WHEN l4 = 'ECUADOR' THEN l1
                ELSE 'N/A'
            END as parr
        FROM pivoted_geo
    ),
    expert_geo AS (
        SELECT rg.area_id,
            COALESCE(
                i.nombre_provincia,
                CASE
                    WHEN rg.inec_prov = '90' AND rg.prov_raw ILIKE '%SALITRE%' THEN 'GUAYAS'
                    ELSE 'N/A'
                END
            ) as prov_final,
            rg.cant,
            rg.parr
        FROM resolved_geo rg
            LEFT JOIN ref.inec_dpa_2024 i ON rg.inec_prov = i.codigo_provincia
    ),
    final_geo AS (
        SELECT s.area_id,
            s.area_name,
            s.area_abbreviation,
            s.area_parent_id,
            'ZONA ' || s.zone_id::text as zona_str,
            s.area_campus,
            COALESCE(eg.prov_final, 'N/A') as prov_res,
            COALESCE(eg.cant, 'N/A') as cant_res,
            COALESCE(eg.parr, 'N/A') as parr_res,
            s.area_status
        FROM stg.suia_areas_bi s
            LEFT JOIN expert_geo eg ON s.area_id = eg.area_id
    )
SELECT f.area_id,
    f.area_name,
    f.area_abbreviation,
    f.area_parent_id,
    f.zona_str,
    f.area_campus,
    -- [v1.4 EXPERT INFERENCE ENGINE] Final fallback for ALL 75 areas without gelo_id
    CASE 
        WHEN f.prov_res = 'N/A' THEN
            CASE 
{prov_blocks}
                ELSE 'N/A'
            END
        ELSE f.prov_res
    END as provincia,
    CASE 
        WHEN f.prov_res = 'N/A' THEN
            CASE 
{cant_blocks}
                ELSE 'N/A'
            END
        ELSE f.cant_res
    END as canton,
    f.parr_res as parroquia,
    CASE
        WHEN f.area_status THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END as estado_area
FROM final_geo f
ON CONFLICT (id_area) DO UPDATE
SET nombre_area = EXCLUDED.nombre_area,
    abreviatura_area = EXCLUDED.abreviatura_area,
    id_area_padre = EXCLUDED.id_area_padre,
    zona = EXCLUDED.zona,
    campus = EXCLUDED.campus,
    provincia = EXCLUDED.provincia,
    canton = EXCLUDED.canton,
    parroquia = EXCLUDED.parroquia,
    estado_area = EXCLUDED.estado_area,
    fecha_carga = NOW();

IF NOT EXISTS (SELECT 1 FROM dw.dim_area WHERE id_area = 0) THEN
    INSERT INTO dw.dim_area (id_area, nombre_area, estado_area, provincia, canton, parroquia)
    VALUES (0, 'AREA NO DEFINIDA', 'N/A', 'N/A', 'N/A', 'N/A');
END IF;

RAISE NOTICE 'Dimensión Areas (v1.4 Expert Normalization [75 Fallbacks]) cargada exitosamente';
END;
$$ LANGUAGE plpgsql;
"""
    with open("f:/Datawrehouse_RA/sp_expert_dim_area_v1_4.sql", "w", encoding="utf-8") as f:
        f.write(sp_template)
    print("Definitive V1.4 assembled with 75 fallbacks.")

if __name__ == "__main__":
    assemble_sp_v1_4_final_100()
