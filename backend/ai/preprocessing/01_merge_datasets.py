from pathlib import Path
import pandas as pd

# =====================================================
# Dataset Path
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BASE_DIR / "datasets" / "raw" / "CICIDS2017"

csv_files = sorted(DATASET_PATH.glob("*.csv"))

print("=" * 70)
print(f"Found {len(csv_files)} CSV files")
print("=" * 70)

# =====================================================
# Read Every CSV
# =====================================================
dataframes = []

for file in csv_files:
    print(f"Loading {file.name}...")
    df = pd.read_csv(file)
    print(f"Shape : {df.shape}")

    dataframes.append(df)

# =====================================================
# Merge Dataset
# =====================================================
print("\nMerging datasets...")

merged_df = pd.concat(dataframes, ignore_index=True)

print("=" * 70)
print("Merged Successfully")
print("=" * 70)

print("Final Shape :", merged_df.shape)

# =====================================================
# Save
# =====================================================
OUTPUT_PATH = BASE_DIR / "datasets" / "processed"

OUTPUT_PATH.mkdir(exist_ok=True)

merged_df.to_csv(
    OUTPUT_PATH / "merged_dataset.csv",
    index=False
)

print("\nMerged dataset saved successfully.")