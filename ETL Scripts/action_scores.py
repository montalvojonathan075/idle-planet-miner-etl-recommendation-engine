"""
action_scores.py
----------------

Calculates:

- ROI
- Breakeven
- Hybrid Score

Inputs
------
action_gains.csv

Outputs
-------
action_gains.csv

Adds:
    roi_raw
    roi_factor
    roi_percent
    breakeven_seconds
    breakeven_display
    roi_score
    breakeven_score
    hybrid_score
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

from score_calculations import (
    roi_raw,
    roi_scale_factor,
    scaled_roi,
    roi_percent,
    breakeven_seconds,
    format_breakeven,
    roi_score,
    breakeven_score,
    hybrid_score,
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

    input_path = os.path.join(OUT_DIR, "action_gains.csv")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing file: {input_path}")

    df = pd.read_csv(input_path)

    logger.info(f"Loaded {len(df)} actions.")

    return df


# ==========================================================
# APPLY SCORES
# ==========================================================


def apply_scores(df: pd.DataFrame) -> pd.DataFrame:

    # --------------------------------------
    # ROI RAW
    # --------------------------------------

    df["roi_raw"] = df.apply(lambda row: roi_raw(row["gain"], row["cost"]), axis=1)

    roi_values = df["roi_raw"].tolist()

    factor = roi_scale_factor(roi_values)

    df["roi_factor"] = factor

    df["roi_scaled"] = df["roi_raw"].apply(lambda x: scaled_roi(x, factor))

    df["roi_percent"] = df["roi_raw"].apply(lambda x: roi_percent(x, factor))

    # --------------------------------------
    # BREAKEVEN
    # --------------------------------------

    df["breakeven_seconds"] = df.apply(
        lambda row: breakeven_seconds(row["cost"], row["gain"]), axis=1
    )

    df["breakeven_display"] = df["breakeven_seconds"].apply(format_breakeven)

    # --------------------------------------
    # ROI SCORE
    # --------------------------------------

    min_roi = df["roi_scaled"].min()

    max_roi = df["roi_scaled"].max()

    df["roi_score"] = df["roi_scaled"].apply(lambda x: roi_score(x, min_roi, max_roi))

    # --------------------------------------
    # BREAKEVEN SCORE
    # --------------------------------------

    min_breakeven = df["breakeven_seconds"].min()

    max_breakeven = df["breakeven_seconds"].max()

    df["breakeven_score"] = df["breakeven_seconds"].apply(
        lambda x: breakeven_score(x, min_breakeven, max_breakeven)
    )

    # --------------------------------------
    # HYBRID SCORE
    # --------------------------------------

    df["hybrid_score"] = df.apply(
        lambda row: hybrid_score(row["roi_score"], row["breakeven_score"]), axis=1
    )

    logger.info(f"Calculated scores for " f"{len(df)} actions.")

    return df


# ==========================================================
# SAVE
# ==========================================================


def save_data(df: pd.DataFrame):

    output_path = os.path.join(OUT_DIR, "action_scores.csv")

    df.to_csv(output_path, index=False)

    logger.info(f"Created action_scores.csv " f"with {len(df)} actions.")

    action_gains_path = os.path.join(OUT_DIR, "action_gains.csv")

    if os.path.exists(action_gains_path):

        os.remove(action_gains_path)

        logger.info("Removed action_gains.csv")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting action_scores pipeline.")

    try:

        df = load_data()

        df = apply_scores(df)

        save_data(df)

        runtime = time.time() - start_time

        logger.info(
            f"action_scores completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"action_scores failed: {e}")

        raise
