"""Read/write helpers for the ``data/`` folders (Parquet, with date parsing)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from mastr_analysis.config import RAW_DIR

# Columns the public JSON API returns as ISO strings.
DATE_COLUMNS = (
    "DatumLetzteAktualisierung",
    "EinheitRegistrierungsdatum",
    "InbetriebnahmeDatum",
    "InbetriebnahmeDatumAmAktuellenOrt",
    "GeplantesInbetriebsnahmeDatum",
    "EndgueltigeStilllegungDatum",
    "EegInbetriebnahmeDatum",
    "EegAnlageRegistrierungsdatum",
    "GenehmigungRegistrierungsdatum",
    "KwkAnlageInbetriebnahmedatum",
)


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert known MaStR date columns to ``datetime64`` (in place, returns df)."""
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.tz_localize(None)
    return df


def save_parquet(df: pd.DataFrame, name: str, directory: Path = RAW_DIR) -> Path:
    """Save ``df`` as ``<directory>/<name>.parquet`` and return the path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.parquet"
    # Object columns with mixed types (e.g. ints and None) trip up pyarrow;
    # cast them to string to keep the write robust.
    out = df.copy()
    for col in out.columns[out.dtypes == "object"]:
        if out[col].map(type).nunique() > 1:
            out[col] = out[col].astype("string")
    out.to_parquet(path, index=False)
    return path


def load_parquet(name: str, directory: Path = RAW_DIR) -> pd.DataFrame:
    """Load ``<directory>/<name>.parquet`` with date columns parsed."""
    return parse_dates(pd.read_parquet(directory / f"{name}.parquet"))
