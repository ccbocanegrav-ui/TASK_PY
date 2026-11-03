"""Create a weighted ENAHO poverty bar chart."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[4]
DATA_PATH = ROOT / "salidas" / "personas_2024.parquet"


def _group_values(frame: pd.DataFrame, dimension: str) -> pd.Series:
    if dimension == "area":
        if "urbano" not in frame:
            raise KeyError("La base no contiene la variable urbano.")
        return frame["urbano"].map({True: "Urbana", False: "Rural"})
    if dimension == "sexo":
        if "p207" not in frame:
            raise KeyError("La base no contiene p207, necesaria para el corte por sexo.")
        sex = pd.to_numeric(frame["p207"], errors="coerce")
        return sex.map({1: "Hombres", 2: "Mujeres"})
    if dimension == "edad":
        if "p208a" not in frame:
            raise KeyError("La base no contiene p208a, necesaria para el corte por edad.")
        age = pd.to_numeric(frame["p208a"], errors="coerce")
        return pd.cut(
            age,
            bins=[-1, 17, 29, 44, 59, float("inf")],
            labels=["0–17", "18–29", "30–44", "45–59", "60+"],
        )
    raise ValueError(f"Corte desconocido: {dimension}")


def weighted_rates(frame: pd.DataFrame, dimension: str) -> pd.Series:
    required = ["pobre", "facpob07"]
    missing = [column for column in required if column not in frame]
    if missing:
        raise KeyError(f"Faltan columnas de análisis: {', '.join(missing)}")

    working = frame.copy()
    working["grupo"] = _group_values(working, dimension)
    working["peso"] = pd.to_numeric(working["facpob07"], errors="coerce")
    working["pobre_num"] = working["pobre"].astype(float)
    working = working.dropna(subset=["grupo", "peso", "pobre_num"])
    if working.empty or (working["peso"] <= 0).any():
        raise ValueError("No hay datos válidos o facpob07 contiene pesos no positivos.")

    working["peso_pobre"] = working["pobre_num"] * working["peso"]
    grouped = working.groupby("grupo", observed=False)
    rates = grouped["peso_pobre"].sum() / grouped["peso"].sum() * 100
    rates = rates.dropna().sort_values(ascending=False)
    if rates.empty:
        raise ValueError(f"No se pudo calcular pobreza por {dimension}.")
    return rates


def make_chart(rates: pd.Series, dimension: str, year: int, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"pobreza_{dimension}_{year}.png"
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(rates.index.astype(str), rates.values, color="#4472C4")
    ax.bar_label(bars, labels=[f"{value:.1f}%" for value in rates.values], padding=3)
    ax.set_ylim(0, max(100, float(rates.max()) * 1.15))
    ax.set_ylabel("% de personas")
    ax.set_title(f"Pobreza por {dimension} — Perú, {year}")
    ax.legend(
        handles=[Patch(color="#4472C4", label="% de personas")],
        loc="upper right",
        frameon=False,
    )
    ax.text(
        0,
        -0.18,
        f"Fuente: INEI, ENAHO {year}",
        transform=ax.transAxes,
        ha="left",
        va="top",
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--por", choices=["area", "sexo", "edad"], default="area")
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--entrada", type=Path, default=DATA_PATH)
    parser.add_argument("--salida", type=Path, default=ROOT / "figuras")
    args = parser.parse_args()
    if not args.entrada.is_file():
        raise FileNotFoundError(
            f"No existe {args.entrada}. Ejecuta primero la skill limpiando-enaho."
        )

    rates = weighted_rates(pd.read_parquet(args.entrada), args.por)
    output = make_chart(rates, args.por, args.anio, args.salida)
    print(rates.to_string(float_format=lambda value: f"{value:.1f}%"))
    print(f"Figura guardada en: {output}")


if __name__ == "__main__":
    main()
