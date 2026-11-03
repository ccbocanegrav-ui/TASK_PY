---
name: limpiando-enaho
description: Limpia y une los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI para crear una base de personas con pobreza y factor de expansión. Úsala cuando pidan limpiar, unir o analizar la ENAHO, consultar pobreza o preparar datos para un gráfico o mapa.
argument-hint: [año]
---

# Limpiar la ENAHO

1. El proyecto solo incluye el código 966 de la ENAHO 2024. Si faltan
   `datos/966-Modulo34.zip` o `datos/966-Modulo02.zip`, pide al usuario que los
   descargue del INEI. No simules resultados con datos inventados.
2. Ejecuta desde la raíz del proyecto. Si recibes un año, pásalo con
   `--anio $0`; si no, omite esa opción (el script usa 2024 por defecto):

   ```bash
   uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio $0
   ```

3. Lee `salidas/validacion.txt`. Si algún control falla, explica el error y no
   uses la base como si fuera válida. La tasa debe estar a no más de 0.1 puntos
   porcentuales de 27.6 % y deben quedar 108,664 residentes habituales.
4. Responde usando `salidas/personas_2024.parquet`. Toda cifra de personas se
   pondera con `facpob07`.
5. Antes de usar una variable no descrita en la base, consulta
   [reference.md](reference.md).
