# DOCUMENTACIÓN TÉCNICA: DATA WAREHOUSE RA - REGISTRO GENERADOR DE DESECHOS (RGD)
**Versión:** 2.1.0
**Fecha:** 13 de Mayo de 2026

---

## 0. PORTADA Y CONTROL DE VERSIONES

### Proyecto: Estabilización y Granularidad del Pipeline RGD
**Responsable:** Ingeniería de Datos / Arquitectura de Datos
**Alcance:** Ingesta Integral, Modelado Dimensional y Geoposicionamiento.

| Versión | Fecha | Autor | Cambios |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 01/04/2026 | Arquitecto RA | Estructura inicial del DWH. |
| 2.0.0 | 10/05/2026 | Ingeniería Datos | Integración de Puntos de Generación. |
| 2.1.0 | 13/05/2026 | Antigravity AI | Solución de Unicidad y Geo-Resolution. |

---

## 1. ARQUITECTURA DEL SISTEMA

El sistema opera bajo un modelo **Híbrido de Ingeniería de Datos** que combina la robustez de Pentaho (Spoon) para orquestación legacy y Python para lógica avanzada de geoposicionamiento.

### Diagrama de Flujo de Datos
- **Fuentes**: SUIA III (Servidor 179) y COA (RCOA).
- **Staging**: Tablas temporales en el esquema `stg`.
- **Enriquecimiento**: Módulo Python `geo_resolver.py` inyecta geografía vía GeoJSON.
- **DW**: Almacenamiento final en el esquema `dw`.

---

## 2. MODELO DIMENSIONAL (ESTRELLA)

Se ha implementado una granularidad a nivel de **Punto de Generación**, permitiendo análisis geoespaciales precisos.

### Entidades Principales
- **dim_waste_generator**: Metadatos del establecimiento.
- **dim_punto_generacion**: Ubicación exacta, coordenadas y geografía normalizada.
- **fact_waste_generation**: Hechos de generación, entrega y almacenamiento.

---

## 3. PROCESOS ETL Y GEOPOSICIONAMIENTO

### Pipeline de Ingesta
1. **Extracción**: Python extrae datos enriquecidos con JOINs geográficos desde la fuente.
2. **Geo-Resolución**: Si un punto carece de provincia/cantón, el motor de Python realiza un cruce espacial usando coordenadas X/Y.
3. **Carga (UPSERT)**: Se utiliza lógica `ON CONFLICT` para mantener la integridad de los datos por Punto de Generación.

---

## 4. GUÍA OPERACIONAL

### Protocolo de Mantenimiento
Para recuperar el sistema ante errores de restricción o duplicados:
1. Ejecutar `force_cleanup.py`.
2. Aplicar cambios con `apply_sql_changes.py`.
3. Lanzar el orquestador `run_full_rgd_etl.py`.

---

## 5. GLOSARIO DE TÉRMINOS DE NEGOCIO

- **RGD**: Registro Generador de Desechos. Identificador único legal del establecimiento.
- **Punto de Generación**: Sitio físico específico dentro de un predio donde se origina el residuo.
- **Métrica Generada**: Volumen bruto de residuos reportados en el año fiscal.

---

## FIRMAS DE RESPONSABILIDAD

| ELABORADO POR | REVISADO POR | APROBADO POR |
| :--- | :--- | :--- |
| <br><br>____________________ | <br><br>____________________ | <br><br>____________________ |
| **Ingeniería de Datos** | **Arquitectura de Datos** | **Gerencia de TI / Producto** |
| Fecha: 13/05/2026 | Fecha: 13/05/2026 | Fecha: 13/05/2026 |
