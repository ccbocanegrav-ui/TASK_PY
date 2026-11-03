"""Build a validated person-level ENAHO 2024 parquet file."""

from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT / "datos"
OUTPUT_DIR = ROOT / "salidas"
EXPECTED_PEOPLE = 108_664
EXPECTED_POVERTY_PERCENT = 27.6
POVERTY_TOLERANCE_POINTS = 0.1
HOUSEHOLD_KEYS = ["conglome", "vivienda", "hogar"]
PERSON_KEYS = [*HOUSEHOLD_KEYS, "codperso"]


def _find_module(module_number: str) -> Path:
    matches = sorted(DATA_DIR.glob(f"966-Modulo{module_number}*"))
    if not matches:
        raise FileNotFoundError(
            f"No se encontró el módulo {module_number} en {DATA_DIR}. "
            "Descarga el ZIP de microdatos del INEI."
        )
    preferred = [path for path in matches if path.is_file() and path.suffix.lower() == ".zip"]
    if preferred:
        return preferred[0]
    if len(matches) > 1:
        raise ValueError(
            f"Hay varias entradas para el módulo {module_number}: "
            + ", ".join(str(path) for path in matches)
        )
    return matches[0]


def _read_stata(path: Path) -> pd.DataFrame:
    if path.is_dir():
        files = sorted(path.rglob("*.dta"))
        if len(files) != 1:
            raise ValueError(f"{path} debe contener exactamente un archivo .dta; encontrados: {len(files)}")
        path = files[0]

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            files = [name for name in archive.namelist() if name.lower().endswith(".dta")]
            if len(files) != 1:
                raise ValueError(f"{path.name} debe contener exactamente un .dta; encontrados: {len(files)}")
            with archive.open(files[0]) as source:
                return pd.read_stata(io.BytesIO(source.read()), convert_categoricals=False)

    if path.suffix.lower() != ".dta":
        raise ValueError(f"Formato no compatible: {path}")
    return pd.read_stata(path, convert_categoricals=False)


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).lower() for column in frame.columns]
    return frame


def _key_as_text(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    return values.str.replace(r"\.0$", "", regex=True)


def _require_columns(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise KeyError(f"Faltan columnas requeridas en {label}: {', '.join(missing)}")


def _weighted_poverty_percent(frame: pd.DataFrame) -> float:
    weights = pd.to_numeric(frame["facpob07"], errors="coerce")
    poor = frame["pobre"].astype(bool)
    if weights.isna().any() or (weights <= 0).any():
        raise ValueError("facpob07 contiene valores nulos o no positivos.")
    return float(weights[poor].sum() / weights.sum() * 100)


def clean(year: int) -> tuple[pd.DataFrame, str]:
    if year != 2024:
        raise ValueError("Este proyecto contiene únicamente los datos ENAHO 2024 (código 966).")

    household = _normalize_columns(_read_stata(_find_module("34")))
    people = _normalize_columns(_read_stata(_find_module("02")))
    _require_columns(household, [*HOUSEHOLD_KEYS, "pobreza", "ubigeo", "estrato"], "módulo 34")
    _require_columns(
        people,
        [*PERSON_KEYS, "p204", "p205", "p206", "facpob07"],
        "módulo 02",
    )

    for column in HOUSEHOLD_KEYS:
        household[column] = _key_as_text(household[column])
    for column in PERSON_KEYS:
        people[column] = _key_as_text(people[column])

    resident = (
        (pd.to_numeric(people["p204"], errors="coerce") == 1)
        & (pd.to_numeric(people["p205"], errors="coerce") == 2)
    ) | (
        (pd.to_numeric(people["p204"], errors="coerce") == 2)
        & (pd.to_numeric(people["p206"], errors="coerce") == 1)
    )
    residents = people.loc[resident].copy()
    people_before_merge = len(residents)

    if household[HOUSEHOLD_KEYS].isna().any().any():
        raise ValueError("Las llaves del módulo 34 contienen valores nulos.")
    if household.duplicated(HOUSEHOLD_KEYS).any():
        raise ValueError("Las llaves del módulo 34 no son únicas.")
    if residents[PERSON_KEYS].isna().any().any():
        raise ValueError("Las llaves de persona contienen valores nulos.")
    if residents.duplicated(PERSON_KEYS).any():
        raise ValueError("La llave de persona no es única después del filtro.")

    merged = residents.merge(
        household,
        on=HOUSEHOLD_KEYS,
        how="left",
        validate="m:1",
        indicator=True,
        suffixes=("", "_hogar"),
    )
    unmatched = int((merged["_merge"] != "both").sum())
    merged = merged.drop(columns="_merge")

    for column in ("pobreza", "ubigeo", "estrato"):
        household_column = f"{column}_hogar"
        if column not in merged and household_column in merged:
            merged[column] = merged[household_column]
    _require_columns(merged, ["pobreza", "ubigeo", "estrato"], "base unida")

    merged["pobreza"] = pd.to_numeric(merged["pobreza"], errors="coerce")
    merged["estrato"] = pd.to_numeric(merged["estrato"], errors="coerce")
    merged["facpob07"] = pd.to_numeric(merged["facpob07"], errors="coerce")
    merged["ubigeo"] = (
        _key_as_text(merged["ubigeo"]).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    )
    if merged[["pobreza", "estrato", "facpob07", "ubigeo"]].isna().any().any():
        raise ValueError("Hay valores faltantes en variables necesarias para el análisis.")
    if not merged["pobreza"].isin([1, 2, 3]).all():
        raise ValueError("La variable pobreza contiene códigos fuera de 1, 2 y 3.")
    if not merged["estrato"].between(1, 8).all():
        raise ValueError("La variable estrato contiene códigos inesperados.")

    merged["departamento"] = merged["ubigeo"].str[:2]
    merged["urbano"] = merged["estrato"] <= 5
    merged["pobre"] = merged["pobreza"] <= 2
    poverty_percent = _weighted_poverty_percent(merged)

    checks = [
        ("residentes_habituales", len(merged) == EXPECTED_PEOPLE, f"{len(merged)} (esperado {EXPECTED_PEOPLE})"),
        ("union_sin_perdidas", unmatched == 0, f"{unmatched} hogares sin correspondencia"),
        ("filas_sin_cambios_en_union", len(merged) == people_before_merge, f"{len(merged)} filas"),
        ("llave_persona_unica", not merged.duplicated(PERSON_KEYS).any(), "revisada"),
        (
            "pobreza_nacional_pct",
            abs(poverty_percent - EXPECTED_POVERTY_PERCENT) <= POVERTY_TOLERANCE_POINTS,
            f"{poverty_percent:.2f}% (referencia {EXPECTED_POVERTY_PERCENT:.1f}%; tolerancia {POVERTY_TOLERANCE_POINTS:.1f} pp)",
        ),
    ]
    passed = all(check[1] for check in checks)
    report_lines = [
        "Validación ENAHO 2024",
        f"Estado: {'OK' if passed else 'ERROR'}",
        f"Filas de personas tras filtro: {len(merged)}",
        f"Residentes habituales: {len(merged)}",
        f"Hogares sin correspondencia: {unmatched}",
        f"Pobreza nacional ponderada con facpob07: {poverty_percent:.2f}%",
        "",
        "Controles:",
        *[
            f"{'OK' if check_passed else 'ERROR'} {name}: {detail}"
            for name, check_passed, detail in checks
        ],
    ]
    report = "\n".join(report_lines) + "\n"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "validacion.txt").write_text(report, encoding="utf-8")

    assert len(merged) == people_before_merge, "La unión cambió el número de filas."
    assert unmatched == 0, f"{unmatched} personas no encontraron hogar."
    assert not merged.duplicated(PERSON_KEYS).any(), "La llave de persona no es única."
    assert len(merged) == EXPECTED_PEOPLE, f"Se esperaban {EXPECTED_PEOPLE} personas."
    assert abs(poverty_percent - EXPECTED_POVERTY_PERCENT) <= POVERTY_TOLERANCE_POINTS, (
        f"La pobreza calculada ({poverty_percent:.2f}%) no coincide con 27.6%."
    )
    return merged, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anio", type=int, default=2024, help="Año ENAHO; este proyecto admite 2024.")
    args = parser.parse_args()

    data, report = clean(args.anio)
    output = OUTPUT_DIR / f"personas_{args.anio}.parquet"
    data.to_parquet(output, index=False)
    print(report, end="")
    print(f"Base guardada en: {output}")


if __name__ == "__main__":
    main()
