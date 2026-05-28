#!/usr/bin/env python3

"""
Prospects integration module for fantasy baseball system.
Handles minor league data and prospect projections.
"""

import pandas as pd
from pathlib import Path

from .fetch_prospects import fetch_prospects

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PROSPECT_WEIGHTS = {
    "R": 0.01,
    "HR": 0.02,
    "RBI": 0.015,
    "SB": 0.1,
    "OBP": 0.3,
    "QS": 0.03,
    "ERA": -0.005,
    "WHIP": -0.007,
    "Ks": 0.015,
    "SV": 0.04,
    "HLD": 0.03
}

PLAYER_TYPE_COLUMN = {
    "pitchers": ["%SV", "%HLD", "IP"],
    "batters": ["%HR", "%RBI", "%R", "%SB"]
}

def calculate_prospect_points(prospect_df: pd.DataFrame, player_type: str) -> pd.DataFrame:
    """Calculate fantasy points for prospects based on type."

    # Calculate position-specific stats
    if player_type == "pitchers":
        prospect_df["era_penalty"] = prospect_df["ERA"] * PROSPECT_WEIGHTS["ERA"]
        prospect_df["whip_penalty"] = prospect_df["WHIP"] * PROSPECT_WEIGHTS["WHIP"]
        prospect_df["sv_points"] = prospect_df["%SV"] * PROSPECT_WEIGHTS["SV"]
        prospect_df["hld_points"] = prospect_df["%HLD"] * PROSPECT_WEIGHTS["HLD"]
        prospect_df["ip_extra"] = prospect_df["IP"] * 0.001 * PROSPECT_WEIGHTS["BS"]

    elif player_type == "batters":
        prospect_df["home_run_points"] = prospect_df["HR%"] * PROSPECT_WEIGHTS["HR"]
        prospect_df["rbi_points"] = prospect_df["RBI%"] * PROSPECT_WEIGHTS["RBI"]
        prospect_df["r_points"] = prospect_df["R%"] * PROSPECT_WEIGHTS["R"]
        prospect_df["sb_points"] = prospect_df["SB%"] * PROSPECT_WEIGHTS["SB"]

    # Calculate total points
    prospect_df["prospect_points"] = prospect_df
        .assign(
            era_penalty=prospect_df["ERA"] * PROSPECT_WEIGHTS["ERA"]
            if player_type == "pitchers" else 0,
            whip_penalty=prospect_df["WHIP"] * PROSPECT_WEIGHTS["WHIP"]
            if player_type == "pitchers" else 0,
            sv_points=prospect_df["%SV"] * PROSPECT_WEIGHTS["SV"]
            if player_type == "pitchers" else 0,
            hld_points=prospect_df["%HLD"] * PROSPECT_WEIGHTS["HLD"]
            if player_type == "pitchers" else 0,
            home_run_points=prospect_df["HR%"] * PROSPECT_WEIGHTS["HR"]
            if player_type == "batters" else 0,
            rbi_points=prospect_df["RBI%"] * PROSPECT_WEIGHTS["RBI"]
            if player_type == "batters" else 0,
            r_points=prospect_df["R%"] * PROSPECT_WEIGHTS["R"]
            if player_type == "batters" else 0,
            sb_points=prospect_df["SB%"] * PROSPECT_WEIGHTS["SB"]
            if player_type == "batters" else 0
        ).sum(axis=1)

    return prospect_df


def get_prospect_ranks() -> list:
    """Get ranked prospects combining hitting and pitching prospects."

    # Fetch prospects
    hitters_df = fetch_prospects(playerType="batters").rename(columns={"Name": "player_name"})
    pitchers_df = fetch_prospects(playerType="pitchers").rename(columns={"Name": "player_name"})

    # Calculate points
    hitters_with_points = calculate_prospect_points(hitters_df, "batters")
    pitchers_with_points = calculate_prospect_points(pitchers_df, "pitchers")

    # Normalize points for different skills
    hitters_with_points["normalized_points"] = hitters_with_points["prospect_points"] / hitters_with_points["prospect_points"].max()
    pitchers_with_points["normalized_points"] = pitchers_with_points["prospect_points"] / pitchers_with_points["prospect_points"].max()

    # Merge dataframes
    all_prospects = pd.concat([
        hitters_with_points["player_name".rename("player_id"), hitters_with_points["normalized_points"] + hitters_with_points["prospect_points"]],
        pitchers_with_points["player_id"] + pitchers_with_points["normalized_points"],
        ignore_index=True
    ])

    # Sort and prepare ranking
    return all_prospects.sort_values("points", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    rankings_df = get_prospect_ranks()
    rankings_df.to_csv(DATA_DIR / "prospect_ranks.csv", index=False)
    print(f"Saved {len(rankings_df)} prospects to data/prospect_ranks.csv")