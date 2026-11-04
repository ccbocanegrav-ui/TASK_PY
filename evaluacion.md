# Evaluación: con y sin skills

Cada pedido se corre dos veces desde la raíz del repositorio:

```bash
claude -p "<pedido>" --allowedTools "Bash(uv run:*)"                           # con skills
claude -p "<pedido>" --allowedTools "Bash(uv run:*)" --disallowedTools Skill   # sin skills
```

El pedido va primero: `--allowedTools` y `--disallowedTools` aceptan varios valores y, si van antes, se tragan el
pedido. `--allowedTools` hace falta porque con `-p` nadie puede aprobar comandos y Claude no podría correr los scripts.

Antes de la corrida con skills, borra `salidas/*.parquet` para comprobar que se encadenan.

| Pedido | Skills esperadas | Cifra esperada |
|---|---|---|
| ¿Cuál fue la pobreza en Cusco en 2024? | `limpiando-enaho` | 18.5 % |
| Grafica la pobreza urbana y rural | `graficando-enaho` (+ `limpiando-enaho`) | 24.8 % y 39.3 % |
| Haz un mapa de la pobreza por departamento | `mapeando-enaho` (+ `limpiando-enaho`) | Cajamarca 45.0 %, Ica 6.0 % |

## Resultados (completar con lo que pasó de verdad)

| Pedido | Modo | Skills que se activaron | Cifra | ¿Ponderó? | Cómo se ve la figura |
|---|---|---|---|---|---|
| Pobreza en Cusco | con skills | | | | — |
| Pobreza en Cusco | sin skills | — | | | — |
| Urbana y rural | con skills | | | | |
| Urbana y rural | sin skills | — | | | |
| Mapa por departamento | con skills | | | | |
| Mapa por departamento | sin skills | — | | | |

## Qué cambió al tener las skills

(Escribe aquí 3 o 4 líneas con lo que observaste: fuente de la cifra, validación, encadenamiento, diseño.)

## Lo que se corrigió

(Si una skill no se activó, qué cambiaste en su `description` y qué pasó después.)
