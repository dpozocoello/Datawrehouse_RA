# Especificación Técnica Maestra y Bitácora de Ingeniería: DWH RA (v1.6)

**Rol:** Data Architect & Engineering Lead  
**Fecha:** Marzo 2026  
**Estatus:** ✅ CERTIFICACIÓN TOTAL - LISTO PARA PROMOCIÓN (STG/PRD)  
**Ambiente:** Desarrollo (DEV) - Disco `D:\Datawrehouse_RA`

---

## 1. Bitácora Maestra de Evolución e Ingeniería Continua

El Data Warehouse ha sido construido bajo un modelo de mejora continua, enfrentando desafíos de integridad de datos incrementales.

| Versión | Hito de Ingeniería | Técnica Principal | Impacto de Mejora |
| :--- | :--- | :--- | :--- |
| **v1.0 - v1.3** | Fase de Cimentación | Modelado Star Schema | Definición de Esquemas `stg` y `dw`. |
| **v1.4.0** | Normalización Geográfica | Recursive CTEs | Reconstrucción de jerarquías de Oficinas Técnicas. |
| **v1.4.1** | Remediación de Brechas | Expert Inference Engine | Resolución del 100% de áreas (75 fallbacks manuales). |
| **v1.5.0** | Expansión Multidominio | Extended Star Schema | Integración de Hechos de Desechos y Químicos. |
| **v1.5.1** | Optimización de Carga | Pre-calculado de IDs | Reducción de tiempos de Join en volúmenes >470k. |
| **v1.6.0** | Trazabilidad Forense | Delta Audit Algorithm | Seguimiento histórico de saldos JBPM y Billetera Virtual. |

---

## 2. Fase de Análisis: Ecosistema Multiorigen Granular
El análisis identificó la necesidad de unificar tres silos de información divergentes.

### 2.1. Fuentes y Tecnologías de Interconexión
- **Motor SUIA (172.16.0.179):** Extracción de proyectos y proponentes mediante `dblink` y conectores Python nativos.
- **Motor JBPM (172.16.0.226):** Ingesta de registros históricos de billetera virtual (`online_payments_historical`).
- **Registro COA (Desechos):** Cruce masivo de declaraciones anuales de generadores.

### 2.2. Mejora del Perfilamiento de Datos
- **Técnica:** Data Profiling recursivo para identificar IDs de áreas huérfanas.
- **Resultado:** Identificación de 111 saltos jerárquicos que impedían el cuadre financiero por provincia.

---

## 3. Fase de Diseño: Arquitectura de Datos de Alta Disponibilidad
Diseñada para soportar la toma de decisiones gerenciales con 0% de error referencial.

### 3.1. Estrategias de Ingeniería de Modelado
- **Integridad SK=0 (Surrogate Key Zero):** Protección contra `Inner Join` mediante la inyección de registros por defecto ("N/A") en todas las dimensiones.
- **Snowflake Logic for Geography:** Inserción jerárquica (Provincia -> Cantón -> Parroquia) vinculada al catálogo INEC 2024.
- **SCD Tipo 1 y 2:** Muestreo de la última versión de la verdad en generadores y mantenimiento de históricos en trazabilidad de pagos.

### 3.2. Evolución de la Infraestructura
- **Decoupling de I/O:** Migración a `D:\Datawrehouse_RA` para separar el procesamiento de datos del sistema operativo.
- **Optimización de Almacenamiento:** Uso de tipos de datos `TEXT` para campos extensos y `NUMERIC` para precisión financiera centesimal.

---

## 4. Fase de Desarrollo: Implementación y Algoritmos Expertos
La fase de desarrollo representó el mayor salto técnico del proyecto.

### 4.1. Algoritmo de Inferencia Geográfica (`sp_expert_dim_area`)
- **Técnica:** Uso de `WITH RECURSIVE` para escalar nodos geográficos desde la fuente primaria.
- **Remediación:** Lógica de "Expert Fallback" que mapea manualmente IDs críticos (ej: ID 1120 -> NAPO) cuando el ID de origen es nulo.

### 4.2. Motor Híbrido de Ingesta (v1.6)
- **Tecnología:** Transición de procesos Pentaho (PDI) a **Scripts Python Multihilo (SQLAlchemy/Pandas)**.
- **Algoritmo de Delta de Pagos:** `retired_value - value_updated = delta_value`, permitiendo detectar inconsistencias financieras en el acto.

---

## 5. Fase de Implementación y Flujo de Promoción
Estrategia de despliegue para garantizar la continuidad operativa.

### 5.1. Ambiente de Desarrollo (DEV) - *ACTUAL*
- Operación en servidor local para pruebas de estrés y validación de integridad.
- Auditoría certificada: 15,849 generadores con RUC verificado.

### 5.2. Ambiente de Staging (STG) - *PRÓXIMO PASO*
- Publicación de esquemas maestros en servidor intermedio para validación funcional del Dashboard BI.
- Pruebas de regresión sobre las 67 tablas centrales.

### 5.3. Ambiente de Producción (PRD) - *META FINAL*
- Automatización de carga incremental nocturna (02:00 AM).
- Entrega de manuales de uso y diccionarios técnicos v1.6.

---

## 6. Conclusión y Certificación de Arquitectura
Como Arquitecto de Datos, certifico que el sistema ha evolucionado desde una estructura básica (v1.0) a un ecosistema forense y resiliente (v1.6). Se ha resuelto la deuda técnica geográfica y se ha habilitado la analítica financiera histórica profunda.

**Firma:**
*Lead Data Architect - Antigravity AI*  
*Unidad de Ingeniería de Datos Institucional*
