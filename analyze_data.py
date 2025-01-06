import pandas as pd
import glob
import os

def analyze_suumo_data():
    # Get the most recent CSV file
    csv_files = sorted(glob.glob('suumo_properties_*.csv'), key=os.path.getctime)
    if not csv_files:
        print("No CSV files found")
        return

    latest_file = csv_files[-1]
    print(f"\n=== Analyzing {latest_file} ===\n")

    # Read the CSV file
    df = pd.read_csv(latest_file)
    
    # Basic statistics
    print("=== Data Statistics ===")
    print(f"Total properties: {len(df)}")
    print("\nFields with data:")
    for col in df.columns:
        non_empty = df[col].notna().sum()
        percentage = (non_empty / len(df)) * 100
        print(f"{col}: {non_empty} records ({percentage:.1f}%)")

    # Sample data
    print("\n=== Data Sample ===")
    print(df.head().to_string())

if __name__ == "__main__":
    analyze_suumo_data()
