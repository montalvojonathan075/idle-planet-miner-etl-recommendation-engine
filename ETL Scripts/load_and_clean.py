"""
load_and_clean.py
-----------------

Loads raw tab-separated data files, applies cleaning functions,
validates data quality, and saves cleaned DataFrames to CSV.

Features
--------
- Loads Planets.txt and Ores.txt from Raw Data/
- Cleans currency, yields, scientific notation
- Standardizes column names
- Validates required schema
- Validates business rules
- Validates planet yield percentages
- Validates ore symbols
- Validates planet numbering
- Saves cleaned DataFrames to DataFrames/
- Logs all pipeline activity
- Tracks runtime
"""

import os
import time
import logging
from typing import Dict, List

import pandas as pd

# ==========================================================
# PATH CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "Raw Data")
OUT_DIR = os.path.join(BASE_DIR, "DataFrames")
LOG_FILE = os.path.join(OUT_DIR, "pipeline_log.txt")

os.makedirs(OUT_DIR, exist_ok=True)

# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers.clear()

file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ==========================================================
# CLEANING FUNCTIONS
# ==========================================================


def clean_currency(series: pd.Series) -> pd.Series:
    """
    Clean currency-like values into floats.
    """

    return (
        series.astype(str)
        .str.strip()
        .replace(
            {
                r"\$": "",
                ",": "",
                "-": "0",
                "None": "0",
                "NaN": "0",
                "—": "0",
            },
            regex=True,
        )
        .replace("", "0")
        .astype(float)
        .fillna(0.0)
    )


def clean_yield(series: pd.Series) -> pd.Series:
    """
    Convert percentage strings to decimal values.

    Example:
        80% -> 0.80
    """

    return (
        series.astype(str)
        .str.strip()
        .str.replace("%", "", regex=False)
        .replace("", "0")
        .astype(float)
        .fillna(0.0)
        / 100.0
    )


def clean_scientific(series: pd.Series) -> pd.Series:
    """
    Convert scientific notation strings into floats.
    """

    return pd.to_numeric(series.astype(str).str.strip(), errors="coerce").fillna(0.0)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert columns to lowercase snake_case.
    """

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("#", "num")
        .str.replace(r"[^a-z0-9_]", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )

    logger.info(f"Standardized columns: {list(df.columns)}")

    return df


def convert_numeric(df: pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
    """
    Convert columns to numeric values.
    """

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def clean_ore_columns(df: pd.DataFrame, ore_cols=None) -> pd.DataFrame:
    """
    Standardize ore columns.
    """

    if ore_cols is None:
        ore_cols = ["ore_1", "ore_2", "ore_3"]

    for col in ore_cols:

        if col in df.columns:

            df[col] = df[col].fillna("").astype(str).str.strip()

    return df


# ==========================================================
# VALIDATION FUNCTIONS
# ==========================================================


def validate_columns(df: pd.DataFrame, required_cols, aliases=None):
    """
    Validate required schema.
    """

    if aliases:
        df.rename(columns=aliases, inplace=True)

    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    logger.info("Schema validation passed.")


def validate_business_rules(df_planets: pd.DataFrame):
    """
    Validate business logic rules.
    """

    if (df_planets["unlock_price"] <= 0).any():

        invalid_count = (df_planets["unlock_price"] <= 0).sum()

        raise ValueError(f"{invalid_count} invalid unlock prices found.")

    if (df_planets["distance"] <= 0).any():

        invalid_count = (df_planets["distance"] <= 0).sum()

        raise ValueError(f"{invalid_count} invalid distances found.")

    logger.info("Business rule validation passed.")


def validate_planet_numbers(df_planets: pd.DataFrame):
    """
    Validate planet numbers are unique and positive.
    """

    if (df_planets["planet_num"] <= 0).any():

        invalid_count = (df_planets["planet_num"] <= 0).sum()

        raise ValueError(f"{invalid_count} invalid planet numbers found.")

    if df_planets["planet_num"].duplicated().any():

        duplicate_count = df_planets["planet_num"].duplicated().sum()

        raise ValueError(f"{duplicate_count} duplicate planet numbers found.")

    logger.info("Planet number validation passed.")


def validate_ore_symbols(df_ores: pd.DataFrame):
    """
    Ensure ore symbols remain unique.
    """

    if df_ores["symbol"].duplicated().any():

        duplicate_count = df_ores["symbol"].duplicated().sum()

        raise ValueError(f"{duplicate_count} duplicate ore symbols found.")

    logger.info("Ore symbol validation passed.")


def validate_planet_yields(df_planets: pd.DataFrame):
    """
    Validate ore yields total roughly 100%.
    """

    yield_cols = ["ore_1_yield", "ore_2_yield", "ore_3_yield"]

    existing_cols = [c for c in yield_cols if c in df_planets.columns]

    if not existing_cols:
        return

    totals = df_planets[existing_cols].sum(axis=1)

    invalid = df_planets[(totals < 0.99) | (totals > 1.01)]

    if not invalid.empty:

        raise ValueError(
            f"Found {len(invalid)} planets " "with yield totals not equal to 100%."
        )

    logger.info("Yield validation passed.")


# ==========================================================
# ETL PIPELINE
# ==========================================================


def load_and_clean(data_dir=DATA_DIR, out_dir=OUT_DIR) -> Dict[str, pd.DataFrame]:

    start_time = time.time()

    logger.info("Starting load_and_clean pipeline.")

    try:

        df_planets = pd.read_csv(os.path.join(data_dir, "Planets.txt"), sep="\t")

        df_ores = pd.read_csv(os.path.join(data_dir, "Ores.txt"), sep="\t")

    except FileNotFoundError as e:

        logger.error(f"Missing required input file: {e}")

        raise

    except Exception as e:

        logger.error(f"Unexpected file loading error: {e}")

        raise

    # ------------------------------------------------------
    # Standardize Columns
    # ------------------------------------------------------

    df_planets = standardize_columns(df_planets)

    df_ores = standardize_columns(df_ores)

    # ------------------------------------------------------
    # Schema Validation
    # ------------------------------------------------------

    validate_columns(
        df_planets,
        {
            "planet_num",
            "name",
            "telescope",
            "unlock_price",
            "distance",
        },
    )

    validate_columns(
        df_ores,
        {
            "ore",
            "symbol",
            "stars",
            "base_amount",
        },
    )

    # ------------------------------------------------------
    # Ore Cleaning
    # ------------------------------------------------------

    df_ores["base_amount"] = clean_currency(df_ores["base_amount"])

    df_ores = convert_numeric(df_ores, ["stars"])

    # ------------------------------------------------------
    # Planet Cleaning
    # ------------------------------------------------------

    df_planets["unlock_price"] = clean_scientific(df_planets["unlock_price"])

    df_planets["distance"] = pd.to_numeric(df_planets["distance"], errors="coerce")

    df_planets["planet_num"] = pd.to_numeric(
        df_planets["planet_num"], errors="coerce"
    ).astype("Int64")

    for col in [
        "ore_1_yield",
        "ore_2_yield",
        "ore_3_yield",
    ]:

        if col in df_planets.columns:

            df_planets[col] = clean_yield(df_planets[col])

    df_planets = clean_ore_columns(df_planets)

    # ------------------------------------------------------
    # Data Validation
    # ------------------------------------------------------

    validate_business_rules(df_planets)

    validate_planet_numbers(df_planets)

    validate_ore_symbols(df_ores)

    validate_planet_yields(df_planets)

    # ------------------------------------------------------
    # Save Outputs
    # ------------------------------------------------------

    planets_path = os.path.join(out_dir, "df_planets.csv")

    ores_path = os.path.join(out_dir, "df_ores.csv")

    df_planets.to_csv(planets_path, index=False)

    df_ores.to_csv(ores_path, index=False)

    # ------------------------------------------------------
    # Data Quality Summary
    # ------------------------------------------------------

    logger.info("---------- Data Quality Summary ----------")

    logger.info(f"Planet Records: {len(df_planets)}")

    logger.info(f"Ore Records: {len(df_ores)}")

    logger.info(f"Unique Planets: " f"{df_planets['planet_num'].nunique()}")

    logger.info(f"Unique Ore Symbols: " f"{df_ores['symbol'].nunique()}")

    # ------------------------------------------------------
    # Final Logging
    # ------------------------------------------------------

    runtime = time.time() - start_time

    logger.info(f"Loaded and cleaned {len(df_planets)} planets.")

    logger.info(f"Loaded and cleaned {len(df_ores)} ores.")

    logger.info(f"Output saved to: {out_dir}")

    logger.info(f"Pipeline completed successfully " f"in {runtime:.2f} seconds.")

    return {
        "planets": df_planets,
        "ores": df_ores,
    }


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    load_and_clean()
