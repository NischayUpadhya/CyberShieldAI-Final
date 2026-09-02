"""
===============================================================================
File        : 04_feature_engineering.py
Project     : CyberShield AI
Description : Performs feature engineering on the cleaned CICIDS2017 dataset.

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
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =============================================================================
# Helper Functions
# =============================================================================

def safe_divide(numerator, denominator):
    """
    Performs element-wise division while safely handling division by zero.
    """

    result = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(
            numerator,
            dtype=np.float64
        ),
        where=denominator != 0
    )

    return result


def create_engineered_features(df):
    """
    Creates additional network-flow features.
    """

    logging.info("Creating engineered network features...")

    # -------------------------------------------------------------------------
    # Packet Ratio
    # -------------------------------------------------------------------------

    if {
        "Total Fwd Packets",
        "Total Backward Packets"
    }.issubset(df.columns):

        df["Fwd_Bwd_Packet_Ratio"] = safe_divide(
            df["Total Fwd Packets"].to_numpy(),
            df["Total Backward Packets"].to_numpy()
        )

    # -------------------------------------------------------------------------
    # Byte Ratio
    # -------------------------------------------------------------------------

    if {
        "Total Length of Fwd Packets",
        "Total Length of Bwd Packets"
    }.issubset(df.columns):

        df["Fwd_Bwd_Byte_Ratio"] = safe_divide(
            df["Total Length of Fwd Packets"].to_numpy(),
            df["Total Length of Bwd Packets"].to_numpy()
        )

    # -------------------------------------------------------------------------
    # Packet Length Ratio
    # -------------------------------------------------------------------------

    if {
        "Fwd Packet Length Mean",
        "Bwd Packet Length Mean"
    }.issubset(df.columns):

        df["Fwd_Bwd_Avg_Packet_Length_Ratio"] = safe_divide(
            df["Fwd Packet Length Mean"].to_numpy(),
            df["Bwd Packet Length Mean"].to_numpy()
        )

    # -------------------------------------------------------------------------
    # Forward Packet Percentage
    # -------------------------------------------------------------------------

    if {
        "Total Fwd Packets",
        "Total Backward Packets"
    }.issubset(df.columns):

        total_packets = (
            df["Total Fwd Packets"]
            + df["Total Backward Packets"]
        )

        df["Fwd_Packet_Percentage"] = safe_divide(
            df["Total Fwd Packets"].to_numpy(),
            total_packets.to_numpy()
        )

    # -------------------------------------------------------------------------
    # Forward Byte Percentage
    # -------------------------------------------------------------------------

    if {
        "Total Length of Fwd Packets",
        "Total Length of Bwd Packets"
    }.issubset(df.columns):

        total_bytes = (
            df["Total Length of Fwd Packets"]
            + df["Total Length of Bwd Packets"]
        )

        df["Fwd_Byte_Percentage"] = safe_divide(
            df["Total Length of Fwd Packets"].to_numpy(),
            total_bytes.to_numpy()
        )

    # -------------------------------------------------------------------------
    # Flow Duration in Seconds
    # -------------------------------------------------------------------------

    if "Flow Duration" in df.columns:

        df["Flow_Duration_Seconds"] = (
            df["Flow Duration"] / 1_000_000
        )

    # -------------------------------------------------------------------------
    # Average Bytes per Packet
    # -------------------------------------------------------------------------

    if {
        "Total Length of Fwd Packets",
        "Total Length of Bwd Packets",
        "Total Fwd Packets",
        "Total Backward Packets"
    }.issubset(df.columns):

        total_bytes = (
            df["Total Length of Fwd Packets"]
            + df["Total Length of Bwd Packets"]
        )

        total_packets = (
            df["Total Fwd Packets"]
            + df["Total Backward Packets"]
        )

        df["Average_Bytes_Per_Packet"] = safe_divide(
            total_bytes.to_numpy(),
            total_packets.to_numpy()
        )

    # -------------------------------------------------------------------------
    # Active / Idle Ratio
    # -------------------------------------------------------------------------

    if {
        "Active Mean",
        "Idle Mean"
    }.issubset(df.columns):

        df["Active_Idle_Ratio"] = safe_divide(
            df["Active Mean"].to_numpy(),
            df["Idle Mean"].to_numpy()
        )

    # -------------------------------------------------------------------------
    # Forward / Backward Packet Rate Ratio
    # -------------------------------------------------------------------------

    if {
        "Fwd Packets/s",
        "Bwd Packets/s"
    }.issubset(df.columns):

        df["Fwd_Bwd_Packet_Rate_Ratio"] = safe_divide(
            df["Fwd Packets/s"].to_numpy(),
            df["Bwd Packets/s"].to_numpy()
        )

    logging.info("Engineered features created successfully.")

    return df


def create_attack_categories(df):
    """
    Creates a high-level attack category for analysis.

    Attack_Category is derived from Label and MUST NOT be used as
    a model input feature because it would cause target leakage.
    """

    logging.info("Creating attack categories...")

    def categorize(label):

        label = str(label).strip()

        if label == "BENIGN":
            return "BENIGN"

        if label.startswith("DoS"):
            return "DoS"

        if label == "DDoS":
            return "DDoS"

        if label == "PortScan":
            return "PortScan"

        if label in {"FTP-Patator", "SSH-Patator"}:
            return "BruteForce"

        if label.startswith("Web Attack"):
            return "WebAttack"

        if label == "Bot":
            return "Bot"

        if label == "Infiltration":
            return "Infiltration"

        if label == "Heartbleed":
            return "Heartbleed"

        return "Other"

    df["Attack_Category"] = df["Label"].map(categorize)

    logging.info("Attack categories created successfully.")

    return df


# =============================================================================
# Main Function
# =============================================================================

def main():

    start_time = time.time()

    try:

        logging.info("Starting Feature Engineering...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        INPUT_DATASET = (
            BASE_DIR
            / "datasets"
            / "processed"
            / "cleaned_dataset.csv"
        )

        OUTPUT_DIR = (
            BASE_DIR
            / "datasets"
            / "processed"
        )

        OUTPUT_DIR.mkdir(exist_ok=True)

        OUTPUT_DATASET = (
            OUTPUT_DIR
            / "engineered_dataset.csv"
        )

        EVALUATION_DIR = BASE_DIR / "evaluation"
        EVALUATION_DIR.mkdir(exist_ok=True)

        REPORT_PATH = (
            EVALUATION_DIR
            / "Feature_Engineering_Report.txt"
        )

        # =====================================================================
        # Check Input Dataset
        # =====================================================================

        if not INPUT_DATASET.exists():

            logging.error(
                f"Cleaned dataset not found:\n{INPUT_DATASET}"
            )

            return

        # =====================================================================
        # Load Dataset
        # =====================================================================

        logging.info("Loading cleaned dataset...")

        df = pd.read_csv(INPUT_DATASET)

        logging.info(
            f"Dataset loaded successfully: {df.shape}"
        )

        # =====================================================================
        # Clean Column Names
        # =====================================================================

        df.columns = df.columns.str.strip()

        # =====================================================================
        # Clean Labels
        # =====================================================================

        if "Label" not in df.columns:

            logging.error(
                "Target column 'Label' was not found."
            )

            return

        df["Label"] = (
            df["Label"]
            .astype(str)
            .str.strip()
        )

        # =====================================================================
        # Original Feature Count
        # =====================================================================

        original_column_count = len(df.columns)

        # =====================================================================
        # Create Engineered Features
        # =====================================================================

        df = create_engineered_features(df)

        # =====================================================================
        # Create Attack Categories
        # =====================================================================

        df = create_attack_categories(df)

        # =====================================================================
        # Handle Invalid Numeric Values
        # =====================================================================

        logging.info(
            "Checking engineered features for invalid values..."
        )

        numeric_columns = df.select_dtypes(
            include=[np.number]
        ).columns

        inf_count = np.isinf(
            df[numeric_columns]
        ).sum().sum()

        nan_count = df[numeric_columns].isna().sum().sum()

        if inf_count > 0:

            logging.warning(
                f"Found {inf_count} infinite values."
            )

            df[numeric_columns] = df[
                numeric_columns
            ].replace(
                [np.inf, -np.inf],
                np.nan
            )

        if nan_count > 0:

            logging.warning(
                f"Found {nan_count} NaN values."
            )

            df[numeric_columns] = df[
                numeric_columns
            ].fillna(0)

        # =====================================================================
        # Optimize Numeric Data Types
        # =====================================================================

        logging.info(
            "Optimizing numeric data types..."
        )

        for column in numeric_columns:

            if pd.api.types.is_float_dtype(
                df[column]
            ):

                df[column] = df[column].astype(
                    np.float32
                )

        # =====================================================================
        # Feature List
        # =====================================================================

        engineered_columns = [
            "Fwd_Bwd_Packet_Ratio",
            "Fwd_Bwd_Byte_Ratio",
            "Fwd_Bwd_Avg_Packet_Length_Ratio",
            "Fwd_Packet_Percentage",
            "Fwd_Byte_Percentage",
            "Flow_Duration_Seconds",
            "Average_Bytes_Per_Packet",
            "Active_Idle_Ratio",
            "Fwd_Bwd_Packet_Rate_Ratio"
        ]

        created_features = [
            column
            for column in engineered_columns
            if column in df.columns
        ]

        # =====================================================================
        # Save Dataset
        # =====================================================================

        logging.info(
            "Saving engineered dataset..."
        )

        df.to_csv(
            OUTPUT_DATASET,
            index=False
        )

        logging.info(
            f"Engineered dataset saved:\n{OUTPUT_DATASET}"
        )

        # =====================================================================
        # Generate Report
        # =====================================================================

        end_time = time.time()
        execution_time = end_time - start_time

        label_distribution = (
            df["Label"]
            .value_counts()
        )

        category_distribution = (
            df["Attack_Category"]
            .value_counts()
        )

        with open(
            REPORT_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("=" * 80 + "\n")
            f.write(
                "CYBERSHIELD AI - FEATURE ENGINEERING REPORT\n"
            )
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Original Shape : "
                f"({df.shape[0]}, "
                f"{original_column_count})\n"
            )

            f.write(
                f"Final Shape    : "
                f"{df.shape}\n\n"
            )

            f.write(
                f"Original Columns : "
                f"{original_column_count}\n"
            )

            f.write(
                f"Final Columns    : "
                f"{len(df.columns)}\n\n"
            )

            f.write("=" * 80 + "\n")
            f.write("ENGINEERED FEATURES\n")
            f.write("=" * 80 + "\n")

            for feature in created_features:
                f.write(f"- {feature}\n")

            f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("LABEL DISTRIBUTION\n")
            f.write("=" * 80 + "\n")

            f.write(
                str(label_distribution)
            )

            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("ATTACK CATEGORY DISTRIBUTION\n")
            f.write("=" * 80 + "\n")

            f.write(
                str(category_distribution)
            )

            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY\n")
            f.write("=" * 80 + "\n")

            f.write(
                f"Initial Infinite Values : "
                f"{inf_count}\n"
            )

            f.write(
                f"Initial NaN Values       : "
                f"{nan_count}\n"
            )

            f.write(
                f"Final Infinite Values    : "
                f"{np.isinf(df[numeric_columns]).sum().sum()}\n"
            )

            f.write(
                f"Final NaN Values         : "
                f"{df[numeric_columns].isna().sum().sum()}\n"
            )

            f.write("\n")

            f.write(
                "=" * 80 + "\n"
            )

            f.write(
                f"Execution Time : "
                f"{execution_time:.2f} seconds\n"
            )

        # =====================================================================
        # Final Output
        # =====================================================================

        print("\n" + "=" * 80)
        print("FEATURE ENGINEERING COMPLETED")
        print("=" * 80)

        print(
            f"Original Shape : "
            f"({df.shape[0]}, {original_column_count})"
        )

        print(
            f"Final Shape    : "
            f"{df.shape}"
        )

        print(
            f"New Features   : "
            f"{len(created_features)}"
        )

        print(
            f"Execution Time : "
            f"{execution_time:.2f} seconds"
        )

        print("=" * 80)

        logging.info(
            "Feature Engineering completed successfully."
        )

    except Exception as e:

        logging.exception(
            f"Unexpected error: {e}"
        )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()