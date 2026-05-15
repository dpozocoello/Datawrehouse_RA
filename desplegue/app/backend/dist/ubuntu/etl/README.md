# ETL Data Warehouse — Regularización Ambiental (Versión Python)

Implementación en Python del proceso ETL del Data Warehouse de Regularización Ambiental (`dw_reg_v1`), equivalente al Job Maestro de Pentaho (`JOB_CARGA_DWH_REGULARIZACION.kjb`).

## Requisitos Previos

- **Python** 3.8 o superior
- **PostgreSQL** con las bases `dw_reg_v1`, `suia_enlisy`, `suia_bpms_enlisy_app`, `jbpmdb`, `jbpmdb_prod_old`
- Acceso de red a los servidores remotos (172.16.0.179, 172.16.0.226)

## Instalación

```bash
cd F:\Datawrehouse_RA\ETL_p
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar ETL completo (18 pasos)
python etl_main.py

# Solo verificación post-ETL (conteos de tablas)
python etl_main.py --verificar

# Ejecutar desde un paso específico (ej: solo v2/v3)
python etl_main.py --desde 14

# Ejecutar un rango de pasos
python etl_main.py --desde 9 --hasta 13
```

## Estructura del Proyecto

```
ETL_p/
├── etl_main.py              ← Orquestador principal (punto de entrada)
├── config.py                ← Conexiones, parámetros, feature flags
├── connections.py           ← Gestión de conexiones y funciones genéricas
├── utils.py                 ← Logging, métricas, verificación
├── requirements.txt         ← Dependencias Python
├── README.md                ← Esta documentación
├── ingesta/
│   ├── __init__.py
│   └── ingesta_all.py       ← 9 funciones de extracción (TRX_01 a TRX_09)
├── transformacion/
│   ├── __init__.py
│   └── transformacion_all.py ← 9 funciones de transformación (SPs + SQL)
└── log/                     ← Logs diarios (etl_YYYYMMDD.log)
```

## Secuencia de Ejecución (18 pasos)

| # | Paso | Tipo | Descripción |
|---|------|------|-------------|
| 1 | TRX_01 | Ingesta | SUIA RCOA → `stg.suia_rcoa_bi` |
| 2 | TRX_02 | Ingesta | SUIA COA → `stg.suia_coa_bi` |
| 3 | TRX_03 | Ingesta | JBPM Sector → `stg.jbpm_sector_bi` |
| 4 | TRX_04 | Ingesta | JBPM 4 Categorías → `stg.jbpm_4cat_bi` |
| 5 | TRX_05 | Ingesta | JBPM Hidrocarburos → `stg.jbpm_hidro_bi` ⚠️ *deshabilitado* |
| 6 | TRX_06 | Ingesta | SNAP Variables → `stg.jbpm_snap_variables` |
| 7 | TRX_07 | Ingesta | Pagos JBPM → `stg.online_payments_bi` |
| 8 | TRX_08 | Ingesta | Pagos SUIA → `stg.financial_transaction_bi` |
| 9 | SP | Transformación | `sp_consolidar_staging()` — UNION ALL staging |
| 10 | SP | Transformación | `sp_carga_dimensiones()` — 7 dimensiones |
| 11 | SP | Transformación | `sp_carga_hechos()` — fact_regularizacion + SNAP |
| 12 | SP | Transformación | `sp_carga_dim_pago()` — dim_pago |
| 13 | SP | Transformación | `sp_carga_fact_pago()` — fact_pago deduplicado |
| 14 | SQL | v2 | UPDATE area_responsable en dim_proyecto |
| 15 | SP | v2 | `sp_carga_proyecto_geografia()` — Bridge M:N |
| 16 | TRX_09 | v3 | Pagos Históricos → `stg.online_payments_historical_bi` |
| 17 | SQL | v3 | Recálculo montos JBPM con saldos históricos |
| 18 | SP | v2/v3 | `sp_calcular_secuencia_pagos()` |

## Configuración

### Conexiones

Editar `config.py` o usar variables de entorno:

| Variable | Valor Default | Descripción |
|----------|---------------|-------------|
| `SUIA_HOST` | 172.16.0.179 | Servidor SUIA |
| `SUIA_PORT` | 5632 | Puerto SUIA |
| `JBPM_HOST` | 172.16.0.226 | Servidor JBPM |
| `JBPM_PORT` | 5432 | Puerto JBPM |
| `DWH_HOST` | localhost | Servidor DWH |
| `DWH_PORT` | 5432 | Puerto DWH |
| `DWH_DATABASE` | dw_reg_v1 | Base DWH |
| `ETL_LOG_LEVEL` | INFO | Nivel de log |

### Habilitar/Deshabilitar Pasos

En `config.py`, modificar el diccionario `PASOS_HABILITADOS`:

```python
PASOS_HABILITADOS = {
    "TRX_05_JBPM_HIDRO": False,  # Deshabilitado
    # ... resto de pasos
}
```

## Logs

Los logs se generan en `ETL_p/log/` con el formato `etl_YYYYMMDD.log`:

```
2026-03-05 08:00:01 | INFO     | [TRX_01_SUIA_RCOA] ▶ INICIANDO...
2026-03-05 08:00:15 | INFO     | [TRX_01_SUIA_RCOA] ✓ COMPLETADO en 0m 14.2s
```

## Equivalencia con Pentaho

| Componente Python | Componente Pentaho |
|-------------------|--------------------|
| `etl_main.py` | `JOB_CARGA_DWH_REGULARIZACION.kjb` |
| `ingesta/ingesta_all.py` → `ejecutar_trx_01()` | `TRX_01_INGESTA_SUIA_RCOA.ktr` |
| `transformacion/transformacion_all.py` → `sp_consolidar_staging()` | Entrada SQL "SP Consolidar Staging" |
| `config.PASOS_HABILITADOS` | Hops habilitados/deshabilitados en el Job |
| `--desde 14 --hasta 18` | Ejecutar manualmente solo los pasos v2/v3 |
