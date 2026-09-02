"""
===============================================================================
File        : 06_train_test_split.py
Project     : CyberShield AI
Description : Creates stratified training, validation, and testing datasets
              from the selected CICIDS2017 features.

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
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =============================================================================
# Configuration
# =============================================================================

RANDOM_STATE = 42

TEST_SIZE = 0.15
VALIDATION_SIZE = 0.15

# Final proportions:
# Train      = 70%
# Validation = 15%
# Test       = 15%


# =============================================================================
# Main Function
# =============================================================================

def main():

    start_time = time.time()

    try:

        logging.info("Starting Train/Validation/Test Split...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        DATASET_PATH = (
            BASE_DIR
            / "datasets"
            / "processed"
            / "engineered_dataset.csv"
        )

        FEATURE_LIST_PATH = (
            BASE_DIR
            / "evaluation"
            / "Selected_Features.txt"
        )

        OUTPUT_DIR = (
            BASE_DIR
            / "datasets"
            / "final"
        )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        EVALUATION_DIR = BASE_DIR / "evaluation"
        EVALUATION_DIR.mkdir(exist_ok=True)

        REPORT_PATH = (
            EVALUATION_DIR
            / "Train_Test_Split_Report.txt"
        )

        LABEL_MAPPING_PATH = (
            EVALUATION_DIR
            / "Label_Mapping.csv"
        )

        # =====================================================================
        # Validate Input Files
        # =====================================================================

        if not DATASET_PATH.exists():

            logging.error(
                f"Engineered dataset not found:\n{DATASET_PATH}"
            )

            return

        if not FEATURE_LIST_PATH.exists():

            logging.error(
                f"Selected feature list not found:\n"
                f"{FEATURE_LIST_PATH}"
            )

            return

        # =====================================================================
        # Load Selected Feature Names
        # =====================================================================

        logging.info("Loading selected feature list...")

        with open(
            FEATURE_LIST_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            selected_features = [
                line.strip()
                for line in f
                if line.strip()
            ]

        logging.info(
            f"Selected features: {len(selected_features)}"
        )

        # =====================================================================
        # Load Dataset
        # =====================================================================

        logging.info(
            "Loading engineered dataset..."
        )

        columns_to_load = selected_features + [
            "Label"
        ]

        df = pd.read_csv(
            DATASET_PATH,
            usecols=columns_to_load
        )

        logging.info(
            f"Dataset loaded: {df.shape}"
        )

        # =====================================================================
        # Validate Columns
        # =====================================================================

        missing_features = [
            feature
            for feature in selected_features
            if feature not in df.columns
        ]

        if missing_features:

            logging.error(
                f"Missing selected features: "
                f"{missing_features}"
            )

            return

        # =====================================================================
        # Separate Features and Target
        # =====================================================================

        X = df[selected_features].copy()

        y = df["Label"].astype(str).str.strip()

        logging.info(
            f"Feature matrix shape: {X.shape}"
        )

        # =====================================================================
        # Check Data Quality
        # =====================================================================

        logging.info(
            "Checking feature matrix..."
        )

        X = X.replace(
            [np.inf, -np.inf],
            np.nan
        )

        missing_values = int(
            X.isna().sum().sum()
        )

        if missing_values > 0:

            logging.warning(
                f"Found {missing_values} missing values. "
                f"Replacing with zero."
            )

            X = X.fillna(0)

        # =====================================================================
        # Encode Labels
        # =====================================================================

        logging.info(
            "Encoding target labels..."
        )

        label_encoder = LabelEncoder()

        y_encoded = label_encoder.fit_transform(y)

        label_mapping = pd.DataFrame(
            {
                "Encoded_Label": range(
                    len(label_encoder.classes_)
                ),
                "Original_Label": label_encoder.classes_
            }
        )

        label_mapping.to_csv(
            LABEL_MAPPING_PATH,
            index=False
        )

        logging.info(
            f"Number of classes: "
            f"{len(label_encoder.classes_)}"
        )

        # =====================================================================
        # Display Class Distribution
        # =====================================================================

        class_distribution = pd.Series(
            y_encoded
        ).value_counts().sort_index()

        print("\n" + "=" * 80)
        print("CLASS DISTRIBUTION")
        print("=" * 80)

        for encoded_label, count in class_distribution.items():

            original_label = (
                label_encoder.inverse_transform(
                    [encoded_label]
                )[0]
            )

            percentage = (
                count / len(y_encoded)
            ) * 100

            print(
                f"{encoded_label:2d} | "
                f"{original_label:<30} | "
                f"{count:>10,} | "
                f"{percentage:6.2f}%"
            )

        # =====================================================================
        # First Split: Train + Temporary
        # =====================================================================

        logging.info(
            "Creating stratified train/test split..."
        )

        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y_encoded,
            test_size=TEST_SIZE + VALIDATION_SIZE,
            random_state=RANDOM_STATE,
            stratify=y_encoded
        )

        # =====================================================================
        # Second Split: Validation + Test
        # =====================================================================

        # Temporary set = 30% of total.
        #
        # We need validation = 15%
        # Test = 15%
        #
        # Therefore validation is 50% of temporary set.

        validation_fraction = (
            VALIDATION_SIZE
            / (TEST_SIZE + VALIDATION_SIZE)
        )

        logging.info(
            "Creating stratified validation/test split..."
        )

        X_validation, X_test, y_validation, y_test = (
            train_test_split(
                X_temp,
                y_temp,
                test_size=1 - validation_fraction,
                random_state=RANDOM_STATE,
                stratify=y_temp
            )
        )

        # =====================================================================
        # Convert to Efficient NumPy Types
        # =====================================================================

        X_train = X_train.to_numpy(
            dtype=np.float32
        )

        X_validation = X_validation.to_numpy(
            dtype=np.float32
        )

        X_test = X_test.to_numpy(
            dtype=np.float32
        )

        y_train = np.asarray(
            y_train,
            dtype=np.int8
        )

        y_validation = np.asarray(
            y_validation,
            dtype=np.int8
        )

        y_test = np.asarray(
            y_test,
            dtype=np.int8
        )

        # =====================================================================
        # Save Data
        # =====================================================================

        logging.info(
            "Saving train/validation/test datasets..."
        )

        np.save(
            OUTPUT_DIR / "X_train.npy",
            X_train
        )

        np.save(
            OUTPUT_DIR / "X_validation.npy",
            X_validation
        )

        np.save(
            OUTPUT_DIR / "X_test.npy",
            X_test
        )

        np.save(
            OUTPUT_DIR / "y_train.npy",
            y_train
        )

        np.save(
            OUTPUT_DIR / "y_validation.npy",
            y_validation
        )

        np.save(
            OUTPUT_DIR / "y_test.npy",
            y_test
        )

        # =====================================================================
        # Save Feature Names
        # =====================================================================

        with open(
            OUTPUT_DIR / "feature_names.txt",
            "w",
            encoding="utf-8"
        ) as f:

            for feature in selected_features:
                f.write(feature + "\n")

        # =====================================================================
        # Dataset Shapes
        # =====================================================================

        train_shape = X_train.shape
        validation_shape = X_validation.shape
        test_shape = X_test.shape

        # =====================================================================
        # Generate Report
        # =====================================================================

        end_time = time.time()

        execution_time = (
            end_time - start_time
        )

        with open(
            REPORT_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("=" * 80 + "\n")
            f.write(
                "CYBERSHIELD AI - TRAIN/TEST SPLIT REPORT\n"
            )
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Original Dataset Shape : "
                f"{df.shape}\n"
            )

            f.write(
                f"Number of Features : "
                f"{len(selected_features)}\n"
            )

            f.write(
                f"Number of Classes : "
                f"{len(label_encoder.classes_)}\n\n"
            )

            f.write("=" * 80 + "\n")
            f.write("DATASET SPLITS\n")
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Training Shape   : "
                f"{train_shape}\n"
            )

            f.write(
                f"Validation Shape : "
                f"{validation_shape}\n"
            )

            f.write(
                f"Testing Shape    : "
                f"{test_shape}\n\n"
            )

            f.write(
                "Split Ratio : 70% Train / "
                "15% Validation / 15% Test\n\n"
            )

            f.write("=" * 80 + "\n")
            f.write("LABEL MAPPING\n")
            f.write("=" * 80 + "\n\n")

            f.write(
                label_mapping.to_string(
                    index=False
                )
            )

            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write(
                f"Execution Time : "
                f"{execution_time:.2f} seconds\n"
            )

        # =====================================================================
        # Final Output
        # =====================================================================

        print("\n" + "=" * 80)
        print("TRAIN / VALIDATION / TEST SPLIT COMPLETED")
        print("=" * 80)

        print(
            f"Features        : "
            f"{len(selected_features)}"
        )

        print(
            f"Classes         : "
            f"{len(label_encoder.classes_)}"
        )

        print(
            f"Training        : "
            f"{train_shape}"
        )

        print(
            f"Validation      : "
            f"{validation_shape}"
        )

        print(
            f"Testing         : "
            f"{test_shape}"
        )

        print(
            f"Execution Time  : "
            f"{execution_time:.2f} seconds"
        )

        print("=" * 80)

        logging.info(
            "Train/Validation/Test split completed successfully."
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