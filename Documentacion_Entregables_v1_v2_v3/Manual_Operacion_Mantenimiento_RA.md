# Manual de Operación y Mantenimiento (TI) — DWH RA
**Versión:** 1.0 | **Fecha:** 08 de mayo de 2026

## 1. Operación del Pipeline ETL

La carga de datos del DWH RA está orquestada mediante scripts Batch y SQL que deben ejecutarse bajo un orden estricto.

### Ejecución Diaria Automatizada
El proceso principal es `job_diario_dwh.bat`. Este script debe estar programado en el **Programador de Tareas de Windows** del servidor de integración, configurado para ejecutarse diariamente a las 02:00 AM.

**Flujo interno del job:**
1.  **Extracciones v1:** Carga de datos base hacia la capa `stg`.
2.  **Bridge v2:** Ejecución de `ddl_dwh_v2.sql` para poblar `dim_geografia` jerárquica y `fact_proyecto_geografia`.
3.  **Conciliación Global v3:** Ejecución de `etl_carga_datos_v3.sql` para el cálculo histórico de costos de pagos.

### Ejecución Manual (On-Demand)
En caso de requerir una carga fuera de horario o tras una caída del sistema:
1. Abrir CMD como Administrador.
2. Navegar a: `D:\Datawrehouse_RA\jobs\`
3. Ejecutar: `job_diario_dwh.bat`
4. Revisar los logs generados en `D:\Datawrehouse_RA\logs\` buscando la palabra `ERROR`.

## 2. Resolución de Problemas (Troubleshooting)

### Diferencias en Montos de Pago
Si los usuarios reportan que un proyecto hereda un valor de depósito global duplicado:
1. Verificar si el script v3 corrió correctamente.
2. Ejecutar manualmente el SP `sp_calcular_secuencia_pagos` sobre el `tramit_number` afectado.

### Deadlocks o Bloqueos en Base de Datos
Si los scripts fallan por bloqueos durante la actualización de `fact_pago`:
1. Ejecutar el script `D:\Datawrehouse_RA\find_pg_blockers.py` o revisar vistas `pg_stat_activity`.
2. Matar (Kill) procesos huérfanos que estén bloqueando las tablas transaccionales.

## 3. Política de Respaldos (Backups)

La base de datos analítica principal se denomina `dw_reg_v1`.

*   **Frecuencia:** Diaria (Completa), retención de 7 días. Semanal (Histórica), retención de 3 meses.
*   **Herramienta:** `pg_dump` con formato comprimido (`-Fc`).
*   **Ejecución:** Programar el script `create_local_backups.py` para correr a las 01:00 AM (antes del ETL).
*   **Almacenamiento:** Los archivos `.dump` deben almacenarse en un volumen o SAN separado del disco operativo del servidor.
