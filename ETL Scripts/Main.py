"""
main.py
-------

Runs the ETL pipeline in sequence.
"""

import os
import sys
import time
import logging
import subprocess

import questionnaire

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
# HELPERS
# ==========================================================


def run_script(script_path: str) -> bool:
    """
    Execute a pipeline script.

    Returns
    -------
    True if successful.
    False if failed.
    """

    script_name = os.path.basename(script_path)

    try:

        logger.info(f"Starting {script_name}")

        subprocess.run(
            [sys.executable, script_path],
            check=True,
            cwd=PROJECT_DIR,
        )

        logger.info(f"Completed {script_name}")

        return True

    except (subprocess.CalledProcessError, FileNotFoundError) as e:

        logger.error(f"Failed {script_name}: {e}")

        return False


# ==========================================================
# ETL PIPELINE
# ==========================================================


def run_etl_pipeline():

    scripts = [
        os.path.join(BASE_DIR, "load_and_clean.py"),
        os.path.join(BASE_DIR, "planet_worth.py"),
        os.path.join(BASE_DIR, "planet_levels.py"),
        os.path.join(BASE_DIR, "planet_metrics.py"),
        os.path.join(BASE_DIR, "possible_actions.py"),
        os.path.join(BASE_DIR, "action_gains.py"),
        os.path.join(BASE_DIR, "action_scores.py"),
        os.path.join(BASE_DIR, "decision_engine.py"),
    ]

    for script in scripts:

        success = run_script(script)

        if not success:

            raise RuntimeError(f"Pipeline halted at " f"{os.path.basename(script)}")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    logger.info("=================================")

    logger.info("Starting Idle Planet Miner Optimizer")

    logger.info("=================================")

    try:

        # ----------------------------------
        # STARTUP MENU (ONCE)
        # ----------------------------------

        startup_result = questionnaire.start_questionnaire()

        if startup_result == "exit":

            logger.info("User ended session.")

            raise SystemExit

        # ----------------------------------
        # RECOMMENDATION LOOP
        # ----------------------------------

        while True:

            start_time = time.time()

            run_etl_pipeline()

            runtime = time.time() - start_time

            logger.info(f"ETL Pipeline Completed " f"Successfully " f"({runtime:.2f}s)")

            result = questionnaire.recommendation_loop()

            if result == "exit":

                logger.info("User ended session.")

                break

            if result == "continue":

                logger.info("Refreshing ETL after " "player action.")

                continue

    except Exception as e:

        logger.error(f"Pipeline Failed: {e}")

        raise
