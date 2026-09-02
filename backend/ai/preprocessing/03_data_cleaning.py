"""
===============================================================================
File        : 03_data_cleaning.py
Project     : CyberShield AI
Description : Cleans the merged CICIDS2017 dataset.

Author      : Nischay Upadhya P
Version     : 1.0
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def main():

    start_time = time.time()

    try:

        logging.info("Starting Data Cleaning...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        INPUT_DATASET = (
            BASE_DIR /
            "datasets" /
            "processed" /
            "merged_dataset.csv"
        )

        OUTPUT_DIR = (
            BASE_DIR /
            "datasets" /
            "processed"
        )

        OUTPUT_DIR.mkdir(exist_ok=True)

        OUTPUT_DATASET = OUTPUT_DIR / "cleaned_dataset.csv"

        EVALUATION_DIR = BASE_DIR / "evaluation"
        EVALUATION_DIR.mkdir(exist_ok=True)

        REPORT_PATH = EVALUATION_DIR / "Cleaning_Report.txt"

        # =====================================================================
        # Load Dataset
        # =====================================================================

        if not INPUT_DATASET.exists():
            logging.error("Merged dataset not found.")
            return

        df = pd.read_csv(INPUT_DATASET)

        logging.info("Dataset loaded successfully.")

        # =====================================================================
        # Clean Column Names
        # =====================================================================

        df.columns = df.columns.str.strip()

        # =====================================================================
        # Replace Infinite Values
        # =====================================================================

        logging.info("Replacing infinite values...")

        inf_count = np.isinf(
            df.select_dtypes(include=[np.number])
        ).sum().sum()

        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True
        )

        # =====================================================================
        # Missing Values
        # =====================================================================

        missing_before = df.isnull().sum().sum()

        logging.info(f"Missing values before cleaning : {missing_before}")

        # Fill numeric missing values using median

        numeric_columns = df.select_dtypes(include=[np.number]).columns

        df[numeric_columns] = df[numeric_columns].fillna(
            df[numeric_columns].median()
        )

        missing_after = df.isnull().sum().sum()

        # =====================================================================
        # Remove Duplicate Rows
        # =====================================================================

        duplicate_rows = df.duplicated().sum()

        df.drop_duplicates(inplace=True)

        # =====================================================================
        # Remove Constant Columns
        # =====================================================================

        constant_columns = [
            col for col in df.columns
            if df[col].nunique() == 1
        ]

        df.drop(columns=constant_columns, inplace=True)

        # =====================================================================
        # Save Clean Dataset
        # =====================================================================

        df.to_csv(
            OUTPUT_DATASET,
            index=False
        )

        logging.info("Cleaned dataset saved successfully.")

        # =====================================================================
        # Generate Report
        # =====================================================================

        end_time = time.time()

        execution_time = end_time - start_time

        with open(REPORT_PATH, "w", encoding="utf-8") as f:

            f.write("=" * 80 + "\n")
            f.write("CYBERSHIELD AI - CLEANING REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Original Shape : {pd.read_csv(INPUT_DATASET).shape}\n")
            f.write(f"Final Shape    : {df.shape}\n\n")

            f.write(f"Infinite Values Found : {inf_count}\n")
            f.write(f"Missing Before : {missing_before}\n")
            f.write(f"Missing After  : {missing_after}\n\n")

            f.write(f"Duplicate Rows Removed : {duplicate_rows}\n\n")

            f.write("Constant Columns Removed\n")
            f.write(str(constant_columns))
            f.write("\n\n")

            f.write(f"Execution Time : {execution_time:.2f} seconds\n")

        logging.info("Cleaning report generated.")

        print("\n" + "=" * 80)
        print("DATA CLEANING COMPLETED")
        print("=" * 80)

        print(f"Final Dataset Shape : {df.shape}")
        print(f"Missing Values      : {missing_after}")
        print(f"Duplicate Removed   : {duplicate_rows}")
        print(f"Constant Columns    : {len(constant_columns)}")

        print("=" * 80)

    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    main()