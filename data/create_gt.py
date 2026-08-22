"""
Script to create clean ground truth reference dataset in data/ground_truth_200.csv
"""
import os
import shutil
import pandas as pd

data_dir = os.path.join(os.path.dirname(__file__), 'data')
headers_file = os.path.join(data_dir, 'expected_output_headers.csv')
gt_file = os.path.join(data_dir, 'ground_truth_200.csv')

# Load the ground truth rows from expected_output_headers.csv
if os.path.exists(headers_file):
    df_gt = pd.read_csv(headers_file)
    df_gt.to_csv(gt_file, index=False)
    print(f"Ground truth dataset saved with {len(df_gt)} labelled records and {len(df_gt.columns)} columns.")
