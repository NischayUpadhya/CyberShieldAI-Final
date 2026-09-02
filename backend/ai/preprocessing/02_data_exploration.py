"""
===============================================================================
File        : 02_data_exploration.py
Project     : CyberShield AI
Description : Performs Exploratory Data Analysis (EDA) on the merged
              CICIDS2017 dataset and generates reports.

Author      : Nischay Upadhya P
Version     : 1.1
===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

import logging
import time
from pathlib import Path

import pandas as pd

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =============================================================================
# Main Function
# =============================================================================


def main():

    start_time = time.time()

    try:

        logging.info("Starting Exploratory Data Analysis...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        DATASET_PATH = (
            BASE_DIR /
            "datasets" /
            "processed" /
            "merged_dataset.csv"
        )

        EVALUATION_DIR = BASE_DIR / "evaluation"
        EVALUATION_DIR.mkdir(exist_ok=True)

        REPORT_PATH = EVALUATION_DIR / "EDA_Report.txt"
        SUMMARY_PATH = EVALUATION_DIR / "Summary_Statistics.csv"
        INFO_PATH = EVALUATION_DIR / "Dataset_Info.txt"
        COLUMNS_PATH = EVALUATION_DIR / "Column_Names.txt"

        # =====================================================================
        # Check Dataset
        # =====================================================================

        if not DATASET_PATH.exists():
            logging.error(f"Dataset not found:\n{DATASET_PATH}")
            return

        # =====================================================================
        # Load Dataset
        # =====================================================================

        logging.info("Loading merged dataset...")

        df = pd.read_csv(DATASET_PATH)

        df.columns = df.columns.str.strip()

        logging.info("Dataset loaded successfully.")

        # =====================================================================
        # Dataset Information
        # =====================================================================

        dataset_shape = df.shape
        total_columns = len(df.columns)

        memory_usage = (
            df.memory_usage(deep=True).sum()
            / 1024
            / 1024
        )

        datatype_summary = df.dtypes.value_counts()

        logging.info(f"Dataset Shape : {dataset_shape}")
        logging.info(f"Total Columns : {total_columns}")
        logging.info(f"Memory Usage  : {memory_usage:.2f} MB")

        print("=" * 80)
        print("DATASET INFORMATION")
        print("=" * 80)

        print(f"\nShape : {dataset_shape}")
        print(f"Total Columns : {total_columns}")

        print("\nFirst 10 Columns:")
        print(df.columns[:10].tolist())

        print("\nData Types Summary:")
        print(datatype_summary)

        print(f"\nMemory Usage : {memory_usage:.2f} MB")

        # =====================================================================
        # Missing Values
        # =====================================================================

        print("\n" + "=" * 80)
        print("MISSING VALUES")
        print("=" * 80)

        missing_values = df.isnull().sum()

        print(missing_values[missing_values > 0])

        # =====================================================================
        # Duplicate Rows
        # =====================================================================

        print("\n" + "=" * 80)
        print("DUPLICATE ROWS")
        print("=" * 80)

        duplicate_rows = df.duplicated().sum()

        print(duplicate_rows)

        # =====================================================================
        # Label Distribution
        # =====================================================================

        print("\n" + "=" * 80)
        print("LABEL DISTRIBUTION")
        print("=" * 80)

        label_distribution = df["Label"].value_counts()

        print(label_distribution)

        # =====================================================================
        # Summary Statistics
        # =====================================================================

        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)

        summary = df.describe().T

        print(summary.head())

        summary.to_csv(
            SUMMARY_PATH,
            index=True
        )

        logging.info("Summary statistics saved.")

        # =====================================================================
        # Dataset Info
        # =====================================================================

        with open(INFO_PATH, "w", encoding="utf-8") as f:
            df.info(buf=f, memory_usage="deep")

        logging.info("Dataset info saved.")

        # =====================================================================
        # Column Names
        # =====================================================================

        with open(COLUMNS_PATH, "w", encoding="utf-8") as f:
            for column in df.columns:
                f.write(column + "\n")

        logging.info("Column names saved.")

        # =====================================================================
        # Execution Time
        # =====================================================================

        end_time = time.time()
        execution_time = end_time - start_time

        # =====================================================================
        # Generate Report
        # =====================================================================

        with open(REPORT_PATH, "w", encoding="utf-8") as f:

            f.write("=" * 80 + "\n")
            f.write("CYBERSHIELD AI - EDA REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Dataset Shape : {dataset_shape}\n")
            f.write(f"Total Columns : {total_columns}\n")
            f.write(f"Memory Usage : {memory_usage:.2f} MB\n\n")

            f.write("=" * 80 + "\n")
            f.write("DATA TYPE SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(str(datatype_summary))
            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("MISSING VALUES\n")
            f.write("=" * 80 + "\n")
            f.write(str(missing_values[missing_values > 0]))
            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("DUPLICATE ROWS\n")
            f.write("=" * 80 + "\n")
            f.write(str(duplicate_rows))
            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("LABEL DISTRIBUTION\n")
            f.write("=" * 80 + "\n")
            f.write(str(label_distribution))
            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write(f"Execution Time : {execution_time:.2f} seconds\n")

        logging.info("EDA report generated successfully.")

        print("\n" + "=" * 80)
        print(f"Execution Time : {execution_time:.2f} seconds")
        print("=" * 80)

        logging.info("EDA completed successfully.")

    except Exception as e:
        logging.exception(f"Unexpected Error: {e}")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()