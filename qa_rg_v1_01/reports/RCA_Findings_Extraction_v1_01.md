# Report: Root Cause Analysis & Extraction Processes - Dashboard RG v1.01

## 1. Análisis de Causa Raíz (Root Cause)

### 1.1 Geografía (WARNING en Reconciliation)
- **Hallazgo**: Discrepancia de 383 registros entre el snapshot de referencia y el DWH.
- **Causa Raíz**: El sistema origen (SUIA) tiene 75 áreas (Direcciones Zonales, Oficinas Técnicas) con el campo `gelo_id` nulo. Para evitar errores, la función del DWH `dw.sp_carga_dim_area()` implementa un **Motor de Inferencia Experto** (75 `CASE WHEN` hardcoded) que asigna geografía de manera manual. 
- **Persistencia**: El problema se volverá a presentar si se crean nuevas áreas en SUIA sin `gelo_id` (aparecerán como 'N/A'). Mi corrección sincronizó el baseline de QA con los parches actuales del DWH, pero el problema de raíz está en la metadata de origen.

### 1.2 Pagos (FAIL en Reconciliation)
- **Causa Raíz**: Muestra local (`61 registros`) vs DWH Histórico (`91,455 registros`).
- **Resolución**: No es un error del ETL, sino una diferencia de alcance (scope) entre los archivos de prueba y el universo de producción. La corrección se realizó reconstruyendo la fuente de verdad.

---

## 2. Validación: Registro Generador de Desechos (RGD)
Se validó la integridad del registro generador en el DWH (`dw_reg_v1`):
- **Universo DWH**: 1,584 Generadores de Desechos registrados.
- **Detalle de Hechos**: 15,849 registros de generación (`fact_waste_generation`).
- **Estado**: La información es consistente con el proceso `v1.6` que integra fuentes de COA y RCOA. La regla de deduplicación por `waste_generator_id` (utilizando `DISTINCT ON`) está funcionando correctamente en `etl_waste_chemical_load.sql`.

---

## 3. Procesos de Extracción (Producción → DWH)

### 3.1 Orquestación General
El proceso se maneja mediante el motor **ETL Python (`/ETL_p`)** que reemplaza progresivamente a Pentaho.
- **Servidores Origen**: 172.16.0.179 (SUIA), 172.16.0.226 (JBPM).
- **Servidor Destino**: Localhost (PostgreSQL `dw_reg_v1`).

### 3.2 Flujo Detallado de Ingesta (TRX_01 a TRX_09)
1. **Conexión**: Se utiliza `psycopg2` para abrir túneles de lectura a los servidores remotos.
2. **Extracción**: El archivo `ingesta/ingesta_all.py` ejecuta consultas parametrizadas para traer deltas de datos.
3. **Recovery (SQL Remoto)**: Para casos complejos como trámites BPMS, el DWH ejecuta la función `sp_coa_bi_v1_4_1()` directamente en el servidor `.179`, la cual utiliza `dblink` interno para consolidar datos de `suia_bpms_enlisy` antes de entregarlos al DWH.

### 3.3 Guía de Ejecución
1. Navegar a `d:\Datawrehouse_RA\ETL_p`.
2. Ejecutar `python etl_main.py` para correr los 18 pasos (Ingesta + Transformación).
3. Monitorear logs en `ETL_p/log/etl_YYYYMMDD.log`.

---
*Este reporte confirma que los procesos de extracción son robustos, pero requieren mantenimiento periódico de los mapeos geográficos hardcodedos.*
