# data/

Nothing in here is committed except the `.gitkeep` markers — every file is
reproducible from the public MaStR API via `mastr fetch ...`,
`scripts/build_datasets.py` or a notebook.

| Folder | Contents |
|---|---|
| `raw/` | Untouched API extracts as Parquet, one file per query (`batteries_berlin.parquet`, ...). Written by `mastr_analysis.io.save_parquet`. |
| `interim/` | Cleaned / joined intermediate tables. |
| `processed/` | Final analysis tables that feed figures and reports. |

Naming: `<topic>_<scope>.parquet`, lowercase, underscores (e.g. `pv_bayern.parquet`,
`chp_gas_nrw.parquet`).

The public API returns a fixed column set per dataset; date columns are ISO
strings and are parsed on load by `mastr_analysis.io.load_parquet`.
