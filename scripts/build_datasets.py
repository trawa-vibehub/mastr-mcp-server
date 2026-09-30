"""Build the standard raw extracts for this repo: batteries, PV and CHP units.

Run with::

    uv run scripts/build_datasets.py --bundesland Berlin
    uv run scripts/build_datasets.py --bundesland Bayern --min-capacity-kw 100

Output goes to ``data/raw/<name>_<bundesland>.parquet``. Nationwide PV is
several million rows — always scope by Bundesland or capacity first, or use
``--max-pages`` for a sample.
"""

from __future__ import annotations

import logging

import click

from mastr_analysis import fetch_power_generation, save_parquet
from mastr_analysis.config import TECH_BIOMASS, TECH_NATURAL_GAS, TECH_SOLAR, TECH_STORAGE


@click.command()
@click.option("--bundesland", default="Berlin", show_default=True)
@click.option(
    "--min-capacity-kw", default=30, show_default=True, help="Bruttoleistung floor in kW."
)
@click.option("--max-pages", type=int, default=None, help="Limit pages per dataset (sampling).")
def main(bundesland: str, min_capacity_kw: int, max_pages: int | None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    suffix = bundesland.lower().replace(" ", "_").replace("-", "_")
    common = {"bundesland": bundesland, "capacity>": min_capacity_kw}

    datasets = {
        f"batteries_{suffix}": {"tech": TECH_STORAGE, **common},
        f"pv_{suffix}": {"tech": TECH_SOLAR, **common},
        # CHP (KWK) is not an energy carrier in MaStR; the KwkAnlage* columns are
        # populated on the generation unit. Biomass and natural gas cover the bulk.
        f"chp_biomass_{suffix}": {"tech": TECH_BIOMASS, **common},
        f"chp_gas_{suffix}": {"tech": TECH_NATURAL_GAS, **common},
    }

    for name, filters in datasets.items():
        df = fetch_power_generation(filters, max_pages=max_pages)
        if name.startswith("chp_") and "KwkAnlageMastrNummer" in df.columns:
            df = df[df["KwkAnlageMastrNummer"].notna()]
        path = save_parquet(df, name)
        click.echo(f"{name}: {len(df):,} rows -> {path}")


if __name__ == "__main__":
    main()
