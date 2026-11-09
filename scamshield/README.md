# 🛡️ ScamShield

A scam/fraud triage assistant that helps everyday people — not just technical
users — figure out whether a message, call, or offer is a scam, in plain
language (English + Hindi/Hinglish), with clear next steps.

## Problem

Digital fraud (UPI scams, fake job offers, phishing, loan-app scams) is a
massive and growing problem in India. Existing scam-detection tools are
mostly English-only, built for technical users, and give flat yes/no
answers with no explanation or guidance on what to actually do next.

## What ScamShield does

1. User pastes a suspicious message (or describes a call/offer).
2. A fast, fine-tuned multilingual classifier does first-pass triage.
3. For ambiguous cases, an LLM asks 1-3 clarifying diagnostic questions
   (e.g. "Did they ask for your OTP?") before concluding.
4. Output: scam category, confidence level, plain-language explanation,
   and concrete next steps (where to report, what not to do).

## Architecture

```
User message (EN / HI / Hinglish)
        |
Language detection
        |
Fine-tuned classifier (fast path) --- high confidence --> Result
        |
    low confidence
        |
LLM diagnostic Q&A (asks clarifying questions)
        |
Final classification + confidence + advice (in user's language)
```

## Why this design

- **Cascade architecture** (cheap classifier first, LLM only when needed)
  mirrors real production systems that balance cost, speed, and accuracy.
- **Multilingual by design**, not an English tool with translation bolted
  on — most real scam texts in India are Hinglish, not pure English or
  pure Hindi.
- **Validated, not assumed**: classifier performance is evaluated on a
  held-out test set, broken down by category AND by language, so
  weaknesses are visible rather than hidden.

## Repo structure

```
data/
  raw/        - unprocessed source material
  labeled/    - labeled dataset (see docs/labeling_guide.md)
  splits/     - train/val/test splits (generated, not hand-edited)
models/
  train_classifier.py   - fine-tunes multilingual classifier
app/
  app.py                - Gradio interface (deployed to HF Spaces)
docs/
  labeling_guide.md      - labeling schema and rules
```

## Status

🚧 Early build — dataset collection in progress. See `docs/labeling_guide.md`
for the labeling schema.

## Roadmap

- [ ] Collect + label ~1000-1400 examples across 7 scam categories + legitimate
- [ ] Train + evaluate multilingual classifier (per-category, per-language metrics)
- [ ] Build LLM diagnostic Q&A flow
- [ ] Deploy Gradio app to Hugging Face Spaces
- [ ] Validation study with real (non-technical) users
- [ ] Publish dataset + model + space on Hugging Face Hub
- [ ] Write up methodology and findings

## Reporting scams (India)

- National Cyber Crime Helpline: **1930**
- Online: **cybercrime.gov.in**
