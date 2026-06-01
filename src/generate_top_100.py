#!/usr/bin/env python3

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def main():
    # Load fantasy rankings
    try:
        df = pd.read_csv(DATA_DIR / "fantasy_rankings.csv")
    except FileNotFoundError:
        print("Error: fantasy_rankings.csv not found. Run projections.py first.")
        return

    # Sort by fantasy points and select top 100
    top_100 = df.sort_values("fantasy_points", ascending=False).head(100)
    
    # Save to CSV
    top_100.to_csv(DATA_DIR / "top_100_dynasty.csv", index=False)
    print("Top 100 Dynasty Players list generated!")

if __name__ == "__main__":
    main()