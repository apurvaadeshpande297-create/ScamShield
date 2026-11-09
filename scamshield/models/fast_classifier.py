"""
ScamShield Fast Multilingual Classifier Engine.

Implements a lightweight, fast TF-IDF + Multinomial Naive Bayes classifier
in pure Python standard library for instant inference without heavy dependencies.
Saves model weights to fast_classifier_model.json.
"""

import csv
import math
import json
import re
import os
from collections import defaultdict, Counter

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in", "for",
    "on", "with", "this", "that", "it", "you", "your", "my", "or", "be", "at"
}


def tokenize(text: str):
    """
    Extracts word tokens (lowercase) and character n-grams (3-grams) for robust
    multilingual & Hinglish pattern matching.
    """
    text_clean = text.lower()
    words = re.findall(r"\w+", text_clean)
    words_filtered = [w for w in words if w not in STOPWORDS]

    # Also compute character 3-grams to catch spelling variations (e.g., 'karein', 'karo', 'karna')
    char_ngrams = []
    for word in words:
        if len(word) >= 3:
            for i in range(len(word) - 2):
                char_ngrams.append("cng_" + word[i:i+3])

    return words_filtered + char_ngrams


class FastScamClassifier:
    def __init__(self):
        self.categories = []
        self.doc_counts = defaultdict(int)
        self.feature_counts = defaultdict(lambda: defaultdict(int))
        self.feature_totals = defaultdict(int)
        self.vocab = set()
        self.total_docs = 0

    def fit(self, samples):
        """
        Train Naive Bayes model on samples [(text, category), ...]
        """
        for text, category in samples:
            self.total_docs += 1
            self.doc_counts[category] += 1
            tokens = tokenize(text)
            for token in tokens:
                self.feature_counts[category][token] += 1
                self.feature_totals[category] += 1
                self.vocab.add(token)

        self.categories = list(self.doc_counts.keys())

    def predict(self, text: str):
        """
        Predict category and confidence score for input text.
        Returns: (best_category, confidence_score)
        """
        if not self.total_docs:
            return "legitimate", 0.50

        tokens = tokenize(text)
        vocab_size = len(self.vocab)
        scores = {}

        for cat in self.categories:
            # Prior probability log P(cat)
            prior = math.log(self.doc_counts[cat] / self.total_docs)
            log_prob = prior
            cat_total = self.feature_totals[cat] + vocab_size

            for token in tokens:
                if token in self.vocab:
                    count = self.feature_counts[cat][token]
                    log_prob += math.log((count + 1) / cat_total)

            scores[cat] = log_prob

        # Softmax normalization to obtain probabilities
        max_log = max(scores.values())
        exp_scores = {cat: math.exp(score - max_log) for cat, score in scores.items()}
        sum_exp = sum(exp_scores.values())
        probs = {cat: exp_scores[cat] / sum_exp for cat in exp_scores}

        best_cat = max(probs, key=probs.get)
        confidence = probs[best_cat]

        return best_cat, confidence

    def save(self, filepath: str):
        data = {
            "categories": self.categories,
            "doc_counts": dict(self.doc_counts),
            "feature_counts": {k: dict(v) for k, v in self.feature_counts.items()},
            "feature_totals": dict(self.feature_totals),
            "vocab": list(self.vocab),
            "total_docs": self.total_docs,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            return False
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.categories = data["categories"]
        self.doc_counts = defaultdict(int, data["doc_counts"])
        self.feature_counts = defaultdict(lambda: defaultdict(int))
        for k, v in data["feature_counts"].items():
            self.feature_counts[k] = defaultdict(int, v)
        self.feature_totals = defaultdict(int, data["feature_totals"])
        self.vocab = set(data["vocab"])
        self.total_docs = data["total_docs"]
        return True


def train_and_eval():
    train_path = os.path.join("..", "data", "splits", "train.csv")
    test_path = os.path.join("..", "data", "splits", "test.csv")
    model_path = os.path.join(".", "fast_classifier_model.json")

    train_samples = []
    with open(train_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            train_samples.append((r["text"], r["category"]))

    clf = FastScamClassifier()
    clf.fit(train_samples)
    clf.save(model_path)
    print(f"Model trained on {len(train_samples)} samples and saved to {model_path}")

    # Evaluate on test set
    test_samples = []
    with open(test_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            test_samples.append((r["text"], r["category"], r.get("language", "en")))

    correct = 0
    total = len(test_samples)
    per_lang_correct = defaultdict(int)
    per_lang_total = defaultdict(int)

    for text, true_cat, lang in test_samples:
        pred_cat, conf = clf.predict(text)
        is_correct = pred_cat == true_cat
        if is_correct:
            correct += 1
            per_lang_correct[lang] += 1
        per_lang_total[lang] += 1

    accuracy = correct / total if total > 0 else 0
    print(f"\n=== TEST SET ACCURACY ===")
    print(f"Overall Test Accuracy: {accuracy:.2%} ({correct}/{total})")

    print("\n=== PER-LANGUAGE ACCURACY ===")
    for lang, l_tot in per_lang_total.items():
        l_corr = per_lang_correct[lang]
        l_acc = l_corr / l_tot if l_tot > 0 else 0
        print(f"Language '{lang}': {l_acc:.2%} ({l_corr}/{l_tot})")


if __name__ == "__main__":
    train_and_eval()
