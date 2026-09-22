"""
planet_metrics.py
-----------------

Applies core formulas to the current player state.

Inputs
------
planet_levels.csv
planet_data.csv

Outputs
-------
planet_metrics.csv

Notes
-----
- Does NOT modify or delete planet_levels.csv
- Merges static planet data with player state
- Applies core Idle Planet Miner formulas
- Generates metrics for recommendation engine
"""

import sys
import os
import time
import logging

import pandas as pd

# ==========================================================
# PATH SETUP
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.dirname(BASE_DIR)

OUT_DIR = os.path.join(PROJECT_DIR, "DataFrames")

CALC_DIR = os.path.join(BASE_DIR, "calculations")

sys.path.append(CALC_DIR)

# ==========================================================
# IMPORT CORE FORMULAS
# ==========================================================

from core_metrics import (
    mining_rate,
    ship_speed,
    cargo,
    calculate_trip_time,
    calculate_efficiency,
    calculate_deposit,
)

# ==========================================================
# LOGGING
# ==========================================================

LOG_FILE = os.path.join(OUT_DIR, "pipeline_log.txt")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.handlers.clear()

file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# ==========================================================
# DATA LOADING
# ==========================================================


def load_data():

    levels_path = os.path.join(OUT_DIR, "planet_levels.csv")

    data_path = os.path.join(OUT_DIR, "planet_data.csv")

    if not os.path.exists(levels_path):
        raise FileNotFoundError(f"Missing file: {levels_path}")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing file: {data_path}")

    df_levels = pd.read_csv(levels_path)

    df_planets = pd.read_csv(data_path)

    logger.info(f"Loaded {len(df_levels)} planet states.")

    logger.info(f"Loaded {len(df_planets)} planet records.")

    return df_levels, df_planets


# ==========================================================
# MERGE DATA
# ==========================================================


def merge_data(df_levels: pd.DataFrame, df_planets: pd.DataFrame) -> pd.DataFrame:

    df = pd.merge(df_levels, df_planets, on=["planet_num", "planet_name"], how="left")

    logger.info(f"Merged dataset contains " f"{len(df)} planets.")

    return df


# ==========================================================
# METRIC APPLICATION
# ==========================================================


def apply_planet_metrics(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Applying planet metrics.")

    # --------------------------------------
    # Initialize Metrics
    # --------------------------------------

    df["mining_rate"] = 0.0
    df["ship_speed"] = 0.0
    df["cargo"] = 0

    df["trip_time"] = 0.0
    df["efficiency"] = 0.0
    df["deposit"] = 0.0

    # --------------------------------------
    # Unlocked Planets
    # --------------------------------------

    unlocked_mask = df["status"] == "Unlocked"

    # --------------------------------------
    # Core Rates
    # --------------------------------------

    df.loc[unlocked_mask, "mining_rate"] = df.loc[unlocked_mask, "mining_lvl"].apply(
        mining_rate
    )

    df.loc[unlocked_mask, "ship_speed"] = df.loc[unlocked_mask, "speed_lvl"].apply(
        ship_speed
    )

    df.loc[unlocked_mask, "cargo"] = df.loc[unlocked_mask, "cargo_lvl"].apply(cargo)

    # --------------------------------------
    # Secondary Metrics
    # --------------------------------------

    df = calculate_trip_time(df, "distance", "ship_speed")

    df = calculate_efficiency(df, "mining_rate", "trip_time", "cargo")

    df = calculate_deposit(df, "mining_rate", "trip_time", "cargo", "efficiency")

    logger.info("Planet metrics successfully applied.")

    return df


# ==========================================================
# SAVE OUTPUT
# ==========================================================


def save_planet_metrics(
    df: pd.DataFrame, output_path: str = os.path.join(OUT_DIR, "planet_metrics.csv")
):

    df.to_csv(output_path, index=False)

    logger.info(f"Created planet_metrics.csv " f"with {len(df)} planets.")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting planet_metrics pipeline.")

    try:

        df_levels, df_planets = load_data()

        df = merge_data(df_levels, df_planets)

        df_metrics = apply_planet_metrics(df)

        save_planet_metrics(df_metrics)

        runtime = time.time() - start_time

        logger.info(
            f"planet_metrics completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"planet_metrics failed: {e}")

        raise
