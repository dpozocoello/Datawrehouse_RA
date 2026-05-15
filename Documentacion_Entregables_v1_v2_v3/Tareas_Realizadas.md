# Validación Integral DWH — Geografía, Pagos y ETL

## 1. Investigación de Estructura DWH
- [x] Revisar estructura de `dim_geografia`, `dim_actividad`, `fact_regularizacion`, `fact_pago`
- [x] Revisar tablas de staging y relaciones
- [x] Revisar ETL existente (DDL y SPs)

## 2. Validación Geográfica (Relación Recursiva)
- [x] Analizar múltiples ubicaciones por proyecto
- [x] Validar que cada proyecto pertenece a una misma actividad económica
- [x] Proponer relación recursiva en `dim_geografia` si aplica
- [x] Comparar selección geográfica DWH vs producción

## 3. Validación de Pagos (Depósito Inicial / Ordinal)
- [x] Analizar lógica de depósito inicial vs pagos subsecuentes
- [x] Identificar ordenamiento por fecha e identificador ordinal
- [x] Calcular valor de cada transacción según diferencia ordenada
- [x] Comparar con datos de producción

## 4. Análisis Estructural DWH vs Producción
- [x] Comparar estructura de tablas DWH vs vista de producción
- [x] Identificar campos faltantes o transformaciones no implementadas
- [x] Documentar hallazgos

## 5. Propuesta de Cambios (v2)
- [x] Crear carpeta `f:\Datawrehouse_RA\v2\` con scripts DDL, ETL y SP
- [x] Documentar cambios propuestos en plan de implementación
- [x] Crear `ddl_dwh_v2.sql`
- [x] Crear `etl_carga_datos_v2.sql`
- [x] Crear `sp_carga_fact_pago_v2.sql`
- [x] Crear `consulta_pagos_dw_v2.sql`
- [x] Ejecutar y verificar cambios en la BD

## 6. DWH v3 - Pagos Detallados (Históricos)
- [x] Construir DDL para `stg.online_payments_historical_bi`
- [x] Construir ETL para extraer `online_payments_historical` vía `dblink`
- [x] Modificar `sp_carga_fact_pago` para calcular saldos diferenciales
- [x] Extaer consulta v3 y comparar con PROD
- [x] Validar y generar informe final v3
