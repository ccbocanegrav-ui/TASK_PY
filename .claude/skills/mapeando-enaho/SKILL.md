---
name: mapeando-enaho
description: Mapea la pobreza de la ENAHO del INEI por departamento en Perú usando códigos UBIGEO y límites GeoJSON. Úsala cuando pidan un mapa, coropleta o mapa departamental de pobreza ENAHO.
argument-hint: [año]
---

# Mapear la ENAHO

Si no existe `salidas/personas_2024.parquet`, usa primero la skill
`limpiando-enaho` y confirma que `salidas/validacion.txt` tenga estado OK.

Antes de ejecutar, confirma que exista
`datos/peru_departamental_simple.geojson`. Ejecuta desde la raíz:

Si recibes un año, pásalo con `--anio $0`; de lo contrario, omite esa opción
(el script usa 2024 por defecto):

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --anio $0
```

La unión geográfica siempre se hace con `ubigeo[:2]` y `FIRST_IDDP` como códigos
de texto con dos dígitos; nunca por nombre. Exige los 25 departamentos con
datos, mantén Lima (15) y Callao (07) separados, pondera con `facpob07` y usa
una escala secuencial de un solo color. El PNG se guarda a 200 dpi en `mapas/`.
No reportes resultados si falla una validación.
