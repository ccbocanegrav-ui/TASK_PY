# Skills para trabajar con la ENAHO 2024

Este proyecto reúne tres skills de Claude Code para limpiar los módulos 34 y 02
del INEI, graficar indicadores ponderados y mapear la pobreza por departamento.
Los archivos de microdatos se mantienen localmente en `datos/` y no se suben a
git.

## Requisitos

- Git, Python 3.10 o posterior y [uv](https://docs.astral.sh/uv/).
- Claude Code para activar las skills.
- Los dos ZIP de microdatos y el GeoJSON indicados abajo.

## Datos de entrada

Descarga y guarda en `datos/`:

1. [Módulo 34, sumaria (código 966)](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip)
   como `966-Modulo34.zip`.
2. [Módulo 02, miembros (código 966)](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip)
   como `966-Modulo02.zip`.
3. [Límites departamentales de Perú](https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson)
   como `peru_departamental_simple.geojson`.

El código 966 corresponde a la ENAHO 2024. `datos/` está excluida de git. Los
scripts leen un `.dta` suelto, un directorio con `.dta` o un ZIP que contenga un
único archivo `.dta`; no es necesario extraer los ZIP.

## Instalación y ejecución

Desde PowerShell, en la raíz del proyecto:

```powershell
uv sync
uv run python .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run python .claude/skills/graficando-enaho/scripts/graficar.py --por area --anio 2024
uv run python .claude/skills/mapeando-enaho/scripts/mapear.py --anio 2024
```

La limpieza produce `salidas/personas_2024.parquet` y
`salidas/validacion.txt`. El gráfico produce un PNG en `figuras/`; el mapa,
`mapas/pobreza_departamento.png`. Los scripts detienen la ejecución con un
error explícito cuando faltan entradas, variables o validaciones.

Para escoger otro corte gráfico, usa `--por sexo` o `--por edad`. Todas las
cifras se ponderan con `facpob07`. El corte por edad usa grupos 0–17, 18–29,
30–44, 45–59 y 60 años o más.

## Skills de Claude Code

Las skills están en `.claude/skills/`. En Claude Code puedes invocarlas con:

- `/limpiando-enaho 2024`
- `/graficando-enaho area`
- `/mapeando-enaho 2024`

También se activan automáticamente cuando la solicitud coincide con su
descripción. Las skills de gráficos y mapas indican que primero se ejecute
`limpiando-enaho` si falta la base parquet.

## Evaluación manual

Abre [evaluacion.md](./evaluacion.md) y registra los resultados después de
ejecutar las solicitudes con Claude Code. La tabla es una plantilla; no se
marcan skills ni cifras como verificadas hasta ejecutarlas con los datos
locales.
