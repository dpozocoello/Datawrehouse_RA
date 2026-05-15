-- Esquema de Referencia y Catálogo INEC 2024
-- Fase A: Normalización contra el Catálogo Nacional
CREATE SCHEMA IF NOT EXISTS ref;
DROP TABLE IF EXISTS ref.inec_dpa_2024;
CREATE TABLE ref.inec_dpa_2024 (
    codigo_provincia CHAR(2) PRIMARY KEY,
    nombre_provincia VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255)
);
INSERT INTO ref.inec_dpa_2024 (codigo_provincia, nombre_provincia)
VALUES ('01', 'AZUAY'),
    ('02', 'BOLIVAR'),
    ('03', 'CAÑAR'),
    ('04', 'CARCHI'),
    ('05', 'COTOPAXI'),
    ('06', 'CHIMBORAZO'),
    ('07', 'EL ORO'),
    ('08', 'ESMERALDAS'),
    ('09', 'GUAYAS'),
    ('10', 'IMBABURA'),
    ('11', 'LOJA'),
    ('12', 'LOS RIOS'),
    ('13', 'MANABI'),
    ('14', 'MORONA SANTIAGO'),
    ('15', 'NAPO'),
    ('16', 'PASTAZA'),
    ('17', 'PICHINCHA'),
    ('18', 'TUNGURAHUA'),
    ('19', 'ZAMORA CHINCHIPE'),
    ('20', 'GALAPAGOS'),
    ('21', 'SUCUMBIOS'),
    ('22', 'ORELLANA'),
    ('23', 'SANTO DOMINGO DE LOS TSACHILAS'),
    ('24', 'SANTA ELENA'),
    ('90', 'ZONAS NO DELIMITADAS');
COMMENT ON TABLE ref.inec_dpa_2024 IS 'Catálogo Maestro de Provincias del Ecuador - Fuente: INEC DPA 2024';