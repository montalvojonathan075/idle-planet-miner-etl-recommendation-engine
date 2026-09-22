"""
action_gains.py
---------------

Calculates cost and gain for every
possible action.

Inputs
------
possible_actions.csv
planet_metrics.csv

Outputs
-------
action_gains.csv

Adds:
    cost
    gain

Filters:
    gain > 0
"""

import os
import sys
import time
import logging

import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CALC_DIR = os.path.join(BASE_DIR, "calculations")

sys.path.append(CALC_DIR)

PROJECT_DIR = os.path.dirname(BASE_DIR)

OUT_DIR = os.path.join(PROJECT_DIR, "DataFrames")

LOG_FILE = os.path.join(OUT_DIR, "pipeline_log.txt")

# ==========================================================
# IMPORTS
# ==========================================================

from gain_calculations import (
    unlock_gain,
    mining_upgrade_gain,
    speed_upgrade_gain,
    cargo_upgrade_gain,
)

from core_metrics import (
    upgrade_price,
)

# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.handlers.clear()

file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# ==========================================================
# LOAD DATA
# ==========================================================


def load_data():

    actions_path = os.path.join(OUT_DIR, "possible_actions.csv")

    metrics_path = os.path.join(OUT_DIR, "planet_metrics.csv")

    if not os.path.exists(actions_path):
        raise FileNotFoundError(f"Missing file: {actions_path}")

    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"Missing file: {metrics_path}")

    df_actions = pd.read_csv(actions_path)

    df_metrics = pd.read_csv(metrics_path)

    logger.info(f"Loaded {len(df_actions)} actions.")

    logger.info(f"Loaded {len(df_metrics)} planets.")

    return df_actions, df_metrics


# ==========================================================
# CALCULATE COSTS + GAINS
# ==========================================================


def apply_gains(df_actions: pd.DataFrame, df_metrics: pd.DataFrame) -> pd.DataFrame:

    gains = []
    costs = []

    for _, action in df_actions.iterrows():

        planet_num = action["planet_num"]

        planet = df_metrics.loc[df_metrics["planet_num"] == planet_num].iloc[0]

        action_type = action["action_type"]

        gain_value = 0.0
        cost_value = 0.0

        # --------------------------------------
        # Unlock
        # --------------------------------------

        if action_type == "unlock":

            gain_value = unlock_gain(
                distance=planet["distance"], planet_worth=planet["planet_worth_num"]
            )

            cost_value = planet["unlock_price"]

        # --------------------------------------
        # Mining
        # --------------------------------------

        elif action_type == "mining":

            gain_value = mining_upgrade_gain(
                mining_level=planet["mining_lvl"],
                cargo_value=planet["cargo"],
                trip_time=planet["trip_time"],
                current_deposit=planet["deposit"],
                planet_worth=planet["planet_worth_num"],
            )

            cost_value = upgrade_price(planet["mining_lvl"], planet["unlock_price"])

        # --------------------------------------
        # Speed
        # --------------------------------------

        elif action_type == "speed":

            gain_value = speed_upgrade_gain(
                mining_rate_value=planet["mining_rate"],
                speed_level=planet["speed_lvl"],
                cargo_value=planet["cargo"],
                distance=planet["distance"],
                current_deposit=planet["deposit"],
                planet_worth=planet["planet_worth_num"],
            )

            cost_value = upgrade_price(planet["speed_lvl"], planet["unlock_price"])

        # --------------------------------------
        # Cargo
        # --------------------------------------

        elif action_type == "cargo":

            gain_value = cargo_upgrade_gain(
                mining_rate_value=planet["mining_rate"],
                cargo_level=planet["cargo_lvl"],
                trip_time=planet["trip_time"],
                current_deposit=planet["deposit"],
                planet_worth=planet["planet_worth_num"],
            )

            cost_value = upgrade_price(planet["cargo_lvl"], planet["unlock_price"])

        gains.append(gain_value)

        costs.append(cost_value)
    df_actions["cost"] = costs
    df_actions["gain"] = gains

    logger.info(f"Calculated costs and gains for {len(df_actions)} actions.")

    # --------------------------------------
    # KEEP PROFITABLE ACTIONS ONLY
    # --------------------------------------

    original_count = len(df_actions)

    df_actions = df_actions[df_actions["gain"] > 0].copy()

    removed_count = original_count - len(df_actions)

    logger.info(f"Removed {removed_count} " f"actions with non-positive gain.")

    logger.info(f"Remaining profitable actions: " f"{len(df_actions)}")

    return df_actions


# ==========================================================
# SAVE
# ==========================================================


def save_actions(df: pd.DataFrame):

    output_path = os.path.join(OUT_DIR, "action_gains.csv")

    df.to_csv(output_path, index=False)

    logger.info(f"Created action_gains.csv " f"with {len(df)} actions.")

    possible_actions_path = os.path.join(OUT_DIR, "possible_actions.csv")

    if os.path.exists(possible_actions_path):

        os.remove(possible_actions_path)

        logger.info("Removed possible_actions.csv")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting action_gains pipeline.")

    try:

        df_actions, df_metrics = load_data()

        df_actions = apply_gains(df_actions, df_metrics)

        save_actions(df_actions)

        runtime = time.time() - start_time

        logger.info(
            f"action_gains completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"action_gains failed: {e}")

        raise
