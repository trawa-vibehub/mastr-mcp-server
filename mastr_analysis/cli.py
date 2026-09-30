"""``mastr`` command line: pull MaStR extracts into ``data/raw`` as Parquet.

Examples::

    mastr fetch power_generation -f tech=storage -f bundesland=Berlin -o storage_berlin
    mastr fetch power_generation -f tech=solar -f "capacity>=1000" --max-pages 2 -o pv_sample
    mastr count power_generation -f tech=storage
    mastr count power_generation -f tech=storage -f status="In Betrieb"
"""

from __future__ import annotations

import logging
import re
from typing import Any

import click

from mastr_analysis import fetch as fetch_mod
from mastr_analysis.config import RAW_DIR
from mastr_analysis.io import save_parquet

DATASETS = ["power_generation", "power_consumption", "gas_production", "gas_consumption"]

# key may carry an operator suffix (capacity>, postcode:, eeg_key!?, ...)
_FILTER_RE = re.compile(r"^(?P<key>[A-Za-z_]+(?:!=|!%|!\?|[%:$><?!])?)=(?P<value>.*)$")


def _parse_filters(raw: tuple[str, ...]) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    for item in raw:
        m = _FILTER_RE.match(item)
        if not m:
            raise click.BadParameter(f"expected KEY=VALUE, got {item!r}", param_hint="--filter")
        filters[m.group("key")] = _coerce(m.group("value"))
    return filters


def _coerce(value: str) -> Any:
    """'true'/'false' -> bool, plain numbers -> int/float, everything else stays a string.

    Numbers with leading zeros (postcodes like 01067) are kept as strings.
    """
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    if re.fullmatch(r"-?(0|[1-9]\d*)(\.\d+)?", value):
        return float(value) if "." in value else int(value)
    return value


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def cli(verbose: bool) -> None:
    """Fetch and inspect Marktstammdatenregister data."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


_filter_option = click.option(
    "-f",
    "--filter",
    "filters",
    multiple=True,
    help="Filter as KEY=VALUE; KEY may end with an operator (capacity>=1000, postcode:=10). "
    "Repeatable. Same keys as the MCP tools.",
)


@cli.command()
@click.argument("dataset", type=click.Choice(DATASETS))
@_filter_option
@click.option("-o", "--output", required=True, help="Output name (without .parquet) in data/raw.")
@click.option("--page-size", default=fetch_mod.MAX_PAGE_SIZE, show_default=True)
@click.option("--max-pages", type=int, default=None, help="Limit pages (for sampling).")
def fetch(
    dataset: str, filters: tuple[str, ...], output: str, page_size: int, max_pages: int | None
) -> None:
    """Download all rows matching the filters to data/raw/<output>.parquet."""
    flt = _parse_filters(filters)
    click.echo(f"Fetching {dataset} with filters {flt}")
    df = fetch_mod.fetch_all(
        fetch_mod._search_fns()[dataset], flt, page_size=page_size, max_pages=max_pages
    )
    path = save_parquet(df, output, RAW_DIR)
    click.echo(f"Wrote {len(df):,} rows x {df.shape[1]} cols -> {path}")


@cli.command()
@click.argument("dataset", type=click.Choice(DATASETS))
@_filter_option
def count(dataset: str, filters: tuple[str, ...]) -> None:
    """Print the number of rows matching the filters (no download)."""
    flt = _parse_filters(filters)
    click.echo(f"{fetch_mod.count(dataset, flt):,}")


if __name__ == "__main__":
    cli()
