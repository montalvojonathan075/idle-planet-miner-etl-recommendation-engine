"""
questionnaire.py
----------------

Handles:

1. Continue Existing Galaxy
2. New Galaxy
3. Update Existing Galaxy
4. Exit

Displays recommendations from:

    choices.csv

Updates:

    planet_levels.csv

Returns:

    "continue"
    "exit"
"""

import os
import pandas as pd

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(PROJECT_DIR, "DataFrames")

PLANET_LEVELS_FILE = os.path.join(DATA_DIR, "planet_levels.csv")

PLANET_DATA_FILE = os.path.join(DATA_DIR, "planet_data.csv")

CHOICES_FILE = os.path.join(DATA_DIR, "choices.csv")

# ==========================================================
# HELPERS
# ==========================================================


def exit_program():

    print("\nSession Ended.")

    print("Goodbye.\n")

    return "exit"


def normalize_menu_choice(value: str):

    value = value.strip().lower()

    if value in {"exit", "x"}:
        return "exit"

    return value


def load_levels():

    return pd.read_csv(PLANET_LEVELS_FILE)


def save_levels(df):

    df.to_csv(PLANET_LEVELS_FILE, index=False)


# ==========================================================
# NEW GALAXY
# ==========================================================


def reset_galaxy():

    df = load_levels()

    df["status"] = "Locked"

    df["mining_lvl"] = 0
    df["speed_lvl"] = 0
    df["cargo_lvl"] = 0

    save_levels(df)

    print("\nNew Galaxy Created.")


# ==========================================================
# UPDATE GALAXY
# ==========================================================


def update_galaxy():

    levels_df = load_levels()

    planets_df = pd.read_csv(PLANET_DATA_FILE)

    highest = int(input("\nHighest unlocked planet: "))

    levels_df["status"] = "Locked"

    levels_df["mining_lvl"] = 0
    levels_df["speed_lvl"] = 0
    levels_df["cargo_lvl"] = 0

    for planet_num in range(1, highest + 1):

        planet_name = planets_df.loc[
            planets_df["planet_num"] == planet_num, "planet_name"
        ].iloc[0]

        print()

        print(f"Planet {planet_num} - " f"{planet_name}")

        print("Mining, Speed, Cargo")

        raw = input("> ")

        mining, speed, cargo = [int(x.strip()) for x in raw.split(",")]

        mask = levels_df["planet_num"] == planet_num

        levels_df.loc[mask, "status"] = "Unlocked"

        levels_df.loc[mask, "mining_lvl"] = mining

        levels_df.loc[mask, "speed_lvl"] = speed

        levels_df.loc[mask, "cargo_lvl"] = cargo

    save_levels(levels_df)

    print("\nGalaxy Updated.")


# ==========================================================
# APPLY CHOICE
# ==========================================================


def apply_choice(selected):

    df = load_levels()

    action = selected["action"]

    if action.startswith("Unlock Planet"):

        planet_num = int(action.split()[2])

        mask = df["planet_num"] == planet_num

        df.loc[mask, "status"] = "Unlocked"

        df.loc[
            mask,
            [
                "mining_lvl",
                "speed_lvl",
                "cargo_lvl",
            ],
        ] = [1, 1, 1]

    elif action.startswith("Mining Upgrade"):

        planet_num = int(action.split()[3])

        mask = df["planet_num"] == planet_num

        df.loc[mask, "mining_lvl"] += 1

    elif action.startswith("Cargo Upgrade"):

        planet_num = int(action.split()[3])

        mask = df["planet_num"] == planet_num

        df.loc[mask, "cargo_lvl"] += 1

    elif action.startswith("Speed Upgrade"):

        planet_num = int(action.split()[3])

        mask = df["planet_num"] == planet_num

        df.loc[mask, "speed_lvl"] += 1

    save_levels(df)

    print()

    print("Progress Saved.")

    print("Refreshing Recommendations...")

    return "continue"


# ==========================================================
# DISPLAY RECOMMENDATIONS
# ==========================================================


def show_recommendations():

    df = pd.read_csv(CHOICES_FILE)

    print()

    print("=" * 40)

    print("Recommendations")

    print("=" * 40)

    labels = [
        "A. Best ROI",
        "B. Best Hybrid",
        "C. Best Breakeven",
        "D. Cheapest",
    ]

    for idx, row in df.iterrows():

        print()

        print(labels[idx])

        if pd.isna(row["action"]):

            print("No available action")

        else:

            print(row["action"])

            print(f"Cost: {row['cost']}")

            print(f"Gain: {row['gain']}")

            print(row["summary"])

    print()

    print("X. Exit")

    return df


# ==========================================================
# STARTUP MENU
# ==========================================================


def startup_menu():

    print()

    print("=" * 40)

    print("Idle Planet Miner Optimizer")

    print("=" * 40)

    print()

    print("1. Continue Existing Galaxy")

    print("2. New Galaxy")

    print("3. Update Existing Galaxy")

    print("4. Exit")

    value = normalize_menu_choice(input("\nSelection: "))

    if value == "1":

        return "continue"

    elif value == "2":

        reset_galaxy()

        return "continue"

    elif value == "3":

        update_galaxy()

        return "continue"

    elif value in {
        "4",
        "exit",
    }:

        return exit_program()

    print("\nInvalid selection.")

    return startup_menu()


# ==========================================================
# RECOMMENDATION LOOP
# ==========================================================


def recommendation_loop():

    choices_df = show_recommendations()

    selection = normalize_menu_choice(input("\nChoose A-D: "))

    if selection in {
        "x",
        "exit",
    }:

        return exit_program()

    mapping = {
        "a": 0,
        "1": 0,
        "b": 1,
        "2": 1,
        "c": 2,
        "3": 2,
        "d": 3,
        "4": 3,
    }

    if selection not in mapping:

        print("\nInvalid Choice.")

        return "continue"

    selected = choices_df.iloc[mapping[selection]]

    if pd.isna(selected["action"]) or selected["action"] == "":

        print("\nNo Action Available.")

        return "continue"

    return apply_choice(selected)


# ==========================================================
# STARTUP ONLY
# ==========================================================


def start_questionnaire():

    return startup_menu()


if __name__ == "__main__":

    start_questionnaire()
