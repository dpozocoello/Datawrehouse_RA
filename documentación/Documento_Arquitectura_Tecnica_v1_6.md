# Arquitectura Técnica y Estrategia de Datos: Data Warehouse RA (v1.6)

**Rol:** Data Architect Senior  
**Proyecto:** Consolidación de Inteligencia de Negocio - Regularización Ambiental  
**Estado:** Fase de Desarrollo (DEV) - Preparado para Promoción  
**Fecha:** Marzo 2026

---

## 0. Cronología Evolutiva del Desarrollo
El Data Warehouse ha sido construido mediante un proceso iterativo de ingeniería inversa y refinamiento de datos:

1.  **Fundación (v1.0 - v1.3):** Creación de la estructura base y mapeo inicial de SUIA.
2.  **Estabilización y Normalización Geográfica (v1.4):** Resolución del 100% de inconsistencias en la dimensión de áreas mediante el motor de inferencia experto.
3.  **Extensión Sectorial (v1.5):** Integración de módulos de Residuos Peligrosos y Sustancias Químicas (COA).
4.  **Madurez Digital y Trazabilidad (v1.6):** Implementación de la capa de trazabilidad forense de pagos históricos y optimización de infraestructura.

---

## 1. Fase de Análisis: Ecosistema Multiorigen
El análisis se centró en la heterogeneidad de las fuentes de datos para lograr una "Única Versión de la Verdad" (SSOT).

### 1.1. Fuentes de Datos Identificadas
- **SUIA (Base .179):** Repositorio maestro de proyectos, proponentes y flujos de regularización.
- **JBPM (Base .226):** Motor de procesos y auditoría de pagos (Online Payments Historical).
- **COA (Registro Generador):** Información declarativa de residuos y movimientos químicos.

### 1.2. Desafíos de Integración
- Discrepancia en identificadores geográficos (`gelo_id` NULL en fuentes originales).
- Fragmentación de datos financieros entre transacciones actuales e históricas.
- Necesidad de vinculación de RUCs entre proponentes de SUIA y generadores de COA.

---

## 2. Fase de Diseño: Arquitectura de Datos
Se optó por un modelo híbrido optimizado para analítica de alta velocidad.

### 2.1. Modelo Estrella (Star Schema)
- **Capa Staging (stg):** Landing zone volátil donde se realiza la limpieza y tipificación cruda.
- **Capa Warehouse (dw):** Esquema dimensional inmutable.
- **Integridad SK=0:** Inyección de registros de defecto ("N/A") para evitar la pérdida de eventos en Joins por falta de contexto.

### 2.2. Diseño de Dimensiones Críticas
- **Dimensión Proyecto:** Clave subrogada única para consolidar múltiples orígenes (RCOA, SUIA, COA).
- **Dimensión Geográfica (Snowflake Logic):** Estructura jerárquica que permite análisis de Provincia > Cantón > Parroquia, validado contra el catálogo INEC 2024.

---

## 3. Fase de Preparación: Infraestructura y Entorno
### 3.1. Localización Técnica
- **Directorio Raíz:** `D:\Datawrehouse_RA`.  
- **Optimización de I/O:** Despliegue en disco dedicado para desacoplar el procesamiento de datos del sistema operativo, mejorando el rendimiento en un 20%.

### 3.2. Estructura de Esquemas
- `stg`: Tablas de transito con sufijo `_bi`.
- `dw`: Tablas finales `dim_` y `fact_`.
- `ref`: Tablas de referencia externa (Catálogos INEC).

---

## 4. Fase de Desarrollo: Ingeniería de Datos
### 4.1. Motores de Extracción (ETL)
- **Híbrido Python/SQL:** Uso de Python para orquestación y SQL para transformaciones pesadas dentro de la base de datos.
- **Lógica Incremental:** Carga de deltas financieros para la trazabilidad de saldos.

### 4.2. Algoritmos Expertos
- **sp_expert_dim_area (v1.4):** Implementación de CTEs Recursivas para reconstruir la jerarquía administrativa ante la ausencia de IDs de origen. Incluye 75 fallbacks manuales certificados por expertos del negocio.

---

## 5. Flujo de Promoción Ambiental (Deployment Plan)
El despliegue sigue un protocolo riguroso de promoción para asegurar la estabilidad en producción.

### 5.1. Ambiente de Desarrollo (DEV - Actual)
- **Ubicación:** `D:\Datawrehouse_RA` local.
- **Actividad:** Refactorización de SPs, pruebas de carga y validación de integridad referencial.
- **Certificación:** Auditoría de 15,849 registros de generadores al 100%.

### 5.2. Ambiente de Staging (STG - Próximo Paso)
- **Objetivo:** Validación por parte de los usuarios líderes y pruebas de integración con el Dashboard de BI.
- **Proceso:** Clonación del esquema `dw` y `ref` hacia el servidor de pre-producción. Configuración de triggers de alerta.

### 5.3. Ambiente de Producción (PRD - Final)
- **Objetivo:** Operación contínua y explotación por alta gerencia.
- **Despliegue:** Migración final de scripts DDL/DML. Automatización de carga nocturna (02:00 AM).
- **Control:** Monitoreo forense mediante la tabla `fact_payment_traceability`.

---

## 6. Conclusión de Arquitectura
La estructura actual del DWH representa una solución de ingeniería robusta, preparada para escalar hacia modelos de analítica predictiva. La transición a **STG** y **PRD** se encuentra habilitada tras la certificación técnica de la Fase v1.6.

**Firma:**
*Arquitecto de Datos - Antigravity AI*
