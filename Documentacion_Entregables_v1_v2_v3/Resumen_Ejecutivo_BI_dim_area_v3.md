# Resumen Ejecutivo para Analista BI
## Actualización `dw.dim_area` v3.0 — Jerarquía Recursiva de Áreas de Control Ambiental

| | |
|---|---|
| **Fecha** | 2026-05-07 |
| **Preparado por** | Equipo de Arquitectura de Datos y Ciencia de Datos |
| **Destinatario** | Analista BI — Experto en Desarrollo de Dashboards |
| **Base de datos** | `dw_reg_v1` — PostgreSQL 17 (localhost:5432) |
| **Fuente origen** | `suia_enlisy` — PostgreSQL (172.16.0.179:5632) |

---

## 1. ¿Qué cambió y por qué?

La dimensión `dw.dim_area` almacena las áreas institucionales que controlan los procesos de regularización ambiental en Ecuador. Hasta la versión anterior, la tabla contenía únicamente atributos planos (nombre, abreviatura, provincia, cantón) y una referencia al padre (`id_area_padre`) sin materializar la jerarquía.

**Problema concreto para el dashboard:** Para saber "cuántos expedientes tiene la Zona 1 y todas sus oficinas técnicas", era necesario escribir una consulta recursiva de 20+ líneas. Power BI y Tableau no ejecutan CTEs recursivas nativas — lo que hacía imposible implementar drill-down jerárquico en el dashboard sin vistas intermedias.

**Solución implementada:** Se materializaron los tres niveles de la jerarquía directamente en `dim_area` y se creó una bridge table (`dw.bridge_area_jerarquia`) con todas las relaciones ancestro-descendiente precalculadas.

---

## 2. Estructura de la jerarquía (fuente confirmada: SUIA producción)

La jerarquía tiene exactamente **3 niveles** y **1.099 áreas activas**:

```
NIVEL 1 — Raíces (558 nodos, sin padre)
│
├── Planta Central        [PC]   268 áreas  — Unidades nacionales del Ministerio
├── Ente Acreditado       [EA]   255 áreas  — GADs y entidades externas habilitadas
├── Dirección Provincial  [DP]    25 áreas  — Representaciones provinciales raíz
└── Coordinación Zonal [ZONALES]  10 áreas  — Coordinaciones regionales

NIVEL 2 — Hijos directos (531 nodos)
│
├── PC   181 — Subunidades de Planta Central
├── DP   148 — Sub-Direcciones provinciales
├── EA   144 — Sub-Entes acreditados
├── OT    48 — Oficinas Técnicas  ← dependen de ZONALES
└── DZ    10 — Direcciones Zonales ← dependen de ZONALES

NIVEL 3 — Nietos (10 nodos, todos tipo PC)
└── Ejemplo:
    SUBSECRETARÍA DE PATRIMONIO NATURAL
     └── DIRECCIÓN DE BOSQUES
          └── PROGRAMA AMAZONÍA SIN FUEGO
```

---

## 3. Campos nuevos disponibles en `dw.dim_area`

### 3.1 Campos existentes desde v2.0 (referencia)

| Campo | Descripción |
|---|---|
| `sk_area` | Surrogate key — usar en JOINs con tablas de hechos |
| `id_area` | Business key — ID natural de SUIA |
| `nombre_area` | Nombre completo del área |
| `abreviatura_area` | Sigla corta |
| `id_area_padre` | ID del área padre (NULL si es raíz) |
| `tipo_area` | Nombre del tipo institucional |
| `siglas_tipo_area` | Código: `PC`, `EA`, `DP`, `OT`, `DZ`, `ZONALES` |
| `nombre_area_padre` | Nombre del área padre |
| `provincia` | Provincia resuelta (100% cobertura) |
| `canton` | Cantón resuelto por jerarquía geográfica |
| `canton_directo` | Cantón por FK directa (alta precisión — 58 áreas) |
| `es_emisora_aaa` | TRUE si el área emite Autorizaciones Ambientales |
| `es_seguimiento_aaa` | TRUE si el área realiza seguimiento de AAA |
| `es_proyecto_inversion` | TRUE si está vinculada a proyectos de inversión pública |

### 3.2 Campos NUEVOS en v3.0 — Jerarquía materializada

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `nivel_jerarquico` | SMALLINT | Nivel en la jerarquía: 1, 2 o 3 | `2` |
| `l1_id` | INTEGER | ID del ancestro raíz (nivel 1) | `10` |
| `l1_nombre` | VARCHAR | Nombre del ancestro raíz | `COORDINACIÓN ZONAL 1` |
| `l1_siglas_tipo` | VARCHAR | Tipo del ancestro raíz | `ZONALES` |
| `l2_id` | INTEGER | ID del ancestro nivel 2 (NULL si el nodo es raíz) | `254` |
| `l2_nombre` | VARCHAR | Nombre del ancestro nivel 2 | `DIRECCIÓN ZONAL 1` |
| `l2_siglas_tipo` | VARCHAR | Tipo del ancestro nivel 2 | `DZ` |
| `ruta_ids` | VARCHAR | Cadena de IDs del camino completo | `"10/254/312"` |
| `ruta_nombres` | TEXT | Breadcrumb legible completo | `"COORD ZONAL 1 > DIR ZONAL 1 > OT ESMERALDAS"` |
| `es_hoja` | BOOLEAN | TRUE si el nodo no tiene hijos | `true` |

### 3.3 Nueva tabla: `dw.bridge_area_jerarquia`

| Campo | Tipo | Descripción |
|---|---|---|
| `sk_area_descendiente` | INTEGER | FK a `dw.dim_area.sk_area` (el nodo hijo/nieto) |
| `sk_area_ancestro` | INTEGER | FK a `dw.dim_area.sk_area` (el nodo padre/abuelo) |
| `id_area_descendiente` | INTEGER | Business key descendiente |
| `id_area_ancestro` | INTEGER | Business key ancestro |
| `distancia` | SMALLINT | 0=self, 1=padre directo, 2=abuelo |
| `es_hoja` | BOOLEAN | El descendiente es nodo terminal |
| `es_raiz` | BOOLEAN | El ancestro es nodo raíz |

**Filas actuales:** 1.650 pares (1.099 self + 541 padre-hijo + 10 abuelo-nieto)

---

## 4. Métricas de calidad del dato

| Indicador | Valor | Cobertura |
|---|---|---|
| Total áreas en dimensión | 1.099 | — |
| Áreas con nivel jerarquico | 1.099 | 100% |
| Áreas con ruta completa | 1.099 | 100% |
| Áreas con provincia | 1.099 | 100% — 26 provincias |
| Áreas con cantón (recursivo) | 78 | 7% |
| Áreas con cantón directo | 58 | 5% (alta precisión) |
| Áreas activas (`estado_area`) | 1.084 | 99% |
| Áreas hoja (terminales) | 995 | 91% |
| Áreas emisoras de AAA | 319 | 29% |
| Áreas con seguimiento AAA | 304 | 28% |

---

## 5. Capacidades analíticas habilitadas para el dashboard

### 5.1 Drill-down jerárquico nativo (Power BI / Tableau)

Con la bridge table, Power BI puede implementar jerarquías padre-hijo usando los campos `sk_area_ancestro` y `sk_area_descendiente`. El usuario puede navegar:

```
COORDINACIÓN ZONAL 1
  └── DIRECCIÓN ZONAL 1
        ├── OT ESMERALDAS
        ├── OT IMBABURA
        └── OT CARCHI
```

**Sin** necesidad de DAX recursivo ni vistas intermedias.

### 5.2 Filtros por nivel (sin JOIN adicional)

```sql
-- Solo raíces (nivel organizacional más alto)
WHERE nivel_jerarquico = 1

-- Solo Oficinas Técnicas (siempre nivel 2, siempre hoja)
WHERE siglas_tipo_area = 'OT'

-- Solo nodos operativos terminales
WHERE es_hoja = TRUE AND es_emisora_aaa = TRUE
```

### 5.3 Consolidación por ancestro (sin CTE recursiva)

```sql
-- Expedientes de toda la Zona 1 (raíz + hijos + nietos)
SELECT zona.nombre_area, COUNT(f.sk_expediente) AS expedientes
FROM dw.fact_regularizacion f
JOIN dw.dim_area d           ON f.sk_area = d.sk_area
JOIN dw.bridge_area_jerarquia b ON b.sk_area_descendiente = d.sk_area
JOIN dw.dim_area zona        ON b.sk_area_ancestro = zona.sk_area
WHERE zona.siglas_tipo_area = 'ZONALES'
  AND b.distancia >= 0
GROUP BY zona.nombre_area;
```

### 5.4 Breadcrumb en fichas de detalle

El campo `ruta_nombres` permite mostrar el camino completo de cualquier área:

> `SUBSECRETARÍA DE PATRIMONIO NATURAL > DIRECCIÓN DE BOSQUES > PROGRAMA AMAZONÍA SIN FUEGO`

Útil como tooltip o encabezado de ficha individual.

### 5.5 KPIs de cobertura institucional

| KPI propuesto | Campos a usar |
|---|---|
| % de zonas con OT activas | `siglas_tipo_area='OT'`, `estado_area`, `l1_nombre` |
| Áreas emisoras de AAA por provincia | `es_emisora_aaa`, `provincia` |
| Expedientes por árbol institucional | `bridge_area_jerarquia` + `fact_regularizacion` |
| Distribución por tipo y nivel | `nivel_jerarquico`, `siglas_tipo_area` |

---

## 6. Recomendaciones prioritarias para evaluación del dashboard actual

### Verificar y corregir

1. **Filtros de tipo de área:** si el dashboard actual filtra por nombre de área en lugar de `siglas_tipo_area`, los resultados pueden mezclar tipos. Migrar a filtro por `siglas_tipo_area IN ('OT', 'DP', ...)`.

2. **Métricas de expedientes por zona:** actualmente podrían sumar solo el área raíz sin incluir sus hijos/nietos. Usar `bridge_area_jerarquia` para consolidar la jerarquía completa.

3. **Mapa geográfico:** migrar de `canton` (resolución recursiva, menor precisión) a `canton_directo` para las 58 áreas que lo tienen disponible, usando un `COALESCE(canton_directo, canton)`.

### Nuevos visuales propuestos

| Visual | Campos requeridos |
|---|---|
| Árbol jerárquico interactivo | `bridge_area_jerarquia`, `nivel_jerarquico`, `siglas_tipo_area` |
| Tarjeta de área con breadcrumb | `ruta_nombres`, `tipo_area`, `es_emisora_aaa` |
| Mapa de cobertura por provincia | `provincia`, `nivel_jerarquico`, `es_emisora_aaa` |
| Tabla drill-down Zona → DP → OT | `l1_nombre`, `l2_nombre`, `nombre_area` |

---

## 7. Guía de acceso rápido

**Conexión DBeaver / Power BI:**
- Host: `localhost` | Puerto: `5432`
- Base de datos: `dw_reg_v1`
- Usuario: `postgres`
- Schema principal: `dw`
- Tablas clave: `dw.dim_area`, `dw.bridge_area_jerarquia`, `dw.fact_regularizacion`

**Consulta de validación inicial:**
```sql
SELECT nivel_jerarquico, siglas_tipo_area,
       COUNT(*) AS total,
       SUM(CASE WHEN es_hoja THEN 1 ELSE 0 END) AS terminales,
       SUM(CASE WHEN es_emisora_aaa THEN 1 ELSE 0 END) AS emisoras_aaa
FROM dw.dim_area
WHERE id_area > 0
GROUP BY nivel_jerarquico, siglas_tipo_area
ORDER BY nivel_jerarquico, total DESC;
```

---

*Documento generado por Equipo de Arquitectura de Datos — DWH Regularización Ambiental v3.0*
*Versión: 1.0 | Fecha: 2026-05-07 | Entorno validado: dw_reg_v1 @ localhost:5432*
