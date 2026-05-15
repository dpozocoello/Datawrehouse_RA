# Catálogo Maestro de Scripts SQL: Data Warehouse RA (v1.4)
**Trazabilidad Completa de Ingesta, Transformación y Carga (ETL)**

---

## 1. Resumen de Gobernanza de Scripts
Este catálogo detalla la lógica técnica de cada componente SQL del ecosistema. Todos los procesos están diseñados para ejecutarse en el motor **PostgreSQL 16+** mediante orquestación en Pentaho.

| Script / Componente | Función Principal | Capa Impactada | Resiliencia |
| :--- | :--- | :--- | :--- |
| `setup_reference_data_v1_4.sql` | Inicialización de Catálogos e Integridad | `ref`, `dw` | Alta (Self-healing) |
| `dw.sp_consolidar_staging()` | Unificación de 9 fuentes transaccionales | `stg` | Media (Truncate) |
| `dw.sp_carga_dim_area()` | Inferencia Experta Geográfica v1.4 | `dw.dim_area` | Crítica (100% Paridad) |
| `dw.sp_carga_hechos()` | Carga de Regularización Ambiental | `dw.fact_regularizacion` | Alta (FK Guard) |
| `dw.sp_carga_fact_pago()` | Consolidación Financiera (Deduplicada) | `dw.fact_pago` | Alta (Secuencia) |

---

## 2. Detalle por Script de Extracción e Ingesta

### 2.1. `dw.sp_consolidar_staging()`
**Objetivo**: Unificar el esquema dispar de múltiples orígenes en una tabla plana de staging.

-   **ORIGEN**:
    *   Sistemas Transaccionales (Vía Pentaho):
        -   `coa_mae.tmp_rcoa_bi` (RCOA)
        -   `suia_iii.tmp_coa_bi` (SUIA COA)
        -   `vm_sector_subsector_bi` (JBPM SECTOR)
        -   `vm_cuatro_categorias_bi` (JBPM 4 CAT)
        -   `vwt_hidrocarbonos_bi` (JBPM HIDRO)
-   **DESTINO**: `stg.consolidado_proyectos`
-   **LÓGICA**: Realiza un `INSERT INTO ... SELECT` con transformaciones menores de tipos de datos y asignación de etiquetas de `origen` para trazabilidad forense.

### 2.2. Ingesta de Pagos JBPM/SUIA (Scripts Diversos)
-   **ORIGEN**:
    *   `online_payment.online_payments` (jbpmdb @ 172.16.0.226)
    *   `suia_iii.financial_transaction` (suia_enlisy @ 172.16.0.179)
-   **DESTINO**:
    *   `stg.online_payments_bi`
    *   `stg.financial_transaction_bi`
-   **LÓGICA**: Extracción directa mediante componentes Pentaho para alimentar la `fact_pago`.

---

## 3. Detalle de Procedimientos Almacenados (Transformación y Carga)

### 3.1. `dw.sp_carga_dim_area()` (Versión Experta v1.4)
**Objetivo**: Resolver brechas geográficas en oficinas técnicas y zonales.

-   **ORIGEN**: `stg.suia_areas_bi`, `stg.geographical_locations_bi`, `ref.inec_dpa_2024`.
-   **DESTINO**: `dw.dim_area`
-   **SCRIPTS ASOCIADOS**: `sp_expert_dim_area_v1_4.sql`
-   **FRAGMENTO CLAVE**: 
    ```sql
    -- Lógica de Inferencia Manual para 75 IDs huérfanos
    CASE 
        WHEN area_id = 1120 THEN 'NAPO' -- OFICINA TÉCNICA TENA
        WHEN area_id = 1085 THEN 'NAPO' -- DIRECCIÓN ZONAL 8
        -- ...
    END as provincia
    ```

### 3.2. `dw.sp_carga_hechos()`
**Objetivo**: Generar la tabla de hechos de regularización ambiental.

-   **ORIGEN**: `stg.consolidado_proyectos` + Todas las Dimensiones (`dw.dim_*`).
-   **DESTINO**: `dw.fact_regularizacion`
-   **LÓGICA DE INTEGRIDAD**: 
    Usa `LEFT JOIN` y `COALESCE(sk, 0)`. Esto asegura que si un proyecto no tiene un área o proponente válido, se asigne al registro **N/A (SK=0)** en lugar de fallar la carga.

### 3.3. `dw.sp_carga_fact_pago()`
**Objetivo**: Cargar la fact table de pagos con lógica de deduplicación.

-   **ORIGEN**: `stg.online_payments_bi`, `stg.financial_transaction_bi`.
-   **DESTINO**: `dw.fact_pago`
-   **LÓGICA**: Utiliza `DISTINCT ON (... id_transaccion_origen)` para evitar la duplicidad de pagos en proyectos multi-proceso.

---

## 4. Scripts de Mantenimiento e Integridad

### 4.1. `setup_reference_data_v1_4.sql`
**Objetivo**: Restablecer el estado inicial del DWH post-limpieza.
-   **LÓGICA**:
    ```sql
    INSERT INTO dw.dim_area (sk_area, id_area, nombre_area, provincia)
    VALUES (0, 0, 'AREA NO DEFINIDA', 'N/A')
    ON CONFLICT DO NOTHING;
    ```
-   **DESTINO**: Esquemas `ref` y registros maestros de todas las dimensiones `dw`.

### 4.2. `cleanup_dwh_v1_4.sql`
**Objetivo**: Purga segura del DWH.
-   **FLUJO**: 
    1. Truncate de Fact Tables.
    2. Delete selectivo de Dimensiones (preservando SK=0 si es posible).
    3. Reinicio de secuencias (`ALTER SEQUENCE ... RESTART`).

---

## 5. Glosario de Orígenes de Datos (Metadata)

| Sistema Origen | Servidor / IP | Base de Datos | Schema / Tabla |
| :--- | :--- | :--- | :--- |
| **SUIA Core** | 172.16.0.179 | suia_enlisy | `suia_iii`, `coa_mae`, `public` |
| **JBPM Prod** | 172.16.0.226 | jbpmdb | `online_payment.online_payments` |
| **JBPM Old** | 172.16.0.226 | jbpmdb_prod_old | `public.vm_sector_subsector_bi` |

---
**Documentado por**: Arquitectura de Datos & Antigravity AI
**Uso**: Manual de Desarrollo y Auditoría SQL
**Versión**: 1.4 (Final Catalogue)
