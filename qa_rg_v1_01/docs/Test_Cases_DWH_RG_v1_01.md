# Test Cases: Data Warehouse (Technical) - RG v1.01

## 1. Módulo: Exactitud (Accuracy)
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DWH_01** | Reconciliación `fact_regularizacion` | 1. Contar registros en fuentes (.xlsx) vs `stg` vs `dw`. | Conteos coinciden al 100%. |
| **TC_DWH_02** | Reconciliación `fact_pago` | 1. Sumar `monto_pago` en `pagos_prod.csv` vs `dw.fact_pago`. | Sumas coinciden (tolerancia 0.01). |
| **TC_DWH_03** | Registro a Registro (Muestra) | 1. Seleccionar 100 PKs de `samples.csv`. 2. Validar todos los campos en DWH. | 0 discrepancias encontradas. |

## 2. Módulo: Completitud (Completeness)
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DWH_04** | Detección de Nulls Críticos | 1. Query sobre `dw.fact_*` buscando nulos en PK/SK. | 0 registros con nulos en campos clave. |
| **TC_DWH_05** | Gaps Temporales | 1. Agrupar conteos por `año_registro`. 2. Buscar meses sin datos. | Continuidad lógica en la serie temporal. |

## 3. Módulo: Consistencia e Integridad
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DWH_06** | Integridad Referencial | 1. Validar que todas las FK en `fact` existan en `dim`. | 0 FKs huérfanas (o asignadas a SK=0). |
| **TC_DWH_07** | Jerarquía Geográfica | 1. Cruzar `dim_geografia` con `ref_cantons.csv`. | 100% de cantones pertenecen a sus provincias. |

## 4. Módulo: Oportunidad (Timeliness)
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DWH_08** | SLA de Carga | 1. Consultar `max(fecha_carga)` en tablas críticas. | Fecha <= Hoy - 1 día. |
