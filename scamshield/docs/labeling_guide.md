# ScamShield Labeling Guide

## Columns

| Column | Description |
|---|---|
| id | Unique integer |
| text | The raw message (SMS/WhatsApp/email/call transcript) |
| language | `en`, `hi_roman` (Hinglish, Hindi in Roman script), `hi_deva` (Hindi in Devanagari) |
| is_scam | 1 = scam, 0 = legitimate |
| category | One of the categories below |
| confidence_note | Short note on WHY you labeled it this way (helps you stay consistent, and is gold for your writeup) |
| source | Where the example came from (reddit, kaggle_dataset_name, friend_forwarded, manual_example, news_article) |

## Categories (v1 — start with these, expand later if needed)

1. **phishing** — fake bank/KYC/account-verification links, fake "your account is blocked" messages
2. **fake_job** — work-from-home offers, "registration fee" jobs, fake HR messages
3. **loan_app_scam** — instant loan apps, no-document loans, upfront processing fees
4. **upi_fraud** — fake refund requests, "wrong transfer, send it back," QR code scams, fake payment confirmation screenshots
5. **lottery_scam** — KBC/lottery/prize winning messages
6. **investment_scam** — guaranteed returns, crypto/stock tips, Ponzi-style messages
7. **fake_customer_care** — fake bank/company helpline numbers found via search engines
8. **legitimate** — real, non-scam messages (you need plenty of these as negative examples!)

## Rules to stay consistent

- If a message could fit two categories, pick the PRIMARY intent (e.g. a fake job that also asks for a "registration fee" via UPI → `fake_job`, not `upi_fraud`, because the job offer is the hook)
- Always write a one-line `confidence_note` — even something simple like "asks for OTP" or "urgency + link" — this becomes useful data for error analysis later
- Aim for roughly balanced categories. Don't collect 500 phishing examples and 20 investment scams — your model will just get lazy and always guess phishing.
- Include AMBIGUOUS/tricky legitimate messages too (e.g. a real bank SMS that sounds urgent) — these are the hard negatives that make your evaluation meaningful. A dataset with only obvious scams and obvious legit messages will make your model look better than it actually is.

## Target dataset size (v1)

- ~150-200 examples per category x 7 scam categories = ~1000-1400
- Plus ~300-400 legitimate examples (mix of obvious and tricky/urgent-sounding real messages)
- Roughly 60% English, 40% Hindi/Hinglish (adjust based on what you can actually source)

## Where to source examples

- Existing datasets: search Hugging Face Hub / Kaggle for "SMS spam," "phishing dataset," "fraud SMS India"
- Public scam-warning posts (people sharing screenshots to warn others) — Reddit, Twitter/X
- News articles describing common scam scripts (paraphrase the pattern, don't copy article text verbatim)
- Ask friends/family to forward real scam texts/WhatsApp messages they've received (redact real phone numbers/names before adding to dataset)
- For legitimate examples: your own real bank/delivery/utility SMS (redact personal info)

## Privacy note

Before adding any real forwarded message to the dataset, strip out:
- Real phone numbers
- Real names
- Real account/order numbers
- Anything else personally identifying

Replace with placeholders like `<PHONE>`, `<NAME>`, `<ORDER_ID>`.
