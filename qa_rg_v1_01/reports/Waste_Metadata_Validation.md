# Report: Pentaho Integration & Waste Metadata Validation

## 1. Integración con Pentaho
El archivo `etl_waste_chemical_load.sql` es orquestado dentro del Job Maestro de Regularización.

- **Job**: `Jobs/JOB_CARGA_DWH_REGULARIZACION.kjb`
- **Paso**: `INGESTA_WASTE_CHEMICAL`
- **Mecanismo**: Este paso ejecuta el orquestador Python (`etl_orchestrator_waste_chemical.py`) el cual lee y aplica los scripts SQL de extracción y carga.

## 2. Validación de Campos: dangerous_waste_key y danger_class_key

Se realizó un análisis de calidad de datos sobre las tablas de staging y dimensiones para explicar la ausencia de datos en estos campos:

### 2.1 Hallazgos en Staging (`stg.stg_fact_waste_generation`)
- **Universo**: 469,314 registros extraídos.
- **danger_class_id**: **0 registros** cuentan con este ID. La columna está vacía en su totalidad (100% NULL/vacio).
- **dangerous_waste_id**: Solo **10 registros** (0.002%) tienen un valor no-nulo, los cuales resultaron ser cadenas vacías o espacios en blanco en el origen.

### 2.2 Hallazgos en Dimensiones
- **dw.dim_dangerous_waste**: Contiene solo **1 registro activo** (ID: 1).
- **dw.dim_dangerous_classification**: Contiene **69 registros**.

### 2.3 Explicación del Problema
Los campos `dangerous_waste_key` y `danger_class_key` aparecen como NULL en la tabla de hechos final (`dw.fact_waste_generation`) por tres razones:
1. **Falta de Datos en Origen**: La gran mayoría de los registros de generación de residuos en SUIA no tienen clasificaciones de peligrosidad asociadas en la tabla `coa_waste_generator_record.waste_record`.
2. **Integridad Referencial**: Para los 10 registros que tienen ID, este no coincide con el único registro cargado en la dimensión (ID: 1), resultando en un NULL tras el `LEFT JOIN`.
3. **Mantenimiento**: La extracción de dimensiones (`extract.sql`) solo trae registros `is_active = TRUE`. Si los hechos hacen referencia a códigos inactivos, se pierden en el join.

---
**Conclusión**: No es un error del proceso ETL, sino un reflejo de la baja completitud de estos atributos específicos en el sistema transaccional de origen para los registros vinculados a proyectos.
