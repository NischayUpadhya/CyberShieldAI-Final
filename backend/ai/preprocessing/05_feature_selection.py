"""
===============================================================================
File        : 05_feature_selection.py
Project     : CyberShield AI
Description : Performs feature-quality analysis and feature selection on the
              engineered CICIDS2017 dataset.

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
from sklearn.ensemble import RandomForestClassifier


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

SAMPLE_SIZE = 100_000
CORRELATION_THRESHOLD = 0.95
RANDOM_STATE = 42
TOP_FEATURES = 40


# =============================================================================
# Main Function
# =============================================================================

def main():

    start_time = time.time()

    try:

        logging.info("Starting Feature Selection...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        INPUT_DATASET = (
            BASE_DIR
            / "datasets"
            / "processed"
            / "engineered_dataset.csv"
        )

        EVALUATION_DIR = BASE_DIR / "evaluation"
        EVALUATION_DIR.mkdir(exist_ok=True)

        FEATURE_LIST_PATH = (
            EVALUATION_DIR
            / "Selected_Features.txt"
        )

        IMPORTANCE_PATH = (
            EVALUATION_DIR
            / "Feature_Importance.csv"
        )

        CORRELATION_PATH = (
            EVALUATION_DIR
            / "Highly_Correlated_Features.csv"
        )

        REPORT_PATH = (
            EVALUATION_DIR
            / "Feature_Selection_Report.txt"
        )

        # =====================================================================
        # Check Input Dataset
        # =====================================================================

        if not INPUT_DATASET.exists():

            logging.error(
                f"Engineered dataset not found:\n{INPUT_DATASET}"
            )

            return

        # =====================================================================
        # Load Dataset
        # =====================================================================

        logging.info("Loading engineered dataset...")

        df = pd.read_csv(INPUT_DATASET)

        logging.info(
            f"Dataset loaded successfully: {df.shape}"
        )

        # =====================================================================
        # Validate Target
        # =====================================================================

        if "Label" not in df.columns:

            logging.error(
                "Target column 'Label' was not found."
            )

            return

        # =====================================================================
        # Exclude Target and Metadata
        # =====================================================================

        excluded_columns = [
            "Label",
            "Attack_Category"
        ]

        feature_columns = [
            column
            for column in df.columns
            if column not in excluded_columns
        ]

        X = df[feature_columns]

        logging.info(
            f"Initial feature count: {len(feature_columns)}"
        )

        # =====================================================================
        # Keep Numeric Features Only
        # =====================================================================

        numeric_features = X.select_dtypes(
            include=[np.number]
        ).columns.tolist()

        non_numeric_features = [
            column
            for column in feature_columns
            if column not in numeric_features
        ]

        if non_numeric_features:

            logging.warning(
                f"Non-numeric features excluded: "
                f"{non_numeric_features}"
            )

        X = X[numeric_features]

        # =====================================================================
        # Check Invalid Values
        # =====================================================================

        logging.info(
            "Checking for NaN and infinite values..."
        )

        nan_counts = X.isna().sum()

        inf_counts = np.isinf(X).sum()

        total_nan = int(nan_counts.sum())
        total_inf = int(inf_counts.sum())

        logging.info(
            f"NaN values: {total_nan}"
        )

        logging.info(
            f"Infinite values: {total_inf}"
        )

        # =====================================================================
        # Replace Invalid Values
        # =====================================================================

        if total_inf > 0:

            X = X.replace(
                [np.inf, -np.inf],
                np.nan
            )

        if X.isna().sum().sum() > 0:

            X = X.fillna(0)

        # =====================================================================
        # Remove Zero-Variance Features
        # =====================================================================

        logging.info(
            "Checking for zero-variance features..."
        )

        variance = X.var()

        zero_variance_features = variance[
            variance == 0
        ].index.tolist()

        if zero_variance_features:

            X = X.drop(
                columns=zero_variance_features
            )

        logging.info(
            f"Zero-variance features removed: "
            f"{len(zero_variance_features)}"
        )

        # =====================================================================
        # Correlation Analysis
        # =====================================================================

        logging.info(
            f"Creating representative sample of "
            f"{SAMPLE_SIZE:,} rows..."
        )

        sample_size = min(
            SAMPLE_SIZE,
            len(X)
        )

        sample = X.sample(
            n=sample_size,
            random_state=RANDOM_STATE
        )

        logging.info(
            "Calculating feature correlations..."
        )

        correlation_matrix = sample.corr()

        upper_triangle = correlation_matrix.where(
            np.triu(
                np.ones(
                    correlation_matrix.shape
                ),
                k=1
            ).astype(bool)
        )

        highly_correlated = []

        for column in upper_triangle.columns:

            correlated_columns = upper_triangle[
                column
            ][
                upper_triangle[column].abs()
                > CORRELATION_THRESHOLD
            ].index.tolist()

            for correlated_column in correlated_columns:

                correlation_value = (
                    upper_triangle.loc[
                        correlated_column,
                        column
                    ]
                )

                highly_correlated.append(
                    {
                        "Feature_1": correlated_column,
                        "Feature_2": column,
                        "Correlation": correlation_value
                    }
                )

        correlation_df = pd.DataFrame(
            highly_correlated
        )

        if not correlation_df.empty:

            correlation_df.to_csv(
                CORRELATION_PATH,
                index=False
            )

        logging.info(
            f"Highly correlated feature pairs: "
            f"{len(correlation_df)}"
        )

        # =====================================================================
        # Remove Highly Correlated Features
        # =====================================================================

        correlated_features_to_remove = set()

        if not correlation_df.empty:

            for _, row in correlation_df.iterrows():

                feature_1 = row["Feature_1"]
                feature_2 = row["Feature_2"]

                # Keep the first feature and remove the second.
                correlated_features_to_remove.add(
                    feature_2
                )

        X_reduced = X.drop(
            columns=list(
                correlated_features_to_remove
            ),
            errors="ignore"
        )

        logging.info(
            f"Highly correlated features removed: "
            f"{len(correlated_features_to_remove)}"
        )

        # =====================================================================
        # Prepare Sample for Feature Importance
        # =====================================================================

        importance_sample_size = min(
            SAMPLE_SIZE,
            len(X_reduced)
        )

        importance_sample = X_reduced.sample(
            n=importance_sample_size,
            random_state=RANDOM_STATE
        )

        # =====================================================================
        # Target Sample
        # =====================================================================

        y = df.loc[
            importance_sample.index,
            "Label"
        ]

        # =====================================================================
        # Random Forest Feature Importance
        # =====================================================================

        logging.info(
            "Training Random Forest for feature importance..."
        )

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            class_weight="balanced_subsample"
        )

        model.fit(
            importance_sample,
            y
        )

        # =====================================================================
        # Feature Importance
        # =====================================================================

        importance_df = pd.DataFrame(
            {
                "Feature": X_reduced.columns,
                "Importance": model.feature_importances_
            }
        )

        importance_df = importance_df.sort_values(
            by="Importance",
            ascending=False
        ).reset_index(drop=True)

        importance_df.to_csv(
            IMPORTANCE_PATH,
            index=False
        )

        # =====================================================================
        # Select Top Features
        # =====================================================================

        selected_features = (
            importance_df
            .head(TOP_FEATURES)
            ["Feature"]
            .tolist()
        )

        # =====================================================================
        # Save Selected Feature Names
        # =====================================================================

        with open(
            FEATURE_LIST_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            for feature in selected_features:
                f.write(feature + "\n")

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
                "CYBERSHIELD AI - FEATURE SELECTION REPORT\n"
            )
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Dataset Shape : {df.shape}\n"
            )

            f.write(
                f"Initial Numeric Features : "
                f"{len(numeric_features)}\n"
            )

            f.write(
                f"Zero-Variance Features Removed : "
                f"{len(zero_variance_features)}\n"
            )

            f.write(
                f"Highly Correlated Features Removed : "
                f"{len(correlated_features_to_remove)}\n"
            )

            f.write(
                f"Final Candidate Features : "
                f"{len(X_reduced.columns)}\n"
            )

            f.write(
                f"Selected Features : "
                f"{len(selected_features)}\n\n"
            )

            f.write("=" * 80 + "\n")
            f.write("SELECTED FEATURES\n")
            f.write("=" * 80 + "\n")

            for feature in selected_features:
                f.write(f"- {feature}\n")

            f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("TOP FEATURE IMPORTANCE\n")
            f.write("=" * 80 + "\n")

            f.write(
                importance_df.head(TOP_FEATURES).to_string(
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
        print("FEATURE SELECTION COMPLETED")
        print("=" * 80)

        print(
            f"Initial Numeric Features : "
            f"{len(numeric_features)}"
        )

        print(
            f"Zero-Variance Removed     : "
            f"{len(zero_variance_features)}"
        )

        print(
            f"Highly Correlated Removed : "
            f"{len(correlated_features_to_remove)}"
        )

        print(
            f"Final Candidate Features  : "
            f"{len(X_reduced.columns)}"
        )

        print(
            f"Selected Features         : "
            f"{len(selected_features)}"
        )

        print(
            f"Execution Time            : "
            f"{execution_time:.2f} seconds"
        )

        print("=" * 80)

        logging.info(
            "Feature Selection completed successfully."
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