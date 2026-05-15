# QA Test Plan: Dashboard RG v1.01 (Data Warehouse)

## 1. Alcance
Validación integral de la carga de datos del Dashboard RG v1.01 desde fuentes transaccionales hasta la capa de presentación.

## 2. Cronograma de Pruebas
| Actividad | Duración (Estimada) | Responsable |
| :--- | :--- | :--- |
| **Profilado de Fuentes** | 1 día | QA Engineer |
| **Pruebas de Integridad (Cargas)** | 2 días | Data Engineer / QA |
| **Pruebas de Exactitud (Rec.)** | 2 días | Business Analyst / QA |
| **Pruebas de Dashboard (UI)** | 1 día | QA Engineer |

## 3. Entregables de Calidad
1. **RTM (Traceability Matrix)**: Mapeo de KPI -> Tabla DWH -> Columna Origen.
2. **DQ Rules Catalog**: Lista de validaciones automáticas ejecutadas.
3. **Test Cases DWH**: Casos técnicos de validación de esquemas y datos.
4. **Reporte de Resultados**: Scorecard final de calidad.

## 4. Estrategia de Muestreo
- **Muestreo Estratificado**: Basado en fechas de carga (últimos 3 meses), volumen por sistema origen y casos de borde (registros con nulos permitidos vs NO permitidos).
- **Tamaño Muestral**: Mínimo 100 registros por tabla de hechos crítica para comparación manual.

## 5. Recursos Necesarios
- Credenciales de solo lectura en los servidores `172.16.0.179` y `172.16.0.226`.
- Acceso a las carpetas locales de `D:\Datawrehouse_RA` donde residen las fuentes.

## 6. Gestión de Defectos
- **Severidad**: Crítica (Datos Incorrectos), Alta (Datos Faltantes), Media (Inconsistencia Estética), Baja (Sugerencia).
- **Triage**: Revisión diaria de defectos con el equipo de Desarrollo.
