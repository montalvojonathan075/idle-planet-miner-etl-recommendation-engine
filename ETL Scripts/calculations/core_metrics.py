"""
core_metrics.py
---------------

Provides foundational calculations for the ETL pipeline:

- Core upgrade formulas
    - mining rate
    - ship speed
    - cargo
    - upgrade price

- Trip time
- Efficiency
- Deposit per trip
"""

import decimal
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ==========================================================
# VALIDATION
# ==========================================================


def validate_level(level: int) -> None:
    """
    Validate upgrade level.

    Level 0 is reserved for locked planets.
    Formulas should normally only be applied
    to unlocked planets (level >= 1).
    """

    if level < 0:

        raise ValueError(f"Invalid level: {level}. " "Levels must be >= 0.")


# ==========================================================
# CORE UPGRADE FORMULAS
# ==========================================================


def mining_rate(level: int) -> float:
    """
    Upgraded Base Mining Rate
    at a given level.
    """

    validate_level(level)

    return 0.25 + 0.1 * (level - 1) + 0.017 * (level - 1) ** 2


def ship_speed(level: int) -> float:
    """
    Upgraded Base Ship Speed
    at a given level.
    """

    validate_level(level)

    return 1 + 0.2 * (level - 1) + (1 / 75) * (level - 1) ** 2


def cargo(level: int) -> int:
    """
    Upgraded Base Cargo.

    Uses banker's rounding
    (round half to even).
    """

    validate_level(level)

    raw_value = 5 + 2 * (level - 1) + 0.1 * (level - 1) ** 2

    return int(
        decimal.Decimal(raw_value).quantize(
            decimal.Decimal("1"), rounding=decimal.ROUND_HALF_EVEN
        )
    )


def upgrade_price(level: int, unlock_price: float) -> float:
    """
    Base Upgrade Price
    required to reach level + 1.
    """

    validate_level(level)

    return (unlock_price / 20) * (1.3 ** (level - 1))


# ==========================================================
# TRIP TIME
# ==========================================================


def calculate_trip_time(
    df: pd.DataFrame, distance_col: str, speed_col: str, output_col: str = "trip_time"
) -> pd.DataFrame:
    """
    Trip Time

    Formula:
        (2 * distance) / speed

    Represents a round trip from
    mothership to planet and back.
    """

    df[output_col] = (2 * df[distance_col]) / (df[speed_col].replace(0, np.inf))

    logger.info(f"Trip time calculated " f"for {len(df)} planets.")

    return df


# ==========================================================
# EFFICIENCY
# ==========================================================


def calculate_efficiency(
    df: pd.DataFrame,
    mining_rate_col: str,
    trip_time_col: str,
    cargo_col: str,
    output_col: str = "efficiency",
) -> pd.DataFrame:
    """
    Efficiency

    Formula:
        (mining_rate * trip_time)
        / cargo

    Interpretation:

    efficiency < 1
        Cargo never fills.

    efficiency >= 1
        Cargo fills completely.
    """

    df[output_col] = (df[mining_rate_col] * df[trip_time_col]) / (
        df[cargo_col].replace(0, np.inf)
    )

    logger.info(f"Efficiency calculated " f"for {len(df)} planets.")

    return df


# ==========================================================
# DEPOSIT
# ==========================================================


def calculate_deposit(
    df: pd.DataFrame,
    mining_rate_col: str,
    trip_time_col: str,
    cargo_col: str,
    eff_col: str = "efficiency",
    output_col: str = "deposit",
) -> pd.DataFrame:
    """
    Deposit Per Trip

    If efficiency < 1:

        deposit =
        mining_rate * trip_time

    If efficiency >= 1:

        deposit =
        cargo
    """

    df[output_col] = np.where(
        df[eff_col] < 1.0, (df[mining_rate_col] * df[trip_time_col]), df[cargo_col]
    )

    logger.info(f"Deposit calculated " f"for {len(df)} planets.")

    return df


# ==========================================================
# RUNNER
# ==========================================================


def apply_core_metrics(
    df: pd.DataFrame,
    mining_rate_col: str,
    distance_col: str,
    speed_col: str,
    cargo_col: str,
) -> pd.DataFrame:
    """
    Apply all core metric calculations
    in sequence.
    """

    df = calculate_trip_time(df, distance_col, speed_col)

    df = calculate_efficiency(df, mining_rate_col, "trip_time", cargo_col)

    df = calculate_deposit(df, mining_rate_col, "trip_time", cargo_col, "efficiency")

    logger.info(f"Core metrics applied " f"for {len(df)} planets.")

    return df
