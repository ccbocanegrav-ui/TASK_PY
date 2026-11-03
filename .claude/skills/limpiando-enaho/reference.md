# Referencia de la base limpia

## Unidad y llaves

Cada fila representa a una persona residente habitual. La llave única es
`conglome`, `vivienda`, `hogar`, `codperso`. La unión de personas con hogares
usa las tres primeras columnas y valida una relación muchos-a-uno.

## Variables preparadas

| Variable | Descripción |
|---|---|
| `pobreza` | Clasificación de pobreza del módulo sumaria; 1 y 2 se consideran pobres. |
| `pobre` | Indicador booleano derivado de `pobreza <= 2`. |
| `facpob07` | Factor de expansión de personas; pondera todos los estimados de personas. |
| `ubigeo` | Código de seis dígitos; los dos primeros identifican el departamento. |
| `departamento` | Código departamental textual derivado de `ubigeo[:2]`. |
| `urbano` | Indicador booleano derivado de `estrato <= 5`. |
| `estrato` | Estrato geográfico del hogar. |
| `p207` | Sexo de la persona en el módulo de miembros, cuando está disponible. |
| `p208a` | Edad de la persona en años, cuando está disponible. |

Los nombres originales de columnas se convierten a minúsculas. Los campos
originales no enumerados se conservan; verifica el diccionario del INEI antes
de interpretarlos.

## Cálculo de pobreza

La tasa se calcula como la suma ponderada de `pobre` dividida entre la suma de
`facpob07`, expresada en porcentaje. No uses `factor07` para estimados de
personas. Las cifras de esta base pueden diferir ligeramente de las calculadas
con la sumaria y sus ponderaciones de hogares.
