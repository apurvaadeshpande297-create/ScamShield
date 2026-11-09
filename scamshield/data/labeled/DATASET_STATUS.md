# Dataset Status — v0 (bootstrap)

## What's in `scam_dataset.csv` right now (1,255 rows)

| Source | Rows | Labeling method | Trustworthiness |
|---|---|---|---|
| Seed examples (hand-written) | 8 | Manual | High — but tiny |
| UCI SMS Spam Collection (relabeled) | 1,247 | **Keyword-heuristic auto-labeling** | **Low-medium — NOT verified** |

## Important: the UCI-derived labels are NOT ground truth yet

The 1,247 relabeled rows only had a real `spam`/`ham` label originally. I mapped
`ham → legitimate` (safe, reliable) but the *specific scam category*
(`phishing`, `lottery_scam`, `loan_app_scam`, etc.) for the ~750 spam messages
was assigned automatically using simple keyword matching — e.g. a message
containing "won" or "prize" got labeled `lottery_scam`. This is a reasonable
starting guess, but it WILL contain mistakes (e.g. a message that says "click
here to claim your prize" could arguably be both `phishing` and
`lottery_scam` — the heuristic just picks one).

**Before training a real model on this, you should:**
1. Spot-check a random sample (e.g. 100 rows) of the auto-labeled rows and
   correct any wrong categories by hand
2. Note the `confidence_note` column — every UCI-derived row is flagged
   `auto_categorized_by_keyword_heuristic_NEEDS_MANUAL_REVIEW` so you can
   filter/find them easily
3. Report this honestly in your writeup: *"~750 examples were bootstrapped
   from an existing spam dataset using weak/heuristic labels, then manually
   spot-checked and corrected."* This is completely normal ML practice
   (it's literally called "weak supervision") and reviewers respect
   transparency about it far more than a dataset that looks perfectly clean
   with no explanation.

## What's still missing (the important gap)

- **Hindi/Hinglish content**: only 3 rows right now (the seed examples).
  The entire UCI dataset is English/UK-context. This is your single
  biggest gap — without real Hinglish scam examples, your "multilingual"
  claim won't hold up, and this is also the most valuable/differentiated
  part of your project. Priority #1 for hand-collection.
- **India-specific scam types**: UPI fraud, fake KYC/bank-block messages,
  PM-KISAN/government scheme scams, fake customer care numbers found via
  search — the UCI set has almost none of these (1 upi_fraud example,
  0 real India-context phishing). These need to come from real Indian
  scam reports or hand-collection.
- **fake_job category**: only 1 example total. Needs real examples.

## Recommended next step

Focus data collection specifically on: Hinglish text + India-specific scam
types (UPI fraud, fake bank/KYC messages, fake job offers with registration
fees, government scheme scams). The English/general-phishing categories are
now reasonably covered as a v0 baseline.
