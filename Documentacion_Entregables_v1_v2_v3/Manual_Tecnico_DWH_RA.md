# Data Warehouse Regularización Ambiental (RA) — Manual Técnico Integral
**Versión:** 3.0 | **Fecha:** 08 de mayo de 2026

## 1. Resumen Ejecutivo
El Data Warehouse de Regularización Ambiental (DWH RA) consolida la información transaccional de los sistemas SUIA (Sistema Único de Información Ambiental) enfocándose en proyectos, pagos, ubicaciones geográficas y procesos de regularización. La versión 3.0 implementa una arquitectura avanzada para relaciones geográficas recursivas (M:N) y cálculo diferencial de pagos históricos.

## 2. Arquitectura General
El DWH RA sigue una arquitectura tradicional de tres capas desplegada sobre PostgreSQL:
*   **Staging Area (`stg`):** Réplica 1:1 de las tablas fuentes del sistema SUIA y JBPM (ej. `stg.online_payments_historical_bi`). 
*   **Dimensional (`dw`):** Modelo en estrella y copo de nieve con dimensiones consolidadas y tablas de hechos.
*   **Data Mart (`dm`):** Vistas analíticas optimizadas para el consumo del Dashboard RA.

## 3. Modelo de Datos Dimensional (dw)

### Tablas de Hechos (Facts)
*   `fact_pago`: Registra transacciones financieras. Incorpora `secuencia_pago`, `es_deposito_inicial` y `monto_acumulado`.
*   `fact_proyecto_geografia`: Tabla "Bridge" (M:N) que asocia un proyecto con múltiples parroquias (`es_principal` indica la ubicación primaria).

### Dimensiones Principales
*   `dim_proyecto`: Metadatos del proyecto, incluyendo el campo recuperado `area_responsable`.
*   `dim_geografia`: Modelo jerárquico recursivo (Provincia → Cantón → Parroquia) usando `sk_padre`. Contiene 1,390 registros unificados.
*   `dim_fecha`: Dimensión de tiempo estándar para análisis temporal.
*   `dim_estado`: Estados de los trámites y regularizaciones.

## 4. Lógica de Transformación de Negocio (ETL v3)

### Cálculo Histórico Global de Pagos
El ETL implementa lógica diferencial usando *Window Functions* (`LAG/LEAD`) sobre `stg.online_payments_historical_bi`. Esto permite deducir el costo exacto por proyecto a partir de un depósito global (ej. cálculo de saldo decreciente).

### Jerarquía Geográfica Múltiple
Los proyectos con afectación multi-parroquial se procesan generando N filas en la tabla bridge `fact_proyecto_geografia`, resolviendo las inconsistencias heredadas del DWH v1 que solo permitía 1 ubicación.

## 5. Diccionario de Datos (Muestra)

| Tabla | Columna | Tipo | Descripción |
| :--- | :--- | :--- | :--- |
| `dw.dim_geografia` | `sk_geografia` | INT PK | Clave subrogada geográfica |
| `dw.dim_geografia` | `sk_padre` | INT FK | Referencia recursiva a la entidad contenedora (ej. Cantón de una Parroquia) |
| `dw.fact_pago` | `secuencia_pago` | INT | Orden ordinal de descuento dentro de un trámite |
| `dw.dim_proyecto` | `area_responsable` | VARCHAR | Oficina o unidad de negocio encargada del proyecto |
