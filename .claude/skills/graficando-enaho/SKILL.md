---
name: graficando-enaho
description: Grafica indicadores de pobreza de la ENAHO del INEI, ponderados por persona, por área urbana o rural, sexo o edad. Úsala cuando pidan gráficos, barras o comparaciones de pobreza ENAHO.
argument-hint: [area|sexo|edad]
---

# Graficar la ENAHO

Si no existe `salidas/personas_2024.parquet`, usa primero la skill
`limpiando-enaho` y confirma que `salidas/validacion.txt` tenga estado OK.

Ejecuta desde la raíz del proyecto. Si recibes un argumento, úsalo como corte
con `--por $0`; si no, omite esa opción (el script usa `area` por defecto):

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por $0 --anio 2024
```

La salida debe guardarse en `figuras/`. Usa siempre `facpob07`; barras con eje
desde cero, ordenadas cuando el corte lo permita, un solo color y el valor
rotulado en cada barra. El título indica indicador y año. Incluye la fuente
«Fuente: INEI, ENAHO 2024» y una leyenda con la unidad «% de personas». No
reportes resultados sin validar la salida del script.
