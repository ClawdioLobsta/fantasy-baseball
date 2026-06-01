#!/usr/bin/env python3

"""
Calculate fantasy baseball projections and rankings.
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename: str) -> pd.DataFrame:
    try:
        return pd.read_csv(DATA_DIR / filename)
    except FileNotFoundError:
        return pd.DataFrame()


def compute_fantasy_points(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna(0)

    # Hitter formula: (R + HR*2 + RBI + SB*2) * OBP
    hitter_mask = df["position"].str.contains("P", na=False) == False
    df["fantasy_points"] = 0.0

    df.loc[hitter_mask, "fantasy_points"] = (
        df.loc[hitter_mask, "R"]
        + df.loc[hitter_mask, "HR"] * 2
        + df.loc[hitter_mask, "RBI"]
        + df.loc[hitter_mask, "SB"] * 2
    ) * df.loc[hitter_mask, "OBP"]

    pitcher_mask = df["position"].str.contains("P", na=False)
    df.loc[pitcher_mask, "fantasy_points"] = (
        df.loc[pitcher_mask, "QS"] * 5
        - df.loc[pitcher_mask, "ERA"] * 2
        + (1 / df.loc[pitcher_mask, "WHIP"].replace(0, float("inf"))) * 3
        + df.loc[pitcher_mask, "Ks"] * 0.5
        + (df.loc[pitcher_mask, "SV"] + df.loc[pitcher_mask, "HLD"]) * 2
    )

    return df


def main():
    hitters = load_csv("hitters.csv")
    pitchers = load_csv("pitchers.csv")

    if hitters.empty and pitchers.empty:
        print("No data found. Run fetch_stats.py first.")
        return

    hitters["position"] = hitters["position"].fillna("HITTER")
    pitchers["position"] = pitchers["position"].fillna("PITCHER")
    df = pd.concat([hitters, pitchers], ignore_index=True)

    df = compute_fantasy_points(df)
    df = df.sort_values("fantasy_points", ascending=False)

    df.to_csv(DATA_DIR / "fantasy_rankings.csv", index=False)
    print(f"Saved {len(df)} players to data/fantasy_rankings.csv")