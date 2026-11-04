# Referencia ENAHO 2024

| Módulo | Archivo dentro del zip | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|---|
| 34 Sumaria | `sumaria-2024.dta` | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` |
| 02 Miembros | `enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` |

No uses `sumaria-2024-12g.dta` (gasto en 12 grupos).

## Variables de las bases limpias
`departamento` = `ubigeo[:2]` · `urbano` = `estrato <= 5` · `pobre` = `pobreza <= 2` · `pobre_extremo` = `pobreza == 1`
· `peso` (hogares) = `factor07 × mieperho` · `sexo` de `p207` · `edad` de `p208a` · `grupo_edad`: 0-13, 14-17,
18-29, 30-44, 45-59, 60 y más.

Residente habitual: `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)`.

## Cifras oficiales 2024
Pobreza 27.6 % (sumaria 27.58 %; personas 27.53 %) · extrema 5.5 % · urbana 24.8 % / rural 39.3 % ·
Lima Metropolitana (`dominio == 8`) 28.2 % · 33,691 hogares · 108,664 residentes habituales.

## Trampas
1. Ceros a la izquierda: `conglome` y `ubigeo` van como texto.
2. La columna del año llega como `aÑo`: se renombra `anio`.
3. No todos son residentes: 117,721 filas, 108,664 residentes.
4. Sin `validate="m:1"` un hogar repetido multiplica personas sin avisar.
5. Sin factor de expansión, 33,691 hogares no dicen nada del país.
6. `pobreza` es un código: pobre es `pobreza <= 2`, no un promedio.

## Departamentos
01 Amazonas · 02 Áncash · 03 Apurímac · 04 Arequipa · 05 Ayacucho · 06 Cajamarca · 07 Callao · 08 Cusco ·
09 Huancavelica · 10 Huánuco · 11 Ica · 12 Junín · 13 La Libertad · 14 Lambayeque · 15 Lima · 16 Loreto ·
17 Madre de Dios · 18 Moquegua · 19 Pasco · 20 Piura · 21 Puno · 22 San Martín · 23 Tacna · 24 Tumbes · 25 Ucayali.
