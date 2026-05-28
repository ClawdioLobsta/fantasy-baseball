#!/usr/bin/env python3
"""
Fetch top minor‑league prospects using pybaseball's `top_prospects` helper.
The data is saved to `data/prospects.csv` for later merging with
hitting/pitching projections.
"""

from pathlib import Path
import pandas as pd

# Import the function from pybaseball (installed in our venv)
from pybaseball import top_prospects

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def fetch_prospects(team: str | None = None, player_type: str | None = None) -> pd.DataFrame:
    """Return a DataFrame of top prospects.

    Args:
        team: Optional team abbreviation (e.g., "NYY").
        player_type: "batters", "pitchers", or None for both.
    """
    df = top_prospects(teamName=team, playerType=player_type)
    # Standardize column names for later merging
    df = df.rename(columns={"Name": "player_name", "Team": "team"}