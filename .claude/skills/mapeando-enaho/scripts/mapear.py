"""Mapa coroplético de pobreza por departamento, unido por código (nunca por nombre)."""
import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

MEDIDAS = {"pobreza": ("pobre", "Pobreza monetaria"), "extrema": ("pobre_extremo", "Pobreza extrema")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--medida", choices=MEDIDAS, default="pobreza")
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--salidas", default="salidas")
    ap.add_argument("--geojson", default="datos/peru_departamental_simple.geojson")
    ap.add_argument("--referencia", default="referencias/pobreza_departamento_2024.csv")
    ap.add_argument("--mapas", default="mapas")
    a = ap.parse_args()

    f = Path(a.salidas) / f"hogares_{a.anio}.parquet"
    if not f.exists():
        raise SystemExit(f"No existe {f}. Usa primero la skill limpiando-enaho.")
    if not Path(a.geojson).exists():
        raise SystemExit(f"No existe {a.geojson}. Bájalo (ver README).")
    ind, nombre = MEDIDAS[a.medida]

    # sumaria ponderada con factor07 x mieperho (columna peso)
    h = pd.read_parquet(f)
    h["_n"] = h[ind] * h["peso"]
    g = h.groupby("departamento")[["_n", "peso"]].sum()
    tabla = (g["_n"] / g["peso"] * 100).astype(float).round(1).rename("pct").reset_index()

    # unir por código de 2 dígitos como texto
    geo = gpd.read_file(a.geojson)
    geo["FIRST_IDDP"] = geo["FIRST_IDDP"].astype(str).str.zfill(2)
    mapa = geo.merge(tabla, left_on="FIRST_IDDP", right_on="departamento", how="left", validate="1:1")

    sin_dato = mapa.loc[mapa.pct.isna(), "NOMBDEP"].tolist()
    if len(mapa) != 25 or sin_dato:
        raise SystemExit(f"Unión fallida: {len(mapa)} polígonos, sin dato: {sin_dato}")
    if not {"07", "15"} <= set(mapa.FIRST_IDDP):
        raise SystemExit("Lima (15) y Callao (07) deben ir separados")

    if a.anio == 2024 and a.medida == "pobreza":
        ref = pd.read_csv(a.referencia, dtype={"ccdd": str}).set_index("ccdd").pobreza_pct
        dif = {c: (v, ref[c]) for c, v in zip(tabla.departamento, tabla.pct) if abs(v - ref[c]) > 0.05}
        if dif:
            raise SystemExit(f"No replica la referencia 2024 (calculado, referencia): {dif}")

    fig, ax = plt.subplots(figsize=(7.5, 9.5))
    mapa.plot(column="pct", ax=ax, cmap="Oranges", vmin=0, vmax=mapa.pct.max(), edgecolor="white",
              linewidth=0.6, legend=True, legend_kwds={"label": f"{nombre} (% de personas)", "shrink": 0.5})
    ax.set_axis_off()
    ax.set_title(f"{nombre} por departamento, {a.anio}", fontsize=14)
    fig.text(0.02, 0.02, f"Fuente: INEI, ENAHO {a.anio} (sumaria), ponderado con factor07 × mieperho",
             color="#6B6B6B", fontsize=8)

    Path(a.mapas).mkdir(exist_ok=True)
    nom = "pobreza_departamento" if a.medida == "pobreza" else f"{a.medida}_departamento"
    fig.savefig(Path(a.mapas) / f"{nom}.png", dpi=200, bbox_inches="tight")
    mapa[["FIRST_IDDP", "NOMBDEP", "pct"]].to_csv(Path(a.mapas) / f"{nom}.csv", index=False)
    top, low = mapa.loc[mapa.pct.idxmax()], mapa.loc[mapa.pct.idxmin()]
    print(f"25 departamentos con dato. Mayor: {top.NOMBDEP} {top.pct} %. Menor: {low.NOMBDEP} {low.pct} %.")
    print(f"guardado {Path(a.mapas) / (nom + '.png')}")


if __name__ == "__main__":
    main()
