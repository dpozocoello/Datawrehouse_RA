-- Setup Reference Data v1.4
-- Ensures schemas and default SK=0 records exist.
CREATE SCHEMA IF NOT EXISTS ref;
CREATE TABLE IF NOT EXISTS ref.inec_dpa_2024 (
    codigo_provincia CHAR(2) PRIMARY KEY,
    nombre_provincia VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255)
);
-- Dimension Initialization (SK=0)
INSERT INTO dw.dim_area (
        sk_area,
        id_area,
        nombre_area,
        provincia,
        canton,
        parroquia
    )
VALUES (0, 0, 'AREA NO DEFINIDA', 'N/A', 'N/A', 'N/A') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_proyecto (sk_proyecto, codigo_proyecto, nombre_proyecto)
VALUES (0, 'N/A', 'PROYECTO NO DEFINIDO') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_proponente (
        sk_proponente,
        ced_ruc_proponente,
        nombre_proponente
    )
VALUES (0, 'N/A', 'PROPONENTE NO DEFINIDO') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_actividad (
        sk_actividad,
        codigo_actividad,
        actividad_economica
    )
VALUES (0, 'N/A', 'ACTIVIDAD NO DEFINIDA') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_geografia (sk_geografia, provincia, canton, parroquia)
VALUES (0, 'N/A', 'N/A', 'N/A') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_estado (
        sk_estado,
        estado_proceso,
        estado_proyecto,
        estado_tramite
    )
VALUES (0, 'N/A', 'N/A', 'N/A') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_tiempo (sk_tiempo, fecha)
VALUES (0, '1900-01-01') ON CONFLICT DO NOTHING;
INSERT INTO dw.dim_capa_ambiental (sk_capa, id_layer_origen, nombre_capa, descripcion_capa, categoria)
VALUES (0, 0, 'CAPA NO DEFINIDA', 'N/A', 'N/A') ON CONFLICT DO NOTHING;
-- INEC Catalog
INSERT INTO ref.inec_dpa_2024 (codigo_provincia, nombre_provincia)
SELECT '01',
    'AZUAY'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '01'
    )
UNION ALL
SELECT '02',
    'BOLIVAR'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '02'
    )
UNION ALL
SELECT '03',
    'CAÑAR'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '03'
    )
UNION ALL
SELECT '04',
    'CARCHI'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '04'
    )
UNION ALL
SELECT '05',
    'COTOPAXI'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '05'
    )
UNION ALL
SELECT '06',
    'CHIMBORAZO'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '06'
    )
UNION ALL
SELECT '07',
    'EL ORO'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '07'
    )
UNION ALL
SELECT '08',
    'ESMERALDAS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '08'
    )
UNION ALL
SELECT '09',
    'GUAYAS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '09'
    )
UNION ALL
SELECT '10',
    'IMBABURA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '10'
    )
UNION ALL
SELECT '11',
    'LOJA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '11'
    )
UNION ALL
SELECT '12',
    'LOS RIOS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '12'
    )
UNION ALL
SELECT '13',
    'MANABI'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '13'
    )
UNION ALL
SELECT '14',
    'MORONA SANTIAGO'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '14'
    )
UNION ALL
SELECT '15',
    'NAPO'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '15'
    )
UNION ALL
SELECT '16',
    'PASTAZA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '16'
    )
UNION ALL
SELECT '17',
    'PICHINCHA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '17'
    )
UNION ALL
SELECT '18',
    'TUNGURAHUA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '18'
    )
UNION ALL
SELECT '19',
    'ZAMORA CHINCHIPE'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '19'
    )
UNION ALL
SELECT '20',
    'GALAPAGOS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '20'
    )
UNION ALL
SELECT '21',
    'SUCUMBIOS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '21'
    )
UNION ALL
SELECT '22',
    'ORELLANA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '22'
    )
UNION ALL
SELECT '23',
    'SANTO DOMINGO DE LOS TSACHILAS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '23'
    )
UNION ALL
SELECT '24',
    'SANTA ELENA'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '24'
    )
UNION ALL
SELECT '90',
    'ZONAS NO DELIMITADAS'
WHERE NOT EXISTS (
        SELECT 1
        FROM ref.inec_dpa_2024
        WHERE codigo_provincia = '90'
    );