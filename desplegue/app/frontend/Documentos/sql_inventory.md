# Inventario de Consultas SQL - Dashboard RG v1.01

Este documento contiene el inventario técnico de todas las consultas SQL ejecutadas por el Dashboard para poblar las diferentes pestañas y funcionalidades.

## 1. Integridad y Control (Pestaña 1)

### Resumen de Integridad
**Uso:** Muestra el estado general de carga del Data Warehouse.
```sql
SELECT * FROM dw.v_integridad_dashboard;
```

### Análisis de Discrepancias
**Uso:** Identifica proyectos presentes en las tablas de Stage que no han sido migrados a las dimensiones (DIM).
**Parámetros:** `:stg_table` (Nombre de la tabla de stage)
```sql
SELECT s.codigo_proyecto, s.nombre_proyecto, s.fecha_registro
FROM {stg_table} s
WHERE NOT EXISTS (
    SELECT 1 FROM dw.dim_proyecto p 
    WHERE p.codigo_proyecto = s.codigo_proyecto
)
AND s.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
LIMIT 200;
```

---

## 2. Orígenes y Periodos (Pestaña 2)

### Proyectos por Origen
**Uso:** Estadísticas de volumen y fechas extremas por sistema origen (JBPM, SUIA, COA).
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
ORDER BY cantidad_proyectos DESC;
```

### Reporte Detallado del Periodo
**Uso:** Lista detallada de trámites iniciados en un rango de fechas.
**Parámetros:** `:start_date`, `:end_date`
```sql
SELECT DISTINCT ON (p.codigo_proyecto, f.origen)
    p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental,
    f.origen, f.proceso, e.estado_proceso, e.estado_tramite,
    f.fecha_inicio_proceso, f.fecha_fin_proceso
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
WHERE f.fecha_inicio_proceso BETWEEN :start_date AND :end_date
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY p.codigo_proyecto, f.origen, f.fecha_inicio_proceso DESC;
```

---

## 3. Validador de Proyecto (Pestaña 3)

### Historial de Tareas
**Uso:** Muestra cronológicamente cada paso que ha seguido un proyecto individual.
**Parámetros:** `:cp` (Código de Proyecto)
```sql
SELECT 
    f.proceso, f.tarea, e.estado_proceso, e.estado_tramite, 
    f.fecha_inicio_tarea, f.fecha_fin_tarea, u.usuario_tarea
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
LEFT JOIN dw.dim_usuario u ON f.sk_usuario = u.sk_usuario
WHERE p.codigo_proyecto = :cp
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY f.fecha_inicio_tarea DESC;
```

### Detalle de Pagos
**Uso:** Recupera los cobros asociados a un proyecto para su visualización y fusión.
**Parámetros:** `:cp` (Código de Proyecto)
```sql
SELECT 
    fp.numero_tramite, fp.numero_transaccion, fp.monto_pagado,
    dp.tipo_pago, dt.fecha as fecha_pago, fp.proceso_bpm,
    fp.tarea_bpm, fp.origen, fp.secuencia_pago
FROM dw.fact_pago fp
JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
JOIN dw.dim_pago dp ON fp.sk_pago = dp.sk_pago
LEFT JOIN dw.dim_tiempo dt ON fp.sk_fecha_pago = dt.sk_tiempo
WHERE p.codigo_proyecto = :cp
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY dt.fecha ASC, fp.secuencia_pago ASC;
```

---

## 4. Análisis Geográfico y Pagos Generales (Pestañas 4 y 5)

### Agregación Geográfica
**Uso:** Resumen de volumen de proyectos por niveles de jerarquía.
**Parámetros:** `:sd`, `:ed` (Fechas)
```sql
WITH ProyectosUnicos AS (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia, sk_area
    FROM dw.fact_regularizacion
    WHERE fecha_inicio_proceso BETWEEN :sd AND :ed
    ORDER BY sk_proyecto, fecha_inicio_proceso DESC
)
SELECT 
    geo.provincia, geo.canton, geo.parroquia, da.nombre_area as oficina_tecnica, 
    COUNT(DISTINCT p.codigo_proyecto) as cantidad_proyectos
FROM ProyectosUnicos f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
GROUP BY 1, 2, 3, 4;
```

### Reporte General de Pagos
**Uso:** Listado consolidado de cobros a nivel nacional con filtros geográficos.
```sql
SELECT 
    dt.fecha as fecha_pago, p.codigo_proyecto, p.nombre_proyecto,
    p.tipo_permiso_ambiental, COALESCE(fp.numero_tramite, fp.numero_transaccion) as tramite,
    fp.numero_transaccion, fp.numero_tramite, fp.monto_pagado,
    fp.proceso_bpm, fp.tarea_bpm, geo.provincia, geo.canton, geo.parroquia,
    area.nombre_area as oficina_tecnica, fp.origen, fp.secuencia_pago
FROM dw.fact_pago fp
JOIN dw.dim_proyecto p ON fp.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_tiempo dt ON fp.sk_fecha_pago = dt.sk_tiempo
LEFT JOIN (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia, sk_area 
    FROM dw.fact_regularizacion ORDER BY sk_proyecto, fecha_inicio_proceso DESC
) fr ON p.sk_proyecto = fr.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON fr.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area area ON fr.sk_area = area.sk_area
WHERE dt.fecha BETWEEN :sd AND :ed
AND p.nombre_proyecto != 'Proyecto Recuperado (JBPM)'
ORDER BY dt.fecha DESC;
```

---

## 5. Gestión y Estadística (Pestaña 6)

### Indicadores Globales de Gestión
**Uso:** KPIs maestros: Estratégicos, tiempos de resolución, cobertura.
```sql
SELECT 
    COUNT(DISTINCT p.codigo_proyecto) as total_proyectos,
    COUNT(DISTINCT CASE WHEN p.estrategico = 'SI' THEN p.codigo_proyecto END) as proyectos_estrategicos,
    COUNT(DISTINCT da.nombre_area) as total_oficinas,
    COUNT(DISTINCT f.sk_geografia) as total_localidades,
    AVG(EXTRACT(EPOCH FROM (f.fecha_fin_proceso - f.fecha_inicio_proceso))/86400) as dias_promedio_resolucion
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
WHERE f.fecha_inicio_proceso BETWEEN :sd AND :ed;
```

### Ficha Técnica de Proyecto (Arquitectura)
**Uso:** Vista 360 del proyecto, integrando proponente, ubicación y estatus de intersección.
```sql
WITH BridgeCheck AS (
    SELECT b.sk_proyecto, COUNT(*) as detail_count
    FROM dw.bridge_interseccion_ambiental b
    JOIN dw.dim_proyecto p ON b.sk_proyecto = p.sk_proyecto
    WHERE p.codigo_proyecto = :cp
    GROUP BY b.sk_proyecto
)
SELECT 
    p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental,
    p.tipo_sector, p.tipo_ente, p.sistema, p.estrategico, p.area_responsable,
    prop.nombre_proponente, prop.ced_ruc_proponente,
    geo.provincia, geo.canton, geo.parroquia, da.nombre_area as oficina_tecnica,
    f.superficie_proyecto,
    CASE 
        WHEN f.interseccion_snap NOT IN ('NO', 'N/A', '') AND f.interseccion_snap IS NOT NULL 
        OR bc.detail_count > 0 THEN 'C' ELSE 'S' 
    END as interseccion_snap,
    f.numero_resolucion, f.fecha_resolucion, f.ente_acreditado,
    MIN(f.fecha_inicio_proceso) as primera_fecha_inicio,
    MAX(f.fecha_fin_proceso) as ultima_fecha_fin,
    COUNT(DISTINCT f.tarea) as total_tareas_realizadas,
    MAX(e.estado_proceso) as estado_actual,
    EXTRACT(EPOCH FROM (MAX(f.fecha_fin_proceso) - MIN(f.fecha_inicio_proceso)))/86400 as dias_totales_proceso
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
JOIN dw.dim_estado e ON f.sk_estado = e.sk_estado
LEFT JOIN dw.dim_proponente prop ON f.sk_proponente = prop.sk_proponente
LEFT JOIN dw.dim_geografia geo ON f.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON f.sk_area = da.sk_area
LEFT JOIN BridgeCheck bc ON p.sk_proyecto = bc.sk_proyecto
WHERE p.codigo_proyecto = :cp
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19;
```

---

## 6. Superposición y Geopolítica (Pestañas 7 y 8)

### Análisis de Intersecciones (Tabla Puente)
**Uso:** Cruce dinámico con capas ambientales SNAP/Bosques. Consolidación de capas por fila.
```sql
WITH LatestFact AS (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia, sk_proponente, sk_area, interseccion_snap
    FROM dw.fact_regularizacion ORDER BY sk_proyecto, fecha_inicio_proceso DESC
)
SELECT 
    p.codigo_proyecto, p.nombre_proyecto, p.tipo_permiso_ambiental, p.sistema,
    geo.provincia, geo.canton, geo.parroquia, da.nombre_area as oficina_tecnica,
    prop.nombre_proponente as proponente,
    CASE 
        WHEN lf.interseccion_snap NOT IN ('NO', 'N/A', '') AND lf.interseccion_snap IS NOT NULL 
        OR EXISTS (SELECT 1 FROM dw.bridge_interseccion_ambiental b WHERE b.sk_proyecto = p.sk_proyecto) 
        THEN 'Interseca' ELSE 'No Interseca'
    END as estado_interseccion,
    (
        SELECT COALESCE(string_agg(DISTINCT c.nombre_capa, ', '), 'SIN CAPAS ESPECÍFICAS')
        FROM dw.bridge_interseccion_ambiental b
        JOIN dw.dim_capa_ambiental c ON b.sk_capa = c.sk_capa
        WHERE b.sk_proyecto = p.sk_proyecto
    ) as capas_ambientales
FROM dw.dim_proyecto p
JOIN LatestFact lf ON p.sk_proyecto = lf.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON lf.sk_geografia = geo.sk_geografia
LEFT JOIN dw.dim_area da ON lf.sk_area = da.sk_area
LEFT JOIN dw.dim_proponente prop ON lf.sk_proponente = prop.sk_proponente
WHERE p.nombre_proyecto != 'Proyecto Recuperado (JBPM)';
```

### Map Metrics (Geopolítica)
**Uso:** Cálculo de porcentajes de impacto para el mapa de calor de Plotly.
```sql
WITH GeoReciente AS (
    SELECT DISTINCT ON (sk_proyecto) sk_proyecto, sk_geografia, interseccion_snap
    FROM dw.fact_regularizacion ORDER BY sk_proyecto, fecha_inicio_proceso DESC
),
IntersectionStatus AS (
    SELECT p.sk_proyecto,
        MAX(CASE WHEN gr.interseccion_snap NOT IN ('NO', 'N/A', '') AND gr.interseccion_snap IS NOT NULL 
            OR b.sk_proyecto IS NOT NULL THEN 1 ELSE 0 END) as tiene_interseccion
    FROM dw.dim_proyecto p
    JOIN GeoReciente gr ON p.sk_proyecto = gr.sk_proyecto
    LEFT JOIN dw.bridge_interseccion_ambiental b ON p.sk_proyecto = b.sk_proyecto
    GROUP BY p.sk_proyecto
)
SELECT 
    geo.{provincia|canton} as ubicacion,
    COUNT(DISTINCT p.sk_proyecto) as total_proyectos,
    SUM(ist.tiene_interseccion) as total_intersecciones,
    (SUM(ist.tiene_interseccion)::float / NULLIF(COUNT(DISTINCT p.sk_proyecto), 0) * 100) as porcentaje_interseccion
FROM dw.dim_proyecto p
JOIN GeoReciente gr ON p.sk_proyecto = gr.sk_proyecto
JOIN IntersectionStatus ist ON p.sk_proyecto = ist.sk_proyecto
LEFT JOIN dw.dim_geografia geo ON gr.sk_geografia = geo.sk_geografia
GROUP BY 1;
```

---

## 7. Desechos y Químicos (Pestañas 9 y 10)

### Inventario de Desechos
```sql
SELECT 
    COALESCE(g.provincia, 'No Definida') as provincia,
    COALESCE(t.waste_name, 'Sin Clasificación') as tipo_desecho,
    SUM(f.quantity_generated) as total_generado,
    SUM(f.quantity_delivered) as total_entregado,
    COALESCE(f.unit, 'u') as unit, f.record_year
FROM dw.fact_waste_generation f
JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
GROUP BY 1, 2, 5, 6;
```

### Inventario de Químicos
```sql
SELECT 
    COALESCE(s.substance_name, 'Desconocida') as substance_name,
    COALESCE(s.classification, 'Sin Clasificación') as classification,
    SUM(f.dose) as dosis_total,
    COALESCE(f.dose_unit, 'u') as dose_unit,
    AVG(f.dose) as dosis_promedio, f.usage_year
FROM dw.fact_chemical_application f
JOIN dw.dim_chemical_substance s ON f.chemical_key = s.chemical_key
GROUP BY 1, 2, 4, 6;
```
