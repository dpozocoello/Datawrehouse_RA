# 📊 Guía de Uso del Data Warehouse para BI y Analítica

Esta documentación describe cómo explotar la estructura del Data Warehouse (`dw_reg_v1`) para generar reportes, dashboards y análisis de datos avanzados.

---

## 1. Fundamentos del Modelo Estrella
El DWH está diseñado bajo un esquema de **Hechos (Facts)** y **Dimensiones (Dimensions)**.

*   **Tablas de Hechos:** Contienen métricas cuantitativas (montos, superficies, conteos) y claves foráneas a las dimensiones.
*   **Tablas Dimensionales:** Contienen atributos descriptivos (nombres, categorías, ubicaciones) que se usan para filtrar y agrupar los datos.

---

## 2. Principales Áreas de Análisis

### 2.1 Análisis de Regularización Ambiental
**Tabla Principal:** `dw.fact_regularizacion`
**Fuentes Involucradas:** SUIA (RCOA/COA) y JBPM (4 Cat/Hidro).

| Atributo Clave | Uso en BI |
| :--- | :--- |
| `interseccion_snap` | Identificar proyectos en áreas protegidas. |
| `superficie_proyecto` | Análisis de magnitud de impacto ambiental. |
| `sk_fecha_registro` | Evolución temporal de ingresos de trámites. |
| `sk_estado` | Monitoreo de cuellos de botella por estado de proceso. |

### 2.2 Análisis Financiero (Pagos)
**Tabla Principal:** `dw.fact_pago`
**Fuentes Involucradas:** JBPM (Online Payments) y SUIA (Financial Transactions).

| Atributo Clave | Uso en BI |
| :--- | :--- |
| `monto_transaccion` | Recaudación bruta por trámite. |
| `monto_acumulado` | Evolución del pago total de un proyecto en el tiempo. |
| `secuencia_pago` | Identificar si es pago inicial, multa o complementario. |
| `origen` | Comparar eficiencia de recaudación entre sistemas (JBPM vs SUIA). |

---

## 3. Ejemplos de Consultas SQL (Analíticas)

### A. Recaudación Mensual por Tipo de Trámite (Sector, 4Cat, COA, RECOA)
Útil para dashboards de finanzas para comparar la recaudación entre los diferentes tipos de licenciamiento.
```sql
SELECT 
    t.anio,
    t.nombre_mes,
    fr.origen as tipo_tramite,  -- Identifica si es Sector, 4 Categorías, COA o RECOA
    f.origen as sistema_pago,    -- Identifica si el pago vino de JBPM o SUIA
    SUM(f.monto_transaccion) as total_recaudado,
    COUNT(DISTINCT f.id_fact_pago) as num_transacciones
FROM dw.fact_pago f
JOIN dw.dim_tiempo t ON f.sk_fecha_pago = t.sk_tiempo
JOIN dw.fact_regularizacion fr ON f.sk_proyecto = fr.sk_proyecto
GROUP BY 1, 2, 3, 4
ORDER BY t.anio DESC, t.mes;
```

### B. Proyectos en Áreas Protegidas (SNAP) por Provincia
Identifica zonas de mayor sensibilidad ambiental.
```sql
SELECT 
    g.provincia,
    COUNT(*) as total_proyectos,
    SUM(f.superficie_proyecto) as hectareas_totales
FROM dw.fact_regularizacion f
JOIN dw.dim_geografia g ON f.sk_geografia = g.sk_geografia
WHERE f.interseccion_snap = 'SI'
GROUP BY 1
ORDER BY 2 DESC;
```

### C. Top 10 Proponentes con Mayor Inversión/Pagos
Identifica a los principales operadores económicos.
```sql
SELECT 
    p.nombre_proponente,
    COUNT(DISTINCT f.sk_proyecto) as num_proyectos,
    SUM(f.monto_transaccion) as total_pagado
FROM dw.fact_pago f
JOIN dw.dim_proyecto dp ON f.sk_proyecto = dp.sk_proyecto
JOIN dw.fact_regularizacion fr ON fr.sk_proyecto = dp.sk_proyecto
JOIN dw.dim_proponente p ON fr.sk_proponente = p.sk_proponente
GROUP BY 1
ORDER BY 3 DESC
LIMIT 10;
```

### D. Tiempo de Ciclo por Tipo de Proyecto
(Requiere que las fechas de inicio y fin estén pobladas en `fact_regularizacion`)
```sql
SELECT 
    dp.sistema_origen,
    AVG(f.fecha_fin_proceso - f.fecha_inicio_proceso) as dias_promedio_tramite
FROM dw.fact_regularizacion f
JOIN dw.dim_proyecto dp ON f.sk_proyecto = dp.sk_proyecto
WHERE f.fecha_fin_proceso IS NOT NULL
GROUP BY 1;
```

---

## 4. Mejores Prácticas para BI (Power BI / Tableau / Looker)

1.  **Filtrado por Tiempo:** Siempre use `dw.dim_tiempo` para los filtros de fecha. No use las columnas de fecha directamente de las tablas de hechos para asegurar consistencia.
2.  **Relaciones:** En su herramienta de BI, configure relaciones de **1 a Muchos (1:N)** desde las dimensiones hacia los hechos.
3.  **Métricas:**
    *   Para montos monetarios, use la función `SUM`.
    *   Para cantidad de proyectos, use `COUNT(DISTINCT sk_proyecto)`.
4.  **Geografía:** Use `dw.dim_geografia` para mapas, ya que los nombres están normalizados (limpios de tildes o variaciones de escritura).

---
**Generado por:** Arquitectura DWH
**Fecha:** 2026-03-05
