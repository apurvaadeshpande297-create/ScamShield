"""
ScamShield classifier training script.

Fine-tunes a multilingual transformer to classify messages into scam
categories (or legitimate). Designed to work with English + Hindi/Hinglish
text using a multilingual base model.

Usage:
    python train_classifier.py --data ../data/labeled/scam_dataset.csv

Requires:
    pip install transformers datasets scikit-learn pandas torch --break-system-packages
"""

import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)

# Multilingual base model — handles English + Hindi (Roman & Devanagari) reasonably well.
# Alternative to try: "ai4bharat/indic-bert" (trained specifically on Indian languages,
# may perform better on Hinglish — worth benchmarking both once you have data).
BASE_MODEL = "distilbert-base-multilingual-cased"


def load_data(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "category"])
    labels = sorted(df["category"].unique().tolist())
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}
    df["label"] = df["category"].map(label2id)
    return df, label2id, id2label


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    report = classification_report(labels, preds, output_dict=True, zero_division=0)
    return {
        "accuracy": report["accuracy"],
        "macro_f1": report["macro avg"]["f1-score"],
        "weighted_f1": report["weighted avg"]["f1-score"],
    }


def main(args):
    df, label2id, id2label = load_data(args.data)
    print(f"Loaded {len(df)} examples across {len(label2id)} categories:")
    print(df["category"].value_counts())

    train_df, temp_df = train_test_split(
        df, test_size=0.3, stratify=df["label"], random_state=42
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df["label"], random_state=42
    )
    print(f"\nSplit sizes -> train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}")

    # Save splits so results are reproducible and test set stays untouched until final eval
    train_df.to_csv("../data/splits/train.csv", index=False)
    val_df.to_csv("../data/splits/val.csv", index=False)
    test_df.to_csv("../data/splits/test.csv", index=False)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=128)

    train_ds = Dataset.from_pandas(train_df[["text", "label"]]).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(val_df[["text", "label"]]).map(tokenize, batched=True)
    test_ds = Dataset.from_pandas(test_df[["text", "label"]]).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=len(label2id), id2label=id2label, label2id=label2id
    )

    training_args = TrainingArguments(
        output_dir="./checkpoints",
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )

    trainer.train()

    # Final evaluation on held-out test set (never touched during training/tuning)
    print("\n=== FINAL TEST SET EVALUATION ===")
    preds = trainer.predict(test_ds)
    y_pred = np.argmax(preds.predictions, axis=-1)
    y_true = test_df["label"].values

    print(classification_report(y_true, y_pred, target_names=list(label2id.keys()), zero_division=0))

    # Per-language breakdown — important for your writeup (English vs Hindi/Hinglish performance)
    print("\n=== PER-LANGUAGE BREAKDOWN ===")
    for lang in test_df["language"].unique():
        mask = (test_df["language"] == lang).values
        if mask.sum() == 0:
            continue
        lang_report = classification_report(
            y_true[mask], y_pred[mask], output_dict=True, zero_division=0
        )
        print(f"{lang}: accuracy={lang_report['accuracy']:.3f}, "
              f"macro_f1={lang_report['macro avg']['f1-score']:.3f}, n={mask.sum()}")

    model.save_pretrained("./scamshield-classifier")
    tokenizer.save_pretrained("./scamshield-classifier")
    print("\nModel saved to ./scamshield-classifier")
    print("Push to Hub with: model.push_to_hub('your-username/scamshield-classifier')")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="../data/labeled/scam_dataset.csv")
    args = parser.parse_args()
    main(args)
