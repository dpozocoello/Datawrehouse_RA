-- AGREGAR RESTRICCIONES UNIQUE PARA PERMITIR ON CONFLICT EN EL ETL
ALTER TABLE dw.dim_waste_generator ADD CONSTRAINT dw_dim_waste_generator_id_unique UNIQUE (waste_generator_id);
ALTER TABLE dw.dim_waste_type ADD CONSTRAINT dw_dim_waste_type_id_unique UNIQUE (cawa_id);
ALTER TABLE dw.dim_dangerous_waste ADD CONSTRAINT dw_dim_dangerous_waste_id_unique UNIQUE (dw_id);
ALTER TABLE dw.dim_dangerous_classification ADD CONSTRAINT dw_dim_dangerous_classification_id_unique UNIQUE (class_id);
ALTER TABLE dw.dim_chemical_substance ADD CONSTRAINT dw_dim_chemical_substance_id_unique UNIQUE (chemical_id);
ALTER TABLE dw.dim_chemical_storage ADD CONSTRAINT dw_dim_chemical_storage_id_unique UNIQUE (storage_id);
