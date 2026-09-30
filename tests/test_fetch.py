"""Unit tests for the pagination helper (no network)."""

from __future__ import annotations

import pandas as pd
import pytest

from mastr_analysis.cli import _parse_filters
from mastr_analysis.fetch import fetch_all


def _fake_search(total: int, page_size_seen: list[int]):
    def search(filters, page=1, page_size=100):
        page_size_seen.append(page_size)
        start = (page - 1) * page_size
        rows = [
            {"Id": i, "Bruttoleistung": float(i)}
            for i in range(start, min(start + page_size, total))
        ]
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "count": len(rows),
            "results": rows,
        }

    search.__name__ = "fake_search"
    return search


def test_fetch_all_pages_through_everything():
    seen: list[int] = []
    df = fetch_all(
        _fake_search(23, seen), {"tech": "storage"}, page_size=10, sleep_s=0, show_progress=False
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 23
    assert df["Id"].tolist() == list(range(23))
    assert seen == [10, 10, 10]
    assert df.attrs["total"] == 23
    assert df.attrs["filters"] == {"tech": "storage"}


def test_fetch_all_respects_max_pages():
    seen: list[int] = []
    df = fetch_all(
        _fake_search(50, seen), {}, page_size=10, max_pages=2, sleep_s=0, show_progress=False
    )
    assert len(df) == 20
    assert len(seen) == 2


def test_fetch_all_raises_on_error():
    def failing(filters, page=1, page_size=100):
        return {"error": "boom", "url": "x"}

    with pytest.raises(RuntimeError, match="boom"):
        fetch_all(failing, {}, show_progress=False)


def test_parse_filters_handles_operators_and_types():
    assert _parse_filters(
        ("tech=storage", "capacity>=1000", "postcode:=10", "dso_large=true", "eeg_key!?=")
    ) == {
        "tech": "storage",
        "capacity>": 1000,
        "postcode:": 10,
        "dso_large": True,
        "eeg_key!?": "",
    }
    assert _parse_filters(("status=In Betrieb", "postcode=01067")) == {
        "status": "In Betrieb",
        "postcode": "01067",
    }
