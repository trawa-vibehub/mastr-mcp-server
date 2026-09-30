"""Paths and settings for the analysis project.

Loads the repo-root ``.env`` (if present) so that ``MASTR_USER`` /
``MASTR_TOKEN`` are visible to the vendored ``mastr_mcp`` package, which
otherwise only looks for a ``.env`` inside ``mastr-mcp-server/``.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(REPO_ROOT / ".env", override=False)

DATA_DIR = Path(os.environ.get("MASTR_DATA_DIR", REPO_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURES_DIR = REPO_ROOT / "reports" / "figures"

# Public JSON API: 5000 is the hard maximum accepted by the MaStR portal.
MAX_PAGE_SIZE = 5000

# Energy-carrier shortcuts most relevant to this repo (see mastr_mcp.config
# for the full list of 20 carriers and their German aliases).
TECH_STORAGE = "storage"  # Stromspeicher (batteries, pumped hydro, ...)
TECH_SOLAR = "solar"  # PV
TECH_BIOMASS = "biomass"  # most CHP in MaStR is biomass- or gas-fired
TECH_NATURAL_GAS = "natural_gas"

# Battery-technology dropdown id used by MaStR (column "Batterietechnologie").
BATTERY_TECH_LITHIUM = 727
