"""
calculations.py
---------------
Provides mathematical functions for ROI, breakeven, hybrid scoring, and worth calculations
used in the Idle Planet Miner ETL pipeline.

These functions quantify the efficiency and profitability of mining, speed, cargo, and unlock
actions. They are used downstream in the ETL process to generate upgrade recommendations
and prioritize actions based on return on investment and breakeven time.
"""

import math
import decimal
import logging
import pandas as pd

# --- Configurable constants ---
STAR_BONUS: float = 0.2  # Each star increases ore value by 20%


# --- Core upgrade formulas (from Idle Planet Miner wiki) ---
def mining_rate(level: int) -> float:
    """Upgraded Base Mining Rate at a given level."""
    return 0.25 + 0.1 * (level - 1) + 0.017 * (level - 1) ** 2


def ship_speed(level: int) -> float:
    """Upgraded Base Ship Speed at a given level."""
    return 1 + 0.2 * (level - 1) + (1 / 75) * (level - 1) ** 2


def cargo_capacity(level: int) -> int:
    """Upgraded Base Cargo at a given level (rounded half-to-even)."""
    raw_value = 5 + 2 * (level - 1) + 0.1 * (level - 1) ** 2
    return int(
        decimal.Decimal(raw_value).quantize(
            decimal.Decimal("1"), rounding=decimal.ROUND_HALF_EVEN
        )
    )


def upgrade_price(level: int, unlock_price: float) -> float:
    """Base Upgrade Price to reach level+1."""
    return (unlock_price / 20) * (1.3 ** (level - 1))


# --- Efficiency and deposit ---
def calc_efficiency(
    mining: float, distance: float, speed: float, cargo: float
) -> float:
    """Efficiency = mining throughput / cargo throughput."""
    trip_time: float = (2 * distance) / speed
    cargo_throughput: float = cargo / trip_time
    mining_throughput: float = mining * 60
    return mining_throughput / cargo_throughput


def calc_deposit(
    mining: float, distance: float, speed: float, cargo: float, efficiency: float
) -> float:
    """Deposit per second depends on bottleneck."""
    trip_time: float = (2 * distance) / speed
    cargo_throughput: float = cargo / trip_time
    mining_throughput: float = mining * 60
    return mining_throughput if efficiency < 1.0 else cargo_throughput


def calc_earning(worth: float, deposit_per_sec: float) -> float:
    """Income per second = worth * deposit/sec."""
    return worth * deposit_per_sec


# --- ROI Functions ---
def calc_mining_roi(
    level: int,
    total_worth: float,
    unlock_price: float,
    distance: float,
    cargo_level: int,
) -> tuple[float, float]:
    """ROI for mining upgrades (only relevant when mining bottleneck)."""
    mining_curr = mining_rate(level)
    speed_curr = ship_speed(level)
    cargo_curr = cargo_capacity(cargo_level)
    eff_curr = calc_efficiency(mining_curr, distance, speed_curr, cargo_curr)

    if eff_curr >= 1.0:
        logging.warning("Mining ROI returned (0.0, inf): efficiency already at 100%.")
        return (0.0, float("inf"))

    mining_next = mining_rate(level + 1)
    eff_next = calc_efficiency(mining_next, distance, speed_curr, cargo_curr)

    deposit_curr = calc_deposit(mining_curr, distance, speed_curr, cargo_curr, eff_curr)
    deposit_next = calc_deposit(mining_next, distance, speed_curr, cargo_curr, eff_next)
    delta_earning = calc_earning(total_worth, deposit_next) - calc_earning(
        total_worth, deposit_curr
    )

    upgrade_cost = upgrade_price(level, unlock_price)
    if delta_earning <= 0:
        logging.warning("Mining ROI returned (0.0, inf): no positive earning gain.")
        return (0.0, float("inf"))

    roi = delta_earning / upgrade_cost
    breakeven = upgrade_cost / delta_earning
    return (roi, breakeven)


def calc_speed_roi(
    level: int,
    total_worth: float,
    unlock_price: float,
    distance: float,
    cargo_level: int,
) -> tuple[float, float]:
    """ROI for speed upgrades (only relevant when cargo bottleneck)."""
    mining_curr = mining_rate(level)
    speed_curr = ship_speed(level)
    cargo_curr = cargo_capacity(cargo_level)
    eff_curr = calc_efficiency(mining_curr, distance, speed_curr, cargo_curr)

    if eff_curr < 1.0:
        logging.warning("Speed ROI returned (0.0, inf): mining is bottleneck.")
        return (0.0, float("inf"))

    speed_next = ship_speed(level + 1)
    eff_next = calc_efficiency(mining_curr, distance, speed_next, cargo_curr)

    deposit_curr = calc_deposit(mining_curr, distance, speed_curr, cargo_curr, eff_curr)
    deposit_next = calc_deposit(mining_curr, distance, speed_next, cargo_curr, eff_next)
    delta_earning = calc_earning(total_worth, deposit_next) - calc_earning(
        total_worth, deposit_curr
    )

    upgrade_cost = upgrade_price(level, unlock_price)
    if delta_earning <= 0:
        logging.warning("Speed ROI returned (0.0, inf): no positive earning gain.")
        return (0.0, float("inf"))

    roi = delta_earning / upgrade_cost
    breakeven = upgrade_cost / delta_earning
    return (roi, breakeven)


def calc_cargo_roi(
    level: int,
    total_worth: float,
    unlock_price: float,
    distance: float,
    cargo_level: int,
) -> tuple[float, float]:
    """ROI for cargo upgrades (only relevant when cargo bottleneck)."""
    mining_curr = mining_rate(level)
    speed_curr = ship_speed(level)
    cargo_curr = cargo_capacity(cargo_level)
    eff_curr = calc_efficiency(mining_curr, distance, speed_curr, cargo_curr)

    if eff_curr < 1.0:
        logging.warning("Cargo ROI returned (0.0, inf): mining is bottleneck.")
        return (0.0, float("inf"))

    cargo_next = cargo_capacity(cargo_level + 1)
    eff_next = calc_efficiency(mining_curr, distance, speed_curr, cargo_next)

    deposit_curr = calc_deposit(mining_curr, distance, speed_curr, cargo_curr, eff_curr)
    deposit_next = calc_deposit(mining_curr, distance, speed_curr, cargo_next, eff_next)
    delta_earning = calc_earning(total_worth, deposit_next) - calc_earning(
        total_worth, deposit_curr
    )

    upgrade_cost = upgrade_price(level, unlock_price)
    if delta_earning <= 0:
        logging.warning("Cargo ROI returned (0.0, inf): no positive earning gain.")
        return (0.0, float("inf"))

    roi = delta_earning / upgrade_cost
    breakeven = upgrade_cost / delta_earning
    return (roi, breakeven)


def calc_unlock_roi(
    unlock_price: float, total_worth: float, distance: float
) -> tuple[float, float]:
    """ROI for unlocking a new planet."""
    if unlock_price <= 0 or total_worth <= 0 or distance <= 0:
        logging.warning("Unlock ROI returned (0.0, inf): invalid parameters.")
        return (0.0, float("inf"))

    mining_lvl = mining_rate(1)
    speed_lvl = ship_speed(1)
    cargo_lvl = cargo_capacity(1)

    eff = calc_efficiency(mining_lvl, distance, speed_lvl, cargo_lvl)
    deposit = calc_deposit(mining_lvl, distance, speed_lvl, cargo_lvl, eff)
    earning = calc_earning(total_worth, deposit)

    if earning <= 0:
        logging.warning("Unlock ROI returned (0.0, inf): no positive earning gain.")
        return (0.0, float("inf"))

    roi = earning / unlock_price
    breakeven = unlock_price / earning
    return (roi, breakeven)


# --- Hybrid scoring ---
def normalize_roi_values(rois: list[float]) -> list[float]:
    """
    Normalize ROI values so max ROI is never below 0.01% and never above 100%.
    - If max ROI < 0.01%, scale all ROI values by 100.
    - Clamp all ROI values to a maximum of 100%.
    """
    if not rois:
        return rois
    max_roi = max(rois)
    if max_roi < 0.01:
        return [min(r * 100, 100.0) for r in rois]
    return [min(r, 100.0) for r in rois]


def calc_hybrid_score(
    roi: float, breakeven: float, weight_roi: float = 0.6, weight_breakeven: float = 0.4
) -> float:
    """Weighted score combining ROI and breakeven."""
    if roi <= 0 or breakeven == float("inf"):
        return 0.0
    adjusted_roi: float = math.log1p(roi)
    inv_breakeven: float = 1 / max(breakeven, 1.0)  # clamp to avoid extreme skew
    return (adjusted_roi * weight_roi) + (inv_breakeven * weight_breakeven)


# --- Worth calculation with stars ---
def calc_planet_worth(
    ores: dict[str, float],
    ore_symbols: list[str],
    ore_yields: list[float],
    ore_stars: dict[str, int],
) -> float:
    """Calculate total worth of a planet based on ores, yields, and star bonuses."""
    worth: float = 0.0
    for symbol, yield_pct in zip(ore_symbols, ore_yields):
        if symbol and symbol in ores:
            stars: int = ore_stars.get(symbol, 0)
            adjusted_value: float = ores[symbol] * (1 + STAR_BONUS * stars)
            worth += adjusted_value * yield_pct
    return worth


# --- Time formatting ---
def format_time(seconds: float) -> str:
    """
    Format seconds into human-readable time (d h m s).
    Returns 'N/A' for invalid or infinite values.
    """
    if seconds == float("inf") or seconds <= 0:
        return "N/A"
    if seconds < 1:
        seconds = 1

    seconds = int(seconds)
    days: int = seconds // 86400
    hours: int = (seconds % 86400) // 3600
    minutes: int = (seconds % 3600) // 60
    secs: int = seconds % 60

    if days > 0:
        return f"{days}d {hours}h {minutes}m {secs}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


# --- Action Builder ---
def build_actions(df_state: pd.DataFrame, planet_data: pd.DataFrame) -> pd.DataFrame:
    """
    Build df_actions based on current galaxy state and efficiency rules.
    Rules:
      - If planet is locked → Unlock Planet
      - If planet is unlocked:
          * If EFF < 100 → Upgrade Mining
          * If EFF >= 100 → Upgrade Speed and Upgrade Cargo
    """
    actions = []

    for _, planet in df_state.iterrows():
        planet_num = int(planet["Planet #"])
        name = planet["Name"]
        unlocked = bool(planet["Unlocked"])

        # ✅ Correct lookups using planets_clean.csv
        unlock_price = planet_data.loc[
            planet_data["planet_num"] == planet_num, "unlock_price"
        ].values[0]
        distance = planet_data.loc[
            planet_data["planet_num"] == planet_num, "distance"
        ].values[0]

        # Compute worth from ores and yields
        ore_symbols = [
            planet_data.loc[planet_data["planet_num"] == planet_num, "ore_1"].values[0],
            planet_data.loc[planet_data["planet_num"] == planet_num, "ore_2"].values[0],
            planet_data.loc[planet_data["planet_num"] == planet_num, "ore_3"].values[0],
        ]
        ore_yields = [
            planet_data.loc[
                planet_data["planet_num"] == planet_num, "ore_1_yield"
            ].values[0],
            planet_data.loc[
                planet_data["planet_num"] == planet_num, "ore_2_yield"
            ].values[0],
            planet_data.loc[
                planet_data["planet_num"] == planet_num, "ore_3_yield"
            ].values[0],
        ]

        # assumes you have ore values + star bonuses defined elsewhere
        ores = {}  # e.g. {"C": 1.0, "Fe": 2.0, ...}
        ore_stars = {}  # e.g. {"C": 0, "Fe": 1, ...}
        worth = calc_planet_worth(ores, ore_symbols, ore_yields, ore_stars)

        mining_level = int(planet["Mining Level"])
        speed_level = int(planet["Speed Level"])
        cargo_level = int(planet["Cargo Level"])

        if not unlocked:
            roi, breakeven = calc_unlock_roi(unlock_price, worth, distance)
            actions.append(
                {
                    "Planet #": planet_num,
                    "Name": name,
                    "Action": "Unlock Planet",
                    "ROI (%)": roi,
                    "Breakeven": format_time(breakeven),
                    "Hybrid": calc_hybrid_score(roi, breakeven),
                    "Cost": unlock_price,
                }
            )
        else:
            mining_curr = mining_rate(mining_level)
            speed_curr = ship_speed(speed_level)
            cargo_curr = cargo_capacity(cargo_level)
            eff = calc_efficiency(mining_curr, distance, speed_curr, cargo_curr)

            if eff < 1.0:
                roi, breakeven = calc_mining_roi(
                    mining_level, worth, unlock_price, distance, cargo_level
                )
                actions.append(
                    {
                        "Planet #": planet_num,
                        "Name": name,
                        "Action": "Upgrade Mining",
                        "ROI (%)": roi,
                        "Breakeven": format_time(breakeven),
                        "Hybrid": calc_hybrid_score(roi, breakeven),
                        "Cost": upgrade_price(mining_level, unlock_price),
                    }
                )
            else:
                roi_s, breakeven_s = calc_speed_roi(
                    speed_level, worth, unlock_price, distance, cargo_level
                )
                actions.append(
                    {
                        "Planet #": planet_num,
                        "Name": name,
                        "Action": "Upgrade Speed",
                        "ROI (%)": roi_s,
                        "Breakeven": format_time(breakeven_s),
                        "Hybrid": calc_hybrid_score(roi_s, breakeven_s),
                        "Cost": upgrade_price(speed_level, unlock_price),
                    }
                )

                roi_c, breakeven_c = calc_cargo_roi(
                    cargo_level, worth, unlock_price, distance, cargo_level
                )
                actions.append(
                    {
                        "Planet #": planet_num,
                        "Name": name,
                        "Action": "Upgrade Cargo",
                        "ROI (%)": roi_c,
                        "Breakeven": format_time(breakeven_c),
                        "Hybrid": calc_hybrid_score(roi_c, breakeven_c),
                        "Cost": upgrade_price(cargo_level, unlock_price),
                    }
                )

    df_actions = pd.DataFrame(actions)
    df_actions.to_csv("DataFrames/df_actions.csv", index=False)
    return df_actions
