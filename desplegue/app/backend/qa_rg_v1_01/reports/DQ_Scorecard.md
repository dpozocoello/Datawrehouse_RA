# Report: Data Quality Scorecard - Dashboard RG v1.01

## 1. Métricas de Calidad
- **Health Score**: 94.5%
- **Reglas Ejecutadas**: 8
- **Reglas Fallidas**: 2

## 2. Detalle por Dimensión
| Dimensión | % Cumplimiento | Críticos |
| :--- | :--- | :--- |
| **Exactitud** | 92.0% | 1 (Diff en Fact_Pago) |
| **Completitud** | 99.8% | 0 |
| **Consistencia** | 88.0% | 1 (Brecha en Dim_Area) |
| **Validez** | 99.0% | 0 |

## 3. Top 5 Anomalías Detectadas
1. **Diferencia en Fact_Pago**: Los archivos de muestra (.csv) no contienen el universo completo de pagos históricos.
2. **Jerarquía Geográfica**: Se detectaron 383 localidades en el DWH que no figuran en el `area_geo_hierarchy.json`.
3. **Nulos en Fechas**: Aproximadamente 0.2% de registros en `stg` presentan fechas de registro nulas (permitido por fuente).
4. **Duplicados**: 0 duplicados críticos detectados en `dw.fact_regularizacion`.
5. **SLA**: Cargas completadas exitosamente en las últimas 24h.

## 4. Histórico de Calidad
- Primera evaluación: 94.5% (Baseline v1.01)
