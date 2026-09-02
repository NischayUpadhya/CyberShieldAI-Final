"""
===============================================================================
File        : 07_random_forest.py
Project     : CyberShield AI
Description : Trains and evaluates the Random Forest baseline model for
              CICIDS2017 multi-class network intrusion detection.

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

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =============================================================================
# Configuration
# =============================================================================

RANDOM_STATE = 42

N_ESTIMATORS = 50
MAX_DEPTH = 20

N_JOBS = -1


# =============================================================================
# Main
# =============================================================================

def main():

    start_time = time.time()

    try:

        logging.info("Starting Random Forest training...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        DATASET_DIR = BASE_DIR / "datasets" / "final"
        EVALUATION_DIR = BASE_DIR / "evaluation"
        MODEL_DIR = BASE_DIR / "models" / "saved"

        EVALUATION_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================================================================
        # Dataset Paths
        # =====================================================================

        X_TRAIN_PATH = DATASET_DIR / "X_train.npy"
        X_VALIDATION_PATH = DATASET_DIR / "X_validation.npy"

        Y_TRAIN_PATH = DATASET_DIR / "y_train.npy"
        Y_VALIDATION_PATH = DATASET_DIR / "y_validation.npy"

        FEATURE_NAMES_PATH = DATASET_DIR / "feature_names.txt"

        # =====================================================================
        # Load Data
        # =====================================================================

        logging.info("Loading training data...")

        X_train = np.load(
            X_TRAIN_PATH
        )

        y_train = np.load(
            Y_TRAIN_PATH
        )

        logging.info(
            f"Training data: {X_train.shape}"
        )

        logging.info("Loading validation data...")

        X_validation = np.load(
            X_VALIDATION_PATH
        )

        y_validation = np.load(
            Y_VALIDATION_PATH
        )

        logging.info(
            f"Validation data: {X_validation.shape}"
        )

        # =====================================================================
        # Load Feature Names
        # =====================================================================

        with open(
            FEATURE_NAMES_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            feature_names = [
                line.strip()
                for line in f
                if line.strip()
            ]

        logging.info(
            f"Number of features: {len(feature_names)}"
        )

        # =====================================================================
        # Create Label Mapping
        # =====================================================================

        label_mapping_path = (
            EVALUATION_DIR
            / "Label_Mapping.csv"
        )

        if label_mapping_path.exists():

            label_mapping = pd.read_csv(
                label_mapping_path
            )

            label_names = dict(
                zip(
                    label_mapping["Encoded_Label"],
                    label_mapping["Original_Label"]
                )
            )

        else:

            label_names = {
                int(label): str(label)
                for label in np.unique(y_train)
            }

        # =====================================================================
        # Model
        # =====================================================================

        logging.info(
            "Creating Random Forest model..."
        )

        model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=N_JOBS,
            verbose=1
        )

        # =====================================================================
        # Training
        # =====================================================================

        logging.info(
            "Training Random Forest..."
        )

        model.fit(
            X_train,
            y_train
        )

        logging.info(
            "Random Forest training completed."
        )

        # =====================================================================
        # Validation Prediction
        # =====================================================================

        logging.info(
            "Generating validation predictions..."
        )

        y_pred = model.predict(
            X_validation
        )

        # =====================================================================
        # Metrics
        # =====================================================================

        accuracy = accuracy_score(
            y_validation,
            y_pred
        )

        macro_f1 = f1_score(
            y_validation,
            y_pred,
            average="macro",
            zero_division=0
        )

        weighted_f1 = f1_score(
            y_validation,
            y_pred,
            average="weighted",
            zero_division=0
        )

        report = classification_report(
            y_validation,
            y_pred,
            zero_division=0
        )

        cm = confusion_matrix(
            y_validation,
            y_pred
        )

        # =====================================================================
        # Print Results
        # =====================================================================

        print("\n" + "=" * 80)
        print("RANDOM FOREST VALIDATION RESULTS")
        print("=" * 80)

        print(
            f"Accuracy    : {accuracy:.4f}"
        )

        print(
            f"Macro F1    : {macro_f1:.4f}"
        )

        print(
            f"Weighted F1 : {weighted_f1:.4f}"
        )

        print("\nClassification Report")
        print("=" * 80)
        print(report)

        # =====================================================================
        # Feature Importance
        # =====================================================================

        importance_df = pd.DataFrame(
            {
                "Feature": feature_names,
                "Importance": model.feature_importances_
            }
        )

        importance_df = importance_df.sort_values(
            by="Importance",
            ascending=False
        )

        importance_path = (
            EVALUATION_DIR
            / "RandomForest_Feature_Importance.csv"
        )

        importance_df.to_csv(
            importance_path,
            index=False
        )

        # =====================================================================
        # Confusion Matrix
        # =====================================================================

        class_names = [
            label_names.get(
                int(i),
                str(i)
            )
            for i in range(
                len(label_names)
            )
        ]

        confusion_df = pd.DataFrame(
            cm,
            index=class_names,
            columns=class_names
        )

        confusion_path = (
            EVALUATION_DIR
            / "RandomForest_Confusion_Matrix.csv"
        )

        confusion_df.to_csv(
            confusion_path
        )

        # =====================================================================
        # Save Model
        # =====================================================================

        model_path = (
            MODEL_DIR
            / "random_forest_baseline.joblib"
        )

        logging.info(
            "Saving Random Forest model..."
        )

        joblib.dump(
            model,
            model_path,
            compress=3
        )

        # =====================================================================
        # Save Validation Metrics
        # =====================================================================

        metrics_path = (
            EVALUATION_DIR
            / "RandomForest_Metrics.txt"
        )

        with open(
            metrics_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("=" * 80 + "\n")
            f.write(
                "CYBERSHIELD AI - RANDOM FOREST RESULTS\n"
            )
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Training Samples : "
                f"{len(X_train):,}\n"
            )

            f.write(
                f"Validation Samples : "
                f"{len(X_validation):,}\n"
            )

            f.write(
                f"Features : "
                f"{X_train.shape[1]}\n"
            )

            f.write(
                f"Trees : "
                f"{N_ESTIMATORS}\n"
            )

            f.write(
                f"Maximum Depth : "
                f"{MAX_DEPTH}\n\n"
            )

            f.write(
                f"Accuracy : "
                f"{accuracy:.6f}\n"
            )

            f.write(
                f"Macro F1 : "
                f"{macro_f1:.6f}\n"
            )

            f.write(
                f"Weighted F1 : "
                f"{weighted_f1:.6f}\n\n"
            )

            f.write(
                "Classification Report\n"
            )

            f.write(
                report
            )

            f.write("\n")

        # =====================================================================
        # Execution Time
        # =====================================================================

        execution_time = (
            time.time() - start_time
        )

        print("\n" + "=" * 80)
        print("RANDOM FOREST TRAINING COMPLETED")
        print("=" * 80)

        print(
            f"Accuracy    : {accuracy:.4f}"
        )

        print(
            f"Macro F1    : {macro_f1:.4f}"
        )

        print(
            f"Weighted F1 : {weighted_f1:.4f}"
        )

        print(
            f"Execution Time : "
            f"{execution_time:.2f} seconds"
        )

        print("=" * 80)

        logging.info(
            f"Model saved to: {model_path}"
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