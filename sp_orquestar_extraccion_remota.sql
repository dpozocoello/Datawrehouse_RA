/*
 * SP: Orquestador de Extracción Remota de Biodiversidad (v1.4.1)
 * Autor: Antigravity AI
 * Descripción: Dispara las funciones de extracción en el servidor 172.16.0.179
 * para asegurar que las tablas tmp están pobladas con datos multicanal antes de la ingesta.
 */
CREATE OR REPLACE FUNCTION dw.sp_orquestar_extraccion_remota() RETURNS void AS $$ BEGIN -- 1. Disparar extracción SUIA III (v1.4.1)
    PERFORM *
FROM dblink(
        'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
        'SELECT 1 FROM suia_iii.sp_coa_bi_v1_4_1()'
    ) AS t(ret integer);
-- 2. Disparar extracción COA MAE (v1.4.1)
PERFORM *
FROM dblink(
        'dbname=suia_enlisy port=5632 host=172.16.0.179 user=postgres password=postgres',
        'SELECT 1 FROM coa_mae.sp_rcoa_bi_v1_4_1()'
    ) AS t(ret integer);
RAISE NOTICE 'Extracciones remotas v1.4.1 disparadas exitosamente.';
END;
$$ LANGUAGE plpgsql;