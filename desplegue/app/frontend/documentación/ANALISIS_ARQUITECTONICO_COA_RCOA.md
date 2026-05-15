# Informe Técnico: Análisis de Discrepancia COA vs RCOA

Como Arquitecto de Datos, he analizado la estructura del DWH y el comportamiento del SQL proporcionado. A continuación, el diagnóstico de por qué el filtro por `'COA'` podría estar devolviendo resultados vacíos.

## 1. Diagnóstico Arquitectónico

### A. Registros Huérfanos en la Dimensión (Causa Probable: 80%)
Es común que existan maestros (Generadores tipo `'COA'`) que aún no tienen transacciones reportadas en la tabla de hechos (`dw.fact_waste_generation`). 
- **Verificación**: Si existen en `dim_waste_generator` pero NO existe ningún registro en la Fact Table que los referencie, el query siempre devolverá vacío para ese tipo.

### B. Restricción por INNER JOIN (Causa Probable: 15%)
Tu SQL utiliza `JOIN` (Inner) para `dim_geografia` y `dim_waste_type`. 
- **El Problema**: Si los registros de tipo `'COA'` en la Fact Table tienen la llave geográfica (`geo_location_key`) o la llave de tipo de desecho (`waste_type_key`) como **NULL**, el motor SQL los descarta automáticamente.
- **Diferencia con RCOA**: Es posible que los registros `'RCOA'` tengan sus llaves foráneas completas, mientras que los `'COA'` tengan nulos en estas llaves críticas.

### C. Mismatch por Caracteres Ocultos (Causa Probable: 5%)
El valor `'COA'` en la base de datos podría tener espacios al final (ej. `'COA '`) o caracteres no imprimibles.
- **Verificación**: Un `WHERE generator_type = 'COA'` fallará ante un espacio extra, mientras que un `generator_type LIKE '%COA%'` funcionará.

---

## 2. Recomendación de "Safe Query" para Auditoría

Usa este query para diagnosticar la presencia real de los datos sin las restricciones del INNER JOIN:

```sql
SELECT 
    w.generator_type,
    COUNT(f.*) as total_hechos,
    SUM(CASE WHEN g.sk_geografia IS NULL THEN 1 ELSE 0 END) as sin_geo,
    SUM(CASE WHEN t.waste_type_key IS NULL THEN 1 ELSE 0 END) as sin_tipo_desecho
FROM dw.dim_waste_generator w
LEFT JOIN dw.fact_waste_generation f ON w.waste_generator_key = f.waste_generator_key
LEFT JOIN dw.dim_geografia g ON f.geo_location_key = g.sk_geografia
LEFT JOIN dw.dim_waste_type t ON f.waste_type_key = t.waste_type_key
WHERE w.generator_type ILIKE '%COA%'
GROUP BY 1;
```

**Si este query devuelve resultados pero con `total_hechos = 0`, significa que los generadores COA están cargados pero NO tienen registros de producción en el DWH.**

---
*Análisis generado por Antigravity Data Architecture Suite.*
