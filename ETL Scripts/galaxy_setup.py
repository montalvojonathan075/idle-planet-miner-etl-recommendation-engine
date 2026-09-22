"""
galaxy_setup.py

Handles:

1. Continue Existing Galaxy
2. Start New Galaxy
3. Update Existing Galaxy
4. Exit

Updates:
    planet_levels.csv

Returns:
    continue
    exit
"""

import os
import sys

import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(PROJECT_DIR, "DataFrames")

PLANET_LEVELS = os.path.join(DATA_DIR, "planet_levels.csv")

PLANET_DATA = os.path.join(DATA_DIR, "planet_data.csv")

# ==========================================================
# HELPERS
# ==========================================================


def load_levels():

    if not os.path.exists(PLANET_LEVELS):
        raise FileNotFoundError("planet_levels.csv not found.")

    return pd.read_csv(PLANET_LEVELS)


def load_planets():

    if not os.path.exists(PLANET_DATA):
        raise FileNotFoundError("planet_data.csv not found.")

    return pd.read_csv(PLANET_DATA)


def save_levels(df):

    df.to_csv(PLANET_LEVELS, index=False)


# ==========================================================
# DEFAULT DETECTION
# ==========================================================


def is_default_galaxy(df):

    unlocked = df["unlocked"].astype(bool).sum()

    total_levels = (
        df["mining_level"].sum() + df["speed_level"].sum() + df["cargo_level"].sum()
    )

    return unlocked <= 1 and total_levels == 0


# ==========================================================
# NEW GALAXY
# ==========================================================


def create_new_galaxy():

    df = load_levels()

    df["unlocked"] = False

    df["mining_level"] = 0

    df["speed_level"] = 0

    df["cargo_level"] = 0

    planet_1 = df["planet_num"] == 1

    df.loc[planet_1, "unlocked"] = True

    save_levels(df)

    print()

    print("New galaxy created.")

    return "continue"


# ==========================================================
# UPDATE GALAXY
# ==========================================================


def update_galaxy():

    levels_df = load_levels()

    planet_df = load_planets()

    print()

    highest = input("Highest unlocked planet: ").strip()

    if highest.lower() == "exit":

        return "exit"

    highest = int(highest)

    levels_df["unlocked"] = False

    levels_df["mining_level"] = 0

    levels_df["speed_level"] = 0

    levels_df["cargo_level"] = 0

    for planet_num in range(1, highest + 1):

        planet_row = planet_df[planet_df["planet_num"] == planet_num]

        if planet_row.empty:

            continue

        planet_name = planet_row.iloc[0]["name"]

        print()

        print(f"Planet {planet_num}" f" - " f"{planet_name}")

        print("Mining, Speed, Cargo")

        while True:

            raw = input("> ").strip()

            if raw.lower() == "exit":

                return "exit"

            try:

                values = [int(x.strip()) for x in raw.split(",")]

                if len(values) != 3:

                    raise ValueError

                mining = values[0]

                speed = values[1]

                cargo = values[2]

                break

            except:

                print()

                print("Invalid format.")

                print("Example:")

                print("15,2,3")

        idx = levels_df["planet_num"] == planet_num

        levels_df.loc[idx, "unlocked"] = True

        levels_df.loc[idx, "mining_level"] = mining

        levels_df.loc[idx, "speed_level"] = speed

        levels_df.loc[idx, "cargo_level"] = cargo

    save_levels(levels_df)

    print()

    print("Galaxy updated.")

    return "continue"


# ==========================================================
# MENU
# ==========================================================


def show_menu():

    df = load_levels()

    default = is_default_galaxy(df)

    print()

    print("=" * 40)

    print("Idle Planet Miner Optimizer")

    print("=" * 40)

    print()

    if default:

        print("1. New Galaxy")

        print("2. Update Galaxy")

        print("3. Exit")

        print()

        selection = input("Selection: ").strip()

        if selection == "1":

            return create_new_galaxy()

        if selection == "2":

            return update_galaxy()

        if selection == "3":

            return "exit"

    else:

        print("1. Continue Existing Galaxy")

        print("2. New Galaxy")

        print("3. Update Existing Galaxy")

        print("4. Exit")

        print()

        selection = input("Selection: ").strip()

        if selection == "1":

            return "continue"

        if selection == "2":

            return create_new_galaxy()

        if selection == "3":

            return update_galaxy()

        if selection == "4":

            return "exit"

    print()

    print("Invalid selection.")

    return show_menu()


# ==========================================================
# ENTRY POINT
# ==========================================================


def run():

    return show_menu()


if __name__ == "__main__":

    result = run()

    if result == "exit":

        sys.exit()
