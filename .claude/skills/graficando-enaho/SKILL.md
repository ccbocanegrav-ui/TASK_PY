---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza monetaria o extrema de la ENAHO del INEI por área urbana y rural, sexo, grupo de edad o departamento, ponderados y con formato fijo, y los guarda como PNG en figuras/. Úsala cuando pidan graficar, comparar o visualizar la pobreza del Perú con la ENAHO.
argument-hint: [area|sexo|edad|departamento] [pobreza|extrema] [año]
---
# Graficar la ENAHO

1. Si no existen `salidas/personas_<año>.parquet` y `salidas/hogares_<año>.parquet` (2024 si no piden otro),
   usa primero la skill `limpiando-enaho`.
2. Traduce el pedido a un corte: urbano/rural → `area`; hombres/mujeres → `sexo`; niños, jóvenes, adultos
   mayores → `edad`; regiones → `departamento`. Si piden pobreza extrema, `--medida extrema`.
3. Corre: `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por <corte> --medida <medida> --anio <año>`.
   Un corte por gráfico; si piden varios, una corrida por corte.
4. Mira el PNG antes de entregarlo y responde con las cifras que imprime el script y la ruta del archivo.

## Reglas fijas (ya están en el script; no las cambies por pedido)

- Pondera siempre: área y departamento con `factor07 × mieperho` (sumaria); sexo y edad con `facpob07`,
  porque solo existen por persona.
- Barras horizontales que empiezan en cero, ordenadas de menor a mayor (la edad, en su orden natural).
- Un solo color y el valor escrito en cada barra; sin eje X.
- Título que dice qué y cuándo: «Pobreza monetaria por sexo, 2024 (% de personas)».
- Nota al pie: «Fuente: INEI, ENAHO 2024» y el factor usado.
- PNG a 200 dpi en `figuras/<medida>_<corte>_<año>.png`.
