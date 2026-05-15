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
# Ejecutar ETL completo (28 pasos)
python etl_main.py

# Solo verificación post-ETL (conteos de tablas)
python etl_main.py --verificar

# Ejecutar desde un paso específico (ej: solo v2/v3)
python etl_main.py --desde 14

# Ejecutar un rango de pasos
python etl_main.py --desde 9 --hasta 13

# Ejecutar solo Desechos/Químicos e Intersecciones (v1.5/v1.9)
python etl_main.py --desde 24

# Ejecutar solo Intersecciones y recuperación de proyectos
python etl_main.py --desde 26 --hasta 28
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

## Secuencia de Ejecución (28 pasos)

| # | Paso | Tipo | Descripción |
|---|------|------|-------------|
| 1 | SP | Orquestación | `sp_orquestar_extraccion_remota()` — Extracción v1.4.1 |
| 2 | TRX_01 | Ingesta | SUIA RCOA → `stg.suia_rcoa_bi` |
| 3 | TRX_02 | Ingesta | SUIA COA → `stg.suia_coa_bi` |
| 4 | TRX_03 | Ingesta | JBPM Sector → `stg.jbpm_sector_bi` |
| 5 | TRX_04 | Ingesta | JBPM 4 Categorías → `stg.jbpm_4cat_bi` |
| 6 | TRX_05 | Ingesta | JBPM Hidrocarburos → `stg.jbpm_hidro_bi` ⚠️ *deshabilitado* |
| 7 | TRX_06 | Ingesta | SNAP Variables → `stg.jbpm_snap_variables` |
| 8 | TRX_07 | Ingesta | Pagos JBPM → `stg.online_payments_bi` |
| 9 | TRX_08 | Ingesta | Pagos SUIA → `stg.financial_transaction_bi` |
| 10 | TRX_10 | Ingesta | Áreas SUIA → `stg.suia_areas_bi` |
| 11 | TRX_11 | Ingesta | Catálogo Geográfico → `stg.geographical_locations_bi` |
| 12 | SP | Transformación | `sp_consolidar_staging()` — UNION ALL staging |
| 13 | SP | Transformación | `sp_carga_dimensiones()` — 7 dimensiones |
| 14 | SP | Transformación | `sp_carga_dim_area()` — dim_area |
| 15 | SP | Transformación | `sp_carga_hechos()` — fact_regularizacion + SNAP |
| 16 | SP | Transformación | `sp_carga_dim_pago()` — dim_pago |
| 17 | SP | Transformación | `sp_carga_fact_pago()` — fact_pago deduplicado |
| 18 | SQL | v2 | UPDATE area_responsable en dim_proyecto |
| 19 | SP | v2 | `sp_bridge_proyecto_geo()` — Bridge M:N geografía |
| 20 | TRX_09 | v3 | Pagos Históricos → `stg.online_payments_historical_bi` |
| 21 | SQL | v3 | Recálculo montos JBPM con saldos históricos |
| 22 | SP | v2/v3 | `sp_calcular_secuencia_pagos()` |
| 23 | SP | v2 | `sp_carga_puente_ambiental()` — Bridge biodiversidad |
| 24 | Ingesta | v1.5 | Desechos/Químicos → staging waste/chemical |
| 25 | SP | v1.5 | `sp_carga_waste_chemical()` — Fact desechos |
| 26 | Ingesta | v1.9 | Intersecciones ambientales → `stg.stg_intersection` |
| 27 | Recovery | v1.9 | Recuperar proyectos faltantes en dim_proyecto |
| 28 | SP | v1.9 | `sp_carga_dim_intersection()` — Dim intersección |

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
