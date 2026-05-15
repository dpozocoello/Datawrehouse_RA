# Plan Integral de Pruebas y Aseguramiento de Calidad (QA) — DWH RA
**Versión:** 1.0 | **Fecha:** 08 de mayo de 2026

## 1. Estrategia de Pruebas
El objetivo de este plan es certificar la consistencia de los datos del Data Warehouse Regularización Ambiental frente a las fuentes originales de Producción (SUIA/JBPM). La meta de calidad (Threshold) está definida en **\>98% de coincidencia exacta**.

## 2. Entorno de Pruebas
- **Origen (Source):** SUIA_ENLIS (Producción, Esquemas seleccionados).
- **Destino (Target):** `dw_reg_v1` (QA/Test Environment).

## 3. Matriz de Trazabilidad y Casos de Prueba (Test Cases)

### TC-01: Validación de Consistencia Geográfica Múltiple (M:N)
**Objetivo:** Verificar que el DWH captura todas las parroquias asignadas a un único proyecto (Relación recursiva).
**Precondición:** Ejecución exitosa del script DDL v2 y el Bridge.
**Paso a paso:**
1. Consultar en Producción el proyecto `2017-304882` (Debe poseer MACHÁNGARA y CHIQUINTAD).
2. Consultar en DWH `dw.dim_proyecto` (join con `dw.fact_proyecto_geografia` y `dw.dim_geografia`).
**Criterio de Aceptación:** La query al DWH debe retornar exactamente 2 filas para ese proyecto, con ambas parroquias mapeadas correctamente a sus cantones y provincias respectivas usando la llave recursiva `sk_padre`.

### TC-02: Exactitud del Costo Transaccional Diferencial (ETL v3)
**Objetivo:** Confirmar que los proyectos no heredan erróneamente montos globales de un depósito compartido.
**Precondición:** Ejecución exitosa de `etl_carga_datos_v3.sql`.
**Paso a paso:**
1. Seleccionar un `tramit_number` conocido que posea depósitos iniciales compartidos en JBPM.
2. Extraer el costo de ese proyecto en el reporte estático antiguo de Producción.
3. Extraer el `monto_acumulado` del mismo proyecto en `dw.fact_pago`.
**Criterio de Aceptación:** El DWH debe reflejar el costo individual (descontado) del proyecto, en lugar del monto global compartido reportado por Producción. El valor en DWH es la única fuente de verdad contable aceptada.

### TC-03: Trazabilidad del Área Responsable
**Objetivo:** Asegurar que el ETL de carga dimensional preserva la dependencia organizacional.
**Paso a paso:**
1. Contar el número de proyectos en staging (`consolidado_proyectos`) que poseen el campo `ÁREA RESPONSABLE PROYECTO` con valor no nulo.
2. Contar el número de proyectos en `dw.dim_proyecto` con `area_responsable` no nulo.
**Criterio de Aceptación:** La cantidad debe ser exactamente la misma, certificando que no hay pérdida de información durante la transformación dimensional.

## 4. Informe de Ejecución y Resultados
*(Esta sección debe ser completada por el Analista QA tras cada ciclo de pruebas)*

| Fecha de Ejecución | Versión DWH | Total TC | TC Pasados | TC Fallidos | % Coincidencia Final | Firma QA |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| DD/MM/AAAA | v3.0 | 3 | [__] | [__] | __% | ________ |

## 5. Acta de Conformidad Técnica
Se declara que las pruebas arriba descritas validan la integridad de la base de datos analítica, mitigando los riesgos contables identificados en versiones previas.
