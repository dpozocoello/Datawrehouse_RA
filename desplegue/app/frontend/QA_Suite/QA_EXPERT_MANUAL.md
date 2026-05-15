# Manual de Aseguramiento de Calidad (QA): Dashboard RA v1.01

**Estatus del Documento**: Profesional / Auditoría
**Experiencia Aplicada**: +20 Años en Ingeniería de Calidad de Software

## 1. Estrategia de Calidad
Este proyecto utiliza un enfoque de **Pruebas de Pirámide Invertida** focalizado en la integridad de los datos, ya que el valor de negocio reside en el Data Warehouse (DWH).

### 1.1 Niveles de Prueba
- **Capa de Datos (Data Integrity)**: Validación de que los resultados de Streamlit coinciden al 100% con los cálculos crudos del DWH.
- **Auditoría de Calidad (DQ Audit - 5 Pilares)**:
    - **Exactitud**: El dato en DW / Dashboard coincide con el Staging (Fuente).
    - **Completitud**: Verificación de nulos en llaves mandatorias (sk_proyecto, sk_geografia).
    - **Consistencia**: Cruce contra catálogos nacionales (INEC 2024).
    - **Validez**: Reglas de negocio (porcentajes [0-100]).
    - **Oportunidad**: Monitoreo de ventanas de carga (fecha_carga).
- **Capa de Conectividad (Smoke Tests)**: Verificación de disponibilidad de puertos 8103 y 8105.

## 2. Ejecución Automatizada

Se ha proporcionado una suite de herramientas en la carpeta `QA_Suite/`.

### 2.1 Cómo ejecutar la auditoría completa
Navega a la raíz del proyecto y ejecuta el archivo:
`D:\DashboardRA\QA_Suite\RUN_QA_AUDIT.bat`

### 2.2 Interpretación de Resultados
- **PASSED (Verde)**: El sistema cumple con los criterios de calidad.
- **FAILED (Rojo)**: Existe una discrepancia entre el código y los datos o el servicio no está respondiendo.

## 3. Guía de Pruebas Manuales (Especializadas)

| Caso de Prueba | Funcionalidad | Resultado Esperado |
| :--- | :--- | :--- |
| **QA-GEO-01** | Filtro de Provincia | Al cambiar la provincia, el gráfico de barras y el mapa deben actualizarse en < 3s. |
| **QA-SUP-02** | Capa Crítica | Buscar un proyecto con 100% de intersección; verificar que la tarjeta se resalte en rojo. |
| **QA-INT-03** | Consistencia | Comparar el totalizador de la pestaña 1 con el de la pestaña 7 para el mismo periodo. |

## 4. Estándares Técnicos
- El código sigue las normas de **limpieza de variables** (evitando NameErrors).
- Las consultas SQL utilizan `DISTINCT` para evitar inflamiento de métricas.
- Todas las rutas están parametrizadas para la unidad `D:`.

---
*Documento generado para asegurar la excelencia operativa del Dashboard de Regularización Ambiental.*
