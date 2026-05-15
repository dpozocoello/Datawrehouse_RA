 WITH cte_stg AS (
         SELECT 'RCOA-BI'::text AS origen,
            count(*) AS registros_stg
           FROM stg.suia_rcoa_bi
        UNION ALL
         SELECT 'COA-BI'::text,
            count(*) AS count
           FROM stg.suia_coa_bi
        UNION ALL
         SELECT 'JBPM-SECTOR'::text,
            count(*) AS count
           FROM stg.jbpm_sector_bi
        UNION ALL
         SELECT 'JBPM-4CAT'::text,
            count(*) AS count
           FROM stg.jbpm_4cat_bi
        UNION ALL
         SELECT 'JBPM-HIDRO'::text,
            count(*) AS count
           FROM stg.jbpm_hidro_bi
        ), cte_fact AS (
         SELECT fact_regularizacion.origen,
            count(*) AS registros_dw
           FROM dw.fact_regularizacion
          GROUP BY fact_regularizacion.origen
        )
 SELECT s.origen,
    s.registros_stg AS total_produccion,
    COALESCE(f.registros_dw, (0)::bigint) AS total_dwh,
    (s.registros_stg - COALESCE(f.registros_dw, (0)::bigint)) AS diferencia,
        CASE
            WHEN (s.registros_stg = 0) THEN (100)::numeric
            ELSE round((((COALESCE(f.registros_dw, (0)::bigint))::numeric / (s.registros_stg)::numeric) * (100)::numeric), 2)
        END AS porcentaje_integridad
   FROM (cte_stg s
     LEFT JOIN cte_fact f ON ((s.origen = (f.origen)::text)));
