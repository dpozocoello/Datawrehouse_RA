# REPORTE DE INGESTA POST-EJECUCIÓN
## Data Warehouse — Regularización Ambiental & Migración OTRS
### Período de análisis: 2026-04-09 → 2026-04-15
**Generado por:** Arquitecto de Datos — Sistema DWH v1.4  
**Fecha de reporte:** 2026-04-15  
**Fuentes auditadas:** `etl_20260409.log` | `etl_20260415.log` | `job_master_otrs_etl.kjb`

---

## 1. RESUMEN EJECUTIVO

| Proceso | Motor | Última Ejecución | Estado | Registros Totales STG | Registros Totales DW |
|---|---|---|---|---|---|
| ETL DWH Regularización Ambiental | Python 3.14 | 2026-04-09 09:48 – 10:23 | EXITOSO (28/29 pasos) | 2,469,793 | 2,078,052 |
| ETL DWH Regularización Ambiental | Python 3.14 | 2026-04-15 09:32 – 09:41 | EXITOSO (parcial) | +272,558 nuevos módulos | N/A (ejecución parcial) |
| ETL Migración OTRS | Pentaho PDI 11 | Sin ejecución registrada | PENDIENTE | 0 | 0 |

**Hallazgo principal:** La ejecución del 15-Apr incorporó 6 nuevos módulos de ingesta (Importaciones Químicas + Plaguicidas PQA) con **244,313 registros adicionales** no presentes el 09-Apr, evidenciando crecimiento activo del pipeline.

---

## 2. ETL PYTHON — DWH REGULARIZACIÓN AMBIENTAL

### 2.1 Ficha de Ejecución

| Parámetro | Ejecución 1 (09-Apr) | Ejecución 2 (15-Apr) |
|---|---|---|
| Tipo | FULL LOAD (29 pasos) | PARCIAL (módulos seleccionados) |
| Hora inicio | 09:48:17 | 09:32:24 |
| Hora fin | 10:23:37 | 09:41:33 |
| Duración | **35m 17.7s** | **9m 9.0s** |
| Pasos exitosos | 28 | 6 (todos OK) |
| Pasos saltados | 1 (TRX_05 Hidrocarburos) | — |
| Pasos fallidos | 0 | 0 |
| Errores | Ninguno | Ninguno |

---

### 2.2 Capa de Extracción — Origen → Staging

#### FASE 1: Proyectos / Registros Ambientales

| Paso | Sistema Origen | Tabla Destino (stg.*) | Cols | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|---|
| TRX_01 | SUIA — RCOA | `stg.suia_rcoa_bi` | 36 | **429,430** | N/A (no ejecutado) | — |
| TRX_02 | SUIA — COA | `stg.suia_coa_bi` | 36 | **392,025** | N/A | — |
| TRX_03 | JBPM — Sector | `stg.jbpm_sector_bi` | 32 | **79,302** | N/A | — |
| TRX_04 | JBPM — 4 Categorías | `stg.jbpm_4cat_bi` | 32 | **220,762** | N/A | — |
| TRX_05 | JBPM — Hidrocarburos | `stg.jbpm_hidro_bi` | — | ⊘ SALTADO | ⊘ SALTADO | — |
| TRX_06 | SNAP — Variables BPM | `stg.jbpm_snap_variables` | 6 | **0** | N/A | — |
| **Subtotal Proyectos** | | | | **1,121,519** | | |

> `stg.jbpm_hidro_bi` mantiene **6,801 filas** de carga previa (verificación post-ETL).

#### FASE 2: Pagos Transaccionales

| Paso | Sistema Origen | Tabla Destino (stg.*) | Cols | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|---|
| TRX_07 | JBPM — `online_payment` | `stg.online_payments_bi` | 9 | **183,977** | N/A | — |
| TRX_08 | SUIA — `financial_transaction` | `stg.financial_transaction_bi` | 12 | **85,112** | N/A | — |
| TRX_09 | JBPM — `online_payments_historical` | `stg.online_payments_historical_bi` | 17 | **184,297** | N/A | — |
| **Subtotal Pagos** | | | | **453,386** | | |

#### FASE 3: Catálogos de Referencia

| Paso | Sistema Origen | Tabla Destino (stg.*) | Cols | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|---|
| TRX_10 | SUIA — Áreas Institucionales | `stg.suia_areas_bi` | 9 | **1,099** | N/A | — |
| TRX_11 | SUIA — Geografía INEC | `stg.geographical_locations_bi` | 4 | **2,006** | N/A | — |
| **Subtotal Catálogos** | | | | **3,105** | | |

#### FASE 4: Desechos y Químicos (RGD / SUIA III)

| Paso | Sistema Origen | Tabla Destino (stg.*) | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|
| INGESTA_WASTE v2 | SUIA III — `hazardous_waste_generator` | `stg.stg_waste_generator` | **33,755** | **33,800** | **+45** |
| INGESTA_WASTE v2 | SUIA III — `waste_catalogs_parent` | `stg.stg_waste_catalogs_parent` | **1** | **1** | 0 |
| INGESTA_WASTE v2 | SUIA III — `waste_type` | `stg.stg_waste_type` | **1,425** | **1,425** | 0 |
| INGESTA_WASTE v2 | SUIA III — `recovery_points` | `stg.stg_rgd_warehouses` | **26,634** | **26,634** | 0 |
| INGESTA_WASTE v2 | RETCE — `detail_manifests_waste` | `stg.stg_rgd_manifests` | **126,846** | **126,916** | **+70** |
| **Subtotal Desechos** | | | **188,661** | **188,776** | **+115** |

#### FASE 5: Importaciones Químicas PQA *(NUEVO — solo 15-Apr)*

| Paso | Sistema Origen | Tabla Destino (stg.*) | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|
| INGESTA_CHEMICAL_IMPORTS | PQA — `chemical_sustances_records` | `stg.stg_chemical_sustances_records` | 0 | **540** | **+540 ★** |
| INGESTA_CHEMICAL_IMPORTS | PQA — `import_request` | `stg.stg_import_request` | 0 | **648** | **+648 ★** |
| INGESTA_CHEMICAL_IMPORTS | PQA — `detail_import_request` | `stg.stg_detail_import_request` | N/A | **648** | **NUEVO ★** |
| INGESTA_CHEMICAL_IMPORTS | PQA — `chemical_substances_declaration` | `stg.stg_chemical_substances_declaration` | 0 | **2,228** | **+2,228 ★** |
| INGESTA_CHEMICAL_IMPORTS | PQA — `chemical_substances_movements` | `stg.stg_chemical_substances_movements` | 0 | **14,168** | **+14,168 ★** |
| INGESTA_CHEMICAL_IMPORTS | PQA — `project_mapping` | `stg.stg_project_mapping` | 0 | **226,621** | **+226,621 ★** |
| **Subtotal Importaciones Químicas** | | | **0** | **244,853** | **+244,853** |

#### FASE 6: Plaguicidas PQA

| Paso | Sistema Origen | Tabla Destino (stg.*) | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|
| INGESTA_PESTICIDES | PQA — `pesticide_project` | `stg.stg_pesticide_project` | **1,031** | **1,031** | 0 |
| INGESTA_PESTICIDES | PQA — `products_pqa` | `stg.stg_products_pqa` | **2,801** | **2,802** | **+1** |
| INGESTA_PESTICIDES | PQA — `detail_pesticide_project` | `stg.stg_detail_pesticide_project` | **6,485** | **6,487** | **+2** |
| **Subtotal Plaguicidas** | | | **10,317** | **10,320** | **+3** |

#### FASE 7: Intersecciones Geoespaciales

| Paso | Sistema Origen | Tabla Destino (stg.*) | Registros 09-Apr | Registros 15-Apr | Δ Delta |
|---|---|---|---|---|---|
| INGESTA_INTERSECTION | COA_MAE (179 capas) + SUIA_BPMS | `stg.stg_intersection` | **221,598** | **222,791** | **+1,193** |
| **Subtotal Intersecciones** | | | **221,598** | **222,791** | **+1,193** |

---

### 2.3 Consolidado de Staging por Sistema Origen

| Sistema Origen | Tablas STG Alimentadas | Total Registros (09-Apr) | Total Registros (15-Apr) | Δ Neto |
|---|---|---|---|---|
| SUIA — RCOA | 1 | 429,430 | 429,430 | 0 |
| SUIA — COA | 1 | 392,025 | 392,025 | 0 |
| JBPM — Sector | 1 | 79,302 | 79,302 | 0 |
| JBPM — 4 Categorías | 1 | 220,762 | 220,762 | 0 |
| JBPM — Pagos Online | 1 | 183,977 | 183,977 | 0 |
| JBPM — Pagos Históricos | 1 | 184,297 | 184,297 | 0 |
| SUIA — Transacciones Financieras | 1 | 85,112 | 85,112 | 0 |
| SUIA — Áreas | 1 | 1,099 | 1,099 | 0 |
| SUIA — Geografía INEC | 1 | 2,006 | 2,006 | 0 |
| SUIA III — Generadores RGD | 1 | 33,755 | 33,800 | **+45** |
| SUIA III — Tipos Desechos | 2 | 1,426 | 1,426 | 0 |
| SUIA III — Puntos Recuperación | 1 | 26,634 | 26,634 | 0 |
| RETCE — Manifiestos | 1 | 126,846 | 126,916 | **+70** |
| PQA — Importaciones Químicas | 6 | 0 | **244,853** | **+244,853** |
| PQA — Plaguicidas | 3 | 10,317 | 10,320 | **+3** |
| COA_MAE + SUIA_BPMS — Intersecciones | 1 | 221,598 | 222,791 | **+1,193** |
| **TOTAL STAGING** | **23** | **1,998,586** | **2,244,750** | **+246,164** |

---

### 2.4 Capa de Transformación y Consolidación

| Paso | Tipo | Operación | Resultado 09-Apr |
|---|---|---|---|
| SP_CONSOLIDAR_STAGING | SP PostgreSQL | MERGE multi-origen → `stg.consolidado_proyectos` | **1,128,320 filas** (44.1s) |
| RECALCULO_MONTOS_JBPM | SQL UPDATE | Recálculo saldo_anterior/actual en `stg.online_payments_historical_bi` | **67,557 filas afectadas** |
| UPDATE_AREA_RESPONSABLE | SQL UPDATE | Asignación área responsable a proyectos | **100 filas afectadas** |

---

### 2.5 Capa DW — Staging → Dimensiones

| Paso | Tabla Destino (dw.*) | Fuente STG | Registros 09-Apr | Tipo Carga |
|---|---|---|---|---|
| SP_CARGA_DIMENSIONES | `dw.dim_proyecto` | consolidado_proyectos | **428,132** | UPSERT |
| SP_CARGA_DIMENSIONES | `dw.dim_proponente` | consolidado_proyectos | **139,227** | UPSERT |
| SP_CARGA_DIMENSIONES | `dw.dim_actividad` | consolidado_proyectos | **3,362** | UPSERT |
| SP_CARGA_DIMENSIONES | `dw.dim_geografia` | geographical_locations_bi | **1,637** | UPSERT |
| SP_CARGA_DIMENSIONES | `dw.dim_usuario` | consolidado_proyectos | **92,682** | UPSERT |
| SP_CARGA_DIMENSIONES | `dw.dim_estado` | consolidado_proyectos | **26** | UPSERT |
| SP_CARGA_DIMENSIONES | `dw.dim_tiempo` | consolidado_proyectos | **9,497** | UPSERT |
| SP_CARGA_DIM_AREA | `dw.dim_area` | suia_areas_bi | **1,100** | UPSERT |
| SP_CARGA_DIM_PAGO | `dw.dim_pago` | online_payments_bi | **119** | UPSERT |
| SP_CARGA_DIM_INTERSECTION | `dw.dim_intersection` | stg_intersection | **221,598** | TRUNCATE+INSERT |
| RECOVER_MISSING_PROJECTS | `dw.dim_proyecto` (suplemento) | Producción | +108 (09-Apr) / +797 (15-Apr) | INSERT |
| SETUP_REFERENCE_DATA | Todas las dims | — | SK=0 en todas las dims | INSERT sentinel |
| **TOTAL DIMENSIONES** | **10 tablas** | | **897,948** | |

---

### 2.6 Capa DW — Staging → Tablas de Hechos

| Paso | Tabla Destino (dw.*) | Fuente STG | Registros 09-Apr | Tipo Carga | Duración |
|---|---|---|---|---|---|
| SP_CARGA_HECHOS | `dw.fact_regularizacion` | consolidado_proyectos | **1,224,850** | TRUNCATE+INSERT | 5m 40.2s |
| SP_CARGA_FACT_PAGO | `dw.fact_pago` | online_payments_bi + financial_transaction_bi | **92,536** | MERGE (Parte A+C) | 15.6s |
| SP_BRIDGE_PROYECTO_GEO | `dw.fact_proyecto_geografia` | consolidado_proyectos + geographical_locations | **437,813** | TRUNCATE+INSERT | 31.4s |
| SP_CARGA_PUENTE_AMBIENTAL | `dw.dim_capa_ambiental` | stg_intersection | Puente ambiental | INSERT/UPDATE | 24.9s |
| SP_CARGA_WASTE_CHEMICAL | `dw.dim_waste_type` (+ relacionadas) | stg_waste_type | Ver nota ① | UPSERT | 2.9s |
| SP_SECUENCIA_PAGOS | `stg.online_payments_historical_bi` | (auto) | Secuencias calculadas | UPDATE | 6.2s |
| **TOTAL HECHOS** | **3 tablas fact principales** | | **1,755,199** | | |

> ① `dw.dim_waste_type` reporta 0 filas en verificación final; la función `sp_carga_waste_chemical_v2()` retornó `TRUE` — indica que los desechos se cargan en tablas RGD no incluidas en la verificación estándar.

---

### 2.7 Comparativo de Cambios entre Ejecuciones (09-Apr vs 15-Apr)

Solo módulos ejecutados en ambas fechas:

| Tabla STG | 09-Apr | 15-Apr | Δ Absoluto | Δ % |
|---|---|---|---|---|
| `stg.stg_waste_generator` | 33,755 | 33,800 | **+45** | +0.13% |
| `stg.stg_waste_catalogs_parent` | 1 | 1 | 0 | 0% |
| `stg.stg_waste_type` | 1,425 | 1,425 | 0 | 0% |
| `stg.stg_rgd_warehouses` | 26,634 | 26,634 | 0 | 0% |
| `stg.stg_rgd_manifests` | 126,846 | 126,916 | **+70** | +0.06% |
| `stg.stg_pesticide_project` | 1,031 | 1,031 | 0 | 0% |
| `stg.stg_products_pqa` | 2,801 | 2,802 | **+1** | +0.04% |
| `stg.stg_detail_pesticide_project` | 6,485 | 6,487 | **+2** | +0.03% |
| `stg.stg_intersection` | 221,598 | 222,791 | **+1,193** | +0.54% |
| `dw.dim_proyecto` (recover) | +108 proyectos | +797 proyectos | **+689** | +638% ② |

> ② El salto en proyectos recuperados (+689) refleja que la ejecución del 15-Apr procesó más capas de intersección, exponiendo más referencias a proyectos aún no presentes en `dim_proyecto`.

---

## 3. ETL PENTAHO PDI — MIGRACIÓN OTRS

### 3.1 Ficha del Proceso

| Parámetro | Valor |
|---|---|
| Archivo principal | `repo/jobs/job_master_otrs_etl.kjb` |
| Versión | 1.0 |
| Motor | Pentaho PDI 11 (Kitchen.bat) |
| Modos soportados | `FULL_LOAD` / `INCREMENTAL` (watermark automático) |
| Batch size | 5,000 filas por cursor server-side |
| Estado actual | **SIN EJECUCIÓN REGISTRADA** |
| Logs de ejecución | Directorio `logs/` vacío |
| Datos en output | Directorio `data/output/` vacío |

### 3.2 Arquitectura del Pipeline

```
OTRS PostgreSQL 9.2 (172.16.0.231/otrs)
          │
          ├─ TRF_01: Extraer 8 Tablas Maestras ──────────► stg.queue / users / customer_user
          │                                                  stg.service / sla / ticket_state
          │                                                  stg.ticket_priority / ticket_type
          │
          ├─ TRF_02a: Extraer Tickets (cursor batch) ──► stg.ticket
          ├─ TRF_02b: Extraer Articles (cursor batch) ─► stg.article
          ├─ TRF_02c: Extraer Ticket History ──────────► stg.ticket_history
          │
          ├─ TRF_03: Cargar 8 Dimensiones (UPSERT) ────► dw.dim_queue / dim_agent / dim_customer
          │                                               dw.dim_state / dim_priority / dim_service
          │                                               dw.dim_sla / dim_ticket_type
          │
          ├─ TRF_04: Cargar dim_date (ON CONFLICT DO NOTHING)
          │
          ├─ TRF_05: Cargar fact_ticket ────────────────► dw.fact_ticket
          │           (SK lookup + close_time derivado
          │            + resolution_time_hours + SLA compliance)
          │
          └─ TRF_06: Reporte CSV ───────────────────────► data/output/ingestion_report_YYYYMMDD.csv
                     (métricas desde ctl.etl_job_run)
```

### 3.3 Estimación de Volúmenes (OTRS 3.3.6 — Sin ejecución real)

| Tabla Fuente (OTRS) | Tabla Destino | Estimación Registros | Observación |
|---|---|---|---|
| `otrs.queue` | `stg.queue` → `dw.dim_queue` | ~50–200 | Catálogo de colas de soporte |
| `otrs.users` | `stg.users` → `dw.dim_agent` | ~100–500 | Agentes de soporte |
| `otrs.customer_user` | `stg.customer_user` → `dw.dim_customer` | ~1K–50K | Clientes/usuarios |
| `otrs.service` | `stg.service` → `dw.dim_service` | ~50–200 | Catálogo de servicios |
| `otrs.sla` | `stg.sla` → `dw.dim_sla` | ~10–50 | Acuerdos de nivel de servicio |
| `otrs.ticket_state` | `stg.ticket_state` → `dw.dim_state` | ~10–20 | Estados de tickets |
| `otrs.ticket_priority` | `stg.ticket_priority` → `dw.dim_priority` | ~5–10 | Prioridades |
| `otrs.ticket_type` | `stg.ticket_type` → `dw.dim_ticket_type` | ~10–30 | Tipos de tickets |
| `otrs.ticket` | `stg.ticket` → `dw.fact_ticket` | **A determinar** | Tabla principal — volumen desconocido |
| `otrs.article` | `stg.article` | **A determinar** | Comentarios por ticket |
| `otrs.ticket_history` | `stg.ticket_history` | **A determinar** | Para derivar close_time |

> **Nota:** Los volúmenes reales se determinarán en la primera ejecución. El pipeline soporta FULL_LOAD para primera carga e INCREMENTAL para siguientes (basado en watermark `ctl.etl_job_run.end_time`).

### 3.4 Control de Ejecuciones (CTL Layer)

El job registra cada ejecución en la tabla `ctl.etl_job_run`:

| Campo | Descripción |
|---|---|
| `status` | `START` → `SUCCESS` / `FAIL` |
| `start_time` / `end_time` | Timestamps de inicio y fin |
| `rows_extracted` | Total filas leídas desde OTRS |
| `rows_loaded` | Total filas insertadas/actualizadas en DW |

El reporte post-ejecución se genera automáticamente en `data/output/` como CSV (TRF_06).

---

## 4. ANÁLISIS COMPARATIVO DE COBERTURA DE DATOS

### Origen por Sistema Fuente — Ejecución Completa (09-Apr)

| Sistema | Tipo | Registros en STG | Registros en DW | % Cobertura |
|---|---|---|---|---|
| SUIA — RCOA | Transaccional | 429,430 | 1,224,850 ③ | 100% |
| SUIA — COA | Transaccional | 392,025 | ↑ incluido | 100% |
| JBPM — Sector | Transaccional | 79,302 | ↑ incluido | 100% |
| JBPM — 4 Categorías | Transaccional | 220,762 | ↑ incluido | 100% |
| JBPM — Pagos Online | Transaccional | 183,977 | 92,536 ④ | 100% |
| JBPM — Pagos Históricos | Histórico | 184,297 | ↑ incluido | 100% |
| SUIA — Transacciones | Transaccional | 85,112 | ↑ incluido | 100% |
| SUIA — Áreas | Catálogo | 1,099 | 1,100 | 100% |
| SUIA — Geografía | Catálogo | 2,006 | 1,637 ⑤ | 81.6% |
| SUIA III / RETCE — Desechos | Ambiental | 188,661 | — | En proceso |
| COA_MAE — Intersecciones | Geoespacial | 221,598 | 221,598 | 100% |
| PQA — Químicos/Plaguicidas | Regulatorio | 10,317 | — | En proceso ⑥ |

> ③ `fact_regularizacion` consolida proyectos de RCOA + COA + JBPM (1,128,320 stg → 1,224,850 dw incluyendo proyectos recuperados)  
> ④ `fact_pago` incluye solo pagos con match de proyecto (excluye pagos sin tramite válido)  
> ⑤ Diferencia geográfica: 2,006 ubicaciones INEC vs 1,637 en DW — algunas ubicaciones sin proyectos asociados no generan entrada en dim_geografia  
> ⑥ Los módulos PQA completos se activaron el 15-Apr con 244,853 nuevos registros

---

## 5. INDICADORES DE CALIDAD DE DATOS

| Indicador | Valor | Umbral | Estado |
|---|---|---|---|
| Tasa de éxito de pasos | 28/29 = 96.6% | ≥95% | ✓ OK |
| Pasos con 0 filas esperadas | 5 tablas vacías conocidas | N/A | ✓ INFO |
| Pasos con 0 filas inesperadas | 0 | 0 | ✓ OK |
| Registros de proyectos recuperados (09-Apr) | 108 / 428,132 = 0.03% | <1% | ✓ OK |
| Registros de proyectos recuperados (15-Apr) | 797 | — | ⚠ MONITOREAR |
| Crecimiento stg_intersection (+6 días) | +1,193 = +0.54% | <5% | ✓ OK |
| Crecimiento stg_rgd_manifests (+6 días) | +70 = +0.06% | <5% | ✓ OK |
| Nuevos módulos activos (15-Apr) | +6 módulos PQA | — | ✓ EXPANSIÓN |

---

## 6. ALERTAS Y RECOMENDACIONES

### Alertas

| Prioridad | Proceso | Alerta | Acción Recomendada |
|---|---|---|---|
| MEDIA | Python ETL | `RECOVER_MISSING_PROJECTS` pasó de 108 a 797 proyectos en 6 días | Verificar que los 797 proyectos tienen datos completos en dim_proyecto |
| MEDIA | Python ETL | `dw.dim_waste_type = 0 filas` en verificación | Confirmar tablas de carga RGD fuera del scope de verificación estándar |
| BAJA | Pentaho ETL | Sin ejecución inicial registrada | Ejecutar FULL_LOAD y verificar conexión a OTRS (172.16.0.231) |
| INFO | Python ETL | 6 nuevos módulos PQA activados (+244,853 registros) | Agregar estas tablas a la verificación post-ETL estándar |

### Recomendaciones Arquitecturales

1. **Verificación post-ETL:** Actualizar el bloque de verificación en `etl_main.py` para incluir las nuevas tablas `stg_chemical_sustances_records`, `stg_import_request`, `stg_chemical_substances_declaration`, `stg_chemical_substances_movements`, `stg_project_mapping`, `stg_detail_import_request`.

2. **Ejecución Pentaho OTRS:** Realizar FULL_LOAD inicial para establecer baseline. Verificar disponibilidad del servidor OTRS en `172.16.0.231:5432` antes de ejecutar.

3. **Reporte comparativo automatizado:** Incorporar un paso final en el ETL Python que genere automáticamente el delta entre ejecución actual vs anterior, similar al `TRF_06` del job Pentaho.

4. **Monitoreo RECOVER_MISSING_PROJECTS:** Configurar alerta si este valor supera los 500 proyectos en una ejecución, ya que puede indicar inconsistencias entre fuentes de extracción.

---

*Reporte generado por arquitectura de auditoría DWH — Clasificación: Uso Interno*
