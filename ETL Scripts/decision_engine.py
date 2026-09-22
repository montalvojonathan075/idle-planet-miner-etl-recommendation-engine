"""
decision_engine.py
------------------

Reads:
    action_scores.csv

Creates:
    choices.csv

Recommendations:
    ROI
    Hybrid
    Breakeven
    Cost

Rules:
    No duplicate actions allowed.
"""

import os
import time
import logging

import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.dirname(BASE_DIR)

OUT_DIR = os.path.join(PROJECT_DIR, "DataFrames")

LOG_FILE = os.path.join(OUT_DIR, "pipeline_log.txt")

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
# LOAD
# ==========================================================


def load_data():

    input_path = os.path.join(OUT_DIR, "action_scores.csv")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing file: {input_path}")

    df = pd.read_csv(input_path)

    logger.info(f"Loaded {len(df)} scored actions.")

    return df


# ==========================================================
# HELPERS
# ==========================================================


def action_key(row):

    return (row["action_type"], int(row["planet_num"]))


def build_action_label(row):

    action_type = row["action_type"]

    planet_num = int(row["planet_num"])

    planet_name = row["planet_name"]

    if action_type == "unlock":

        return f"Unlock Planet " f"{planet_num} " f"{planet_name}"

    elif action_type == "mining":

        return f"Mining Upgrade " f"Planet " f"{planet_num} " f"{planet_name}"

    elif action_type == "cargo":

        return f"Cargo Upgrade " f"Planet " f"{planet_num} " f"{planet_name}"

    elif action_type == "speed":

        return f"Speed Upgrade " f"Planet " f"{planet_num} " f"{planet_name}"

    return "Unknown Action"


def blank_choice(reason):

    return {"reason": reason, "action": "", "cost": "", "gain": "", "summary": ""}


def select_first_unused(df, used_actions):

    for _, row in df.iterrows():

        key = action_key(row)

        if key not in used_actions:

            used_actions.add(key)

            return row

    return None


# ==========================================================
# BUILD CHOICES
# ==========================================================


def build_choices(df: pd.DataFrame) -> pd.DataFrame:

    if df is None or df.empty:
        return pd.DataFrame(
            [
                blank_choice("ROI"),
                blank_choice("Hybrid"),
                blank_choice("Breakeven"),
                blank_choice("Cost"),
            ]
        )

    df = df.copy()
    choices = []

    used_actions = set()

    # --------------------------------------
    # ROI
    # --------------------------------------

    roi_df = df.sort_values("roi_score", ascending=False)

    row = select_first_unused(roi_df, used_actions)

    if row is None:

        choices.append(blank_choice("ROI"))

    else:

        choices.append(
            {
                "reason": "ROI",
                "action": build_action_label(row),
                "cost": row["cost"],
                "gain": row["gain"],
                "summary": f"ROI " f"{row['roi_percent']:.1f}%",
            }
        )

    # --------------------------------------
    # HYBRID
    # --------------------------------------

    hybrid_df = df.sort_values("hybrid_score", ascending=False)

    row = select_first_unused(hybrid_df, used_actions)

    if row is None:

        choices.append(blank_choice("Hybrid"))

    else:

        choices.append(
            {
                "reason": "Hybrid",
                "action": build_action_label(row),
                "cost": row["cost"],
                "gain": row["gain"],
                "summary": f"Hybrid " f"{row['hybrid_score']:.1f}",
            }
        )

    # --------------------------------------
    # BREAKEVEN
    # --------------------------------------

    breakeven_df = df.sort_values("breakeven_seconds", ascending=True)

    row = select_first_unused(breakeven_df, used_actions)

    if row is None:

        choices.append(blank_choice("Breakeven"))

    else:

        choices.append(
            {
                "reason": "Breakeven",
                "action": build_action_label(row),
                "cost": row["cost"],
                "gain": row["gain"],
                "summary": row["breakeven_display"],
            }
        )

    # --------------------------------------
    # COST
    # --------------------------------------

    cost_df = df.sort_values("cost", ascending=True)

    row = select_first_unused(cost_df, used_actions)

    if row is None:

        choices.append(blank_choice("Cost"))

    else:

        choices.append(
            {
                "reason": "Cost",
                "action": build_action_label(row),
                "cost": row["cost"],
                "gain": row["gain"],
                "summary": "Lowest Cost",
            }
        )

    return pd.DataFrame(choices)


# ==========================================================
# SAVE
# ==========================================================


def save_data(df: pd.DataFrame):

    output_path = os.path.join(OUT_DIR, "choices.csv")

    df.to_csv(output_path, index=False)

    logger.info(f"Created choices.csv " f"with {len(df)} choices.")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting decision_engine pipeline.")

    try:

        df = load_data()

        choices_df = build_choices(df)

        save_data(choices_df)

        runtime = time.time() - start_time

        logger.info(
            f"decision_engine completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"decision_engine failed: {e}")

        raise
