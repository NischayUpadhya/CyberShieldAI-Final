"""
===============================================================================
File        : 10_xgboost_test.py
Project     : CyberShield AI
Description : Evaluates the trained XGBoost model on the held-out CICIDS2017
              test dataset.

Author      : Nischay Upadhya P
Version     : 1.0
===============================================================================
"""

import logging
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


# =============================================================================
# Logging
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

        logging.info("Starting XGBoost test evaluation...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        DATASET_DIR = BASE_DIR / "datasets" / "final"
        EVALUATION_DIR = BASE_DIR / "evaluation"
        MODEL_DIR = BASE_DIR / "models" / "saved"

        MODEL_PATH = (
            MODEL_DIR /
            "xgboost_baseline.joblib"
        )

        X_TEST_PATH = (
            DATASET_DIR /
            "X_test.npy"
        )

        Y_TEST_PATH = (
            DATASET_DIR /
            "y_test.npy"
        )

        LABEL_MAPPING_PATH = (
            EVALUATION_DIR /
            "Label_Mapping.csv"
        )

        # =====================================================================
        # Validate Files
        # =====================================================================

        required_files = [
            MODEL_PATH,
            X_TEST_PATH,
            Y_TEST_PATH,
            LABEL_MAPPING_PATH,
        ]

        for file_path in required_files:

            if not file_path.exists():

                raise FileNotFoundError(
                    f"Required file not found:\n{file_path}"
                )

        # =====================================================================
        # Load Model
        # =====================================================================

        logging.info(
            "Loading trained XGBoost model..."
        )

        model = joblib.load(
            MODEL_PATH
        )

        logging.info(
            "XGBoost model loaded successfully."
        )

        # =====================================================================
        # Load Test Data
        # =====================================================================

        logging.info(
            "Loading test dataset..."
        )

        X_test = np.load(
            X_TEST_PATH
        )

        y_test = np.load(
            Y_TEST_PATH
        )

        logging.info(
            f"Test data shape: {X_test.shape}"
        )

        # =====================================================================
        # Load Label Mapping
        # =====================================================================

        label_mapping = pd.read_csv(
            LABEL_MAPPING_PATH
        )

        label_names = dict(
            zip(
                label_mapping["Encoded_Label"],
                label_mapping["Original_Label"]
            )
        )

        # =====================================================================
        # Generate Predictions
        # =====================================================================

        logging.info(
            "Generating XGBoost test predictions..."
        )

        y_pred = model.predict(
            X_test
        )

        logging.info(
            "Test predictions generated."
        )

        # =====================================================================
        # Overall Metrics
        # =====================================================================

        accuracy = accuracy_score(
            y_test,
            y_pred
        )

        macro_precision = precision_score(
            y_test,
            y_pred,
            average="macro",
            zero_division=0
        )

        macro_recall = recall_score(
            y_test,
            y_pred,
            average="macro",
            zero_division=0
        )

        macro_f1 = f1_score(
            y_test,
            y_pred,
            average="macro",
            zero_division=0
        )

        weighted_precision = precision_score(
            y_test,
            y_pred,
            average="weighted",
            zero_division=0
        )

        weighted_recall = recall_score(
            y_test,
            y_pred,
            average="weighted",
            zero_division=0
        )

        weighted_f1 = f1_score(
            y_test,
            y_pred,
            average="weighted",
            zero_division=0
        )

        # =====================================================================
        # Classification Report
        # =====================================================================

        target_labels = sorted(
            np.unique(
                np.concatenate(
                    (y_test, y_pred)
                )
            )
        )

        target_names = [
            label_names.get(
                int(label),
                str(label)
            )
            for label in target_labels
        ]

        report = classification_report(
            y_test,
            y_pred,
            labels=target_labels,
            target_names=target_names,
            zero_division=0
        )

        # =====================================================================
        # Confusion Matrix
        # =====================================================================

        cm = confusion_matrix(
            y_test,
            y_pred,
            labels=target_labels
        )

        confusion_df = pd.DataFrame(
            cm,
            index=target_names,
            columns=target_names
        )

        confusion_path = (
            EVALUATION_DIR /
            "XGBoost_Test_Confusion_Matrix.csv"
        )

        confusion_df.to_csv(
            confusion_path
        )

        # =====================================================================
        # Save Classification Report
        # =====================================================================

        report_path = (
            EVALUATION_DIR /
            "XGBoost_Test_Classification_Report.txt"
        )

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("=" * 80 + "\n")
            f.write(
                "CYBERSHIELD AI - XGBOOST TEST RESULTS\n"
            )
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Test Samples : "
                f"{len(y_test):,}\n"
            )

            f.write(
                f"Features : "
                f"{X_test.shape[1]}\n\n"
            )

            f.write("=" * 80 + "\n")
            f.write("OVERALL METRICS\n")
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Accuracy : "
                f"{accuracy:.6f}\n"
            )

            f.write(
                f"Macro Precision : "
                f"{macro_precision:.6f}\n"
            )

            f.write(
                f"Macro Recall : "
                f"{macro_recall:.6f}\n"
            )

            f.write(
                f"Macro F1 : "
                f"{macro_f1:.6f}\n"
            )

            f.write(
                f"Weighted Precision : "
                f"{weighted_precision:.6f}\n"
            )

            f.write(
                f"Weighted Recall : "
                f"{weighted_recall:.6f}\n"
            )

            f.write(
                f"Weighted F1 : "
                f"{weighted_f1:.6f}\n\n"
            )

            f.write("=" * 80 + "\n")
            f.write("CLASSIFICATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(report)

        # =====================================================================
        # Save Metrics CSV
        # =====================================================================

        metrics_df = pd.DataFrame(
            {
                "Metric": [
                    "Accuracy",
                    "Macro Precision",
                    "Macro Recall",
                    "Macro F1",
                    "Weighted Precision",
                    "Weighted Recall",
                    "Weighted F1",
                ],
                "Score": [
                    accuracy,
                    macro_precision,
                    macro_recall,
                    macro_f1,
                    weighted_precision,
                    weighted_recall,
                    weighted_f1,
                ],
            }
        )

        metrics_path = (
            EVALUATION_DIR /
            "XGBoost_Test_Metrics.csv"
        )

        metrics_df.to_csv(
            metrics_path,
            index=False
        )

        # =====================================================================
        # Execution Time
        # =====================================================================

        execution_time = (
            time.time() - start_time
        )

        # =====================================================================
        # Output
        # =====================================================================

        print("\n" + "=" * 80)
        print("XGBOOST TEST RESULTS")
        print("=" * 80)

        print(
            f"Accuracy           : "
            f"{accuracy:.4f}"
        )

        print(
            f"Macro Precision    : "
            f"{macro_precision:.4f}"
        )

        print(
            f"Macro Recall       : "
            f"{macro_recall:.4f}"
        )

        print(
            f"Macro F1           : "
            f"{macro_f1:.4f}"
        )

        print(
            f"Weighted Precision : "
            f"{weighted_precision:.4f}"
        )

        print(
            f"Weighted Recall    : "
            f"{weighted_recall:.4f}"
        )

        print(
            f"Weighted F1        : "
            f"{weighted_f1:.4f}"
        )

        print(
            f"\nExecution Time     : "
            f"{execution_time:.2f} seconds"
        )

        print("=" * 80)

        print("\nClassification Report")
        print("=" * 80)
        print(report)

        logging.info(
            "XGBoost test evaluation completed successfully."
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