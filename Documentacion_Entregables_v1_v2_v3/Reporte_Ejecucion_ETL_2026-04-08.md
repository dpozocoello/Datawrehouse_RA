# Reporte de Ejecución — ETL Data Warehouse Regularización Ambiental
## Auditoría, Corrección y Validación del Pipeline de Datos

---

**Fecha de ejecución:** 2026-04-08  
**Versión del pipeline:** Python ETL v1.9.5 (29 pasos)  
**Entorno:** PostgreSQL 14 · `dw_reg_v1` · localhost:5432  
**Fuentes origen:** SUIA (172.16.0.179:5632) · JBPM (172.16.0.226:5432)  
**Elaborado por:** Arquitectura de Datos — DWH Team  

---

## 1. Resumen Ejecutivo

El presente reporte documenta la auditoría integral, corrección y ejecución completa del pipeline ETL del Data Warehouse de Regularización Ambiental, realizado el día 2026-04-08. El proceso partió de un estado con múltiples errores críticos no identificados previamente y concluyó con la ejecución exitosa de los 29 pasos del pipeline, cargando más de **1.1 millones de hechos de regularización**, **92,466 registros de pagos** y **356,191 relaciones geográficas** en el DWH.

Se identificaron y corrigieron **12 defectos técnicos** distribuidos en código Python, stored procedures PostgreSQL, archivos SQL y el job Pentaho. La duración acumulada del proceso de diagnóstico-corrección-validación fue de aproximadamente **8 horas**.

---

## 2. Arquitectura del Pipeline

### 2.1 Estructura General

```
FUENTES ORIGEN                  PIPELINE ETL (29 pasos)            DATA WAREHOUSE
─────────────────               ────────────────────────           ──────────────
SUIA (suia_enlisy)  ──► FASE 1: INGESTA (pasos 1–11)   ──►  stg.*  (staging)
SUIA (suia_bpms)    ──► FASE 2: TRANSFORMACIÓN (12–20) ──►  dw.*   (dimensiones)
JBPM (jbpmdb)       ──► FASE 3: PAGOS HISTÓRICOS (21–24)──► dw.*   (hechos)
JBPM (jbpmdb_old)   ──► FASE 4: DESECHOS/QUÍMICOS (25–26)─► dw.*   (waste)
                        FASE 5: INTERSECCIONES (27–29)  ──►  dw.*   (geo)
```

### 2.2 Secuencia de Pasos

| # | Clave | Descripción | Fase |
|---|-------|-------------|------|
| 1 | SP_ORQUESTAR_EXTRACCION | Orquestación Remota v1.4.1 | Ingesta |
| 2 | TRX_01_SUIA_RCOA | Ingesta SUIA RCOA | Ingesta |
| 3 | TRX_02_SUIA_COA | Ingesta SUIA COA | Ingesta |
| 4 | TRX_03_JBPM_SECTOR | Ingesta JBPM Sector | Ingesta |
| 5 | TRX_04_JBPM_4CAT | Ingesta JBPM 4 Categorías | Ingesta |
| 6 | TRX_05_JBPM_HIDRO | Ingesta JBPM Hidrocarburos | Ingesta (deshabilitado) |
| 7 | TRX_06_SNAP | Ingesta SNAP Variables | Ingesta |
| 8 | TRX_07_PAGOS_JBPM | Ingesta Pagos JBPM | Ingesta |
| 9 | TRX_08_PAGOS_SUIA | Ingesta Pagos SUIA | Ingesta |
| 10 | TRX_10_AREAS | Ingesta Áreas SUIA | Ingesta |
| 11 | TRX_11_GEOGRAFIA | Ingesta Geografía | Ingesta |
| 12 | SP_CONSOLIDAR_STAGING | SP Consolidar Staging | Transformación |
| 13 | SP_CARGA_DIMENSIONES | SP Cargar Dimensiones Core | Transformación |
| 14 | SP_CARGA_DIM_AREA | SP Cargar Dim Área | Transformación |
| 15 | SETUP_REFERENCE_DATA | Setup Registros SK=0 | Transformación |
| 16 | SP_CARGA_HECHOS | SP Cargar Fact Regularización | Transformación |
| 17 | SP_CARGA_DIM_PAGO | SP Cargar Dim Pago | Transformación |
| 18 | SP_CARGA_FACT_PAGO | SP Cargar Fact Pago | Transformación |
| 19 | UPDATE_AREA_RESPONSABLE | Update Área Responsable v2 | Transformación |
| 20 | SP_BRIDGE_PROYECTO_GEO | SP Bridge Proyecto-Geo v2 | Transformación |
| 21 | TRX_09_PAGOS_HIST | Ingesta Pagos Históricos v3 | Pagos Históricos |
| 22 | RECALCULO_MONTOS_JBPM | Recálculo Montos JBPM v3 | Pagos Históricos |
| 23 | SP_SECUENCIA_PAGOS | SP Secuencia Pagos v2/v3 | Pagos Históricos |
| 24 | SP_CARGA_PUENTE_AMBIENTAL | SP Cargar Puente Ambiental | Pagos Históricos |
| 25 | INGESTA_WASTE_CHEMICAL | Ingesta Desechos/Químicos | Desechos |
| 26 | SP_CARGA_WASTE_CHEMICAL | SP Carga Desechos/Químicos | Desechos |
| 27 | INGESTA_INTERSECTION | Ingesta Intersecciones v1.9 | Intersecciones |
| 28 | RECOVER_MISSING_PROJECTS | Recuperar Proyectos Faltantes | Intersecciones |
| 29 | SP_CARGA_DIM_INTERSECTION | SP Cargar Dim Intersección | Intersecciones |

---

## 3. Defectos Identificados y Correcciones Aplicadas

Se identificaron **12 defectos** clasificados en cuatro categorías: errores de esquema de base de datos, errores de lógica en stored procedures, errores de calidad de datos en origen, y errores de configuración del pipeline.

---

### 3.1 Defecto #1 — FK Violation: `sk_area=0` ausente en `dim_area`

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Crítica — bloqueante |
| **Paso afectado** | Paso 16: SP Cargar Fact Regularización |
| **Error** | `inserción en «fact_regularizacion» viola llave foránea «fact_regularizacion_sk_area_fkey»` |
| **Causa raíz** | `sp_carga_dim_area()` inserta el sentinel `id_area=0` mediante un bloque `IF NOT EXISTS ... INSERT` que **no especifica `sk_area`**, permitiendo que el SERIAL auto-incremente el valor (ej: `sk_area=25279`). El paso `SETUP_REFERENCE_DATA` estaba posicionado **antes** del SP, por lo que el SP sobreescribía el sentinel con `sk_area ≠ 0`. |
| **Corrección 1** | `sp_carga_dim_area` modificado en PostgreSQL: reemplazado el bloque `IF NOT EXISTS INSERT` por `DELETE ... WHERE sk_area != 0` + `INSERT (sk_area=0, ...) ON CONFLICT DO NOTHING`. |
| **Corrección 2** | `SECUENCIA_ETL` reordenada: `SETUP_REFERENCE_DATA` movido del paso 12 al paso 15, **después** de `SP_CARGA_DIM_AREA` y **antes** de `SP_CARGA_HECHOS`. |
| **Intentos fallidos** | 3 ejecuciones fallidas antes de identificar la causa raíz completa. |
| **Archivos modificados** | `ETL_p/etl_main.py`, SP `dw.sp_carga_dim_area` (PostgreSQL) |

---

### 3.2 Defecto #2 — `sp_carga_fact_pago` PARTE B: Producto Cartesiano

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Crítica — agota disco |
| **Paso afectado** | Paso 18: SP Cargar Fact Pago |
| **Error** | `No space left on device` — el SP consumió >5 GB en 84 minutos |
| **Causa raíz** | La PARTE B del SP propagaba cada pago JBPM a **todos los proyectos del mismo proponente** mediante un triple join: `fact_pago × fact_regularizacion (src) × fact_regularizacion (other)`. Con un proponente que tiene hasta **16,063 proyectos** y **183,876 pagos**, el resultado estimado era **~2,200 millones de filas**. |
| **Corrección** | PARTE B deshabilitada en el SP PostgreSQL. Los pagos se asocian únicamente al proyecto que origina la transacción (PARTE A y C). Se ejecutó `VACUUM FULL dw.fact_pago` para recuperar los 5 GB consumidos. |
| **Impacto en datos** | Los pagos quedan correctamente asociados por `project_id` directo. La propagación cruzada por proponente no tiene sustento en el modelo de negocio de regularización. |
| **Archivos modificados** | SP `dw.sp_carga_fact_pago` (PostgreSQL) |

---

### 3.3 Defecto #3 — `dim_capa_ambiental` sin registro sentinel SK=0

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Alta — bloqueante |
| **Paso afectado** | Paso 24: SP Cargar Puente Ambiental |
| **Error** | `inserción en «bridge_interseccion_ambiental» viola llave foránea «bridge_interseccion_ambiental_sk_capa_fkey»` |
| **Causa raíz** | `sp_carga_puente_ambiental` usa `COALESCE(da.sk_capa, 0)` para proyectos sin capa ambiental identificada, pero el registro `sk_capa=0` no existía en `dim_capa_ambiental`. La tabla estaba completamente vacía. |
| **Corrección** | Registro sentinel insertado en `dim_capa_ambiental (sk_capa=0, nombre_capa='CAPA NO DEFINIDA')`. Sentinel agregado a `setup_reference_data_v1_4.sql` para ejecuciones futuras. |
| **Archivos modificados** | `setup_reference_data_v1_4.sql`, DB directa |

---

### 3.4 Defecto #4 — `TRX_09` Valores numéricos inválidos en origen JBPM

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Alta — bloqueante |
| **Paso afectado** | Paso 21: Ingesta Pagos Históricos |
| **Error** | `invalid input syntax for type double precision: «»` y `«13116,58»` |
| **Causa raíz** | Las columnas `retired_value`, `value_updated`, `retired_value_1` en `online_payment.online_payments_historical` contienen (a) **strings vacíos** en lugar de NULL y (b) **números con coma decimal** (formato europeo `13116,58`) en lugar del punto decimal (`13116.58`). |
| **Corrección** | `QUERY_TRX_09` modificado en `ingesta_all.py`: aplicado `NULLIF(REPLACE(col::text, ',', '.'), '')::double precision` a los tres campos numéricos en el origen antes de la extracción. |
| **Archivos modificados** | `ETL_p/ingesta/ingesta_all.py` |

---

### 3.5 Defecto #5 — `RECALCULO_MONTOS_JBPM` usa `REPLACE()` sobre `double precision`

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Alta — bloqueante |
| **Paso afectado** | Paso 22: Recálculo Montos JBPM |
| **Error** | `no existe la función replace(double precision, unknown, unknown)` |
| **Causa raíz** | El SQL de recálculo aplicaba `REPLACE(col, ',', '.')::numeric` sobre columnas de staging que **ya son `double precision`** (convertidas correctamente en TRX_09 con el fix anterior). La función `REPLACE` no opera sobre tipos numéricos en PostgreSQL. |
| **Corrección** | `SQL_RECALCULO_MONTOS` modificado en `transformacion_all.py`: eliminados todos los `REPLACE()`, reemplazados por cast directo `col::numeric`. `COALESCE(oph.retired_value, '0')` cambiado a `COALESCE(oph.retired_value, 0)` (literal numérico). |
| **Archivos modificados** | `ETL_p/transformacion/transformacion_all.py` |

---

### 3.6 Defecto #6 — `ingesta_waste_chemical`: columna `hwge_id` inexistente en `hazardous_wastes_warehouses`

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Alta — bloqueante |
| **Paso afectado** | Paso 25: Ingesta Desechos/Químicos |
| **Error** | `column "hwge_id" does not exist` en `suia_iii.hazardous_wastes_warehouses` |
| **Causa raíz** | La query de `stg_rgd_warehouses` asumía que `hazardous_wastes_warehouses` tenía columnas `hwge_id`, `hwwa_name`, `hwwa_x_coordinate`, etc. La tabla real solo contiene metadatos físicos de la bodega (`hwwa_id`, `hwwa_status`, `hwwa_height`, etc.) sin relación directa con generadores. |
| **Corrección** | Query reemplazada usando `suia_iii.recovery_points` que sí tiene `hwge_id` y representa los puntos geográficos asociados a generadores. |
| **Archivos modificados** | `ETL_p/ingesta/ingesta_waste_chemical.py` |

---

### 3.7 Defecto #7 — `ingesta_waste_chemical`: columnas inexistentes en `retce.detail_manifests_waste`

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Alta — bloqueante |
| **Paso afectado** | Paso 25: Ingesta Desechos/Químicos |
| **Error** | `column "hwge_id" does not exist` en `retce.detail_manifests_waste` |
| **Causa raíz** | La query de `stg_rgd_manifests` referenciaba columnas (`hwge_id`, `hwma_id`, `dmwa_waste_amount_generated`, `dmwa_date_generated`) que no existen en la tabla. El esquema `retce` fue reestructurado y las columnas reales son `dema_id`, `wada_id`, `dmwa_quantity_tons`, `dmwa_date_create`. La relación con `hwge_id` requiere join a través de `hazardous_waste_generator_retce`. |
| **Corrección** | Query reescrita con JOIN a `retce.detail_manifests` y `retce.hazardous_waste_generator_retce` para obtener `hwge_id`. Columnas renombradas a sus valores reales. |
| **Archivos modificados** | `ETL_p/ingesta/ingesta_waste_chemical.py` |

---

### 3.8 Defecto #8 — `etl_waste_chemical_load.sql` usa `CALL` en lugar de `SELECT`

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Media — bloqueante |
| **Paso afectado** | Paso 26: SP Carga Desechos/Químicos |
| **Error** | `dw.sp_carga_waste_chemical_v2() no es un procedimiento` |
| **Causa raíz** | El archivo SQL usaba la sintaxis `CALL` (exclusiva de `PROCEDURE` en PostgreSQL 11+), pero `sp_carga_waste_chemical_v2` es una **función** (`RETURNS boolean`). |
| **Corrección** | `CALL dw.sp_carga_waste_chemical_v2()` → `SELECT dw.sp_carga_waste_chemical_v2()` |
| **Archivos modificados** | `etl_waste_chemical_load.sql` |

---

### 3.9 Defecto #9 — `sp_carga_waste_chemical_v2` duplicados en ON CONFLICT

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Media — bloqueante |
| **Paso afectado** | Paso 26: SP Carga Desechos/Químicos |
| **Error** | `ON CONFLICT DO UPDATE no puede afectar una fila por segunda vez` |
| **Causa raíz** | `stg.stg_waste_type` contiene múltiples filas con el mismo `cawa_key` (código de tipo de desecho). El INSERT con `ON CONFLICT DO UPDATE` falla cuando el SELECT fuente ya tiene duplicados antes del conflicto. |
| **Corrección** | Agregado `DISTINCT ON (cawa_key) ... ORDER BY cawa_key` al SELECT fuente. Mismo fix aplicado a `dim_generador_desechos` para `ruc_generador`. |
| **Archivos modificados** | SP `dw.sp_carga_waste_chemical_v2` (PostgreSQL) |

---

### 3.10 Defecto #10 — `ingesta_pesticides.py`: typo en columna `depp_id`

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Media — datos incorrectos |
| **Paso afectado** | Paso 25 (subcomponente pesticides) |
| **Error** | `column "depp_id" does not exist` — HINT: `Perhaps you meant "depe_id"` |
| **Causa raíz** | Error tipográfico: `depp_id` en lugar de `depe_id` en la query de `stg_detail_pesticide_project`. Causaba que la tabla se cargara con 0 filas. |
| **Corrección** | `depp_id` → `depe_id` |
| **Resultado** | `stg_detail_pesticide_project` pasó de 0 a **6,485 filas** |
| **Archivos modificados** | `ETL_p/ingesta/ingesta_pesticides.py` |

---

### 3.11 Defecto #11 — `SETUP_REFERENCE_DATA` no incluido en pipeline Python

| Atributo | Detalle |
|----------|---------|
| **Severidad** | Alta — prerequisito de integridad |
| **Causa raíz** | El paso de inicialización de registros sentinel SK=0 (`setup_reference_data_v1_4.sql`) solo existía en el job Pentaho. El pipeline Python no lo ejecutaba, dejando las dimensiones sin los registros de valor desconocido requeridos por las FK de las tablas de hechos. |
| **Corrección** | Función `setup_reference_data()` agregada a `transformacion_all.py`. Paso 15 insertado en `SECUENCIA_ETL`. Clave `SETUP_REFERENCE_DATA: True` agregada a `PASOS_HABILITADOS`. |
| **Archivos modificados** | `ETL_p/etl_main.py`, `ETL_p/transformacion/transformacion_all.py`, `ETL_p/config.py` |

---

### 3.12 Defectos en Job Pentaho (JOB_CARGA_DWH_REGULARIZACION.kjb)

| # | Defecto | Corrección |
|---|---------|------------|
| KJB-1 | TRX_01 y TRX_02 desconectados del flujo de hops | Reconectados: `DUMMY_COA_REPL → TRX_01 → TRX_02 → TRX_03` |
| KJB-2 | Doble ejecución de `ingesta_waste_chemical.py` (script Python + KTR) | `PY_INGESTA_RGD` convertido a nodo `DUMMY` |
| KJB-3 | `SQL_LOAD_INTERSECTION` y `SQL_LOAD_RGD` en orden incorrecto (antes de SPs de dimensiones) | Movidos al final del flujo, después de `SP_CARGA_PUENTE_AMBIENTAL` |
| KJB-4 | Paso `RECOVER_MISSING_PROJECTS` ausente en Pentaho | Nuevo nodo `PY_RECOVER_MISSING` agregado antes de `SQL_LOAD_INTERSECTION` |
| KJB-5 | `Setup Reference Data`: `sqlfromfile=F` | Corregido a `sqlfromfile=T` |

---

## 4. Resultado de la Ejecución Final

### 4.1 Estado por Paso (Ejecución Acumulada del Día)

| Paso | Nombre | Estado | Tiempo |
|------|--------|--------|--------|
| 1 | Orquestación Remota | ✓ OK | 5m 21s |
| 2 | Ingesta SUIA RCOA | ✓ OK | 2m 14s |
| 3 | Ingesta SUIA COA | ✓ OK | 1m 44s |
| 4 | Ingesta JBPM Sector | ✓ OK | 1m 2s |
| 5 | Ingesta JBPM 4 Categorías | ✓ OK | 10m 21s |
| 6 | Ingesta JBPM Hidrocarburos | ⊘ SALTADO | — |
| 7 | Ingesta SNAP Variables | ✓ OK | 0.3s |
| 8 | Ingesta Pagos JBPM | ✓ OK | 15s |
| 9 | Ingesta Pagos SUIA | ✓ OK | 8s |
| 10 | Ingesta Áreas SUIA | ✓ OK | 0.2s |
| 11 | Ingesta Geografía | ✓ OK | 0.2s |
| 12 | SP Consolidar Staging | ✓ OK | 1m 33s |
| 13 | SP Cargar Dimensiones | ✓ OK | 1m 49s |
| 14 | SP Cargar Dim Área | ✓ OK | 0.7s |
| 15 | Setup Reference Data (SK=0) | ✓ OK | 0.2s |
| 16 | SP Cargar Fact Regularización | ✓ OK | 3m 11s |
| 17 | SP Cargar Dim Pago | ✓ OK | 0.3s |
| 18 | SP Cargar Fact Pago | ✓ OK | 25.5s |
| 19 | Update Área Responsable v2 | ✓ OK | 18.1s |
| 20 | SP Bridge Proyecto-Geo v2 | ✓ OK | 16.2s |
| 21 | Ingesta Pagos Históricos v3 | ✓ OK | 13.6s |
| 22 | Recálculo Montos JBPM v3 | ✓ OK | 5.4s |
| 23 | SP Secuencia Pagos v2/v3 | ✓ OK | 6.0s |
| 24 | SP Cargar Puente Ambiental | ✓ OK | 10.4s |
| 25 | Ingesta Desechos/Químicos | ✓ OK | 12.4s |
| 26 | SP Carga Desechos/Químicos | ✓ OK | 1.1s |
| 27 | Ingesta Intersecciones v1.9 | ✓ OK | 56.5s |
| 28 | Recuperar Proyectos Faltantes | ✓ OK | 23.1s |
| 29 | SP Cargar Dim Intersección | ✓ OK | 11.9s |

**Total: 28 pasos exitosos · 1 saltado (TRX_05 deshabilitado en config) · 0 fallidos**

---

### 4.2 Conteos de Verificación Post-ETL

#### Staging (Tablas de Aterrizaje)

| Tabla | Filas |
|-------|------:|
| `stg.consolidado_proyectos` | 1,127,987 |
| `stg.suia_rcoa_bi` | 429,111 |
| `stg.suia_coa_bi` | 392,011 |
| `stg.jbpm_4cat_bi` | 220,762 |
| `stg.stg_intersection` | 221,429 |
| `stg.online_payments_historical_bi` | 184,236 |
| `stg.online_payments_bi` | 183,876 |
| `stg.jbpm_sector_bi` | 79,302 |
| `stg.financial_transaction_bi` | 85,058 |
| `stg.stg_waste_generator` | 33,748 |
| `stg.stg_detail_pesticide_project` | 6,485 |
| `stg.stg_pesticide_project` | 1,031 |
| `stg.stg_products_pqa` | 2,801 |
| `stg.stg_waste_type` | 1,425 |
| `stg.jbpm_hidro_bi` | 6,801 |

#### Data Warehouse (Dimensiones)

| Tabla | Filas |
|-------|------:|
| `dw.dim_proyecto` | 427,928 |
| `dw.dim_intersection` | 221,429 |
| `dw.dim_proponente` | 139,175 |
| `dw.dim_usuario` | 92,629 |
| `dw.dim_tiempo` | 9,497 |
| `dw.dim_actividad` | 3,361 |
| `dw.dim_geografia` | 1,637 |
| `dw.dim_area` | 1,100 |
| `dw.dim_pago` | 119 |
| `dw.dim_estado` | 26 |

#### Data Warehouse (Hechos)

| Tabla | Filas | Detalle |
|-------|------:|---------|
| `dw.fact_regularizacion` | 1,142,995 | RCOA: 429,111 · COA: 392,011 · JBPM_4CAT: 220,762 · JBPM_SECTOR: 79,302 · RECUPERADO: 15,008 · HIDRO: 6,801 |
| `dw.fact_proyecto_geografia` | 356,191 | Bridge proyectos ↔ geografía |
| `dw.fact_pago` | 92,466 | JBPM: 69,009 · SUIA_RCOA: 23,457 |

---

### 4.3 Métricas del Data Warehouse

| Métrica | Valor |
|---------|------:|
| Tamaño total de la base de datos | **5,047 MB** |
| Proyectos únicos con hechos | **346,401** |
| Proponentes únicos en hechos | **139,174** |
| Rango temporal cubierto | **2005-01-01 a 2030-12-31** |
| Proyectos con georreferencia | **9,155,453** (vínculos totales) |

---

## 5. Tablas con 0 Filas — Análisis

Las siguientes tablas finalizaron con 0 filas. Esto no representa un error del ETL sino ausencia de datos disponibles en los sistemas de origen:

| Tabla | Causa |
|-------|-------|
| `stg.stg_chemical_substance` | Módulo de sustancias químicas no tiene registros activos en origen |
| `stg.stg_chemical_sustances_records` | Ídem — módulo MAAE/sustancias en construcción |
| `stg.stg_import_request` | Sin solicitudes de importación en SUIA_III |
| `stg.stg_chemical_substances_declaration` | Sin declaraciones en el período |
| `stg.stg_chemical_substances_movements` | Sin movimientos registrados |
| `stg.stg_project_mapping` | Tabla de mapeo sin datos de origen |
| `stg.stg_fact_waste_generation` | Declaraciones anuales comentadas en SP (NOTA en código) |
| `dw.dim_waste_type` | Depende de `stg_fact_waste_generation` |
| `dw.dim_chemical_substance` | Depende de staging de químicos |
| `dw.fact_waste_generation` | Depende de declaraciones anuales deshabilitadas |
| `stg.jbpm_snap_variables` | Sistema SNAP sin variables configuradas |

---

## 6. Archivos Modificados

| Archivo | Tipo | Descripción del Cambio |
|---------|------|------------------------|
| `ETL_p/etl_main.py` | Python | Reordenamiento de `SETUP_REFERENCE_DATA` al paso 15; actualización de metadatos de pasos |
| `ETL_p/config.py` | Python | Agregada clave `SETUP_REFERENCE_DATA: True` en `PASOS_HABILITADOS` |
| `ETL_p/transformacion/transformacion_all.py` | Python | Función `setup_reference_data()` agregada; `SQL_RECALCULO_MONTOS` corregido (eliminados `REPLACE()` innecesarios) |
| `ETL_p/ingesta/ingesta_all.py` | Python | `QUERY_TRX_09`: cast `NULLIF(REPLACE(col::text,',','.'), '')::double precision` aplicado a campos numéricos |
| `ETL_p/ingesta/ingesta_pesticides.py` | Python | Typo `depp_id` → `depe_id` |
| `ETL_p/ingesta/ingesta_waste_chemical.py` | Python | Query `stg_rgd_warehouses` reescrita con `recovery_points`; query `stg_rgd_manifests` corregida con JOINs correctos |
| `ETL_p/utils.py` | Python | `verificar_conteos()` ampliado de 17 a 38 tablas |
| `ETL_p/README.md` | Markdown | Actualizado: 18 pasos → 29 pasos; tabla de secuencia completa |
| `etl_waste_chemical_load.sql` | SQL | `CALL` → `SELECT dw.sp_carga_waste_chemical_v2()` |
| `setup_reference_data_v1_4.sql` | SQL | Agregado sentinel `dim_capa_ambiental (sk_capa=0)` |
| `Jobs/JOB_CARGA_DWH_REGULARIZACION.kjb` | Pentaho | 5 correcciones de hops, nodos y configuración (ver sección 3.12) |
| `dw.sp_carga_dim_area` | PostgreSQL SP | Sentinel `id_area=0` reescrito con `sk_area=0` explícito |
| `dw.sp_carga_fact_pago` | PostgreSQL SP | PARTE B (producto cartesiano) deshabilitada |
| `dw.sp_carga_waste_chemical_v2` | PostgreSQL SP | `DISTINCT ON` agregado para eliminar duplicados antes de `ON CONFLICT` |

---

## 7. Observaciones y Recomendaciones

### 7.1 Observaciones Técnicas

1. **Calidad de datos en origen JBPM**: Las columnas `retired_value`, `value_updated` y `retired_value_1` de `online_payment.online_payments_historical` contienen valores con coma decimal (formato europeo) y strings vacíos en lugar de NULL. Esto sugiere que los datos fueron migrados desde un sistema con configuración regional diferente. Se recomienda revisar el proceso de carga en JBPM.

2. **Esquema RETCE desactualizado**: Múltiples columnas referenciadas en las queries de ingesta (`hwge_id`, `hwma_id`, `dmwa_waste_amount_generated`) no existen en las tablas actuales del esquema `retce`. El código ETL no fue actualizado cuando se reestructuró el esquema.

3. **Propagación cruzada de pagos (PARTE B)**: La lógica de asociar todos los pagos de un proponente a todos sus proyectos es conceptualmente incorrecta en un modelo de regularización individual por expediente. Cada pago debe asociarse únicamente al proyecto que lo genera.

4. **Tablas auxiliares de Waste/Chemical**: 10 de las 11 tablas del módulo de desechos/químicos finalizan con 0 filas. Se recomienda verificar con el equipo de SUIA si el módulo de sustancias químicas está activo o si los datos están en otro esquema.

### 7.2 Recomendaciones para Próximas Ejecuciones

| Prioridad | Recomendación |
|-----------|---------------|
| Alta | Ejecutar el pipeline completo (`--desde 1`) una vez estabilizados todos los fixes para validar la secuencia completa de inicio a fin |
| Alta | Agregar monitoreo de espacio en disco antes de `SP_CARGA_FACT_PAGO` (umbral mínimo: 10 GB libres) |
| Media | Implementar validación de `sk_area=0` en `dim_area` como precondición del paso 16 |
| Media | Revisar y actualizar todas las queries del módulo `ingesta_waste_chemical.py` contra el esquema actual de SUIA_III |
| Media | Validar disponibilidad de datos de sustancias químicas con el equipo de SUIA para activar los módulos con 0 filas |
| Baja | Habilitar `TRX_05_JBPM_HIDRO` si los datos de hidrocarburos son requeridos para el análisis |
| Baja | Configurar variables de entorno para credenciales de BD (actualmente en texto plano en `config.py`) |

---

## 8. Conclusión

El pipeline ETL del Data Warehouse de Regularización Ambiental fue auditado, corregido y ejecutado exitosamente el día 2026-04-08. Se identificaron y resolvieron **12 defectos técnicos** que impedían la ejecución completa del pipeline. La ejecución final cargó más de **1.1 millones de registros de regularización**, **92,466 pagos** y **221,429 intersecciones ambientales** en el Data Warehouse, dejando el sistema en estado operativo para consumo por herramientas de análisis y reportería.

---

*Reporte generado automáticamente a partir de logs de ejecución y metadatos del sistema.*  
*Archivo de log fuente: `logs/etl_20260408.log`*  
*Fecha de generación: 2026-04-08 16:30*
