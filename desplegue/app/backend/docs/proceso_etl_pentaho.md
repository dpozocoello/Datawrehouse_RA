# Proceso ETL: Pentaho Data Integration (PDI)

Pentaho actúa como la capa de orquestación visual y conector de fuentes legacy y procesos de ingesta especializados que requieren una interfaz gráfica o lógica de flujo de datos (KTR).

## 1. Job Maestro: `JOB_CARGA_DWH_REGULARIZACION.kjb`

Es el orquestador principal que coordina la ejecución de tareas.

### Flujo de Trabajo:
1.  **START:** Inicio del proceso.
2.  **Preparación de Entorno:** Limpieza de tablas temporales si es necesario.
3.  **Ejecución de Cargas Python (Ingesta):** Llama a `etl_main.py` mediante pasos de "Shell" para ejecutar las ingestas desde SUIA y COA.
4.  **Transformaciones KTR:** Ejecuta lógicas de flujo de datos que no están en Python (ej: Pagos).
5.  **Carga de Hechos:** Dispara los procesos de transformación final hacia el esquema `dw`.
6.  **Fin Exitoso / Error:** Manejo de notificaciones.

## 2. Transformaciones Críticas (KTR)

### 2.1 Ingesta de Pagos JBPM (`TRX_09_INGESTA_PAGOS_HIST.ktr`)
*   **Función:** Extrae el histórico de transacciones financieras desde la base de datos JBPM.
*   **Lógica:** Consume tablas de auditoría de saldos y procesa la descripción de movimientos para identificar el uso real de cuotas por proyecto.

### 2.2 Variables JBPM (`TRX_06_INGESTA_SNAP.ktr`)
*   **Función:** Identifica si los proyectos intersectan con Áreas Protegidas (SNAP).
*   **Lógica:** Procesa variables serializadas de los procesos de BPM para extraer el indicador de intersección.

## 3. Integración Pentaho-Python

La integración se realiza mediante el componente **Shell** dentro de Pentaho, permitiendo que el Job herede la potencia de procesamiento de Python.

### Configuración del Salto:
- **Comando:** `python f:/Datawrehouse_RA/ETL_p/etl_main.py --desde X --hasta Y`
- **Control de Errores:** Pentaho captura el código de retorno de Python (Exit Code).
    - `0`: Éxito, el Job continúa al siguiente nodo.
    - `1` o superior: Error, el Job se detiene y marca fallo en el log de Pentaho.

## 4. Origen y Destino de Información

| Proceso | Fuente de Datos | Destino (Staging) |
| :--- | :--- | :--- |
| Ingesta General | SUIA ENLISY (Remoto) | `stg.suia_coa_bi` / `stg.suia_rcoa_bi` |
| Transacciones | JBPM (Remoto) | `stg.online_payments_bi` |
| Residuos/Químicos | COA (Local/Remoto) | `stg.stg_waste_generator` / `stg.stg_fact_*` |
