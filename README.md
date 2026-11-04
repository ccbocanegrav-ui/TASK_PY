# enaho-skills

Tres skills de Claude Code para trabajar la ENAHO 2024 del INEI siempre de la misma forma: limpiarla y validarla
contra la pobreza oficial (27.6 %), graficarla y mapearla por departamento.

| Skill | Entra | Sale |
|---|---|---|
| [`limpiando-enaho`](.claude/skills/limpiando-enaho/SKILL.md) | Zip de los módulos 34 y 02 | `salidas/personas_2024.parquet`, `salidas/hogares_2024.parquet`, [`salidas/validacion.txt`](salidas/validacion.txt) |
| [`graficando-enaho`](.claude/skills/graficando-enaho/SKILL.md) | La base limpia y un corte: área, sexo, edad o departamento | `figuras/*.png` |
| [`mapeando-enaho`](.claude/skills/mapeando-enaho/SKILL.md) | La base limpia y el GeoJSON | `mapas/pobreza_departamento.png` y `.csv` |

Se encadenan: si falta la base limpia, graficar y mapear llaman primero a `limpiando-enaho`, así que un solo pedido
(«haz un mapa de la pobreza por departamento») activa dos skills seguidas.

## Instalar

Requiere [uv](https://docs.astral.sh/uv/) y Claude Code.

```bash
git clone <este repositorio> && cd enaho-skills
uv sync
```

Las skills están en `.claude/skills/` y se cargan al abrir Claude Code en esta carpeta (compruébalo con `/skills`).

## Bajar los datos

Desde el navegador, a una carpeta `datos/` (está en `.gitignore`: los microdatos no se suben):

- [Módulo 34, sumaria](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip) → `datos/966-Modulo34.zip`
- [Módulo 02, miembros](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip) → `datos/966-Modulo02.zip`
- [Límites departamentales](https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson) → `datos/peru_departamental_simple.geojson`

`966` es el código de la ENAHO 2024 en el portal del INEI.

## Correr todo

```bash
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por sexo
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por edad
uv run .claude/skills/mapeando-enaho/scripts/mapear.py
```

O en Claude Code, en lenguaje natural:

```text
¿Cuál fue la pobreza en Cusco en 2024?
Grafica la pobreza urbana y rural
Haz un mapa de la pobreza por departamento con la ENAHO 2024
```

## Validación

`limpiar.py` termina con `RESULTADO: VALIDADA` solo si la base replica las cifras oficiales: 27.6 % de pobreza,
5.5 % de pobreza extrema, 33,691 hogares y 108,664 residentes habituales. `mapear.py` compara los 25
departamentos con [`referencias/pobreza_departamento_2024.csv`](referencias/pobreza_departamento_2024.csv).
Resultado de mi corrida: [`salidas/validacion.txt`](salidas/validacion.txt).

## Evaluación

Tres pedidos con y sin skills: [evaluacion.md](evaluacion.md).

## Estructura

```text
.claude/skills/
  limpiando-enaho/   SKILL.md, reference.md, scripts/limpiar.py
  graficando-enaho/  SKILL.md, scripts/graficar.py
  mapeando-enaho/    SKILL.md, scripts/mapear.py
referencias/  salidas/validacion.txt  figuras/  mapas/
evaluacion.md  README.md  pyproject.toml
```

Autora: <Carla Bocanegra>. Basado en la sesión 16 del curso Data Science con Python (d2cml-ai).
