# Informe de Validación Arquitectónica: Estructura RGD (COA vs RCOA)

## 1. Análisis de Relaciones en Producción (172.16.0.179)
Se ha validado que el ecosistema del Registro Generador de Desechos (RGD) opera bajo dos lógicas distintas dependiendo del tipo de proyecto (Legacy vs Nuevo).

### 1.1 Flujo COA (Licenciamiento Ambiental - Legacy)
Para proyectos con códigos tipo `MAE-RA-YYYY-XXXXXX`, la relación se basa en el esquema `suia_iii`:
- **Entidad Proyecto**: `suia_iii.projects_environmental_licensing` (`pren_id`)
- **Entidad Desechos**: `suia_iii.hazardous_wastes_generators` (`pren_id`)
- **Validación**: La extracción actual **no incluye** este flujo, lo que explica la ausencia de datos para proyectos MAE-RA antiguos.

### 1.2 Flujo RCOA (Registro Ambiental - Nuevos)
Para proyectos generados bajo el Código Orgánico del Ambiente (RCOA), la relación usa el esquema `coa_waste_generator_record`:
- **Entidad Proyecto**: `coa_mae.project_licencing_coa` (`prco_id`)
- **Puente**: `coa_waste_generator_record.waste_generator_record_project_licencing_coa` (`prco_id`, `ware_id`)
- **Entidad Desechos**: `coa_waste_generator_record.waste_generator_record_coa` (`ware_id`)
- **Validación**: Este flujo es el que implementa actualmente el orquestador `ingesta_waste_chemical.py`.

---

## 2. Propuesta de Unificación del ETL (v1.6.2)
Para garantizar la integridad del DWH, se propone unificar ambas fuentes en la tabla de hechos `stg.stg_fact_waste_generation` mediante un `UNION ALL`:

```sql
-- EXTRACCIÓN UNIFICADA RGD (HOST 179)
-- Parte A: RCOA (Actual)
SELECT 
    lp.id_proyect AS project_id, 
    w.ware_id AS waste_generator_id, 
    w.ware_creation_date AS date_generated, 
    pt.wada_id AS waste_type_id,
    NULL::int AS dangerous_waste_id, 
    NULL::int AS danger_class_id, 
    pt.wwgp_quantity_kilograms AS quantity_generated, 
    'RCOA' AS source_system
FROM coa_waste_generator_record.waste_generator_record_coa w
JOIN coa_waste_generator_record.waste_generator_record_project_licencing_coa lp 
    ON w.ware_id = lp.ware_id
JOIN coa_waste_generator_record.waste_waste_generation_points pt 
    ON w.ware_id = pt.ware_id

UNION ALL

-- Parte B: COA (Nueva Incorporación)
SELECT 
    pel.pren_id AS project_id,
    hwg.hwge_id AS waste_generator_id,
    hwg.hwge_creation_date AS date_generated,
    hwg.cawa_id AS waste_type_id,
    NULL::int AS dangerous_waste_id,
    NULL::int AS danger_class_id,
    hwg.hwge_quantity AS quantity_generated,
    'COA' AS source_system
FROM suia_iii.hazardous_wastes_generators hwg
JOIN suia_iii.projects_environmental_licensing pel 
    ON hwg.pren_id = pel.pren_id;
```

---

## 3. Validación de Pagos y BPMS
- **Pagos (179/226)**: Los trámites de RGD se identifican por `fitr_payment_type = 3`. Se debe asegurar que el `project_id` en `online_payments_historical` coincida con los IDs obtenidos en la unificación anterior.
- **BPMS (179)**: Se validó que las variables de proceso en `suia_bpms_enlisy_app` permiten rastrear el estado del trámite ("En curso", "Emitido"). Se recomienda incluir el `processinstanceid` en la tabla de hechos para trazabilidad.

---
**Conclusión**: La arquitectura actual del DWH es robusta para RCOA, pero requiere la expansión hacia `suia_iii.hazardous_wastes_generators` para cubrir el espectro completo de proyectos históricos.
