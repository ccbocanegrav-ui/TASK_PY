"""Gráfico de barras horizontales de la pobreza ENAHO por área, sexo, edad o departamento."""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

COLOR, TINTA, SUAVE = "#C2410C", "#1F1F1F", "#6B6B6B"
DEPTOS = {"01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
          "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
          "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
          "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
          "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali"}
# corte -> (base, columna, texto del título, etiquetas). Área y departamento: sumaria con factor07 x mieperho
# (método oficial INEI). Sexo y edad solo existen por persona: facpob07.
CORTES = {"area": ("hogares", "area", "área de residencia", None),
          "departamento": ("hogares", "departamento", "departamento", DEPTOS),
          "sexo": ("personas", "sexo", "sexo", None),
          "edad": ("personas", "grupo_edad", "grupo de edad", None)}
MEDIDAS = {"pobreza": ("pobre", "Pobreza monetaria"), "extrema": ("pobre_extremo", "Pobreza extrema")}
REF_AREA_2024 = {"Urbana": 24.8, "Rural": 39.3}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--por", choices=CORTES, required=True)
    ap.add_argument("--medida", choices=MEDIDAS, default="pobreza")
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--salidas", default="salidas")
    ap.add_argument("--figuras", default="figuras")
    a = ap.parse_args()

    base, col, texto, etiquetas = CORTES[a.por]
    f = Path(a.salidas) / f"{base}_{a.anio}.parquet"
    if not f.exists():
        raise SystemExit(f"No existe {f}. Usa primero la skill limpiando-enaho.")
    df = pd.read_parquet(f)
    peso = "peso" if base == "hogares" else "facpob07"
    ind, nombre = MEDIDAS[a.medida]

    df["_n"] = df[ind] * df[peso]
    g = df.groupby(col, observed=True)[["_n", peso]].sum()
    serie = (g["_n"] / g[peso] * 100).astype(float).round(1)
    if etiquetas:
        serie.index = serie.index.map(etiquetas)
    if a.por == "edad":
        serie = serie.iloc[::-1]          # grupos en su orden natural, el primero arriba
    else:
        serie = serie.sort_values()       # de menor a mayor

    if a.por == "area" and a.anio == 2024 and a.medida == "pobreza":
        for k, v in REF_AREA_2024.items():
            if abs(serie[k] - v) > 0.1:
                raise SystemExit(f"{k}: {serie[k]} no coincide con la cifra oficial {v}")

    fig, ax = plt.subplots(figsize=(8, max(2.6, 0.32 * len(serie) + 1.4)))
    barras = ax.barh(serie.index.astype(str), serie.values, color=COLOR, height=0.68)
    ax.bar_label(barras, labels=[f"{v:.1f} %" for v in serie.values], padding=4, color=TINTA, fontsize=9)
    ax.set_xlim(0, serie.max() * 1.15)        # las barras empiezan en cero
    ax.xaxis.set_visible(False)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=9)
    ax.set_title(f"{nombre} por {texto}, {a.anio} (% de personas)", loc="left", color=TINTA, fontsize=12, pad=12)
    metodo = "factor07 × mieperho" if base == "hogares" else "facpob07"
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {a.anio}. Ponderado con {metodo}.", color=SUAVE, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    Path(a.figuras).mkdir(exist_ok=True)
    out = Path(a.figuras) / f"{a.medida}_{a.por}_{a.anio}.png"
    fig.savefig(out, dpi=200)
    print(serie.iloc[::-1].to_string())
    print(f"\nguardado {out}")


if __name__ == "__main__":
    main()
