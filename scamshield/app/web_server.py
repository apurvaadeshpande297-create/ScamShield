"""
ScamShield v2 — FastAPI Web Server serving imported Stitch UI connected to ScamShield ML Engine.
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

from language_detector import detect_language
try:
    from fast_classifier import FastScamClassifier
except ImportError:
    FastScamClassifier = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "fast_classifier_model.json")
classifier = None

if FastScamClassifier and os.path.exists(MODEL_PATH):
    classifier = FastScamClassifier()
    if classifier.load(MODEL_PATH):
        print(f"Loaded classifier from {MODEL_PATH}")

import json
import urllib.parse

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if HAS_GENAI and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini SDK: {e}")

def get_simulated_llm_response(text: str, category: str, lang: str):
    """
    Simulates LLM response for ambiguous cases, returning relevant follow-up questions based on the candidate category.
    """
    if category == "upi_fraud":
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya sender ne aapse paise receive karne ke liye UPI PIN enter karne ko kaha?",
                "Kya unhone koi QR code scan karne ko bola h?"
            ]
        else:
            return [
                "Did the sender instruct you to scan a QR code or enter your UPI PIN to receive shifts?",
                "Are they claiming the payment was a wrong transfer and demanding an immediate reverse UPI transfer?"
            ]
    elif category == "fake_job":
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya woh aapse shuruat me registration fee ya security deposit maang rahe hain?",
                "Kya yeh Telegram tasks jaise YouTube videos ko like karne se juda hai?"
            ]
        else:
            return [
                "Are they demanding an upfront registration fee or laptop security deposit?",
                "Does the job involve completing video-liking or rating tasks on Telegram for quick commission payouts?"
            ]
    elif category == "loan_app_scam":
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya unhone aapse WhatsApp par koi unverified APK link download karne ko kaha?",
                "Kya loan pass karne ke liye processing fees pehle maangi ja rahi hai?"
            ]
        else:
            return [
                "Did they prompt you to download or install an unverified APK package directly?",
                "Are they charging upfront file/processing fees before releasing the actual loan amount?"
            ]
    elif category == "phishing":
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya message me SIM card block hone ya power cutoff ka simulate / threat dikhaya gaya hai?",
                "Kya unhone account log in karne ke liye koi short link (.bit.ly, .info) bheja h?"
            ]
        else:
            return [
                "Does the communication threaten immediate SIM card deactivation or utility cutoff within hours?",
                "Did they ask you to log in or share an OTP via a short link (e.g. bit.ly, .info, .site)?"
            ]
    elif category == "lottery_scam":
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya unhone aapse prize release karne ke liye upfront tax ya charge maanga?",
                "Kya aapne bina tickets khareede KBC lucky draw jeetne ka alert paaya?"
            ]
        else:
            return [
                "Have they asked you to pay any taxes or clearing fees upfront before release?",
                "Did you get this lucky draw or lottery offer without buying any official tickets?"
            ]
    elif category == "investment_scam":
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya unhone bina risk ke daily high profits / guaranteed double returns ka vada kiya?",
                "Kya aapko kisi crypto VIP study groups me add hone ko kaha gaya?"
            ]
        else:
            return [
                "Are they offering guaranteed high returns with zero risk or daily interest pay?",
                "Did they add you to a Telegram VIP channel for stock/crypto signals?"
            ]
    else:
        if lang in ["hi", "hi_roman"]:
            return [
                "Kya sender ne aapse bank details ya koi urgent personal info share karne ko kaha?",
                "Kya aap pehle se is brand ya person ko jaante hain?"
            ]
        else:
            return [
                "Did the message prompt you to upload personal verification assets or banking passwords?",
                "Are they urging you to act immediately under pressure of account suspension?"
            ]

def run_llm_triage(text: str, category: str, lang: str):
    """
    Triage slow path: runs Gemini LLM API query if key found; fallbacks to smart mock questions otherwise.
    """
    if not (HAS_GENAI and GEMINI_API_KEY):
        return get_simulated_llm_response(text, category, lang)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are VigilantAI's deep semantic triage agent. We have an AMBIGUOUS case.
        Input Message: "{text}"
        Current Candidate Category: "{category}" (lang: {lang})
        
        Since this message is ambiguous, write 2 standard, simple clarifying questions in {lang} to ask the user.
        For example: "Did they ask you to install an APK file?" or "Do you have an active account with this bank?"
        
        Return ONLY a JSON array of these 2 string questions. Do not output markdown, explainers, or any other code block wrappers.
        Example output format:
        ["Question 1", "Question 2"]
        """
        response = model.generate_content(prompt)
        text_clean = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text_clean)
        if isinstance(data, list) and len(data) > 0:
            return data
        return get_simulated_llm_response(text, category, lang)
    except Exception as e:
        print(f"Gemini API invocation error: {e}. Falling back to default questions.")
        return get_simulated_llm_response(text, category, lang)

app = FastAPI(title="ScamShield VigilantAI")

STITCH_DIR = os.path.join(os.path.dirname(__file__), "..", "stitch_import")

REPORT_INFO = {
    "en": "🚨 Call National Cyber Crime Helpline **1930** immediately | Report online at **cybercrime.gov.in**",
    "hi_roman": "🚨 Cyber Helpline **1930** par call karein | Online complaint: **cybercrime.gov.in**",
    "hi": "🚨 राष्ट्रीय साइबर हेल्पलाइन **1930** पर कॉल करें | ऑनलाइन शिकायत: **cybercrime.gov.in**"
}

CATEGORY_METADATA = {
    "upi_fraud": {
        "badge": "💳 UPI FRAUD DETECTED",
        "red_flags": ["Requesting UPI PIN to receive money", "Fake wrong-transfer refund request", "Scanning QR code for cashback"],
        "advice": {
            "en": "Never enter your UPI PIN to RECEIVE money. UPI PIN is strictly used to DEDUCT money from your account.",
            "hi_roman": "Paisa RECEIVE karne ke liye kabhi bhi UPI PIN nahi daalna hota! UPI PIN sirf aapke khate se paisa KATNE ke liye hota h.",
            "hi": "पैसे प्राप्त करने के लिए कभी भी UPI PIN दर्ज न करें! UPI PIN का उपयोग केवल आपके खाते से पैसे काटने के लिए होता है।"
        }
    },
    "fake_job": {
        "badge": "💼 FAKE JOB SCAM",
        "red_flags": ["Upfront registration or security fee required", "Telegram video-liking tasks", "Unrealistic daily earnings"],
        "advice": {
            "en": "Legitimate employers NEVER ask for upfront registration fees or laptop deposit charges.",
            "hi_roman": "Asli company job ke liye kabhi advance paisa nahi maangti. Telegram task scam se bachein.",
            "hi": "असली कंपनियां नौकरी के लिए कभी भी पहले पैसे नहीं मांगतीं।"
        }
    },
    "loan_app_scam": {
        "badge": "💸 LOAN SCAM WARNING",
        "red_flags": ["No CIBIL instant approval", "Upfront file/processing charge required", "Unverified APK download link"],
        "advice": {
            "en": "Instant loan offers asking for processing fees via unverified APK files are illegal lending scams.",
            "hi_roman": "Bina CIBIL ke instant loan pass hone ka message fraud h. Processing fee mat bhejo.",
            "hi": "बिना दस्तावेज़ों के इंस्टेंट लोन का वादा धोखाधड़ी है।"
        }
    },
    "phishing": {
        "badge": "⚠️ PHISHING ATTEMPT",
        "red_flags": ["Threat of account/electricity block within hours", "Suspicious link (bit.ly, .info, .site)", "Asking for OTP"],
        "advice": {
            "en": "This message contains a fake verification link designed to steal your bank credentials or OTP.",
            "hi_roman": "Yeh message aapki bank details churaane ke liye fake link h. Link pe click na karein.",
            "hi": "यह संदेश आपका डेटा चुराने के लिए एक फर्जी लिंक है।"
        }
    },
    "lottery_scam": {
        "badge": "🎁 FAKE LOTTERY SCAM",
        "red_flags": ["KBC or SIM lucky draw win without entering", "Demand for tax before prize release"],
        "advice": {
            "en": "You cannot win a lottery you never bought a ticket for! KBC lottery calls are frauds.",
            "hi_roman": "Jis lottery me tune hissa hi nahi liya usme jeet kaise sakte ho! KBC 25 Lakh call fraud hai.",
            "hi": "जिस लॉटरी में भाग नहीं लिया, उसमें जीत नहीं सकते।"
        }
    },
    "investment_scam": {
        "badge": "📈 INVESTMENT FRAUD",
        "red_flags": ["Guaranteed 100% returns or daily fixed profit", "Telegram crypto tips channel"],
        "advice": {
            "en": "High guaranteed returns with zero risk is a Ponzi investment scam.",
            "hi_roman": "Paisa double karne aur daily fixed profit dene waale saare Telegram groups fraud hote hain.",
            "hi": "कम समय में गारंटीड ज्यादा रिटर्न का वादा पोंजी स्कैम है।"
        }
    },
    "legitimate": {
        "badge": "✅ LIKELY SAFE",
        "red_flags": ["None detected"],
        "advice": {
            "en": "This message appears to be standard non-malicious text or official transaction alert.",
            "hi_roman": "Yeh message normal/safe lag raha hai. Phir bhi OTP kisi se share na karein.",
            "hi": "यह संदेश सामान्य लग रहा है।"
        }
    }
}


class MessageInput(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def read_root():
    home_file = os.path.join(STITCH_DIR, "home.html")
    if os.path.exists(home_file):
        with open(home_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Inject JavaScript redirect logic into the Stitch button to redirect to dashboard
        script_injection = """
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const checkBtn = document.querySelector("button:has(span:contains('security')), button:has(span:contains('Check Message'))") || document.querySelectorAll("main button")[0];
            const textArea = document.querySelector("textarea");
            
            if (checkBtn && textArea) {
                checkBtn.addEventListener("click", function(e) {
                    e.preventDefault();
                    const text = textArea.value.trim();
                    if (!text) { alert("Please paste a suspicious message or link."); return; }
                    window.location.href = "/dashboard?message=" + encodeURIComponent(text);
                });
            }
        });
        </script>
        </body>
        """
        content = content.replace("</body>", script_injection)
        return content
    return HTMLResponse("<h1>Stitch Home HTML not found</h1>")


@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard(message: str = ""):
    # Check if this input text matches one of the preset template examples
    normalized_text = " ".join(message.lower().split())
    is_preset = normalized_text in PRESET_MESSAGES

    # If the user typed any other problem not present in given examples, route to AI side (advanced_ai_mode.html)
    t_file = "dashboard.html" if is_preset else "advanced_ai_mode.html"
    dashboard_file = os.path.join(STITCH_DIR, t_file)

    if os.path.exists(dashboard_file):
        with open(dashboard_file, "r", encoding="utf-8") as f:
            content = f.read()

        js_vars = f"""
        <script>
        window.VIGILANT_MESSAGE = {json.dumps(message)};
        </script>
        """

        script_injection = """
        <script>
        document.addEventListener("DOMContentLoaded", async function() {
            const message = window.VIGILANT_MESSAGE;
            
            // Try to find target identity placeholder or message details and set it
            const targetEl = [...document.querySelectorAll("p, h1")].find(el => el.textContent.includes("suspicious-login-portal-xyz.net"));
            if (targetEl) {
                targetEl.textContent = message;
            }
            
            const subjEl = [...document.querySelectorAll("h1")].find(el => el.textContent.includes("Subject:"));
            if (subjEl) {
                subjEl.textContent = "Subject: " + (message.length > 50 ? message.substring(0, 50) + "..." : message);
            }
            
            // Asynchronously fetch analysis
            try {
                const res = await fetch("/api/analyze", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await res.json();
                
                // Keep processing visible for 3 seconds of simulation
                setTimeout(() => {
                    window.location.href = "/results?message=" + encodeURIComponent(message) + "&data=" + encodeURIComponent(JSON.stringify(data));
                }, 3000);
            } catch (err) {
                console.error("Scan failed", err);
                alert("Error during scan: " + err);
            }
        });
        </script>
        </body>
        """
        content = content.replace("</body>", js_vars + script_injection)
        return content
    return HTMLResponse(f"<h1>Stitch {t_file} not found</h1>")


@app.get("/results", response_class=HTMLResponse)
def read_results(message: str = "", data: str = ""):
    results_file = os.path.join(STITCH_DIR, "scan_results.html")
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            content = f.read()

        js_vars = f"""
        <script>
        window.VIGILANT_MESSAGE = {json.dumps(message)};
        window.VIGILANT_DATA = {data if data else "null"};
        </script>
        """

        script_injection = """
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const message = window.VIGILANT_MESSAGE;
            const data = window.VIGILANT_DATA;
            if (!data) return;
            
            // Update Flagged Content
            const flaggedBox = [...document.querySelectorAll("h2")].find(h => h.textContent.includes("Flagged Content")) || document.querySelectorAll("main h2")[1];
            if (flaggedBox) {
                const contentDiv = flaggedBox.nextElementSibling;
                if (contentDiv) {
                    contentDiv.innerHTML = `<p class="whitespace-pre-wrap">${message.replace(/</g, "&lt;")}</p>`;
                }
            }
            
            // Update Risk Assessment Score & Badges
            const isScam = data.category !== "legitimate";
            const scoreNum = isScam ? Math.round(data.confidence * 100) : Math.round((1 - data.confidence) * 100);
            
            const riskSection = [...document.querySelectorAll("h2")].find(h => h.textContent.includes("Risk Assessment")) || document.querySelectorAll("main h2")[0];
            if (riskSection) {
                const parent = riskSection.parentElement;
                if (parent) {
                    // Update score number
                    const scoreSpan = parent.querySelector("span.text-display-lg") || parent.querySelector("span.font-display-lg");
                    if (scoreSpan) scoreSpan.textContent = scoreNum;
                    
                    // Update badge text and style
                    const badgeDiv = parent.querySelector("div.inline-flex") || parent.querySelector("span.bg-error\\/10");
                    if (badgeDiv) {
                        badgeDiv.className = `inline-flex items-center gap-xs px-sm py-xs rounded-full font-label-md text-label-md ${isScam ? 'bg-error/10 text-error' : 'bg-green-100 text-green-700 bg-green-150'}`;
                        badgeDiv.innerHTML = `<span class="material-symbols-outlined text-[18px]">${isScam ? 'warning' : 'check_circle'}</span> ${data.badge}`;
                    }
                    
                    // Update meter progress width
                    const meterDiv = parent.querySelector("div.bg-error") || parent.querySelector(".bg-error");
                    if (meterDiv) {
                        meterDiv.style.width = scoreNum + "%";
                        if (!isScam) {
                            meterDiv.className = "bg-green-600 h-2 rounded-full";
                        }
                    }
                    
                    // Update route information
                    let routeDiv = parent.querySelector("div.mt-sm");
                    if (!routeDiv) {
                        routeDiv = document.createElement("div");
                        routeDiv.className = "mt-sm pt-sm border-t border-outline-variant/30 flex items-center gap-xs font-label-sm text-xs";
                        parent.appendChild(routeDiv);
                    }
                    routeDiv.innerHTML = `
                        <span class="material-symbols-outlined text-[18px] text-secondary">
                            ${data.route === 'fast_path' ? 'bolt' : 'psychology'}
                        </span>
                        <span class="text-on-surface-variant font-semibold">
                            Route: ${data.route === 'fast_path' ? 'Local Fast Classifier' : 'Deep Triage (AI Side)'}
                        </span>
                    `;
                }
            }
            
            // Update Plain Language Assessment and actions
            const advSection = [...document.querySelectorAll("h2")].find(h => h.textContent.includes("Recommended Actions")) || document.querySelectorAll("main h2")[2];
            if (advSection) {
                const parent = advSection.parentElement;
                if (parent) {
                    // Inject Plain Language Assessment card
                    let plainDesc = parent.querySelector(".plain-lang-desc");
                    if (!plainDesc) {
                        plainDesc = document.createElement("div");
                        plainDesc.className = "plain-lang-desc mb-md bg-white/5 border border-outline/10 text-white p-4 rounded-lg";
                        parent.insertBefore(plainDesc, parent.querySelector("div.grid"));
                    }
                    plainDesc.innerHTML = `
                        <h3 class="font-label-md text-on-tertiary font-bold mb-1">Plain Language Assessment:</h3>
                        <p class="text-sm text-primary-fixed-dim leading-relaxed">${data.advice}</p>
                    `;
                    
                    // Update the 3 cards
                    const cards = parent.querySelectorAll("div.grid > div");
                    if (cards.length >= 3) {
                        const helplineP = cards[2].querySelector("p");
                        if (helplineP) helplineP.textContent = data.helpline;
                    }
                }
            }
            
            // Add red flags if scam
            if (isScam && data.red_flags && data.red_flags.length > 0) {
                const advContainer = [...document.querySelectorAll("h2")].find(h => h.textContent.includes("Recommended Actions"))?.parentElement;
                if (advContainer) {
                    let redFlagsDiv = advContainer.querySelector(".red-flags-section");
                    if (!redFlagsDiv) {
                        redFlagsDiv = document.createElement("div");
                        redFlagsDiv.className = "red-flags-section relative z-10 mt-4 pt-4 border-t border-outline/10 text-white";
                        advContainer.appendChild(redFlagsDiv);
                    }
                    redFlagsDiv.innerHTML = `
                        <h3 class="font-semibold text-white text-sm mb-2">🚩 Key Threat Red Flags Identified:</h3>
                        <ul class="list-disc pl-5 text-sm text-primary-fixed-dim space-y-1">
                            ${data.red_flags.map(rf => `<li>${rf}</li>`).join('')}
                        </ul>
                    `;
                }
            }
            
            // Render Ambiguity Clarification Questions Form if route is llm_api
            if (data.route === 'llm_api' && data.follow_up_questions && data.follow_up_questions.length > 0) {
                let cqDiv = document.getElementById("clarification-form-container");
                if (!cqDiv) {
                    cqDiv = document.createElement("div");
                    cqDiv.id = "clarification-form-container";
                    cqDiv.className = "mt-md p-md bg-sky-950/20 border border-sky-800 rounded-lg text-white";
                    
                    if (flaggedBox) {
                        const flaggedParent = flaggedBox.parentElement;
                        flaggedParent.appendChild(cqDiv);
                    }
                }
                cqDiv.innerHTML = `
                    <h3 class="font-label-md text-label-md text-sky-400 font-bold mb-xs flex items-center gap-xs">
                        <span class="material-symbols-outlined text-secondary text-[20px]">help_center</span>
                        Ambiguity Clarification Questions
                    </h3>
                    <p class="text-[12px] text-gray-300 mb-md leading-relaxed">
                        Our local model requires additional context. Please answer the following questions to help us confirm the threat:
                    </p>
                    <div class="space-y-sm mb-md text-slate-800">
                        ${data.follow_up_questions.map((q, idx) => `
                            <div class="flex flex-col gap-xs bg-slate-900/50 p-2 rounded border border-gray-700/50 text-[12px] text-white">
                                <span class="font-semibold">${q}</span>
                                <div class="flex gap-sm mt-1">
                                    <label class="flex items-center gap-xs cursor-pointer"><input type="radio" name="q_${idx}" class="accent-sky-400" value="yes"> Yes</label>
                                    <label class="flex items-center gap-xs cursor-pointer"><input type="radio" name="q_${idx}" class="accent-sky-400" value="no"> No</label>
                                    <label class="flex items-center gap-xs cursor-pointer"><input type="radio" name="q_${idx}" class="accent-sky-400" value="unsure" checked> Unsure</label>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <button class="bg-sky-600 hover:bg-sky-500 text-white px-md py-sm rounded-lg text-xs font-bold transition-all cursor-pointer" onclick="alert('Thank you. Diagnostic response logged. VigilantAI rules updated.')">
                        Submit Answers
                    </button>
                `;
            }
        });
        </script>
        </body>
        """
        content = content.replace("</body>", script_injection)
        return content
    return HTMLResponse("<h1>Stitch Results HTML not found</h1>")


PRESET_MESSAGES = {
    "aapka sbi account block ho gaya hai. turant is link pe click karke kyc update karein: http://bit.ly/sbi-kyc",
    "congratulations! you have won rs 25,00,000 in kbc lottery. call kbc manager on whatsapp to claim.",
    "bhai galti se aapke phonepe pe ₹5000 chala gaya h. kripya refund kar do ye qr scan karke pin daalo.",
    "part time online job! earn rs 2000-5000 daily by liking youtube videos. contact telegram @job_helper",
    "instant loan approved rs 1,00,000 in 5 mins without cibil score! pay processing fee rs 999.",
    "dear customer, rs. 1450.00 debited from a/c xx4019 on 12-aug-26 at amzn mktp. - hdfc bank- hdfc bank",
    "electricity office: your power will disconnect tonight at 9:30 pm due to unpaid bill. call officer 9876543210.",
    "dear customer, your sim card kyc documentation is invalid. to prevent instant block, call sim support at 8820412354.",
    "urgent: income tax department has cleared your refund of rs 15,200. claim here: http://incometax-gov-refund.net",
    "your fedex parcel contains prohibited items (drug trafficking). customs holding. contact mumbai custom branch immediately."
}


@app.post("/api/analyze")
def analyze_api(input_data: MessageInput):
    text = input_data.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty message")

    lang = detect_language(text)
    category = "legitimate"
    confidence = 0.50

    if classifier:
        category, confidence = classifier.predict(text)

    # Check if this input text matches one of the preset template examples
    normalized_text = " ".join(text.lower().split())
    is_preset = normalized_text in PRESET_MESSAGES

    # Threshold for obvious cases (Fast Classifier = DistilBERT-style local model)
    THRESHOLD = 0.82
    follow_up_questions = []
    
    # If the user typed any other problem not present in given examples, route to AI side (llm_api)
    if is_preset and confidence >= THRESHOLD:
        route = "fast_path"
    else:
        route = "llm_api"
        # Invoke LLM slow/ambiguous path to ask follow-up questions
        follow_up_questions = run_llm_triage(text, category, lang)

    meta = CATEGORY_METADATA.get(category, CATEGORY_METADATA["legitimate"])
    badge = meta["badge"]
    advice = meta["advice"].get(lang, meta["advice"]["en"])
    helpline = REPORT_INFO.get(lang, REPORT_INFO["en"])

    return JSONResponse({
        "category": category,
        "badge": badge,
        "confidence": confidence,
        "language": lang,
        "advice": advice,
        "red_flags": meta["red_flags"],
        "helpline": helpline,
        "route": route,
        "follow_up_questions": follow_up_questions
    })


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
