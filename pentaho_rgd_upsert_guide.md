# Guía de Integración PDI (Pentaho Data Integration) para RGD

Esta guía documenta los pasos necesarios para acoplar la lógica actual de Pentaho con las nuevas estructuras creadas en base de datos (`setup_rgd_control.sql`) y el nuevo wrapper en Python (`rgd_etl_wrapper.py`). El objetivo es lograr un diseño "Non-Breaking".

## 1. Configuración de Dimension Lookup/Update (SCD Tipo 1/2)

Para la tabla `dw.dim_waste_generator`, en lugar de usar un paso "Table Output" o "Insert / Update", debes utilizar **Dimension Lookup/Update**.

### Pasos en Spoon (.ktr):
1. Arrastra el paso **Dimension Lookup/Update** (categoría Data Warehouse).
2. **Connection:** Selecciona tu conexión a `dw_reg_v1`.
3. **Target table:** `dim_waste_generator`.
4. **Keys:** Configura los campos de búsqueda (ej. `codigo`).
5. **Fields:** Mapea el resto de los campos (`generator_name`, etc.).
   - Si deseas **SCD Tipo 1** (sobrescribir historial): Selecciona `Update` en "Type of dimension update".
   - Si deseas **SCD Tipo 2** (mantener historial): Selecciona `Insert` para crear nuevas versiones. Asegúrate de mapear `last_update` como "Date of last update" y usar un campo como `version`.
6. En la pestaña avanzada, asegúrate de utilizar el campo **`is_active`** si estás usando SCD Tipo 2 para marcar los registros actuales.

## 2. Orquestación del Script Python desde Pentaho (.kjb)

El script `rgd_etl_wrapper.py` ahora maneja códigos de salida (Exit Codes). Pentaho debe actuar como el orquestador maestro.

### Pasos en el Job Principal:
1. Añade un paso **Shell** (o "Python Executor" si tienes el plugin).
2. En la pestaña "Script", introduce el comando de ejecución:
   ```bash
   python d:\Datawrehouse_RA\rgd_etl_wrapper.py --db-url ${RGD_DB_URL}
   ```
   *(Asegúrate de definir la variable `${RGD_DB_URL}` en los parámetros del Job o en el archivo `kettle.properties`).*
3. **Captura de Errores (Non-Breaking):**
   - Dibuja un salto condicional (línea verde con un visto) hacia el siguiente paso de éxito.
   - Dibuja un salto incondicional de error (línea roja con una X) hacia un paso de **Mail** o **Write to log**. 
   - El script de Python usará `sys.exit(1)` si ocurre una falla grave de base de datos, lo cual Pentaho detectará y seguirá la ruta roja.
   - Si hay registros rechazados, el script Python los aislará en `dw.staging_rejects`, pero emitirá `sys.exit(0)`, por lo que Pentaho lo considerará "Exitoso" y no detendrá la carga del resto del DWH.

## 3. Trazabilidad

Asegúrate de consultar la tabla `dw.etl_log` y `dw.staging_rejects` al finalizar la ejecución del Job general para comprobar si hubo registros apartados por no cumplir las reglas de calidad de datos.
