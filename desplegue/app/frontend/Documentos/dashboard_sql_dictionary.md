# Diccionario de Consultas SQL - Dashboard de Integridad

Este documento detalla las consultas SQL utilizadas en cada pestaña del dashboard para la extracción y visualización de datos de `dw_reg_v1`.

---

## 📊 Tab 1: KPI de Integridad

### Resumen de Integridad
**Función:** [load_integrity_summary()](file:///d:/DashboardRA/integrity_dashboard.py#29-33)
```sql
SELECT * FROM dw.v_integridad_dashboard
```

### Análisis de Discrepancias (Faltantes)
**Función:** [load_discrepancies(origen)](file:///d:/DashboardRA/integrity_dashboard.py#34-59)
```sql
SELECT s.codigo_proyecto, s.nombre_proyecto, s.fecha_registro
FROM {stg_table} s
WHERE NOT EXISTS (
    SELECT 1 FROM dw.dim_proyecto p 
    WHERE p.codigo_proyecto = s.codigo_proyecto
)
AND s.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
LIMIT 200
```
*Nota: `{stg_table}` se mapea dinámicamente según el origen (ej: `stg.suia_rcoa_bi`).*

---

## 📁 Tab 2: Proyectos por Origen

### Resumen por Sistema
**Función:** [load_projects_by_origin_summary()](file:///d:/DashboardRA/integrity_dashboard.py#500-517)
```sql
SELECT 
    f.origen,
    COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos,
    MIN(f.fecha_inicio_proceso) as fecha_inicio_mas_antigua,
    MAX(f.fecha_inicio_proceso) as fecha_inicio_mas_reciente,
    MAX(f.fecha_fin_proceso) as fecha_fin_mas_reciente
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
GROUP BY f.origen
ORDER BY cantidad_proyectos DESC
```

### Reporte Detallado por Periodo
**Función:** [load_origin_period_report(start_date, end_date, origenes)](file:///d:/DashboardRA/integrity_dashboard.py#518-549)
```sql
SELECT DISTINCT ON (p.codigo_proyecto, f.origen)
    p.codigo_proyecto,
    p.nombre_proyecto,
    p.tipo_permiso_ambiental,
    f.origen,
    f.proceso,
    e.estado_proceso,
    e.estado_tramite,
    f.fecha_inicio_proceso,
    f.fecha_fin_proceso
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
WHERE f.fecha_inicio_proceso BETWEEN :start_date AND :end_date
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
-- Filtro opcional: AND f.origen IN :origenes
ORDER BY p.codigo_proyecto, f.origen, f.fecha_inicio_proceso DESC
```

---

## 🔍 Tab 3: Validador de Proyecto

### Historial de Trámites
**Función:** [load_project_history(codigo_proyecto)](file:///d:/DashboardRA/integrity_dashboard.py#60-82)
```sql
SELECT 
    f.proceso, 
    f.tarea, 
    e.estado_proceso, 
    e.estado_tramite, 
    f.fecha_inicio_tarea, 
    f.fecha_fin_tarea,
    u.usuario_tarea
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
LEFT JOIN dw.dim_usuario u ON f.sk_usuario = u.sk_usuario
WHERE p.codigo_proyecto = :cp
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY f.fecha_inicio_tarea DESC;
```

### Detalle de Pagos
**Función:** [load_project_payments(codigo_proyecto)](file:///d:/DashboardRA/integrity_dashboard.py#83-145)
```sql
SELECT 
    fp.numero_tramite,
    fp.numero_transaccion,
    fp.monto_pagado,
    dp.tipo_pago,
    dt.fecha as fecha_pago,
    fp.proceso_bpm,
    fp.tarea_bpm,
    fp.origen,
    fp.secuencia_pago
FROM dw.fact_pago fp
JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
JOIN dw.dim_pago dp ON fp.sk_pago = dp.sk_pago
LEFT JOIN dw.dim_tiempo dt ON fp.sk_fecha_pago = dt.sk_tiempo
WHERE p.codigo_proyecto = :cp
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY dt.fecha DESC, fp.secuencia_pago ASC
```

---

## 🌎 Tab 4: Análisis Geográfico

### Agregación de Ubicaciones
**Función:** [load_geographic_aggregation(start_date, end_date)](file:///d:/DashboardRA/integrity_dashboard.py#146-176)
```sql
WITH ProyectosUnicos AS (
    SELECT DISTINCT ON (sk_proyecto) 
        sk_proyecto, 
        sk_geografia, 
        sk_area
    FROM dw.fact_regularizacion
    WHERE fecha_inicio_proceso BETWEEN :start_date AND :end_date
    ORDER BY sk_proyecto, fecha_inicio_proceso DESC
)
SELECT 
    COALESCE(NULLIF(TRIM(geo.provincia), ''), 'N/A') as provincia, 
    COALESCE(NULLIF(TRIM(geo.canton), ''), 'N/A') as canton, 
    COALESCE(NULLIF(TRIM(geo.parroquia), ''), 'N/A') as parroquia, 
    COALESCE(NULLIF(TRIM(da.nombre_area), ''), 'N/A') as oficina_tecnica, 
    COALESCE(NULLIF(TRIM(da.zona), ''), 'N/A') as zona_administrativa, 
    COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos
FROM ProyectosUnicos f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
GROUP BY 1, 2, 3, 4, 5
ORDER BY cantidad_proyectos DESC
```

### Matriz de Proyectos Detallada
**Función:** [load_detailed_projects(...)](file:///d:/DashboardRA/integrity_dashboard.py#177-218)
```sql
SELECT DISTINCT ON (p.codigo_proyecto)
    p.codigo_proyecto,
    p.nombre_proyecto,
    p.tipo_permiso_ambiental as tipo_tramite,
    e.estado_proceso,
    da.nombre_area as oficina_tecnica,
    geo.provincia,
    geo.canton,
    f.fecha_inicio_proceso
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
WHERE f.fecha_inicio_proceso BETWEEN :start_date AND :end_date
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
-- Filtros geográficos dinámicos adicionales...
ORDER BY p.codigo_proyecto, f.fecha_inicio_proceso DESC
```

---

## 💰 Tab 5: Reporte General de Pagos

### Reporte de Pagos Consolidado
**Función:** [load_payments_report(start_date, end_date)](file:///d:/DashboardRA/integrity_dashboard.py#219-274)
```sql
SELECT 
    dt.fecha as fecha_pago,
    p.codigo_proyecto,
    p.nombre_proyecto,
    COALESCE(fp.numero_tramite, fp.numero_transaccion) as tramite,
    fp.monto_pagado,
    geo.provincia,
    geo.canton,
    geo.parroquia,
    area.nombre_area as oficina_tecnica,
    p.tipo_permiso_ambiental as tipo_tramite
FROM dw.fact_pago fp
JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_tiempo dt ON fp.sk_fecha_pago = dt.sk_tiempo
LEFT JOIN (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia, sk_area 
    FROM dw.fact_regularizacion 
    ORDER BY sk_proyecto, fecha_inicio_proceso DESC
) fr ON p.sk_proyecto = fr.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON fr.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area area ON fr.sk_area = area.sk_area
WHERE dt.fecha BETWEEN :start_date AND :end_date
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY dt.fecha DESC
LIMIT 15000
```

---

## 📋 Tab 6: Gestión de Regularización

### Resumen de Gestión
**Función:** [load_management_summary(...)](file:///d:/DashboardRA/integrity_dashboard.py#387-420)
```sql
SELECT 
    COUNT(DISTINCT p.codigo_proyecto) as total_proyectos,
    COUNT(DISTINCT da.nombre_area) as total_oficinas,
    COUNT(DISTINCT f.sk_geografia) as total_localidades,
    AVG(EXTRACT(EPOCH FROM (f.fecha_fin_proceso - f.fecha_inicio_proceso))/86400) as dias_promedio_resolucion
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
WHERE f.fecha_inicio_proceso BETWEEN :start_date AND :end_date
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
-- Filtros geográficos dinámicos adicionales...
```

### Reporte de Tareas Paginas
**Función:** [load_management_report(...)](file:///d:/DashboardRA/integrity_dashboard.py#335-386)
```sql
SELECT 
    f.id_fact,
    p.codigo_proyecto,
    p.nombre_proyecto,
    f.proceso,
    f.tarea,
    e.estado_proceso,
    e.estado_tramite,
    COALESCE(da.nombre_area, 'N/A') as oficina_tecnica,
    COALESCE(geo.provincia, 'N/A') as provincia,
    COALESCE(geo.canton, 'N/A') as canton,
    COALESCE(geo.parroquia, 'N/A') as parroquia,
    f.fecha_inicio_proceso,
    f.fecha_fin_proceso
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
WHERE f.fecha_inicio_proceso BETWEEN :start_date AND :end_date
ORDER BY f.fecha_inicio_proceso DESC
LIMIT {limit} OFFSET {offset}
```

---

## 🌲 Tab 7: Superposición Ambiental

### Análisis de Intersecciones
**Función:** [load_environmental_analysis(...)](file:///d:/DashboardRA/integrity_dashboard.py#275-334)
```sql
WITH GeoProyectos AS (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia 
    FROM dw.fact_regularizacion 
    ORDER BY sk_proyecto, fecha_inicio_proceso DESC
),
BaseProyectos AS (
    SELECT 
        p.codigo_proyecto,
        p.nombre_proyecto,
        COALESCE(geo.provincia, 'N/A') as provincia,
        COALESCE(geo.canton, 'N/A') as canton,
        COALESCE(geo.parroquia, 'N/A') as parroquia,
        CASE 
            WHEN b.sk_proyecto IS NOT NULL AND c.nombre_capa NOT ILIKE '%SIN INTERSECCIÓN%' 
            THEN 'Interseca' 
            ELSE 'No Interseca' 
        END as estado_interseccion,
        COALESCE(c.nombre_capa, 'SIN INTERSECCIÓN') as nombre_capa,
        COALESCE(b.detalle_interseccion, 'Sin intersección detectable') as detalle_interseccion
    FROM dw.dim_proyecto p
    LEFT JOIN GeoProyectos fr ON p.sk_proyecto = fr.sk_proyecto
    LEFT JOIN dw.dim_geografia geo ON fr.sk_geografia = geo.sk_geografia
    LEFT JOIN dw.bridge_interseccion_ambiental b ON p.sk_proyecto = b.sk_proyecto
    LEFT JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
    WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
)
SELECT * FROM BaseProyectos
-- Filtros dinámicos de capas y ubicación...
ORDER BY nombre_capa, codigo_proyecto
```

---

## 🗺️ Tab 8: Geopolítica Ambiental

### Mapa de Intersección Provincial
**Función:** [load_geopolitical_intersection()](file:///d:/DashboardRA/integrity_dashboard.py#421-454)
```sql
WITH GeoReciente AS (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia
    FROM dw.fact_regularizacion
    ORDER BY sk_proyecto, fecha_inicio_proceso DESC
)
SELECT 
    geo.provincia, 
    COUNT(DISTINCT p.codigo_proyecto) as total_proyectos_localizados,
    COUNT(DISTINCT b.sk_proyecto) FILTER (WHERE c.nombre_capa NOT ILIKE '%SIN INTERSECCIÓN%') as total_proyectos_con_interseccion
FROM dw.dim_proyecto p
JOIN GeoReciente gr ON p.sk_proyecto = gr.sk_proyecto
JOIN dw.dim_geografia geo ON gr.sk_geografia = geo.sk_geografia
LEFT JOIN dw.bridge_interseccion_ambiental b ON p.sk_proyecto = b.sk_proyecto
LEFT JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
GROUP BY 1
ORDER BY total_proyectos_con_interseccion DESC
```

---

## 🗑️ Tab 9: Registro de Desechos

### Resumen de Generación
**Función:** [load_waste_summary()](file:///d:/DashboardRA/integrity_dashboard.py#550-568)
```sql
SELECT 
    COALESCE(g.provincia, 'No Definida') as provincia,
    COALESCE(t.waste_name, 'Sin Clasificación') as tipo_desecho,
    SUM(f.quantity_generated) as total_generado,
    SUM(f.quantity_delivered) as total_entregado,
    COALESCE(f.unit, 'u') as unit,
    f.record_year
FROM dw.fact_waste_generation f
JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
GROUP BY 1, 2, 5, 6
ORDER BY total_generado DESC
```

### Mapa Geopolítico de Desechos
**Función:** [load_geopolitical_waste()](file:///d:/DashboardRA/integrity_dashboard.py#589-603)
```sql
SELECT 
    COALESCE(provincia, 'No Definida') as provincia,
    COUNT(DISTINCT waste_generator_key) as num_generadores,
    SUM(quantity_generated) as total_generado
FROM dw.fact_waste_generation f
JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
GROUP BY 1
ORDER BY total_generado DESC
```

---

## 🧪 Tab 10: Sustancias Químicas

### Resumen de Aplicación
**Función:** [load_chemical_summary()](file:///d:/DashboardRA/integrity_dashboard.py#570-587)
```sql
SELECT 
    COALESCE(s.substance_name, 'Desconocida') as substance_name,
    COALESCE(s.classification, 'Sin Clasificación') as classification,
    SUM(f.dose) as dosis_total,
    COALESCE(f.dose_unit, 'u') as dose_unit,
    AVG(f.dose) as dosis_promedio,
    f.usage_year
FROM dw.fact_chemical_application f
JOIN dw.dim_chemical_substance s ON f.chemical_key = s.chemical_key
GROUP BY 1, 2, 4, 6
ORDER BY dosis_total DESC
```

---

## 🏷️ Catálogos y Utilidades

### Catálogo Maestro de Ubicaciones y Oficinas
**Función:** [get_mgmt_catalog()](file:///d:/DashboardRA/integrity_dashboard.py#455-499)
```sql
WITH MappingFrecuencia AS (
    SELECT 
        geo.provincia, 
        geo.canton, 
        geo.parroquia,
        da.nombre_area as oficina_tecnica,
        COUNT(*) as frecuencia,
        ROW_NUMBER() OVER(
            PARTITION BY geo.provincia, geo.canton, geo.parroquia 
            ORDER BY COUNT(*) DESC, da.nombre_area ASC
        ) as rank
    FROM dw.fact_regularizacion f
    JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
    JOIN dw.dim_area da ON f.sk_area = da.sk_area
    WHERE geo.provincia IS NOT NULL
    GROUP BY 1, 2, 3, 4
),
UbicacionesMaestras AS (
    SELECT DISTINCT provincia, canton, parroquia FROM dw.dim_geografia
)
SELECT 
    COALESCE(u.provincia, 'N/A') as provincia,
    COALESCE(u.canton, 'N/A') as canton,
    COALESCE(u.parroquia, 'N/A') as parroquia,
    COALESCE(m.oficina_tecnica, 'AREA NO DEFINIDA') as oficina_tecnica
FROM UbicacionesMaestras u
LEFT JOIN MappingFrecuencia m ON 
    u.provincia = m.provincia AND 
    u.canton = m.canton AND 
    u.parroquia = m.parroquia AND 
    m.rank = 1
ORDER BY 1, 2, 3, 4
```
