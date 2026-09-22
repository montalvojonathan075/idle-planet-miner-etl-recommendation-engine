"""
planet_worth.py
---------------

Combines cleaned planets + ores into one dataset.
Calculates planet_worth and outputs planet_data.csv.
Removes intermediate df_planets.csv and df_ores.csv after success.

Assumptions:
- Input files have already been validated by load_and_clean.py
- No duplicate validation is performed here
- This script focuses on business transformations only
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
# BUSINESS LOGIC
# ==========================================================


def calculate_planet_worth(row: pd.Series, ore_worth: dict) -> float:
    """
    Calculate weighted ore value for a planet.

    Planet Worth =
    (Ore1 Yield × Ore1 Value) +
    (Ore2 Yield × Ore2 Value) +
    (Ore3 Yield × Ore3 Value)
    """

    worth = 0.0

    for i in range(1, 4):

        ore_col = f"ore_{i}"
        yield_col = f"ore_{i}_yield"

        ore_symbol = row[ore_col]

        if ore_symbol in ore_worth:

            worth += row[yield_col] * ore_worth[ore_symbol]

    return worth


def build_planet_data(df_planets: pd.DataFrame, df_ores: pd.DataFrame) -> pd.DataFrame:
    """
    Build final planet dataset.
    """

    logger.info("Building ore worth lookup.")

    ore_worth = df_ores.set_index("symbol")["base_amount"].to_dict()

    logger.info(f"Loaded {len(ore_worth)} ore values.")

    logger.info("Calculating planet worth.")

    df_planets["planet_worth_num"] = df_planets.apply(
        lambda row: calculate_planet_worth(row, ore_worth), axis=1
    )

    df_final = df_planets[
        [
            "planet_num",
            "name",
            "unlock_price",
            "distance",
            "planet_worth_num",
        ]
    ].copy()

    df_final.rename(columns={"name": "planet_name"}, inplace=True)

    logger.info(f"Created planet_data for " f"{len(df_final)} planets.")

    return df_final


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    logger.info("Starting planet_worth pipeline.")

    planets_file = os.path.join(OUT_DIR, "df_planets.csv")

    ores_file = os.path.join(OUT_DIR, "df_ores.csv")

    planet_data_file = os.path.join(OUT_DIR, "planet_data.csv")

    try:

        logger.info("Loading cleaned datasets.")

        df_planets = pd.read_csv(planets_file)

        df_ores = pd.read_csv(ores_file)

        logger.info(f"Loaded {len(df_planets)} planets.")

        logger.info(f"Loaded {len(df_ores)} ores.")

        df_final = build_planet_data(df_planets, df_ores)

        df_final.to_csv(planet_data_file, index=False)

        logger.info("Created planet_data.csv")

        # -------------------------------------
        # Remove intermediates only after
        # successful save
        # -------------------------------------

        if os.path.exists(planet_data_file):

            try:

                if os.path.exists(planets_file):
                    os.remove(planets_file)

                if os.path.exists(ores_file):
                    os.remove(ores_file)

                logger.info("Removed " "df_planets.csv and " "df_ores.csv")

            except Exception as e:

                logger.warning(f"Could not remove " f"intermediate files: " f"{e}")

        runtime = time.time() - start_time

        logger.info(
            f"planet_worth completed " f"successfully in " f"{runtime:.2f} seconds."
        )

    except Exception as e:

        logger.error(f"planet_worth failed: {e}")

        raise
