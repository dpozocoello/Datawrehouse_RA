# Test Cases: Dashboard (Functional) - RG v1.01

## 1. Módulo: Visualización y Filtros
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DASH_01** | Filtro de Provincia | 1. Seleccionar 'Pichincha'. 2. Verificar KPIs. | Los valores se filtran correctamente según DWH. |
| **TC_DASH_02** | Drill-down de Actividad | 1. Click en categoría 'Construcción'. 2. Listar proyectos. | El listado coincide con el detalle de la base. |

## 2. Módulo: Veracidad de KPIs
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DASH_03** | KPI: Total Proyectos | 1. Comparar número en pantalla vs `SELECT count(*) FROM dw.fact_regularizacion`. | Valores idénticos. |
| **TC_DASH_04** | KPI: Recaudación Mensual | 1. Validar gráfico de tendencia vs query de sumatorias por mes. | Curva de tendencia visualmente correcta y datos exactos. |

## 3. Módulo: Usabilidad y Reportes
| ID | Descripción | Paso a Paso | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **TC_DASH_05** | Exportación a Excel | 1. Aplicar filtro. 2. Exportar datos. 3. Comparar conteo. | El Excel contiene el mismo número de filas que la UI. |
| **TC_DASH_06** | Tiempo de Respuesta | 1. Cargar dashboard inicial. | Renderizado total en < 3 segundos. |
