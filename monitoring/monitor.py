import os
import json
import numpy as np
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

def run_monitoring_suite(reference_csv="data/housing.csv", output_dir="monitoring/reports"):
    """
    Compares baseline training data against live production requests to detect:
    1. Numerical Feature Drift (Area, Bedrooms, Bathrooms, Stories, Parking)
    2. Data Quality Degradation (NaNs, out-of-range square footage)
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Reference Dataset
    if not os.path.exists(reference_csv):
        print(f"[ERROR] Reference file {reference_csv} not found.")
        return

    ref_df = pd.read_csv(reference_csv)

    # 2. Simulate Production Current Dataset (with slight market inflation & larger area drift)
    np.random.seed(42)
    cur_df = ref_df.copy()
    cur_df["area"] = cur_df["area"] * 1.15 + np.random.normal(0, 50, len(cur_df))
    cur_df["price"] = cur_df["price"] * 1.20

    # 3. Configure Evidently Report
    report = Report(metrics=[
        DataQualityPreset(),
        DataDriftPreset(stat_test="ks", stat_test_threshold=0.05)
    ])

    print("[INFO] Computing Data Drift and Quality metrics across datasets...")
    report.run(reference_data=ref_df, current_data=cur_df)

    html_path = os.path.join(output_dir, "housing_drift_report.html")
    json_path = os.path.join(output_dir, "housing_drift_report.json")

    report.save_html(html_path)
    report.save_json(json_path)

    print(f"[SUCCESS] Monitoring HTML Report: {html_path}")
    print(f"[SUCCESS] Monitoring JSON Metrics: {json_path}")

if __name__ == "__main__":
    run_monitoring_suite()

