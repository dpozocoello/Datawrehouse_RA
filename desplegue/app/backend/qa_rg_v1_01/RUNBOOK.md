# RUNBOOK: Programa de QA Dashboard RG v1.01

## 1. Prerrequisitos
- **Python 3.8+** con las librerías: `pandas`, `psycopg2`, `openpyxl`.
- **Conectividad**: Acceso de lectura a las bases de datos en `172.16.0.179` y `172.16.0.226`.
- **Estructura**: El programa debe residir en `d:\Datawrehouse_RA\qa_rg_v1_01`.

## 2. Cómo Ejecutar las Pruebas
1. Abrir una terminal en `d:\Datawrehouse_RA\qa_rg_v1_01\scripts`.
2. Ejecutar el orquestador principal:
   ```bash
   python qa_runner.py
   ```
3. El script ejecutará automáticamente:
   - Inventario de fuentes.
   - Reconciliación (Source vs DWH).
   - Verificación de SLA (Oportunidad).
   - Checks de Calidad de Datos (SQL).

## 3. Interpretación de Reportes
Los resultados se generan en `/qa_rg_v1_01/reports`:
- `reconciliation_results.csv`: Muestra las diferencias de conteo entre capas.
- `timeliness_data.csv`: Indica si los datos están actualizados.
- `execution_log.txt`: Resumen del estado de cada script.
- Plantillas `.md`: Usar estas plantillas para documentar la evidencia formal (copiar y llenar).

## 4. Gestión de Fallos (Triage)
Si un script marca `FAILED`:
1. Revisar `execution_log.txt` para identificar el script.
2. Ver los logs detallados en la consola.
3. Si es un fallo de datos (ej. `Diff_Pct > 0.1%`), abrir un ticket usando `Defect_Template.md` adjuntando la evidencia generada.

## 5. Captura de Evidencia Manual
Para pruebas de Dashboard (UI), seguir los pasos en `docs/Test_Cases_Dashboard_RG_v1_01.md` y completar el archivo `docs/Evidence_Template.md` con capturas de pantalla.
