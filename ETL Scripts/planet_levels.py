"""
planet_levels.py
----------------

Creates the persistent planet state tracker.

Purpose
-------
Initialize planet_levels.csv from planet_data.csv.

All planets start as:
    status      = Locked
    mining_lvl  = 0
    speed_lvl   = 0
    cargo_lvl   = 0

This file serves as the source of truth for the
player's current galaxy state and will later be
updated by the questionnaire/gameplay layer.
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
# LOGGING CONFIGURATION
# ==========================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.handlers.clear()

file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# ==========================================================
# CORE FUNCTION
# ==========================================================


def initialize_planet_levels(
    input_path: str = os.path.join(OUT_DIR, "planet_data.csv"),
    output_path: str = os.path.join(OUT_DIR, "planet_levels.csv"),
    force_reset: bool = False,
) -> pd.DataFrame:
    """
    Create initial planet state table.

    If a saved galaxy already exists,
    reuse it rather than resetting
    player progress.

    Use force_reset=True to create
    a brand-new galaxy.
    """

    # --------------------------------------
    # Existing Save Found
    # --------------------------------------

    if os.path.exists(output_path) and not force_reset:

        logger.info("planet_levels.csv already exists. " "Using existing galaxy state.")

        return pd.read_csv(output_path)

    # --------------------------------------
    # Build New Galaxy
    # --------------------------------------

    logger.info("Loading planet_data.csv")

    df = pd.read_csv(input_path)

    logger.info(f"Loaded {len(df)} planets.")

    # --------------------------------------
    # Create Default State
    # --------------------------------------

    df["status"] = "Locked"

    df["mining_lvl"] = 0
    df["speed_lvl"] = 0
    df["cargo_lvl"] = 0

    # --------------------------------------
    # Output State Table
    # --------------------------------------

    df_out = df[
        [
            "planet_num",
            "planet_name",
            "status",
            "mining_lvl",
            "speed_lvl",
            "cargo_lvl",
        ]
    ].copy()

    df_out.to_csv(output_path, index=False)

    logger.info(f"Created planet_levels.csv " f"with {len(df_out)} planets.")

    return df_out


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting planet_levels pipeline.")

    try:

        initialize_planet_levels()

        runtime = time.time() - start_time

        logger.info(
            f"planet_levels completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"planet_levels failed: {e}")

        raise
