# Informe de Ejecución Técnica: Arquitectura DWH v1.4.1
**Módulo: Biodiversidad e Intersecciones Ambientales**

---

## 1. Resumen de la Intervención
Se ha completado satisfactoriamente la reingeniería del flujo de biodiversidad. Esta intervención resuelve la brecha de información de ~113k registros que eran omitidos en las versiones anteriores por filtros rígidos de capa.

### 1.1. Servidor de Ejecución
- **Host**: Local (Servidor DWH)
- **Motor**: PostgreSQL 16+
- **Base de Datos**: `Datawarehouse_RA`
- **Esquema de Destino**: `dw`
- **Fecha de Ejecución**: 2026-03-10 | 16:36 COT

---

## 2. Acciones Realizadas (Detalle de Implementación)

### 2.1. Estructura de Datos (DDL)
Se crearon las siguientes tablas en el esquema `dw` para soportar la relación many-to-many entre proyectos y áreas protegidas/patrimonios:
- **`dw.dim_capa_ambiental`**: Dimensión maestra con el catálogo de capas (SNAP, Patrimonio, Zonas Intangibles).
- **`dw.bridge_interseccion_ambiental`**: Tabla puente para el cruce analitico.

### 2.2. Refactorización de Extracción (Stored Procedures)
Se han actualizado y recompilado las funciones en el servidor local que orquestan la extracción vía `dblink`:
- **`suia_iii.sp_coa_bi()`**: Ahora captura `laye_id` IN (2, 3, 4, 11).
- **`coa_mae.sp_rcoa_bi()`**: Sincronizado para captura multicanal.
- **`dw.sp_carga_puente_ambiental()`**: [NUEVO] Lógica de limpieza y población del puente.

---

## 3. Impacto en la Trazabilidad
Mediante este cambio, el sistema captura ahora las siguientes capas de información desde el servidor de origen (`172.16.0.179`):

| Capa Ambiental | ID Origen | Estado Anterior | Estado Actual |
| :--- | :--- | :--- | :--- |
| **SNAP** | 3 | Capturado | **Capturado** |
| **Zonas Intangibles** | 2 | Omitido | **Capturado** |
| **Patrimonio Forestal** | 11 | Omitido | **Capturado** |
| **Bosques Protectores** | 4 | Omitido | **Capturado** |

---

## 4. Estado Final y Verificación
- **Ejecución Scripts**: Éxito (100% aplicado).
- **Consistencia de Datos**: Dimensión poblada con los 4 tipos de capas base.
- **Capacidad de Carga**: El sistema está listo para procesar el volumen total de biodiversidad en el próximo refresco del ETL.

---
**Ingeniería de Datos**: Antigravity AI Data Architecture
**Referencia**: [Analisis_Intersecciones_Ambientales_v1_4.md](file:///f:/Datawrehouse_RA/documentación/Analisis_Intersecciones_Ambientales_v1_4.md)
