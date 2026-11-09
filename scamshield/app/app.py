"""
ScamShield v2 — Interactive Multilingual Scam Triage Assistant.

Features:
  - Language auto-detection (English, Devanagari Hindi, Roman Hinglish).
  - Fast-path Classifier match (TF-IDF + Naive Bayes trained model).
  - Slow-path Interactive Diagnostic Engine asking 1-2 clarifying questions for ambiguous inputs.
  - Multi-lingual advice (EN, HI, Hinglish) & emergency reporting (1930 Helpline, cybercrime.gov.in).
  - State-of-the-art visual Gradio interface with risk meters and Indian scam presets.
"""

import os
import sys
import gradio as gr

# Ensure parent and models directory are in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

from language_detector import detect_language
try:
    from fast_classifier import FastScamClassifier
except ImportError:
    FastScamClassifier = None

# ---- Model Setup ----
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "fast_classifier_model.json")
classifier = None

if FastScamClassifier and os.path.exists(MODEL_PATH):
    classifier = FastScamClassifier()
    if classifier.load(MODEL_PATH):
        print(f"Loaded classifier from {MODEL_PATH}")
    else:
        classifier = None

# ---- Localized Advice & Guidance Engine ----
REPORT_INFO = {
    "en": (
        "🚨 **IMMEDIATE ACTION STEPS**\n"
        "📞 **National Cyber Crime Helpline:** Call **1930** immediately.\n"
        "🌐 **Report Online:** [cybercrime.gov.in](https://cybercrime.gov.in)\n"
        "🏦 **Bank Fraud:** Inform your bank within 24 hours to block accounts/cards if OTP or money was shared."
    ),
    "hi_roman": (
        "🚨 **JALDI KAREIN (NEXT STEPS)**\n"
        "📞 **Cyber Helpline Number:** **1930** par call karein.\n"
        "🌐 **Online Complaint:** [cybercrime.gov.in](https://cybercrime.gov.in) par report karein.\n"
        "🏦 **Bank Alert:** Agar OTP ya paisa share hua h toh turant apne bank ko inform karke card/UPI block karayein."
    ),
    "hi": (
        "🚨 **तत्काल कार्रवाई के चरण**\n"
        "📞 **राष्ट्रीय साइबर अपराध हेल्पलाइन:** **1930** पर तुरंत कॉल करें।\n"
        "🌐 **ऑनलाइन रिपोर्ट करें:** [cybercrime.gov.in](https://cybercrime.gov.in)\n"
        "🏦 **बैंक धोखाधड़ी:** यदि पैसे या OTP साझा किया गया है तो तुरंत अपने बैंक को सूचित करें।"
    ),
}

CATEGORY_METADATA = {
    "upi_fraud": {
        "title": "UPI / Payment Fraud",
        "badge": "💳 UPI FRAUD DETECTED",
        "red_flags": ["Requesting UPI PIN to receive money", "Fake wrong-transfer refund request", "Scanning QR code to get cashback"],
        "advice": {
            "en": "Never enter your UPI PIN to RECEIVE money. UPI PIN is strictly used to DEDUCT money from your account. If anyone asks you to scan a QR code or enter a PIN for cashback or refund, it is 100% a scam.",
            "hi_roman": "Paisa RECEIVE karne ke liye kabhi bhi UPI PIN nahi daalna hota! UPI PIN sirf aapke khate se paisa KATNE ke liye hota h. Agar koi QR scan karke PIN daalne bole, toh woh 100% fraud hai.",
            "hi": "पैसे प्राप्त करने के लिए कभी भी UPI PIN दर्ज न करें! UPI PIN का उपयोग केवल आपके खाते से पैसे काटने के लिए होता है।"
        }
    },
    "fake_job": {
        "title": "Fake Job / Task Scam",
        "badge": "💼 FAKE JOB SCAM",
        "red_flags": ["Upfront registration or security fee required", "Tasks like YouTube video liking on Telegram", "Unrealistic daily earnings (e.g. ₹5,000/day for typing)"],
        "advice": {
            "en": "Legitimate employers NEVER ask for upfront registration fees, security deposits, or laptop kit charges. Work-from-home Telegram task scams promise quick money then block your funds.",
            "hi_roman": "Asli company job ya training ke liye kabhi advance paisa nahi maangti. Telegram par YouTube like karke paise kamane waale saare offer fraud hote hain.",
            "hi": "असली कंपनियां नौकरी के लिए कभी भी पहले पैसे (रजिस्ट्रेशन फीस) नहीं मांगतीं। यह पूरी तरह से फर्जी जॉब स्कैम है।"
        }
    },
    "loan_app_scam": {
        "title": "Illegal Loan App Scam",
        "badge": "💸 LOAN SCAM WARNING",
        "red_flags": ["No CIBIL score instant approval", "Upfront file/processing charge required", "Unverified APK download link"],
        "advice": {
            "en": "Instant loan offers asking for processing fees via unverified APK files or WhatsApp are illegal lending scams. Never grant contact list access to unknown loan apps.",
            "hi_roman": "Bina kisi document aur CIBIL ke instant loan pass hone ka message fraud h. Processing fee maangne waale kisi bhi APK link pe click na karein.",
            "hi": "बिना दस्तावेज और बिना सिबिल स्कोर के इंस्टेंट लोन का वादा धोखाधड़ी है। कभी भी अज्ञात APK डाउनलोड न करें।"
        }
    },
    "fake_customer_care": {
        "title": "Fake Customer Support",
        "badge": "📞 FAKE SUPPORT NUMBER",
        "red_flags": ["Mobile number listed on search engine as official support", "Asking to install AnyDesk/TeamViewer remote apps", "Urgent SIM deactivation threat"],
        "advice": {
            "en": "Never use customer care numbers found directly via Google search. Official banks and services never ask you to install remote control apps like AnyDesk.",
            "hi_roman": "Google search se mila customer care number aksar fake hota h. Asli customer care kabhi AnyDesk app download karne ko nahi bolta.",
            "hi": "गूगल सर्च से मिले कस्टमर केयर नंबर फर्जी हो सकते हैं। आधिकारिक ऐप का ही उपयोग करें।"
        }
    },
    "phishing": {
        "title": "Phishing / Fake KYC Link",
        "badge": "⚠️ PHISHING ATTEMPT",
        "red_flags": ["Threat of account/electricity block within hours", "Suspicious link (bit.ly, .info, .site)", "Asking for PAN/Aadhaar OTP"],
        "advice": {
            "en": "This message contains a fake verification link designed to steal your bank details or OTP. Do not click the link or enter personal credentials.",
            "hi_roman": "Yeh message aapki bank details churaane ke liye fake link h. Link pe click na karein aur na hi OTP share karein.",
            "hi": "यह संदेश आपका व्यक्तिगत डेटा चुराने के लिए एक फर्जी लिंक है। लिंक पर क्लिक न करें।"
        }
    },
    "lottery_scam": {
        "title": "Lottery / Prize Scam",
        "badge": "🎁 FAKE LOTTERY SCAM",
        "red_flags": ["KBC or SIM lucky draw win without participating", "Demand for tax or processing fee before prize release", "Contacting via WhatsApp call"],
        "advice": {
            "en": "You cannot win a lottery you never bought a ticket for! KBC and SIM card lotteries asking for registration tax are classic frauds.",
            "hi_roman": "Jis lottery me tune hissa hi nahi liya usme jeet kaise sakte ho! KBC 25 Lakh lottery waale WhatsApp calls bilkul fraud hote hain.",
            "hi": "आपने जिस लॉटरी में भाग ही नहीं लिया, उसमें जीत नहीं सकते। किसी को भी लॉटरी टैक्स न भेजें।"
        }
    },
    "investment_scam": {
        "title": "Ponzi / Investment Fraud",
        "badge": "📈 INVESTMENT FRAUD",
        "red_flags": ["Guaranteed 100% returns or daily fixed profit", "Telegram stock/crypto tips channel", "Pre-IPO discount schemes"],
        "advice": {
            "en": "High guaranteed returns with zero risk is the hallmark of Ponzi investment scams. Authorized SEBI entities never promise fixed daily returns.",
            "hi_roman": "Kam waqt me paisa double karne aur daily fixed profit dene waale saare Telegram crypto groups fraud hote hain.",
            "hi": "कम समय में गारंटीड ज्यादा रिटर्न का वादा पोंजी स्कैम है। ऐसे ऑफर से बचें।"
        }
    },
    "legitimate": {
        "title": "Likely Legitimate",
        "badge": "✅ LIKELY SAFE",
        "red_flags": ["None detected"],
        "advice": {
            "en": "This message appears to be standard non-malicious text or official transaction alert. Still, stay alert and never share confidential OTPs with callers.",
            "hi_roman": "Yeh message normal/safe lag raha hai. Phir bhi dhyaan rakhein: kabhi kisi ke saath apna OTP ya password share na karein.",
            "hi": "यह संदेश सामान्य लग रहा है। फिर भी, कभी भी अपना OTP या गोपनीय जानकारी साझा न करें।"
        }
    }
}


def analyze_message(message: str, history=None):
    """
    Main triage pipeline: language detection -> fast classifier -> fallback/LLM diagnostic analysis.
    """
    if not message or not message.strip():
        return "Please enter a message or describe a call to analyze."

    lang = detect_language(message)
    category = "legitimate"
    confidence = 0.50

    if classifier:
        category, confidence = classifier.predict(message)
    else:
        msg_lower = message.lower()
        if any(k in msg_lower for k in ["lottery", "kbc", "won", "25 lakh", "prize", "spin"]):
            category, confidence = "lottery_scam", 0.90
        elif any(k in msg_lower for k in ["kyc", "block", "yono", "pan", "bit.ly", "suspended", "link"]):
            category, confidence = "phishing", 0.85
        elif any(k in msg_lower for k in ["upi", "pin", "qr", "gpay", "phonepe", "refund", "scratch"]):
            category, confidence = "upi_fraud", 0.88
        elif any(k in msg_lower for k in ["job", "telegram", "like", "salary", "work from home", "fee"]):
            category, confidence = "fake_job", 0.85
        elif any(k in msg_lower for k in ["loan", "cibil", "apk", "instant cash"]):
            category, confidence = "loan_app_scam", 0.85

    # Threshold checks
    THRESHOLD = 0.82
    route = "fast_path" if confidence >= THRESHOLD else "llm_api"
    
    follow_up_questions = []
    if route == "llm_api":
        try:
            from web_server import run_llm_triage
        except ImportError:
            def run_llm_triage(t, c, l): return []
        follow_up_questions = run_llm_triage(message, category, lang)

    meta = CATEGORY_METADATA.get(category, CATEGORY_METADATA["legitimate"])
    badge = meta["badge"]
    advice = meta["advice"].get(lang, meta["advice"]["en"])
    report_box = REPORT_INFO.get(lang, REPORT_INFO["en"])
    red_flags_str = "\n".join([f"• {rf}" for rf in meta["red_flags"]])

    route_text = "⚡ **Local Fast Classifier** (Obvious case instantly triaged)" if route == "fast_path" else "🤖 **Deep Triage API** (Ambiguous case scaling to LLM)"
    
    questions_block = ""
    if follow_up_questions:
        questions_block = "\n\n### ❓ **Ambiguity Clarification Questions**\n" + \
                         "\n".join([f"- *{q}*" for q in follow_up_questions])

    if category != "legitimate":
        response = (
            f"### {badge}\n"
            f"**Confidence:** `{confidence:.0%}` | **Language Detected:** `{lang.upper()}`\n"
            f"**Triage Route:** {route_text}{questions_block}\n\n"
            f"--- \n"
            f"### 💡 **Plain Language Explanation**\n"
            f"{advice}\n\n"
            f"### 🚩 **Key Red Flags Identified**\n"
            f"{red_flags_str}\n\n"
            f"--- \n"
            f"{report_box}"
        )
    else:
        response = (
            f"### {badge}\n"
            f"**Confidence:** `{confidence:.0%}` | **Language Detected:** `{lang.upper()}`\n"
            f"**Triage Route:** {route_text}{questions_block}\n\n"
            f"--- \n"
            f"### 💡 **Safety Analysis**\n"
            f"{advice}\n\n"
            f"🔒 *Remember: Official banks, Google, or Swiggy will never ask for your password or OTP over SMS/call.*"
        )

    return response


# ---- Gradio UI Interface ----
with gr.Blocks(title="🛡️ ScamShield v2") as demo:
    gr.Markdown(
        """
        # 🛡️ ScamShield — India's Multilingual Scam Triage Assistant
        **Paste a suspicious SMS, WhatsApp message, email, or describe a suspicious call you received.**  
        *Supports English, Devanagari Hindi (हिंदी), and Roman Hinglish.*
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            msg_input = gr.Textbox(
                lines=4,
                placeholder="Example: 'Aapka SBI YONO account block ho gaya hai. Link pe click karke KYC update karein: bit.ly/xyz'...",
                label="Suspicious Message / Call Description",
            )
            submit_btn = gr.Button("🔍 Analyze Scam Risk", variant="primary")
            
            gr.Markdown("### 💡 Quick Try Real Indian Scam Examples:")
            gr.Examples(
                examples=[
                    ["Aapka SBI account block ho gaya hai. Turant is link pe click karke KYC update karein: http://bit.ly/sbi-kyc"],
                    ["Congratulations! You have won Rs 25,00,000 in KBC lottery. Call KBC Manager on WhatsApp to claim."],
                    ["Bhai galti se aapke PhonePe pe ₹5000 chala gaya h. Kripya refund kar do ye QR scan karke PIN daalo."],
                    ["Part time online job! Earn Rs 2000-5000 daily by liking YouTube videos. Contact Telegram @job_helper"],
                    ["Instant Loan approved Rs 1,00,000 in 5 mins without CIBIL score! Pay processing fee Rs 999."],
                    ["Dear Customer, Rs. 1450.00 debited from a/c XX4019 on 12-AUG-26 at AMZN Mktp. - HDFC Bank"],
                ],
                inputs=msg_input,
            )

        with gr.Column(scale=3):
            output_box = gr.Markdown(
                """
                ### 🛡️ Triage Status
                *Enter a message on the left and click **Analyze Scam Risk** to view instant analysis.*
                """
            )

    submit_btn.click(fn=analyze_message, inputs=[msg_input], outputs=[output_box])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", share=False)
