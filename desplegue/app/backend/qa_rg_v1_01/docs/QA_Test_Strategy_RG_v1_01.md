# QA Test Strategy: Dashboard RG v1.01 (Data Warehouse)

## 1. Introducción
Este documento define el enfoque estratégico para el aseguramiento de la calidad (QA) del Dashboard RG v1.01, centrado en la integridad de los datos desde las fuentes hasta la visualización final.

## 2. Objetivos de Calidad
Validar que el Data Warehouse (DWH) cumpla con las 5 dimensiones de calidad de datos:
1. **Exactitud**: Los datos en el dashboard coinciden con las fuentes originales (`coa_mae`, `suia_iii`, `jbpm`).
2. **Completitud**: No existen vacíos de información críticos (nulls inesperados, registros faltantes).
3. **Consistencia**: La información es coherente entre diferentes tablas y dimensiones (ej. jerarquía geográfica).
4. **Validez**: Los datos se ajustan a los dominios y formatos definidos (ej. estados de proyecto, fechas).
5. **Oportunidad**: Los datos están actualizados según el SLA definido (última carga exitosa).

## 3. Alcance de las Pruebas
- **Fuentes (Raw)**: Archivos locales en `D:\Datawrehouse_RA` (.csv, .json, .sql).
- **Staging (`stg`)**: Tablas de carga intermedia en PostgreSQL.
- **Data Warehouse (`dw`)**: Tablas de hechos (`fact_regularizacion`, `fact_pago`) y dimensiones (`dim_geografia`, `dim_area`).
- **Dashboard**: Vistas finales (`v_dashboard_regularizacion`) que alimentan la interfaz.

## 4. Tipos de Pruebas
- **Pruebas de Reconciliación (Control Totals)**: Comparación de conteos y sumatorias entre capas.
- **Pruebas Registro a Registro (Data Comparison)**: Muestreo estratificado para validar campos específicos.
- **Validación de Reglas de Negocio (DQ Checks)**: Ejecución de scripts SQL para detectar anomalías.
- **Pruebas de Integridad Referencial**: Asegurar que todas las FKs tengan correspondencia en sus dimensiones.

## 5. Herramientas y Entorno
- **Base de Datos**: PostgreSQL (Servidores 172.16.0.179 / .226).
- **Lenguajes**: Python 3.x (scripts de validación) y SQL.
- **Modo**: Acceso de LECTURA únicamente.

## 6. Criterios de Aceptación
- 100% de los Control Totals coinciden (o desviaciones documentadas < 0.1%).
- 0 registros duplicados en tablas de hechos.
- SLA de oportunidad cumplido (datos < 24h de antigüedad).
- 0 fallos críticos en integridad referencial.
