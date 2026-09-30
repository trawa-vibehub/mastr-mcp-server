"""Reusable analysis code for Marktstammdatenregister (MaStR) data.

Import order matters: ``config`` loads the repo-root ``.env`` before the
vendored ``mastr_mcp`` package reads ``MASTR_USER`` / ``MASTR_TOKEN``.
"""

from mastr_analysis import config  # noqa: F401  — loads .env first
from mastr_analysis.fetch import (
    fetch_all,
    fetch_gas_consumption,
    fetch_gas_production,
    fetch_power_consumption,
    fetch_power_generation,
)
from mastr_analysis.io import load_parquet, save_parquet

__all__ = [
    "fetch_all",
    "fetch_gas_consumption",
    "fetch_gas_production",
    "fetch_power_consumption",
    "fetch_power_generation",
    "load_parquet",
    "save_parquet",
]
