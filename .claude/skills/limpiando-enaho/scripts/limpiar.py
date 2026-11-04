"""Limpia la ENAHO (módulos 34 y 02), valida contra cifras oficiales y guarda las bases.

Orden fijo: leer, normalizar, filtrar residentes, unir, construir, validar, guardar.
"""
import argparse
import zipfile
from pathlib import Path

import pandas as pd

CODIGOS = {2024: 966, 2023: 906, 2022: 784, 2021: 759, 2020: 737}
LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
POBREZA_OFICIAL = {2024: 27.6, 2023: 29.0, 2022: 27.5, 2021: 25.9, 2020: 30.1}
OFICIAL_2024 = {"hogares": 33_691, "residentes": 108_664, "extrema": 5.5}
TOL = 0.1


def normalizar(col: str) -> str:
    c = col.strip().lower()
    # la columna del año llega como "aÑo" o con la ñ rota
    return "anio" if len(c) == 3 and c[0] == "a" and c[2] == "o" and not c.isascii() else c


def leer_dta(zip_path: Path, nombre: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        hallados = [n for n in zf.namelist() if Path(n).name.lower() == nombre]
        if not hallados:
            raise SystemExit(f"{zip_path.name} no contiene {nombre}")
        with zf.open(hallados[0]) as f:
            df = pd.read_stata(f, convert_categoricals=False)
    df.columns = [normalizar(c) for c in df.columns]
    for c in LLAVES_PERSONA + ["ubigeo"]:  # texto, para no perder ceros a la izquierda
        if c in df:
            df[c] = df[c].astype(str).str.strip()
    return df


def pct(indicador: pd.Series, peso: pd.Series) -> float:
    return float((indicador * peso).sum() / peso.sum() * 100)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--codigo", type=int, help="código del portal INEI si el año no está en CODIGOS")
    ap.add_argument("--datos", default="datos")
    ap.add_argument("--salidas", default="salidas")
    a = ap.parse_args()

    codigo = a.codigo or CODIGOS.get(a.anio)
    if codigo is None:
        raise SystemExit(f"No conozco el código INEI de {a.anio}; usa --codigo")
    datos, salidas = Path(a.datos), Path(a.salidas)
    z34, z02 = (datos / f"{codigo}-Modulo{m}.zip" for m in ("34", "02"))
    faltan = [z.name for z in (z34, z02) if not z.exists()]
    if faltan:
        raise SystemExit(f"Faltan en {datos}/: {', '.join(faltan)}. Bájalos del portal del INEI (ver README).")

    # 1-2. leer y normalizar
    sumaria = leer_dta(z34, f"sumaria-{a.anio}.dta")[
        LLAVES_HOGAR + ["ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07"]]
    miembros = leer_dta(z02, f"enaho01-{a.anio}-200.dta")[
        LLAVES_PERSONA + ["p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]]

    # 3. residentes habituales (definición INEI)
    res = ((miembros.p204 == 1) & (miembros.p205 == 2)) | ((miembros.p204 == 2) & (miembros.p206 == 1))
    personas = miembros[res].copy()

    # 4. unir personas con su hogar; m:1 falla si un hogar está repetido
    base = personas.merge(sumaria, on=LLAVES_HOGAR, how="left", validate="m:1", indicator=True)

    # 5. construir
    base["departamento"] = base.ubigeo.str[:2]
    base["urbano"] = base.estrato <= 5
    base["area"] = base.urbano.map({True: "Urbana", False: "Rural"})
    base["pobre"] = base.pobreza <= 2
    base["pobre_extremo"] = base.pobreza == 1
    base["sexo"] = base.p207.map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base.p208a
    base["grupo_edad"] = pd.cut(base.edad, [-1, 13, 17, 29, 44, 59, 200],
                                labels=["0-13", "14-17", "18-29", "30-44", "45-59", "60 y más"]).astype(str)

    # 6. validar
    p_sumaria = pct(sumaria.pobreza <= 2, sumaria.factor07 * sumaria.mieperho)
    p_personas = pct(base.pobre, base.facpob07)
    p_extrema = pct(sumaria.pobreza == 1, sumaria.factor07 * sumaria.mieperho)
    oficial = POBREZA_OFICIAL.get(a.anio)
    chequeos = [
        ("llaves de hogar únicas en la sumaria", not sumaria.duplicated(LLAVES_HOGAR).any()),
        ("llaves de persona únicas en miembros", not miembros.duplicated(LLAVES_PERSONA).any()),
        ("la unión no perdió ni duplicó filas", len(base) == len(personas)),
        ("toda persona encontró su hogar", bool((base._merge == "both").all())),
        ("ubigeo de 6 dígitos (ceros conservados)", bool(base.ubigeo.str.fullmatch(r"\d{6}").all())),
        ("25 departamentos", base.departamento.nunique() == 25),
        ("sin nulos en pobreza ni facpob07", bool(base[["pobreza", "facpob07"]].notna().all().all())),
    ]
    if oficial is not None:
        chequeos.append((f"pobreza (sumaria) a {TOL} pts de {oficial} %", abs(p_sumaria - oficial) < TOL))
        chequeos.append((f"pobreza (personas, facpob07) a {TOL} pts de {oficial} %", abs(p_personas - oficial) < TOL))
    if a.anio == 2024:
        o = OFICIAL_2024
        chequeos += [
            (f"hogares = {o['hogares']:,}", len(sumaria) == o["hogares"]),
            (f"residentes habituales = {o['residentes']:,}", len(personas) == o["residentes"]),
            (f"pobreza extrema a {TOL} pts de {o['extrema']} %", abs(p_extrema - o["extrema"]) < TOL),
        ]
    ok = all(c for _, c in chequeos)
    lineas = [
        f"ENAHO {a.anio} (código INEI {codigo})",
        f"hogares en la sumaria:     {len(sumaria):,}",
        f"filas del módulo 02:       {len(miembros):,}",
        f"residentes habituales:     {len(personas):,}",
        f"pobreza, sumaria (factor07 x mieperho): {p_sumaria:.2f} %",
        f"pobreza, personas (facpob07):           {p_personas:.2f} %",
        f"pobreza extrema (sumaria):              {p_extrema:.2f} %",
        f"pobreza oficial INEI:      {oficial if oficial is not None else 'sin dato'} %",
        "",
        *[f"[{'OK' if c else 'FALLA'}] {t}" for t, c in chequeos],
        "",
        "RESULTADO: VALIDADA" if ok else "RESULTADO: NO VALIDADA, no uses esta base",
    ]
    salidas.mkdir(exist_ok=True)
    (salidas / "validacion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    if not ok:
        raise SystemExit(1)

    # 7. guardar: personas (sexo, edad) y hogares (método oficial para área y departamento)
    cols = LLAVES_PERSONA + ["ubigeo", "departamento", "dominio", "estrato", "urbano", "area", "sexo", "edad",
                             "grupo_edad", "pobreza", "pobre", "pobre_extremo", "mieperho", "factor07", "facpob07"]
    base[cols].to_parquet(salidas / f"personas_{a.anio}.parquet", index=False)
    hogares = sumaria.assign(
        departamento=sumaria.ubigeo.str[:2], urbano=sumaria.estrato <= 5,
        area=(sumaria.estrato <= 5).map({True: "Urbana", False: "Rural"}),
        pobre=sumaria.pobreza <= 2, pobre_extremo=sumaria.pobreza == 1,
        peso=sumaria.factor07 * sumaria.mieperho)
    hogares.to_parquet(salidas / f"hogares_{a.anio}.parquet", index=False)
    print(f"\nguardado salidas/personas_{a.anio}.parquet y salidas/hogares_{a.anio}.parquet")


if __name__ == "__main__":
    main()
