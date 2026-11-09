"""
Batch CLI test runner for ScamShield backend triage pipeline.
Tests triage analysis across English, Hindi, and Hinglish scam samples.
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

from language_detector import detect_language
from fast_classifier import FastScamClassifier

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "fast_classifier_model.json")

clf = FastScamClassifier()
if clf.load(MODEL_PATH):
    print("[OK] Successfully loaded trained classifier model.\n")

test_samples = [
    "Aapka SBI account block ho gaya hai. Turant is link pe click karke KYC update karein: http://bit.ly/sbi-kyc",
    "Congratulations! You have won Rs 25,00,000 in KBC lottery. Call KBC Manager on WhatsApp to claim.",
    "Bhai galti se aapke PhonePe pe ₹5000 chala gaya h. Kripya refund kar do ye QR scan karke PIN daalo.",
    "Part time online job! Earn Rs 2000-5000 daily by liking YouTube videos. Contact Telegram @job_helper",
    "Instant Loan approved Rs 1,00,000 in 5 mins without CIBIL score! Pay processing fee Rs 999.",
    "Dear Consumer, Electricity power connection will be disconnected tonight at 9:30 PM. Call officer 9123412345.",
    "Dear Customer, Rs. 1450.00 debited from a/c XX4019 on 12-AUG-26 at AMZN Mktp. - HDFC Bank",
    "Bhai shaam ko 7 baje chai pe milte hain, wo office waala document leke aana.",
    "आपका आईसीआईसीआई बैंक खाते का 459032 ओटीपी है। इसे किसी के साथ साझा न करें।",
]

print(f"{'INDEX':<6} | {'LANG':<8} | {'PREDICTED CATEGORY':<20} | {'CONF':<6} | {'SAMPLE TEXT'}")
print("-" * 90)

for i, sample in enumerate(test_samples, 1):
    lang = detect_language(sample)
    cat, conf = clf.predict(sample)
    snippet = sample[:45] + ("..." if len(sample) > 45 else "")
    print(f"{i:<6} | {lang:<8} | {cat:<20} | {conf:.0%}   | {snippet}")
