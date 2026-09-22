"""
report_generator.py
-------------------
Generates actionable upgrade recommendations for Idle Planet Miner
based on ROI, breakeven, and hybrid scoring.

This script:
- Initializes a default galaxy state
- Builds an action DataFrame with upgrade options
- Normalizes ROI and breakeven values for rational hybrid scoring
- Saves results to DataFrames/df_actions.csv
"""

import pandas as pd
from calculations import (
    calc_mining_roi,
    calc_speed_roi,
    calc_cargo_roi,
    calc_unlock_roi,
    calc_hybrid_score,
    calc_efficiency,
    upgrade_price,
    normalize_roi_values,
    format_time,
)
from load_and_clean import load_tables


def init_state(planets: pd.DataFrame) -> pd.DataFrame:
    """
    Initialize a default galaxy state DataFrame.
    All planets start locked with level 0.
    """
    return pd.DataFrame(
        {
            "Planet #": planets["planet_num"],
            "Unlocked": False,
            "Mining Level": 0,
            "Speed Level": 0,
            "Cargo Level": 0,
        }
    )


def build_action_df(planets: pd.DataFrame, df_state: pd.DataFrame) -> pd.DataFrame:
    """
    Build a DataFrame of upgrade actions with ROI, breakeven, and hybrid scores.
    """
    rows: list[list] = []
    unlocked_numbers = df_state.loc[df_state["Unlocked"], "Planet #"].tolist()
    max_unlocked = max(unlocked_numbers) if unlocked_numbers else 0

    for _, p in planets.iterrows():
        unlocked = df_state.loc[
            df_state["Planet #"] == p["planet_num"], "Unlocked"
        ].values[0]

        if not unlocked and p["planet_num"] == max_unlocked + 1:
            roi, breakeven = calc_unlock_roi(
                p["unlock_price"], p["ore_1_yield"], p["distance"]
            )
            hybrid = calc_hybrid_score(roi, breakeven)
            rows.append(
                [
                    p["planet_num"],
                    p["name"],
                    "Unlock Planet",
                    round(roi, 4),
                    format_time(breakeven),
                    round(hybrid, 4),
                    p["unlock_price"],
                ]
            )
        elif unlocked:
            mining_level = int(
                df_state.loc[
                    df_state["Planet #"] == p["planet_num"], "Mining Level"
                ].values[0]
            )
            speed_level = int(
                df_state.loc[
                    df_state["Planet #"] == p["planet_num"], "Speed Level"
                ].values[0]
            )
            cargo_level = int(
                df_state.loc[
                    df_state["Planet #"] == p["planet_num"], "Cargo Level"
                ].values[0]
            )

            eff = calc_efficiency(mining_level, p["distance"], speed_level, cargo_level)

            if eff < 1.0:
                roi, breakeven = calc_mining_roi(
                    mining_level,
                    p["ore_1_yield"],
                    p["unlock_price"],
                    p["distance"],
                    cargo_level,
                )
                hybrid = calc_hybrid_score(roi, breakeven)
                rows.append(
                    [
                        p["planet_num"],
                        p["name"],
                        f"Mining Lv {mining_level+1}",
                        round(roi, 4),
                        format_time(breakeven),
                        round(hybrid, 4),
                        upgrade_price(mining_level, p["unlock_price"]),
                    ]
                )
            else:
                speed_roi, speed_breakeven = calc_speed_roi(
                    speed_level,
                    p["ore_1_yield"],
                    p["unlock_price"],
                    p["distance"],
                    cargo_level,
                )
                cargo_roi, cargo_breakeven = calc_cargo_roi(
                    cargo_level,
                    p["ore_1_yield"],
                    p["unlock_price"],
                    p["distance"],
                    cargo_level,
                )

                if speed_roi > 0:
                    hybrid = calc_hybrid_score(speed_roi, speed_breakeven)
                    rows.append(
                        [
                            p["planet_num"],
                            p["name"],
                            f"Speed Lv {speed_level+1}",
                            round(speed_roi, 4),
                            format_time(speed_breakeven),
                            round(hybrid, 4),
                            upgrade_price(speed_level, p["unlock_price"]),
                        ]
                    )

                if cargo_roi > 0:
                    hybrid = calc_hybrid_score(cargo_roi, cargo_breakeven)
                    rows.append(
                        [
                            p["planet_num"],
                            p["name"],
                            f"Cargo Lv {cargo_level+1}",
                            round(cargo_roi, 4),
                            format_time(cargo_breakeven),
                            round(hybrid, 4),
                            upgrade_price(cargo_level, p["unlock_price"]),
                        ]
                    )

    df_actions = pd.DataFrame(
        rows,
        columns=[
            "Planet #",
            "Name",
            "Action",
            "ROI (%)",
            "Breakeven",
            "Hybrid",
            "Cost",
        ],
    )

    # Normalize ROI values across all actions
    df_actions["ROI (%)"] = normalize_roi_values(df_actions["ROI (%)"].tolist())

    return df_actions


if __name__ == "__main__":
    # Load cleaned tables
    data = load_tables()
    df_planets = data["planets"]

    # Initialize default state (all locked, level 0)
    df_state = init_state(df_planets)

    # Build actions
    df_actions = build_action_df(df_planets, df_state)
    df_actions.to_csv("DataFrames/df_actions.csv", index=False)
