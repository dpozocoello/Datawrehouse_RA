# Catálogo de Consultas Analíticas (DWH RA v1.4)
**Sentencias SQL de Extracción de Información Estratégica**

Este documento contiene las consultas optimizadas para obtener información desde las tablas de Hechos (`dw.fact`) y Dimensiones (`dw.dim`) del Data Warehouse.

---

## 1. Consultas de Regularización Ambiental (Hechos)

### 1.1. Vista General de Proyectos (Matriz Maestra)
Obtiene el detalle completo de los proyectos cargados, integrando sus dimensiones.

```sql
SELECT 
    dp.codigo_proyecto AS "Código Proyecto",
    dp.nombre_proyecto AS "Nombre Proyecto",
    dprop.nombre_proponente AS "Proponente",
    da.actividad_economica AS "Actividad",
    dg.provincia AS "Provincia",
    dg.canton AS "Cantón",
    darea.nombre_area AS "Área Responsable",
    fr.interseccion_snap AS "Cruza SNAP",
    de.estado_proceso AS "Estado Proceso",
    dt.fecha AS "Fecha Registro"
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp ON fr.sk_proyecto = dp.sk_proyecto
JOIN dw.dim_proponente dprop ON fr.sk_proponente = dprop.sk_proponente
JOIN dw.dim_actividad da ON fr.sk_actividad = da.sk_actividad
JOIN dw.dim_geografia dg ON fr.sk_geografia = dg.sk_geografia
JOIN dw.dim_estado de ON fr.sk_estado = de.sk_estado
JOIN dw.dim_tiempo dt ON fr.sk_fecha_registro = dt.sk_tiempo
JOIN dw.dim_area darea ON fr.sk_area = darea.sk_area
ORDER BY dt.fecha DESC;
```

### 1.2. Proyectos con Intersección SNAP (Filtro Crítico)
Filtra específicamente aquellos proyectos que cruzan áreas protegidas.

```sql
SELECT 
    dp.codigo_proyecto,
    dp.nombre_proyecto,
    dg.provincia,
    fr.areas_protegidas AS "Detalle Áreas Protegidas"
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp ON fr.sk_proyecto = dp.sk_proyecto
JOIN dw.dim_geografia dg ON fr.sk_geografia = dg.sk_geografia
WHERE fr.interseccion_snap = 'SI';
```

---

## 2. Consultas Financieras (Pagos)

### 2.1. Resumen de Recaudación por Proponente
Suma todos los pagos realizados por cada empresa/proponente.

```sql
SELECT 
    dprop.nombre_proponente AS "Proponente",
    dprop.ced_ruc_proponente AS "RUC",
    COUNT(fp.id_fact_pago) AS "Número de Pagos",
    SUM(fp.monto_pagado) AS "Total Recaudado"
FROM dw.fact_pago fp
JOIN dw.dim_proyecto dp ON fp.sk_proyecto = dp.sk_proyecto
JOIN dw.dim_proponente dprop ON dp.sk_proponente = dprop.sk_proponente -- Nota: Relación directa vía proyecto
GROUP BY dprop.nombre_proponente, dprop.ced_ruc_proponente
HAVING SUM(fp.monto_pagado) > 0
ORDER BY SUM(fp.monto_pagado) DESC;
```

### 2.2. Detalle de Pagos JBPM vs SUIA
Compara la recaudación entre los dos sistemas de origen.

```sql
SELECT 
    origen AS "Sistema de Origen",
    COUNT(*) AS "Transacciones",
    SUM(monto_pagado) AS "Monto Total"
FROM dw.fact_pago
GROUP BY origen;
```

---

## 3. Consultas Estadísticas y Distribución

### 3.1. Distribución Geográfica por Provincia
Contabiliza proyectos terminados por cada provincia.

```sql
SELECT 
    dg.provincia,
    COUNT(fr.id_fact) AS "Total Proyectos",
    ROUND(CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dw.fact_regularizacion) AS NUMERIC), 2) AS "Porcentaje %"
FROM dw.fact_regularizacion fr
JOIN dw.dim_geografia dg ON fr.sk_geografia = dg.sk_geografia
GROUP BY dg.provincia
ORDER BY "Total Proyectos" DESC;
```

### 3.2. Proyectos por Tipo de Permiso e Impacto
Categoriza los proyectos según su impacto ambiental.

```sql
SELECT 
    dp.tipo_permiso_ambiental AS "Tipo de Permiso",
    COUNT(fr.id_fact) AS "Número de Proyectos"
FROM dw.fact_regularizacion fr
JOIN dw.dim_proyecto dp ON fr.sk_proyecto = dp.sk_proyecto
GROUP BY dp.tipo_permiso_ambiental
ORDER BY 2 DESC;
```

---

## 4. Consultas de Verificación (Integridad)

### 4.1. Auditoría de "Registros No Definidos" (SK=0)
Identifica proyectos que no pudieron asociarse a una dimensión (Calidad de Datos).

```sql
SELECT 
    'Área No Definida' AS "Detección",
    COUNT(*) 
FROM dw.fact_regularizacion 
WHERE sk_area = 0
UNION ALL
SELECT 
    'Geografía No Definida',
    COUNT(*) 
FROM dw.fact_regularizacion 
WHERE sk_geografia = 0;
```

---
**Arquitectura de Datos**: Antigravity AI
**Uso**: Generación de reportes BI y dashboards Ejecutivos.
**Versión**: 1.4
