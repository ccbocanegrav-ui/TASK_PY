---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI, valida contra la pobreza oficial y deja bases de personas y hogares con pobreza y factores de expansión. Úsala siempre que pregunten una cifra de pobreza del Perú (por ejemplo la pobreza en Cusco, Puno o Lima en 2024), o pidan limpiar, unir o analizar la ENAHO, aunque ya exista una tabla en mapas/ o figuras/.
argument-hint: [año]
---
# Limpiar la ENAHO

1. Si faltan los zip en `datos/` (`966-Modulo34.zip`, `966-Modulo02.zip` para 2024), pide al usuario bajarlos del
   portal del INEI (enlaces en el README). No intentes otras URL.
2. Corre exactamente: `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio $0` (2024 si no hay año).
   No reescribas el pipeline ni lo cambies para que pase la validación.
3. Lee `salidas/validacion.txt`. Si dice `NO VALIDADA` o la pobreza difiere del INEI en más de 0.1 puntos,
   detente y muestra qué chequeo falló.
4. Bases que deja:
   - `salidas/personas_<año>.parquet`: un residente habitual por fila; pondera con `facpob07` (sexo, edad).
   - `salidas/hogares_<año>.parquet`: un hogar por fila; pondera con `peso` = `factor07 × mieperho`
     (pobreza nacional, por área y por departamento).
5. Toda cifra va ponderada. Pobre es `pobreza <= 2`; nunca promedies el código `pobreza`.
6. Departamentos por código de dos dígitos (`ubigeo[:2]`), nunca por nombre.
7. Antes de usar una variable que no está en la base, lee [reference.md](reference.md).

## Para responder una cifra

Calcúlala desde las bases validadas, no desde CSV o figuras previas, que pueden ser de otra corrida:

```python
import pandas as pd
h = pd.read_parquet("salidas/hogares_2024.parquet")
c = h[h.departamento == "08"]
print(round((c.pobre * c.peso).sum() / c.peso.sum() * 100, 1))  # Cusco: 18.5
```
