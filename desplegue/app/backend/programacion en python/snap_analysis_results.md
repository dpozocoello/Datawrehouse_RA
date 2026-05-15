# Análisis de la Consulta de Intersección SNAP y BI Dashboard

Durante el análisis del cruce de información entre la base de datos remota (`suia_bpms_enlisy`) y el repositorio local (`vm_unificado_sistemas_bi`), se identificó una consideración clave sobre el SQL provisto para validar la intersección.

## 1. El problema con la consulta original

La consulta propuesta inicialmente:

```sql
SELECT v.processinstanceid, v.value
FROM variableinstancelog v  
WHERE variableid ILIKE '%SNAP%';
```

**Problema:**
La columna `value` en estas filas **no contiene el código del proyecto**. En su lugar, contiene valores booleanos (`true`, `false`) o mensajes de texto como:
- `"Su proyecto interseca con el Sistema Nacional de Áreas Protegidas..."`
- `"Por tanto no puede continuar con el trámite..."`

Intentar hacer un `JOIN` entre este `v.value` y el `"CÓDIGO PROYECTO"` del BI Dashboard siempre resultará en **0 coincidencias**.

## 2. La forma correcta de cruzar la información

Para obtener el Código de Proyecto real ligado a un proceso SNAP, se debe buscar en las variables correspondientes a ese mismo `processinstanceid`. El código del proyecto se guarda bajo las variables `tramite` o `numero_tramite`.

Por lo tanto, la lógica correcta es:
```sql
SELECT v_proj.processinstanceid, v_proj.value AS codigo_proyecto
FROM variableinstancelog v_proj
WHERE v_proj.variableid IN ('tramite', 'numero_tramite')
  AND EXISTS (
      SELECT 1 FROM variableinstancelog v_snap 
      WHERE v_snap.processinstanceid = v_proj.processinstanceid 
      AND v_snap.variableid ILIKE '%SNAP%'
  );
```
*(Nota: El script `unique_snap_dashboard_query.sql` ya implementa esta lógica correctamente a través de un `EXISTS`).*

## 3. Resultados Cuantitativos del Cruce (Intersección Real)

Al ejecutar un script en Python que implementa esta lógica corregida conectándose a ambos servidores (DB `suia_bpms_enlisy` y DB `area_stage_saf_suia`), se obtuvieron las siguientes métricas de intersección:

- **Total de Proyectos Únicos en el BI Dashboard:** 327,770
- **Total de Proyectos con un registro tipo SNAP en el sistema remoto:** 175,153
- **🛑 Proyectos que INTERSECAN (Están en BI y tienen SNAP):** 136,920 proyectos
- **Proyectos en SNAP que NO están en el BI Dashboard:** 38,233 proyectos
- **Proyectos en el BI Dashboard que NO tienen registros SNAP:** 190,850 proyectos

**Conclusión:**
Los proyectos que cumplen con la respuesta de intersección alcanzan la cifra de **136,920** códigos compartidos. Para asegurar resultados precisos en tus reportes, debes utilizar la consulta corregida que extrae el código desde la variable "tramite" basándose en la preexistencia de la variable "SNAP" para ese ID de proceso.
