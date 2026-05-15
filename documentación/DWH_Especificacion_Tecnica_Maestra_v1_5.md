# Especificación Técnica Maestra: Data Warehouse Regularización Ambiental (v1.5.1)
**Ingeniería de Datos, Normalización Experta e Integración de Residuos/Químicos**

---

## 1. Arquitectura del Sistema
### 1.1. Diagrama de Arquitectura de Capas (Evolución v1.5)
El sistema implementa una arquitectura de flujo lineal con enriquecimiento mediante motores de inferencia y orquestación híbrida.

```mermaid
graph TD
    subgraph "Sistemas Origen (Source)"
        SRC_SUIA[SUIA / ENLISY]
        SRC_RCOA[RCOA Database]
        SRC_JBPM[JBPM Database]
        SRC_COA[COA - Residuos/Químicos]
    end

    subgraph "Capa 1: Staging (stg)"
        STG_CORE[stg.suia_rcoa_bi / suia_coa_bi]
        STG_PAGOS[stg.jbpm_pagos / suia_pagos]
        STG_WASTE[stg.stg_waste_... / stg.stg_fact_...]
    end

    subgraph "Capa 2: Data Warehouse (dw)"
        DIM_PROY[dw.dim_proyecto]
        DIM_AREA[dw.dim_area - Expert Logic]
        DIM_WASTE[dw.dim_waste_generator / type]
        FACT_REG[dw.fact_regularizacion]
        FACT_WASTE[dw.fact_waste_generation]
        FACT_PAGO[dw.fact_pago]
    end

    subgraph "Capa 3: Referencia (ref)"
        REF_INEC[ref.inec_dpa_2024]
        REF_MAPS[Fallen back mappings]
    end

    SRC_SUIA --> STG_CORE
    SRC_RCOA --> STG_CORE
    SRC_JBPM --> STG_PAGOS
    SRC_COA --> STG_WASTE

    STG_CORE --> FACT_REG
    STG_WASTE --> FACT_WASTE
    STG_WASTE --> DIM_WASTE
    STG_PAGOS --> FACT_PAGO
    
    REF_INEC --> DIM_AREA
    DIM_AREA --> FACT_REG
```

---

## 2. Flujo de Ejecución Híbrido (ETL Orchestration)
### 2.1. Orquestación Cronológica v1.5
El Job Maestro delega el procesamiento masivo a Python mientras mantiene el control de flujo en Pentaho.

```mermaid
sequenceDiagram
    participant PNT as Pentaho Job Maestro
    participant PY as Python Orchestrator (etl_main)
    participant DB as Postgres (stg/dw)

    Note over PNT, DB: Inicio Ciclo v1.5
    PNT->>DB: SQL: Restore SK=0 (Integridad)
    PNT->>PY: Invoke: etl_main.py --desde 1 --hasta 24
    PY->>DB: Bulk Load: Ingesta SUIA/COA/Waste
    PY-->>PNT: Exit 0 (Success)
    PNT->>DB: KTR: Pagos & SNAP
    PNT->>PY: Invoke: etl_main.py --desde 25 --hasta 25
    PY->>DB: SQL: Transformation (Carga Hechos DW)
    Note over PNT, DB: Auditoría Final & Cierre
```

---

## 3. Diccionario Técnico de Datos (Matriz de Trazabilidad v1.5)

| N° | Componente Funcional | Tabla Origen | Tabla Staging (stg) | Tabla DW (dw) | Proceso de Transformación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Proyectos General | `suia_iii.tmp_coa_bi` | `suia_coa_bi` | `fact_regularizacion` | CLI: Python Ingesta |
| **2** | Pagos JBPM/SUIA | `online_payments` | `jbpm_pagos_bi` | `fact_pago` | KTR: Pentaho Payments |
| **3** | Generación Residuos | `waste_generator_record_coa` | `stg_fact_waste_gen` | `fact_waste_generation` | CLI: Python Waste |
| **4** | Sustancias Químicas | `products_pqa` | `stg_fact_chemical` | `fact_chemical_app` | CLI: Python Chemical |
| **5** | Oficinas Técnicas | `public.areas` | `suia_areas_bi` | `dim_area` | SQL: Inferencia Experta |

---

## 4. Documentación de Scripts y Procedimientos Críticos

### 4.1. `etl_waste_chemical_load.sql` (Optimización v1.5.1)
Este script maneja la carga de los nuevos hechos. 
**Puntos Clave:**
- **Tabla de Staging Indexada:** `stg.tmp_dim_proyecto_optimized` permite cruzar IDs de origen con claves DWH en milisegundos de forma estable en Pentaho.
- **Deduplicación Masiva:** Implementada mediante `DISTINCT ON` para manejar registros repetidos en el COA.
- **Normalización de Unidades:** Conversión de campos de texto (capacidad) a numéricos mediante RegEx.

### 4.2. `sp_carga_dim_area` (Motor de Inferencia Permanente)
Sigue siendo la pieza fundamental para la calidad geográfica (v1.4+) resolviendo el 100% de las áreas mediante fallbacks expertos.

---

## 5. Protocolo de Saneamiento DWH
Para un reset integral en v1.5:
1. Ejecutar script de limpieza de tablas hechos.
2. Limpiar dimensiones (excepto SK=0).
3. **Mantenimiento PIDs:** Ejecutar `list_pg_pids.py` para asegurar que no hay transacciones bloqueantes.

---

**Arquitecto de Datos e IA:** Antigravity AI  
**Versión:** 1.5.1 "Stabilized Engineering Spec"  
**Estado:** Activo 
