# Especificación Técnica: Tab 9 - Registro Nacional de Desechos

Este documento detalla la arquitectura, el modelo de datos y las consultas de negocio que sustentan la pestaña **"9. Desechos"** del Dashboard de Regularización Ambiental.

---

## 1. Objetivo de Negocio
Visualizar y monitorear la generación nacional de desechos peligrosos y especiales, permitiendo un análisis multianual por provincia y tipo de residuo para asegurar el cumplimiento de los registros ambientales.

## 2. Arquitectura de Datos (DWH)
El módulo de desechos utiliza un modelo de **Esquema Estrella** optimizado para consultas analíticas de gran volumen.

### 2.1 Tabla de Hechos Principal: `dw.fact_waste_generation`
Contiene las métricas de generación, entrega y almacenamiento.
- **Métricas**: `quantity_generated`, `quantity_delivered`, `quantity_stored`.
- **Llaves de Dimensión**: `waste_generator_key`, `waste_type_key`, `geo_location_key`, `sk_tiempo`.

### 2.2 Dimensiones Relacionadas
1.  **`dw.dim_waste_type`**: Clasificación del residuo (Nombres, códigos, estado).
2.  **`dw.dim_geografia`**: Ubicación (Provincia, Cantón, Parroquia).
3.  **`dw.dim_waste_generator`**: Información del proponente/generador (Nombre, tipo, código).

---

## 3. Lógica de Visualización (Dashboard)
El dashboard extrae un resumen consolidado mediante la función `load_waste_summary()`.

### 3.1 Consulta de Extracción Principal
```sql
SELECT 
    COALESCE(p.codigo_proyecto, 'N/A') as codigo_proyecto,
    COALESCE(w.codigo, 'N/A') as codigo_rgd,
    COALESCE(g.provincia, 'No Definida') as provincia,
    COALESCE(t.waste_name, 'Sin Clasificación') as tipo_desecho,
    SUM(f.quantity_generated) as total_generado,
    SUM(f.quantity_delivered) as total_entregado,
    COALESCE(f.unit, 'u') as unit,
    f.record_year
FROM dw.fact_waste_generation f
JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
LEFT JOIN dw.dim_proyecto p ON f.sk_proyecto = p.sk_proyecto
LEFT JOIN dw.dim_waste_generator w ON f.waste_generator_key = w.waste_generator_key
GROUP BY 1, 2, 3, 4, 7, 8
ORDER BY total_generado DESC;
```

### 3.2 Reporte de Generadores (Geopolítico)
```sql
SELECT 
    COALESCE(provincia, 'No Definida') as provincia,
    COUNT(DISTINCT waste_generator_key) as num_generadores,
    SUM(quantity_generated) as total_generado
FROM dw.fact_waste_generation f
JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
GROUP BY 1
ORDER BY total_generado DESC;
```

---

## 4. Diccionario de Campos y Unidades
| Campo | Origen | Descripción |
| :--- | :--- | :--- |
| **Código Proyecto** | `dim_proyecto` | Identificador único del proyecto ambiental asociado. |
| **Código RGD** | `dim_waste_generator` | Código del Registro de Generador de Desechos (RGD). |
| **Provincia** | `dim_geografia` | Ubicación política-administrativa del punto de generación. |
| **Tipo de Desecho** | `dim_waste_type` | Nombre técnico según el catálogo nacional de desechos. |
| **Total Generado** | `fact_waste_generation` | Sumatoria de la cantidad reportada como generada en el período. |
| **Total Entregado** | `fact_waste_generation` | Cantidad efectivamente entregada a gestores autorizados. |
| **Record Year** | `fact_waste_generation` | Año fiscal del registro de producción de desechos. |

---

## 5. Próximos Pasos Recomendados
1.  **Mapa de Calor**: Implementar la visualización GeoJSON para la intensidad de generación por provincia.
2.  **Evolución Temporal**: Agregar gráficos de líneas para comparar la generación vs entrega por año.
3.  **Filtro por Categoría**: Integrar la dimensión `dim_dangerous_classification` para filtrar por nivel de peligrosidad.

---
*Documento especificado para el equipo de Datos de Regularización Ambiental.*
