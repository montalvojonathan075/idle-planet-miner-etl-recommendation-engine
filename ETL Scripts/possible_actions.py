"""
possible_actions.py
-------------------

Creates the action universe used by the
recommendation engine.

Rules
-----
- Unlocked planets can be upgraded.
- Each unlocked planet generates:
    Mining +1
    Cargo +1
    Speed +1

- Only the NEXT locked planet may be unlocked.
- All other locked planets are ignored.

Output
------
possible_actions.csv
"""

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

LOG_FILE = os.path.join(OUT_DIR, "pipeline_log.txt")

os.makedirs(OUT_DIR, exist_ok=True)

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


def load_planet_metrics():

    metrics_path = os.path.join(OUT_DIR, "planet_metrics.csv")

    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"Missing file: {metrics_path}")

    df = pd.read_csv(metrics_path)

    logger.info(f"Loaded {len(df)} planets.")

    return df


# ==========================================================
# BUILD ACTIONS
# ==========================================================


def build_possible_actions(df: pd.DataFrame) -> pd.DataFrame:

    actions = []

    # --------------------------------------
    # Upgrade Actions
    # --------------------------------------

    unlocked = df[df["status"] == "Unlocked"]

    for _, row in unlocked.iterrows():

        actions.append(
            {
                "action_type": "mining",
                "planet_num": row["planet_num"],
                "planet_name": row["planet_name"],
                "current_level": row["mining_lvl"],
                "next_level": row["mining_lvl"] + 1,
            }
        )

        actions.append(
            {
                "action_type": "cargo",
                "planet_num": row["planet_num"],
                "planet_name": row["planet_name"],
                "current_level": row["cargo_lvl"],
                "next_level": row["cargo_lvl"] + 1,
            }
        )

        actions.append(
            {
                "action_type": "speed",
                "planet_num": row["planet_num"],
                "planet_name": row["planet_name"],
                "current_level": row["speed_lvl"],
                "next_level": row["speed_lvl"] + 1,
            }
        )

    # --------------------------------------
    # Next Planet Unlock
    # --------------------------------------

    locked = df[df["status"] == "Locked"]

    if not locked.empty:

        next_planet = locked.sort_values("planet_num").iloc[0]

        actions.append(
            {
                "action_type": "unlock",
                "planet_num": next_planet["planet_num"],
                "planet_name": next_planet["planet_name"],
                "current_level": None,
                "next_level": None,
            }
        )

    df_actions = pd.DataFrame(actions)

    logger.info(f"Created " f"{len(df_actions)} possible actions.")

    return df_actions


# ==========================================================
# SAVE
# ==========================================================


def save_actions(df: pd.DataFrame):

    output_path = os.path.join(OUT_DIR, "possible_actions.csv")

    df.to_csv(output_path, index=False)

    logger.info(f"Created possible_actions.csv " f"with {len(df)} actions.")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting possible_actions pipeline.")

    try:

        df_metrics = load_planet_metrics()

        df_actions = build_possible_actions(df_metrics)

        save_actions(df_actions)

        runtime = time.time() - start_time

        logger.info(
            f"possible_actions completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"possible_actions failed: {e}")

        raise
