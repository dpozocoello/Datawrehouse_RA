# Proceso ETL: Módulos Python

El sistema de integración de datos utiliza Python como motor principal de procesamiento paralelo, manejo de reglas de negocio complejas y orquestación de scripts SQL.

## 1. Módulos de Ingesta (Extract & Load to STG)

Los scripts de ingesta se encargan de conectarse a las bases de datos de origen (SUIA-ENLISY, COA) y transferir los datos al esquema `stg` de la base local.

### 1.1 `ingesta_all.py`
*   **Origen:** Servidor Remoto (Oracle/PostgreSQL).
*   **Destino:** `stg.suia_rcoa_bi`, `stg.suia_coa_bi`, etc.
*   **Lógica:** Realiza extracciones masivas filtradas por fecha de actualización. Maneja la normalización inicial de nombres de columnas.

### 1.2 `ingesta_waste_chemical.py`
*   **Módulo Especializado:** Gestiona los nuevos requerimientos de Residuos Peligrosos y Químicos.
*   **Funcionalidades:** 
    *   `UNION ALL` de múltiples fuentes (Sustancias vs Plaguicidas).
    *   Mapeo dinámico de tablas según `waste_chemical_metadata.json`.
    *   Inyección de `project_id` desde tablas de documentos vinculados.

## 2. Módulos de Transformación (Transform)

Ubicados en `ETL_p/transformacion/`, estos módulos ejecutan la lógica de negocio para mover datos de `stg` a `dw`.

### 2.1 `transformacion_all.py`
*   **Flujo:** Llama a una secuencia de Stored Procedures (`sp_consolidar_staging`, `sp_carga_dimensiones`, `sp_carga_hechos`).
*   **SCD Tipo 2:** Maneja la vigencia de registros en `dim_proyecto`.

### 2.2 Scripts SQL (`etl_waste_chemical_load.sql`)
*   **Optimizaciones:** Implementa tablas temporales indexadas para cruzar IDs numéricos con códigos alfanuméricos del DWH.
*   **Limpieza:** RegEx para purga de unidades de medida en campos de capacidad.

## 3. Orquestador Central (`etl_main.py`)

Es el punto de entrada único para la ejecución de todo el Data Warehouse.

### Características Principales:
*   **Control por Pasos:** Permite ejecutar rangos de pasos (ej: `--desde 24 --hasta 25`).
*   **Gestión de Tiempos:** Registra el tiempo de inicio, fin y duración de cada tarea.
*   **Mecanismo de Parada:** Si un paso falla, el orquestador detiene la ejecución para evitar inconsistencias en cascada.
*   **Logs:** Genera trazas detalladas en consola y archivos de log, incluyendo el número de filas afectadas en cada operación DML.

### Secuencia de Orquestación:
1.  **Validación de Conexiones:** Verifica acceso a fuentes de datos.
2.  **Ejecución de Ingestas:** Pasos 1-22 (Paralelizable).
3.  **Ejecución de Transformaciones:** Pasos 23-25 (Secuencial).
4.  **Cierre:** Generación de resumen de ejecución.
