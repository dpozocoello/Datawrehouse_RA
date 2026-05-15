# 🗺️ Matriz de Mapeo Origen-Destino: DWH Regularización (v1.6)

Este documento detalla el linaje de datos (Lineage) desde los sistemas transaccionales hasta las tablas finales en el Data Warehouse.

---

## 1. Módulo: Regularización Ambiental (Core)

| Entidad | Sistema Origen | Tabla Origen | Tabla Staging (`stg`) | Tabla DWH (`dw`) | Motor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Proyectos RCOA** | SUIA-ENLISY (.179) | `coa_mae.tmp_rcoa_bi` | `suia_rcoa_bi` | `fact_regularizacion` | Core: Python |
| **Proyectos COA** | SUIA-ENLISY (.179) | `suia_iii.tmp_coa_bi` | `suia_coa_bi` | `fact_regularizacion` | Core: Python |
| **Puntualizacion SNAP** | SUIA-BPM (.179) | `variableinstancelog` | `jbpm_snap_variables` | `bridge_interseccion_ambiental`| Core: Python |
| **Geografía Política** | SUIA-ENLISY (.179) | `geographical_locations` | `geographical_locations_bi` | `dim_geografia` | Core: Python |
| **Oficinas Técnicas** | SUIA-ENLISY (.179) | `public.areas` | `suia_areas_bi` | `dim_area` | Core: Python |

---

## 2. Módulo: Gestión Financiera e Históricos (v1.6)

| Entidad | Sistema Origen | Tabla Origen | Tabla Staging (`stg`) | Tabla DWH (`dw`) | Motor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pagos Recientes** | JBPM (.226) | `online_payments` | `online_payments_bi` | `fact_pago` | Core: Python |
| **Pagos Históricos** | JBPM (.226) | `online_payments_historical` | `online_payments_historical_bi`| `fact_pago` | Core: Python |
| **Trazabilidad Delta** | JBPM (.226) | `online_payments_historical` | `online_payments_historical_bi`| `fact_payment_traceability`| Core: Python |

---

## 3. Módulo: Residuos y Químicos (v1.6)

| Entidad | Sistema Origen | Tabla Origen | Tabla Staging (`stg`) | Tabla DWH (`dw`) | Motor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Generadores** | COA (.179) | `waste_generator_record_coa` | `stg_waste_generator` | `dim_waste_generator` | Core: Python |
| **Registro RUC** | SUIA (.179) | `master_usuarios` | `stg.master_usuarios` | `dim_waste_generator` | Core: Python |
| **Tipos de Residuos** | COA (.179) | `waste_type_record_coa` | `stg_waste_type` | `dim_waste_type` | Core: Python |
| **Hechos Residuos** | COA (.179) | `waste_generator_record_coa` | `stg_fact_waste_generation` | `fact_waste_generation` | Core: Python |

---

## 4. Diccionario de Transformaciones Críticas

| Transformación | Lógica de Negocio | Scripts / Objetos SQL |
| :--- | :--- | :--- |
| **Consolidación v1.6**| Unifica proyectos de SUIA y JBPM vía Python Engine. | `dw.sp_consolidar_staging()` |
| **Inferencia Area** | Resuelve la jerarquía geográfica política (Localidad -> Provincia). | `dw.sp_carga_dim_area()` |
| **Deduplicación** | Selecciona la versión más reciente por proyecto. | `DISTINCT ON (codigo_proyecto)` |
| **Optimización IDs** | Mapeo de IDs numéricos a códigos SUIA (Estabilizado). | `stg.tmp_dim_proyecto_optimized` |
| **Forense Delta** | Cálculo de diferencia entre saldos históricos. | `dw.fact_payment_traceability` |

---

**Arquitecto de Datos:** Antigravity AI Data Solutions  
**Versión:** 1.6  
**Fecha:** 2026-03-17  
**Ubicación:** `D:\Datawrehouse_RA`
