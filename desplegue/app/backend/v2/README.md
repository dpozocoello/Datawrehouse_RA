# Data Warehouse v2 — Regularización Ambiental

## Cambios respecto a v1

### 1. Geografía: Jerarquía Recursiva + Bridge Table
- `dim_geografia` ahora tiene `sk_padre` y `nivel` (PROVINCIA → CANTON → PARROQUIA)
- Nueva tabla `fact_proyecto_geografia` para relación M:N proyecto ↔ ubicaciones
- Campo `es_principal` marca la ubicación principal por proyecto (última tarea registrada)

### 2. Pagos: Secuencia y Depósito Inicial
- `fact_pago` ahora tiene `secuencia_pago`, `es_deposito_inicial`, `monto_acumulado`
- Constraint `uk_fact_pago_dedup` ampliado a `(sk_proyecto, id_transaccion_origen, origen)` para soportar multi-proyecto
- SP `sp_carga_fact_pago` incluye PARTE B (asociación por proponente vía `tramit_number`)
- SP `sp_calcular_secuencia_pagos` calcula el orden ordinal por trámite

### 3. Proyecto: Campo Faltante
- `dim_proyecto.area_responsable` cargado desde `consolidado_proyectos.area_responsable_proyecto`

## Orden de Ejecución

```bash
# 1. Aplicar cambios estructurales
psql -U postgres -d dw_reg_v1 -f ddl_dwh_v2.sql

# 2. Cargar datos nuevos (bridge table, secuencia pagos, area_responsable)
psql -U postgres -d dw_reg_v1 -f etl_carga_datos_v2.sql

# 3. Verificar con la consulta actualizada
# Ejecutar consulta_pagos_dw_v2.sql en DBeaver
```

## Archivos

| Archivo | Descripción |
|---|---|
| `ddl_dwh_v2.sql` | Cambios DDL (ALTER TABLE, CREATE TABLE) |
| `etl_carga_datos_v2.sql` | SPs y carga de datos para nuevas estructuras |
| `consulta_pagos_dw_v2.sql` | Consulta de verificación con campos nuevos |
