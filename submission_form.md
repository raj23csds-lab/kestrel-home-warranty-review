# Kestrel Home — Submission Form (completed working copy)

> The supplied data pack did not contain a separate official submission-form file. This completed form records the requested decisions and disclosures using the fields inferable from the brief. Transfer these answers into the company's portal/form if one is supplied separately.

## 1. Expected score and rationale

**Expected offline ranking performance:** ROC-AUC approximately **0.60–0.68** and PR-AUC approximately **0.05–0.08** on a future time-based holdout.

**Observed validation reference:** On the time-based holdout (1 April–30 June 2026), ROC-AUC was **0.668** and PR-AUC was **0.071**, with 2.11% fraud prevalence. At the monthly top-40 operating capacity, 4 of 45 fraud outcomes were found across 120 reviews (3.33% precision). The expected future result is uncertain because the event rate is low and the label quality is imperfect.

**Accuracy expectation:** The 97% board target is not a useful standalone test here. In the holdout, all-genuine baseline accuracy was 97.89%, while the model's 0.50-threshold accuracy was 97.70%. I do not claim that the model beats the accuracy baseline or that it will achieve 97%+ useful fraud detection.

## 2. Approach

- Parsed the claim export and joined product and partner reference data.
- Removed rows with blank investigation outcomes from supervised training.
- Deduplicated repeated `claim_id` rows by keeping the first timestamped occurrence; repeated submissions otherwise overweight one case.
- Used a chronological holdout: train before 1 April 2026, validate 1 April–30 June 2026.
- Trained a local CatBoost classifier using claim, product, partner, timing, policy, serial-format and available text fields.
- Retrained the production model on all adjudicated, deduplicated rows and generated one score per row in `test_unlabelled.csv`.
- Scores are uncalibrated ranking scores, not verified fraud probabilities. The operating proposal is top-40 per calendar month for human review, not automatic rejection.

## 3. Key assumptions and unresolved data issues

- `submitted_at` is interpreted as IST, as stated in the operations policy.
- The 1 May 2026 policy change is applied: claims below ₹2,000 may be auto-approved without partner inspection from that date; claims at or above ₹2,000 still require inspection.
- The 215 explicit blank outcomes in the current export are excluded from supervised training.
- The email thread warns that unresolved legacy Zoho cases may have been exported as `0`. These cannot be identified from the supplied fields and may contaminate the not-fraud class.
- The pack says repeated claim IDs can be resubmissions. One row per labelled claim ID is used for training; test IDs are unique.
- The score is a prioritisation aid only. A human investigation must establish the outcome.
- The official evaluation metric/leaderboard score was not specified in the pack; expected ROC-AUC and PR-AUC are therefore stated rather than inventing a single unknown score.

## 4. AI tools and cost disclosure

- **ChatGPT (OpenAI):** used as a coding and documentation assistant to draft/refine implementation, evaluation, memo and submission notes.
- **CatBoost / pandas / scikit-learn:** local open-source Python libraries used for model training and evaluation.
- **Paid model/API usage:** none. The delivered product does not call a hosted LLM or paid prediction API and starts without an API key.
- **Estimated third-party API cost:** ₹0. Local compute, electricity and any optional hosting are not included.
- **Inside the product:** no generative AI is used. The product uses a locally loaded CatBoost model and transparent operational checks.

## 5. What was rejected and why

- **Automatic rejection/payment blocking:** rejected because holdout recall and economics are weak and investigation outcomes are imperfect.
- **Accuracy as the sole KPI:** rejected because the majority-class baseline already exceeds 97% while detecting no fraud.
- **Treating all new partners as suspicious:** rejected because the email explicitly cautions against painting new partners with one brush and the data does not justify such a blanket rule.
- **A paid model API:** not used because the brief requires a no-paid-key startup path and local inference is sufficient for this small workflow.

## 6. Deliverables checklist

- [x] `predictions.csv` at repository root, with `claim_id,score` and one row per test claim.
- [x] Working JSON prediction endpoint (`POST /predict`).
- [x] One-screen local dashboard.
- [x] Evaluation evidence and monthly top-40 backtest.
- [x] One-page decision memo to Ritu.
- [x] README and clean-machine setup.
- [x] AI-tool and cost disclosure.
- [ ] Actual screen recording (up to 3 minutes) — must be recorded by the submitter while running the local app; see `recording_script.md`.
