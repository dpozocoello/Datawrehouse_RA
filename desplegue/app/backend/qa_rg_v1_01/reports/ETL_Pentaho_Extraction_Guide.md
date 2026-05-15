# Guía de Extracción y Validación ETL - Pentaho & Producción

## 1. Proceso de Extracción desde Producción
La extracción de datos desde los servidores de producción (172.16.0.179 y 172.16.0.226) se realiza mediante una arquitectura híbrida de **Pentaho Data Integration (PDI)** y **Python Orchestration**.

### 1.1 Orquestador Pentaho (Carga Regular)
- **Job Maestro**: `Jobs/JOB_CARGA_DWH_REGULARIZACION.kjb`
- **Secuencia de Ejecución**:
  1. `TRX_01` a `TRX_06`: Ingesta de trámites (RCOA, COA, JBPM) y Variables SNAP.
  2. `TRX_07` a `TRX_09`: Ingesta de Pagos (JBPM, SUIA e Históricos).
  3. `TRX_11_INGESTA_GEOGRAFIA`: Ingesta de la tabla maestro de localizaciones.
- **Puntos de Extracción**:
  - **SUIA (.179:5632)**: Esquemas `public`, `suia_iii`, `coa_waste_generator_record`.
  - **JBPM (.226:5432)**: Base `jbpmdb`, `jbpmdb_prod_old`.

### 1.2 Registro Generador de Desechos (ETL Especializado)
Este proceso utiliza scripts SQL específicos (`etl_waste_chemical_extract.sql` y `etl_waste_chemical_load.sql`) orquestados por Python (`etl_orchestrator_waste_chemical.py`).

---

## 2. Resolución de Datos de Localización (geo_location_key)

### 2.1 Causa Raíz del Problema
Se corroboró que en la versión anterior del script `etl_waste_chemical_load.sql`, el campo `geo_location_key` estaba definido explícitamente como `NULL`. Además, la tabla de optimización `stg.tmp_dim_proyecto_optimized` no incluía la llave geográfica del proyecto.

### 2.2 Solución Implementada (Data Engineering Fix)
Se aplicó una corrección al script de carga para heredar la geografía del proyecto consolidado:
1. **Actualización de Optimización**: Se incluyó `sk_geografia` (mapeado desde `dw.fact_regularizacion`) en la tabla temporal de proyectos.
2. **Join de Hechos**: Se modificó el `INSERT` de `dw.fact_waste_generation` para realizar un join con la tabla optimizada, recuperando el `geo_location_key` correspondiente a cada `sk_proyecto`.

### 2.3 Verificación de Datos
- **Ejecución**: Se ejecutó el fix mediante `python etl_orchestrator_waste_chemical.py`.
- **Resultado**: Los registros en `dw.fact_waste_generation` ahora cuentan con su respectiva llave geográfica vinculada al proyecto padre.

---
**Nota para el Ingeniero de Datos**: Para futuras cargas de desechos, asegúrese de que el proyecto haya sido procesado previamente en `fact_regularizacion` para garantizar la consistencia geográfica.
