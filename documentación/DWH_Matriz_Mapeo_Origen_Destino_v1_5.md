# 🗺️ Matriz de Mapeo Origen-Destino: DWH Regularización (v1.5.1)

Este documento detalla el linaje de datos (Lineage) desde los sistemas transaccionales hasta las tablas finales en el Data Warehouse.

---

## 1. Módulo: Regularización Ambiental (Core)

| Entidad | Sistema Origen | Tabla Origen | Tabla Staging (`stg`) | Tabla DWH (`dw`) | Motor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Proyectos RCOA** | SUIA-ENLISY | `coa_mae.tmp_rcoa_bi` | `suia_rcoa_bi` | `fact_regularizacion` | CLI: Python |
| **Proyectos COA** | SUIA-ENLISY | `suia_iii.tmp_coa_bi` | `suia_coa_bi` | `fact_regularizacion` | CLI: Python |
| **Puntualizacion SNAP** | SUIA-BPM | `variableinstancelog` | `jbpm_snap_variables` | `bridge_interseccion_ambiental` | KTR: Pentaho |
| **Geografía Política** | SUIA-ENLISY | `geographical_locations` | `geographical_locations_bi` | `dim_geografia` | CLI: Python |
| **Oficinas Técnicas** | SUIA-ENLISY | `public.areas` | `suia_areas_bi` | `dim_area` | KTR: Pentaho |

---

## 2. Módulo: Gestión Financiera e Históricos

| Entidad | Sistema Origen | Tabla Origen | Tabla Staging (`stg`) | Tabla DWH (`dw`) | Motor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pagos Recientes** | JBPM (jbpmdb) | `online_payments` | `online_payments_bi` | `fact_pago` | KTR: Pentaho |
| **Pagos SUIA** | SUIA-ENLISY | `financial_transaction` | `financial_transaction_bi` | `fact_pago` | KTR: Pentaho |
| **Historial Saldo** | JBPM (jbpmdb) | `online_payments_historical` | `online_payments_historical_bi` | `fact_pago` | KTR: Pentaho |

---

## 3. Módulo: Residuos y Químicos (v1.5)

| Entidad | Sistema Origen | Tabla Origen | Tabla Staging (`stg`) | Tabla DWH (`dw`) | Motor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Generadores** | COA | `waste_generator_record_coa` | `stg_waste_generator` | `dim_waste_generator` | CLI: Python |
| **Tipos de Residuos** | COA | `waste_type_record_coa` | `stg_waste_type` | `dim_waste_type` | CLI: Python |
| **Hechos Residuos** | COA | `waste_generator_record_coa` | `stg_fact_waste_generation` | `fact_waste_generation` | CLI: Python |
| **Sustancias Químicas**| COA | `chemical_substance_record` | `stg_chemical_substance` | `dim_chemical_substance` | CLI: Python |
| **Productos PQA** | COA | `products_pqa` | `stg_chemical_substance` | `dim_chemical_substance` | CLI: Python |
| **Hechos Químicos** | COA | `products_pqa` / `chemical...` | `stg_fact_chemical_application` | `fact_chemical_application` | CLI: Python |

---

## 4. Diccionario de Transformaciones Críticas

| Transformación | Lógica de Negocio | Scripts / Objetos SQL |
| :--- | :--- | :--- |
| **Consolidación** | Unifica proyectos de 5 fuentes distintas. | `dw.sp_consolidar_staging()` |
| **Inferencia Area** | Resuelve la jerarquía geográfica política. | `dw.sp_carga_dim_area()` |
| **Deduplicación** | Selecciona la versión más reciente por proyecto. | `DISTINCT ON (codigo_proyecto)` |
| **Optimización IDs** | Mapeo de IDs numéricos a códigos SUIA (Estabilizado). | `stg.tmp_dim_proyecto_optimized` |
| **Limpieza Químicos** | Homogenización de unidades de medida. | `etl_waste_chemical_load.sql` |

---

**Analista de Datos:** Antigravity AI  
**Versión:** 1.5.1  
**Fecha:** 2026-03-12 
