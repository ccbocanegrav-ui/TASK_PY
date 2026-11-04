---
name: mapeando-enaho
description: Hace un mapa coroplético del Perú con la pobreza monetaria o extrema de la ENAHO del INEI por departamento (región), uniendo por código con los límites de los 25 departamentos, y lo guarda como PNG en mapas/. Úsala cuando pidan un mapa, mapear o ver en el territorio la pobreza por departamento o región.
argument-hint: [pobreza|extrema] [año]
---
# Mapear la ENAHO

1. Si no existe `salidas/hogares_<año>.parquet` (2024 si no piden otro), usa primero la skill `limpiando-enaho`.
   Si falta `datos/peru_departamental_simple.geojson`, pide al usuario bajarlo (enlace en el README).
2. Corre: `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --medida <medida> --anio <año>`.
3. Si el script se detiene porque la unión falló o no replica la referencia 2024, no lo «arregles» uniendo por
   nombre: revisa que los códigos sean texto de dos dígitos y que la base esté validada.
4. Mira el PNG antes de entregarlo. Responde con la ruta, el departamento con mayor y menor pobreza y sus cifras
   (2024: Cajamarca 45.0 %, Ica 6.0 %).

## Reglas fijas (ya están en el script; no las cambies por pedido)

- Une por código: `ubigeo[:2]` con `FIRST_IDDP`, ambos como texto. Nunca por nombre («APURIMAC» ≠ «Apurímac»).
- Exige 25 departamentos y ninguno sin dato; si no, se detiene.
- Lima (15) y Callao (07) van separados.
- Pondera con `factor07 × mieperho` sobre la sumaria.
- Un solo tono de claro a oscuro (`Oranges`) desde 0; nunca arcoíris.
- Leyenda con la unidad (% de personas), título con qué y cuándo, fuente al pie. PNG a 200 dpi en `mapas/`.
- En 2024 comprueba los 25 valores contra `referencias/pobreza_departamento_2024.csv`.
