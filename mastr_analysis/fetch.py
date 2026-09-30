"""Bulk fetching from the public MaStR JSON API into pandas DataFrames.

The vendored ``mastr_mcp`` package already knows the endpoints, the filter
column names, the operator suffixes (``capacity>``, ``postcode:`` ...) and the
dropdown label → id translation. These helpers only add pagination and
DataFrame conversion on top of it, so the same filter dicts you would pass to
the MCP tools work here unchanged.

Example::

    from mastr_analysis import fetch_power_generation

    df = fetch_power_generation({"tech": "storage", "bundesland": "Berlin", "capacity>": 100})
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import pandas as pd
from tqdm.auto import tqdm

from mastr_analysis.config import MAX_PAGE_SIZE

logger = logging.getLogger(__name__)

SearchFn = Callable[..., dict]


def _search_fns() -> dict[str, SearchFn]:
    # Imported lazily: importing mastr_mcp instantiates the FastMCP server and
    # loads the dropdown JSON files, which we don't want at module import.
    from mastr_mcp import tools_public as tp

    return {
        "power_generation": tp.search_power_generation_public,
        "power_consumption": tp.search_power_consumption_public,
        "gas_production": tp.search_gas_production_public,
        "gas_consumption": tp.search_gas_consumption_public,
    }


def fetch_all(
    search_fn: SearchFn,
    filters: dict[str, Any],
    *,
    page_size: int = MAX_PAGE_SIZE,
    max_pages: int | None = None,
    sleep_s: float = 0.2,
    show_progress: bool = True,
    **extra: Any,
) -> pd.DataFrame:
    """Page through a ``search_*_public`` function and return all rows as a DataFrame.

    Parameters
    ----------
    search_fn:
        One of the ``mastr_mcp.tools_public.search_*_public`` callables.
    filters:
        Filter dict in the same format the MCP tools accept.
    page_size:
        Rows per request; the portal caps this at 5000.
    max_pages:
        Stop after this many pages (useful for sampling). ``None`` = all.
    sleep_s:
        Pause between requests to be polite to the portal.
    extra:
        Passed through to ``search_fn`` (e.g. ``connection_type`` for grid
        connection searches).
    """
    page_size = min(page_size, MAX_PAGE_SIZE)
    first = search_fn(**extra, filters=filters, page=1, page_size=page_size)
    if "error" in first:
        raise RuntimeError(f"MaStR request failed: {first['error']}")
    for warning in first.get("warnings", []):
        logger.warning(warning)

    total = int(first["total"])
    rows: list[dict] = list(first["results"])
    n_pages = max(1, -(-total // page_size))  # ceil division
    if max_pages is not None:
        n_pages = min(n_pages, max_pages)

    pages = range(2, n_pages + 1)
    if show_progress and n_pages > 1:
        pages = tqdm(pages, desc=f"{search_fn.__name__} ({total} rows)", unit="page")

    for page in pages:
        time.sleep(sleep_s)
        result = search_fn(**extra, filters=filters, page=page, page_size=page_size)
        if "error" in result:
            raise RuntimeError(f"MaStR request failed on page {page}: {result['error']}")
        rows.extend(result["results"])

    df = pd.DataFrame(rows)
    df.attrs["total"] = total
    df.attrs["filters"] = dict(filters)
    logger.info("Fetched %d of %d rows", len(df), total)
    return df


def fetch_power_generation(filters: dict[str, Any], **kwargs: Any) -> pd.DataFrame:
    """Power generation units (Stromerzeugung): PV, wind, storage, biomass, gas, ..."""
    return fetch_all(_search_fns()["power_generation"], filters, **kwargs)


def fetch_power_consumption(filters: dict[str, Any], **kwargs: Any) -> pd.DataFrame:
    """Power consumption units (Stromverbrauch)."""
    return fetch_all(_search_fns()["power_consumption"], filters, **kwargs)


def fetch_gas_production(filters: dict[str, Any], **kwargs: Any) -> pd.DataFrame:
    """Gas production / storage units (Gaserzeugung)."""
    return fetch_all(_search_fns()["gas_production"], filters, **kwargs)


def fetch_gas_consumption(filters: dict[str, Any], **kwargs: Any) -> pd.DataFrame:
    """Gas consumption units (Gasverbrauch)."""
    return fetch_all(_search_fns()["gas_consumption"], filters, **kwargs)


def count(search_fn_name: str, filters: dict[str, Any]) -> int:
    """Return the total number of matching rows without downloading them."""
    result = _search_fns()[search_fn_name](filters=filters, page=1, page_size=1)
    if "error" in result:
        raise RuntimeError(f"MaStR request failed: {result['error']}")
    return int(result["total"])
