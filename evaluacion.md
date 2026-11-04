# Evaluación: con y sin skills

Cada pedido se corre dos veces:

```bash
# con skills, desde la raíz del repositorio
claude -p "<pedido>" --allowedTools "Bash(uv run:*)" "PowerShell(uv run:*)" Write Edit

# sin skills, desde una copia que solo tiene datos/, pyproject.toml y uv.lock
claude -p "<pedido>" --allowedTools "Bash(uv run:*)" "PowerShell(uv run:*)" Write Edit --disallowedTools Skill
```

- El pedido va primero: `--allowedTools` y `--disallowedTools` aceptan varios valores y, si van antes, se tragan el
  pedido.
- `--allowedTools` hace falta porque con `-p` nadie puede aprobar comandos. En Windows hay que incluir `PowerShell`,
  porque Claude usa esa herramienta tanto como `Bash`.
- La corrida sin skills va en una copia sin `.claude/skills`, README ni `referencias/`: con `--disallowedTools Skill`
  dentro del repositorio, Claude igual lee los `SKILL.md` y los scripts y no es una comparación real.
- Antes de cada corrida, borra `salidas/*.parquet` para comprobar que las skills se encadenan.

| Pedido | Skills esperadas | Cifra esperada |
|---|---|---|
| ¿Cuál fue la pobreza en Cusco en 2024? | `limpiando-enaho` | 18.5 % |
| Grafica la pobreza urbana y rural | `graficando-enaho` (+ `limpiando-enaho`) | 24.8 % y 39.3 % |
| Haz un mapa de la pobreza por departamento | `mapeando-enaho` (+ `limpiando-enaho`) | Cajamarca 45.0 %, Ica 6.0 % |

## Resultados

Corrida del 4 de noviembre de 2026. En la versión sin skills, Claude escribió los scripts pero no pudo correrlos
porque usó `.venv\Scripts\python.exe` en vez de `uv run`; los corrí a mano para ver qué daban.

| Pedido | Modo | Skills que se activaron | Cifra | ¿Ponderó? | Cómo se ve la figura |
|---|---|---|---|---|---|
| Pobreza en Cusco | con skills | `limpiando-enaho` | 18.5 % (validada) | Sí, `factor07 × mieperho` | — |
| Pobreza en Cusco | sin skills | — | No la calculó: dijo «entre 20 % y 27 %» de memoria | No | — |
| Urbana y rural | con skills | `graficando-enaho` → `limpiando-enaho` | 24.8 % y 39.3 % | Sí, `factor07 × mieperho` | Barras horizontales desde cero, un color, valor en cada barra, fuente al pie |
| Urbana y rural | sin skills | — | 24.9 % y **41.3 %** (rural mal por 2 puntos) | Sí, `factor07 × mieperho` | Barras apiladas extrema/no extrema con Nacional; legible, pero no comparable con otras figuras |
| Mapa por departamento | con skills | `mapeando-enaho` → `limpiando-enaho` | Cajamarca 45.0 %, Ica 6.0 %; los 25 iguales a la referencia | Sí, `factor07 × mieperho` | `Oranges` desde 0, leyenda con unidad, sin etiquetas |
| Mapa por departamento | sin skills | — | Cajamarca 45.0 %, Ica 6.0 % | Sí, `factor07 × mieperho` | Escala roja que empieza en 6 %, no en 0; etiquetas encimadas en el norte (Cajamarca, Lambayeque, Amazonas) |

## Qué cambió al tener las skills

- **Fuente de la cifra:** con skills, Cusco salió de la base validada (18.5 %). Sin skills, Claude no tocó los datos y
  respondió de memoria con un rango que no contiene la cifra real.
- **Validación:** sin skills, el gráfico urbano/rural usó estratos 1–6 como urbanos y dio 41.3 % rural en vez de
  39.3 %, sin nada que lo detectara. La skill usa estratos 1–5 y se detiene si no replica el 27.6 % nacional.
- **Encadenamiento:** al borrar los `.parquet`, el gráfico y el mapa llamaron solos a `limpiando-enaho` antes de seguir.
- **Diseño:** con skills, las figuras salen siempre con el mismo formato; sin skills, cada pedido inventa el suyo
  (barras apiladas, escala que no empieza en cero, etiquetas encimadas).

## Lo que se corrigió

- **Comandos de evaluación:** con `claude -p "<pedido>"` a secas, Claude no pudo correr `limpiar.py` porque nadie
  aprobó el permiso; con `--disallowedTools Skill` antes del pedido, la opción se tragó el pedido. Se puso el pedido
  primero y se autorizó `uv run` en `Bash` y `PowerShell`.
- **`limpiando-enaho`:** el paso 2 decía `--anio $0`. Cuando otra skill la llamaba con texto, `$0` se reemplazaba por
  «Pobreza» y Claude tenía que adivinar el año. Ahora dice `--anio <año>`.
- **`graficando-enaho` y `mapeando-enaho`:** no decían qué valores acepta `--medida`, y Claude propuso
  `--medida monetaria`, que no existe. Ahora dicen `pobreza` o `extrema`.
- Las tres skills se activaron a la primera; no hizo falta cambiar ninguna `description`.
