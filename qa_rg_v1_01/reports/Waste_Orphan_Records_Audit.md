# Report: Auditoría de Registros Huérfanos - Desechos 2026

## 1. Validación de Datos (Staging)
Se ejecutó la auditoría sobre la tabla `stg.stg_fact_waste_generation` para identificar registros sin código de proyecto (`project_id IS NULL`).

### Hallazgos Clave:
- **Volumen detectado**: **17,604 registros** en el año 2026 presentan `project_id` nulo.
- **Distribución**: El 100% de estos huérfanos corresponden a extracciones del año 2026.
- **Generadores más afectados**: Los IDs de generador 724, 8144 y 8469 concentran el mayor volumen de reportes sin proyecto vinculado.

## 2. Análisis del Proceso y Causa Raíz

### 2.1 Origen del dato (Producción)
El script de extracción [etl_waste_chemical_extract.sql](file:///d:/Datawrehouse_RA/etl_waste_chemical_extract.sql) realiza un `INNER JOIN` entre la tabla de registros de desechos y la tabla de vinculación de proyectos:

```sql
FROM coa_waste_generator_record.waste_record wr
JOIN coa_waste_generator_record.project_waste pw ON wr.record_id = pw.record_id;
```

**Causa Raíz Detallada**: 
- Al ser un `INNER JOIN`, la existencia de estos registros en el staging confirma que **SÍ existe un vínculo** en la tabla `project_waste` de producción. 
- Sin embargo, el campo `pw.project_id` de esa tabla en producción es **NULL**. 
- Esto ocurre generalmente cuando un generador reporta residuos a través de un portal simplificado o trámites que no requieren estar asociados a un proyecto de regularización ambiental específico (ej: Reportes de solo generador), pero el sistema aún crea la entrada en la tabla intermedia de vinculación.

### 2.2 Proceso Responsable
El proceso que trae esta información es:
1. **Pentaho Job**: `INGESTA_WASTE_CHEMICAL`.
2. **Script Motor**: `etl_orchestrator_waste_chemical.py`.
3. **Capa**: Staging (`stg.stg_fact_waste_generation`), la cual es un espejo fiel de la metadata encontrada en producción.

---
**Recomendación**: Si se requiere que estos registros aparezcan vinculados en el Dashboard, se debe realizar una limpieza de datos en la tabla `coa_waste_generator_record.project_waste` de producción o implementar una lógica de inferencia basada en el `RUC` del generador para asociarlos al proyecto de regularización más reciente del mismo proponente.
