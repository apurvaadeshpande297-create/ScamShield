"""
Script to create stratified train, validation, and test datasets in data/splits/
using Python standard library.
"""

import csv
import random
import os
from collections import defaultdict

dataset_path = os.path.join("..", "data", "labeled", "scam_dataset.csv")
splits_dir = os.path.join("..", "data", "splits")

os.makedirs(splits_dir, exist_ok=True)

rows = []
with open(dataset_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        if r['text'] and r['category']:
            rows.append(r)

print(f"Loaded {len(rows)} valid examples.")

# Group rows by category for stratified sampling
category_groups = defaultdict(list)
for r in rows:
    category_groups[r['category']].append(r)

train_rows = []
val_rows = []
test_rows = []

random.seed(42)

for category, cat_rows in category_groups.items():
    random.shuffle(cat_rows)
    n = len(cat_rows)
    n_train = max(1, int(n * 0.70))
    n_val = max(1, int(n * 0.15)) if n >= 3 else 0
    n_test = n - n_train - n_val
    if n_test <= 0 and n >= 2:
        n_test = 1
        n_train = n - n_val - n_test

    train_rows.extend(cat_rows[:n_train])
    val_rows.extend(cat_rows[n_train:n_train + n_val])
    test_rows.extend(cat_rows[n_train + n_val:])

print(f"Stratified splits -> Train: {len(train_rows)}, Val: {len(val_rows)}, Test: {len(test_rows)}")

def write_csv(path, data, fields):
    with open(path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)

write_csv(os.path.join(splits_dir, "train.csv"), train_rows, fieldnames)
write_csv(os.path.join(splits_dir, "val.csv"), val_rows, fieldnames)
write_csv(os.path.join(splits_dir, "test.csv"), test_rows, fieldnames)

print("Splits successfully generated in data/splits/")
