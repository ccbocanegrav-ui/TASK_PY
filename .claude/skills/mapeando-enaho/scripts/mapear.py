"""Create a weighted department-level ENAHO poverty choropleth."""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
DATA_PATH = ROOT / "salidas" / "personas_2024.parquet"
GEOJSON_PATH = ROOT / "datos" / "peru_departamental_simple.geojson"
EXPECTED_DEPARTMENTS = 25


def _department_code(values: pd.Series) -> pd.Series:
    codes = values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    return codes.str.zfill(2)


def department_rates(people: pd.DataFrame) -> pd.DataFrame:
    required = ["ubigeo", "pobre", "facpob07"]
    missing = [column for column in required if column not in people]
    if missing:
        raise KeyError(f"Faltan columnas de análisis: {', '.join(missing)}")
    frame = people.copy()
    frame["departamento"] = _department_code(frame["ubigeo"].astype("string").str[:2])
    frame["peso"] = pd.to_numeric(frame["facpob07"], errors="coerce")
    frame["pobre_num"] = frame["pobre"].astype(float)
    frame = frame.dropna(subset=["departamento", "peso", "pobre_num"])
    if frame.empty or (frame["peso"] <= 0).any():
        raise ValueError("No hay datos válidos o facpob07 contiene pesos no positivos.")
    frame["peso_pobre"] = frame["pobre_num"] * frame["peso"]
    grouped = frame.groupby("departamento")
    rates = (
        grouped["peso_pobre"].sum()
        .div(grouped["peso"].sum())
        .mul(100)
        .rename("pobreza_pct")
        .reset_index()
    )
    if rates["departamento"].nunique() != EXPECTED_DEPARTMENTS:
        raise ValueError(
            f"Se esperaban {EXPECTED_DEPARTMENTS} departamentos; "
            f"se encontraron {rates['departamento'].nunique()}."
        )
    return rates


def make_map(people: pd.DataFrame, geojson: Path, year: int, output: Path) -> Path:
    if not geojson.is_file():
        raise FileNotFoundError(f"No se encontró el GeoJSON: {geojson}")
    shapes = gpd.read_file(geojson)
    if "FIRST_IDDP" not in shapes.columns:
        raise KeyError("El GeoJSON debe incluir la columna FIRST_IDDP.")
    shapes = shapes.copy()
    shapes["departamento"] = _department_code(shapes["FIRST_IDDP"])
    if shapes["departamento"].duplicated().any():
        raise ValueError("FIRST_IDDP contiene códigos departamentales duplicados.")

    rates = department_rates(people)
    mapped = shapes.merge(rates, on="departamento", how="left", validate="1:1", indicator=True)
    missing = mapped.loc[mapped["_merge"] != "both", "departamento"].tolist()
    if missing or mapped["pobreza_pct"].isna().any():
        raise ValueError(f"Departamentos sin dato de pobreza: {', '.join(missing)}")
    if len(mapped) != EXPECTED_DEPARTMENTS:
        raise ValueError(
            f"El GeoJSON debe tener {EXPECTED_DEPARTMENTS} departamentos; encontrados: {len(mapped)}."
        )
    mapped = mapped.drop(columns="_merge")

    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 10))
    mapped.plot(
        column="pobreza_pct",
        cmap="Blues",
        vmin=0,
        vmax=max(50, float(mapped["pobreza_pct"].max())),
        linewidth=0.5,
        edgecolor="white",
        legend=True,
        legend_kwds={"label": "% de personas pobres", "shrink": 0.65},
        ax=ax,
    )
    ax.set_title(f"Pobreza monetaria por departamento — Perú, {year}", pad=14)
    ax.set_axis_off()
    fig.text(0.1, 0.06, f"Fuente: INEI, ENAHO {year}", ha="left")
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--entrada", type=Path, default=DATA_PATH)
    parser.add_argument("--geojson", type=Path, default=GEOJSON_PATH)
    parser.add_argument(
        "--salida",
        type=Path,
        default=ROOT / "mapas" / "pobreza_departamento.png",
    )
    args = parser.parse_args()
    if not args.entrada.is_file():
        raise FileNotFoundError(
            f"No existe {args.entrada}. Ejecuta primero la skill limpiando-enaho."
        )

    people = pd.read_parquet(args.entrada)
    rates = department_rates(people).sort_values("departamento")
    output = make_map(people, args.geojson, args.anio, args.salida)
    print(rates.to_string(index=False, formatters={"pobreza_pct": lambda value: f"{value:.1f}%"}))
    print(f"Mapa guardado en: {output}")


if __name__ == "__main__":
    main()
