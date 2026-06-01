#!/usr/bin/env python3
"""
Fetch current baseball stats using pybaseball and save to CSV.
"""

import pandas as pd
from pybaseball import batting_stats_bref, pitching_stats_bref
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def fetch_hitter_stats(season: int = 2025) -> pd.DataFrame:
    """Fetch batting stats for all hitters."""
    df = batting_stats_bref(season)
    # Keep relevant columns for fantasy scoring
    cols = ["Name", "Tm", "R", "HR", "RBI", "SB", "OBP"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        print(f"Warning: Missing columns: {missing}")
    return df[[c for c in cols if c in df.columns]].dropna()


def fetch_pitcher_stats(season: int = 2025) -> pd.DataFrame:
    """Fetch pitching stats for all pitchers."""
    df = pitching_stats_bref(season)
    # Keep relevant columns for fantasy scoring (add missing ones as zeros)
    cols = ["Name", "Tm", "QS", "ERA", "WHIP", "Ks", "SV", "HLD"]
    for col in cols:
        if col not in df.columns:
            df[col] = 0  # fill missing stats with 0
    return df[cols]


def main() -> None:
    print("Fetching 2025 hitter stats...")
    hitters = fetch_hitter_stats()
    hitters.to_csv(DATA_DIR / "hitters.csv", index=False)
    print(f"Saved {len(hitters)} hitters to data/hitters.csv")

    print("Fetching 2025 pitcher stats...")
    pitchers = fetch_pitcher_stats()
    pitchers.to_csv(DATA_DIR / "pitchers.csv", index=False)
    print(f"Saved {len(pitchers)} pitchers to data/pitchers.csv")


if __name__ == "__main__":
    main()