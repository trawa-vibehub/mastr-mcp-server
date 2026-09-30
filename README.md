# mastr-mcp

Pull and analyze data from the German **Marktstammdatenregister** (MaStR) — batteries, PV and CHP.

Two layers live in this repo:

1. **`mastr-mcp-server/`** — a vendored copy of [UliRCS/mastr-mcp-server](https://github.com/UliRCS/mastr-mcp-server) (MIT). It exposes MaStR as MCP tools for Cursor / Claude and, more importantly here, contains a Python client for the public MaStR JSON API with filter/dropdown handling. See [`mastr-mcp-server/UPSTREAM.md`](mastr-mcp-server/UPSTREAM.md) for the pinned commit and how to update.
2. **`mastr_analysis/`** — our analysis layer: bulk paginated fetching into pandas, Parquet caching under `data/`, a small `mastr` CLI, and notebooks.

## Layout

```
mastr-mcp/
├── mastr-mcp-server/        # vendored upstream MCP server (do not edit; update via UPSTREAM.md)
├── mastr_analysis/          # reusable analysis code (import this from notebooks)
│   ├── config.py            # paths, .env loading, tech constants
│   ├── fetch.py             # fetch_power_generation(...) etc. -> DataFrame (auto-pagination)
│   ├── io.py                # save_parquet / load_parquet with date parsing
│   ├── cli.py               # `mastr fetch` / `mastr count`
│   └── mcp_server.py        # launches the MCP server with the root .env
├── notebooks/               # NN_topic.ipynb — exploration; keep logic in mastr_analysis/
├── scripts/                 # reproducible dataset builds (build_datasets.py)
├── data/                    # raw/ interim/ processed/ — gitignored, see data/README.md
├── reports/figures/         # exported plots (gitignored)
├── tests/                   # unit tests for mastr_analysis (no network)
├── .cursor/mcp.json         # registers the MaStR MCP server in Cursor
└── pyproject.toml           # uv workspace root (mastr-mcp-server is a member)
```

## Setup

```bash
uv sync                 # creates .venv with analysis deps + editable mastr-mcp-server
cp .env.example .env    # optional: MASTR_USER / MASTR_TOKEN for the SOAP tools
uv run pytest
```

Python ≥ 3.12, [uv](https://docs.astral.sh/uv/) ≥ 0.8. No credentials are needed for anything in `mastr_analysis` — the public JSON API is open. Credentials only unlock the 14 SOAP MCP tools (unit details, delta sync, catalogs).

## Fetching data

Filters use exactly the same keys and operator suffixes as the MCP tools
(`tech`, `bundesland`, `postcode`, `capacity>`, `status`, `postcode:` = starts-with, `eeg_key!?` = not null, ...).
See `mastr-mcp-server/README.md` for the full key list per dataset.

CLI:

```bash
uv run mastr count power_generation -f tech=storage -f bundesland=Berlin
uv run mastr fetch power_generation -f tech=storage -f bundesland=Berlin -o batteries_berlin
uv run mastr fetch power_generation -f tech=solar -f "capacity>=1000" --max-pages 2 -o pv_sample
uv run scripts/build_datasets.py --bundesland Bayern --min-capacity-kw 100
```

Python:

```python
from mastr_analysis import fetch_power_generation, save_parquet, load_parquet

df = fetch_power_generation({"tech": "storage", "bundesland": "Berlin", "capacity>": 100})
save_parquet(df, "batteries_berlin_gt100kw")
df = load_parquet("batteries_berlin_gt100kw")   # dates parsed
```

Datasets: `power_generation` (PV, wind, storage, biomass, gas ... — CHP units carry `KwkAnlage*` columns), `power_consumption`, `gas_production`, `gas_consumption`.

Practical limits: the portal serves 5000 rows per request at ~15–20 s per page for wide result sets. Berlin storage (~31k rows) takes about 2 minutes; nationwide PV is several million rows — always scope by Bundesland / capacity, or sample with `--max-pages`.

## Notebooks

```bash
uv run jupyter lab
```

Start from `notebooks/01_battery_storage_overview.ipynb` (fetch → cache → size classes → commissioning per year → top operators). Number new notebooks `NN_topic.ipynb`; move anything reused twice into `mastr_analysis/`.

## MCP server in Cursor

`.cursor/mcp.json` registers the server as `mastr`; it runs `uv run python -m mastr_analysis.mcp_server` from the workspace root, so the root `.env` is picked up. Reload MCP servers in Cursor settings after `uv sync`. Without credentials 7 public search tools are available; with `MASTR_USER`/`MASTR_TOKEN` 21 tools.

If `${workspaceFolder}` does not resolve in your Cursor version, replace it with the absolute repo path.

## Development

```bash
uv run pytest            # unit tests (no network)
uv run ruff check .      # lint (vendored server and notebooks excluded)
uv run ruff format mastr_analysis scripts tests
```
