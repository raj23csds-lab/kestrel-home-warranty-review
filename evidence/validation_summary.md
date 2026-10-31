# Model validation and operating evidence

## Evaluation design

A chronological holdout was used to reduce look-ahead bias:

- **Training window:** 1 April 2025–31 March 2026.
- **Validation window:** 1 April–30 June 2026.
- **Validation set:** 2,131 unique adjudicated claims, 45 fraud outcomes (2.11%).
- **Review simulation:** highest 40 model scores per calendar month, matching the operations desk's stated maximum capacity.
- The evaluation model used 85 trees (best iteration 84) selected by the validation metric. The production artifact is retrained on all 11,146 unique adjudicated claims.

## Headline metrics

| Metric | Result |
|---|---:|
| ROC-AUC | 0.6681 |
| PR-AUC / Average Precision | 0.0709 |
| Fraud prevalence | 2.11% |
| Brier score | 0.0215 |
| Accuracy at 0.50 threshold | 97.70% |
| All-genuine baseline accuracy | 97.89% |
| Precision at 0.50 threshold | 30.00% |
| Recall at 0.50 threshold | 6.67% |

Confusion matrix at a 0.50 threshold (rows = actual 0/1, columns = predicted 0/1):

| | Predicted genuine | Predicted fraud |
|---|---:|---:|
| Actual genuine | 2,079 | 7 |
| Actual fraud | 42 | 3 |

**Interpretation:** The headline accuracy target is not evidence of a useful fraud model. The all-genuine baseline is more accurate because fraud is rare. Ranking performance is modest and misses most fraud. The score is not calibrated and must not be read as a literal probability.

## Monthly top-40 simulation

| Month | Claims | Fraud outcomes | Fraud in top 40 | Top-40 precision | Random expected fraud in 40 | Fraud claim value found |
|---|---:|---:|---:|---:|---:|---:|
| Apr 2026 | 709 | 9 | 3 | 7.50% | 0.51 | ₹17,060 |
| May 2026 | 709 | 14 | 0 | 0.00% | 0.79 | ₹0 |
| Jun 2026 | 713 | 22 | 1 | 2.50% | 1.23 | ₹1,978 |
| **Total** | **2,131** | **45** | **4** | **3.33%** | **2.53** | **₹19,038** |

Across 120 reviews, 4 were recorded fraud and 116 were genuine. The top-40 ranking found 1.58× the fraud cases expected from random selection in this small holdout. This is a weak lift, not a deployment guarantee.

## Cost illustration from the supplied policy

- Gross fraud claim value identified: **₹19,038**.
- Genuine claims held: **116**.
- Goodwill at ₹380 per genuine claim held: **₹44,080**.
- If each of the 120 reviews creates one service contact at ₹260: **₹31,200**.
- Illustrative net: **₹19,038 − ₹44,080 − ₹31,200 = −₹56,242**, before investigation labour.

This is a sensitivity calculation, not audited realised savings. Finance should validate whether the ₹260 contact cost applies to every review, only false positives, or a subset. If charged only to the 116 genuine holds, the estimated net is −₹55,202.

## Known limitations

1. Only 141 fraud labels remain after removing undecided rows and deduplicating repeated claim IDs; the base rate is very low.
2. The email warns that unresolved legacy Zoho cases may have been migrated as `0`. They cannot be separated from confirmed non-fraud rows using the supplied data.
3. The model may learn historical partner-specific patterns. Partner tenure is not treated as proof, and subgroup review is required.
4. `inspector_note` may be populated only after some operational checks. Confirm it is available at scoring time before deployment.
5. Kestrel Shield coverage is not separately identified in the supplied columns; warranty eligibility checks must be confirmed by staff.
6. The holdout is only three months and has 45 fraud outcomes. Confidence intervals would be wide; no claim of stable 97%+ performance is justified.

**Recommendation:** shadow-mode pilot only, top-40 monthly queue, human decisions, label cleanup, and repeat evaluation after 2–3 months of consistent adjudication.
