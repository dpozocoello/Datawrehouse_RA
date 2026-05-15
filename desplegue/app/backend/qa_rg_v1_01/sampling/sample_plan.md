# Sampling Methodology: Dashboard RG v1.01

## 1. Objetivo
Definir un subconjunto representativo de datos para realizar validaciones registro a registro (Record-to-Record) entre las fuentes y el Data Warehouse.

## 2. Estrategia de Muestreo: Estratificado
Se utilizará un muestreo estratificado para asegurar cobertura en dimensiones críticas:

### Estratos Definidos:
1. **Temporal (Reciente vs Histórico)**:
   - 60% de la muestra: Datos de los últimos 6 meses (Carga Activa).
   - 40% de la muestra: Datos históricos (Migración).
2. **Volumen Proponente**:
   - Muestras de grandes proponentes (con > 10 proyectos).
   - Muestras de proponentes con un solo proyecto.
3. **Casos de Borde (Edge Cases)**:
   - Registros con campos opcionales nulos.
   - Proyectos con múltiples pagos asociados.
   - Proyectos en estados "Inactivo" o "Cancelado".

## 3. Tamaño de la Muestra
- **Población Total**: Identificada en `sources_inventory.csv`.
- **Muestra Objetivo**: 100 registros PK para `fact_regularizacion` y 50 para `fact_pago`.

## 4. Generación de Samples
Los códigos de proyecto se extraerán de `reporte_proyectos_recuperados.csv` y `matriz_regularizacion_ambiental_...xlsx` de forma pseudo-aleatoria dentro de cada estrato.

## 5. Validación
Para cada PK en `samples.csv`, se deben verificar:
- Nombres de proyecto.
- Fechas de registro.
- Montos de pago (si aplica).
- Ubicación geográfica (Provincia/Cantón).
