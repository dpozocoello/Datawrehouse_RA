# 📊 Guía de Uso del Data Warehouse para BI y Analítica (v1.6)

Esta documentación describe cómo explotar la estructura del Data Warehouse (`dw_reg_v1`) para generar reportes, dashboards y análisis de datos avanzados, incluyendo las nuevas capacidades de trazabilidad financiera y gestión de residuos, operando desde la nueva infraestructura en el disco `D:`.

---

## 1. Fundamentos del Modelo Estrella (Expert View)
El DWH está diseñado bajo un esquema de **Hechos (Facts)** y **Dimensiones (Dimensions)** optimizado para consultas de agregación masiva.

*   **Tablas de Hechos:** Contienen métricas cuantitativas (montos, superficies, conteos, deltas financieros). Son tablas de alta cardinalidad.
*   **Tablas Dimensionales:** Contienen atributos descriptivos (nombres, categorías, RUCs, estados) que actúan como "Ejes" de análisis.

---

## 2. Áreas de Análisis Crítico v1.6

### 2.1 Gestión de Residuos (COA/RGD)
**Tablas Principales:** `dw.fact_waste_generation`
**Dimensión Clave:** `dw.dim_waste_generator` (Enriquecida con **RUC** desde SUIA Master).

| Atributo Clave | Valor de Negocio |
| :--- | :--- |
| `ruc_generator` | Permite consolidar la huella ambiental de un grupo económico a pesar de tener múltiples establecimientos. |
| `quantity_generated` | Métricas de peso para cumplimiento de metas de sostenibilidad. |

### 2.2 Trazabilidad Financiera JBPM
**Tabla Principal:** `dw.fact_payment_traceability` (Motor Forense)
**Fuentes:** Ingesta directa de JBPM .226 Historical.

| Atributo Clave | Valor de Negocio |
| :--- | :--- |
| `delta_value` | **Indicador de Alerta:** Muestra la diferencia entre débito y saldo. Un delta != 0 indica una inconsistencia financiera. |
| `retired_value` | Seguimiento de la liquidación de trámites en tiempo real. |

---

## 3. Ejemplos de Consultas Analíticas (Senior Level)

### A. Auditoría de Trazabilidad Financiera
```sql
-- Identificación de inconsistencias en la billetera virtual
SELECT 
    p.codigo_proyecto,
    t.update_date,
    t.retired_value,
    t.value_updated,
    t.delta_value,
    t.description
FROM dw.fact_payment_traceability t
JOIN dw.dim_proyecto p ON t.sk_proyecto = p.sk_proyecto
WHERE ABS(t.delta_value) > 0.01 -- Filtro para evitar ruido de punto flotante
ORDER BY t.update_date DESC;
```

### B. Análisis de Proponentes con Mayor Huella de Residuos
```sql
SELECT 
    g.ruc_generator,
    g.generator_name,
    SUM(f.quantity_generated) as total_kg
FROM dw.fact_waste_generation f
JOIN dw.dim_waste_generator g ON f.waste_generator_key = g.waste_generator_key
GROUP BY 1, 2
ORDER BY 3 DESC;
```

---

## 4. Gobernanza y Calidad de Datos

1.  **Ubicación Técnica:** El DWH reside ahora en `D:\Datawrehouse_RA` para máxima eficiencia de I/O.
2.  **Referencia Geográfica:** Toda la analítica espacial se basa en la **Codificación INEC Oficial** integrada en v1.4 y mantenida en v1.6.
3.  **Integridad Referencial:** Siempre verifique el `SK=0` (N/A) para incluir trámites con información incompleta en los totales generales.

---
**Arquitecto de Software & Datos:** Antigravity AI  
**Versión:** 1.6 (Doc Refactoring)  
**Estado:** ✅ DOCUMENTACIÓN ACTIVA Y REVISADA
