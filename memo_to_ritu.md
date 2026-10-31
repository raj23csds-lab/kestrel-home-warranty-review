# Decision memo — Kestrel Home warranty claim review

**To:** Ritu Deshpande, Head of D2C Operations  
**From:** Warranty Review Project Team  
**Date:** 31 October 2026  
**Subject:** Variant C — fraud-risk prioritisation pilot

## Decision

**Do not switch on automatic claim rejection or payment blocking.** The current data supports a small, supervised prioritisation pilot only. The model is better than random ranking in the historical holdout, but its value is not yet strong enough to justify treating its score as a fraud decision.

## What the historical test says

We trained on earlier adjudicated claims and tested on the later period **1 April–30 June 2026**, without using those later outcomes during training. There were 2,131 unique labelled claims in this holdout, including 45 recorded as fraud (2.11%).

- Ranking quality: ROC-AUC **0.668**; PR-AUC **0.071** (about 3.4× the 2.1% fraud prevalence).
- At a fixed 0.50 score threshold, accuracy was **97.70%**, but simply calling every claim genuine would have scored **97.89%**. The model therefore does not beat the accuracy-only baseline.
- Under the actual desk constraint of 40 reviews per month, the top-40 ranking found **4 fraud cases across 120 reviews** (3.33% precision), versus about **2.5 cases expected** from random selection. It missed most fraud cases.
- The four captured claims totalled **₹19,038** in claimed value. That is **₹159 gross fraud value per review** in this backtest, not net savings.

## Rupee view

For those 120 reviews, 116 were genuine claims. At the policy's average ₹380 goodwill cost, that is **₹44,080**. If each review also creates one service contact at the stated blended ₹260, that adds **₹31,200**. Against ₹19,038 of fraud claims identified, the illustrative net is **–₹56,242**, before investigation labour and other costs. The contact assumption is deliberately explicit; Finance should replace it with actual contact counts before any investment decision.

This is a historical simulation, not a guarantee of future savings. Claim value is treated as the amount avoided only when a reviewed fraud case is confirmed.

## What to do next week

1. Run the dashboard in **shadow mode**: score claims, but do not delay, reject or change payments automatically.
2. Let the desk review no more than 40 claims per month, ranked by score. Record the final outcome, actual amount avoided, whether a genuine customer was delayed, goodwill paid and number of service contacts.
3. Ask Data & IT to resolve the legacy Zoho label problem. The email says Zoho could not store blank outcomes and unresolved cases may have migrated as `0`; those records cannot be distinguished from confirmed genuine claims in this pack.
4. Audit the 4 captured fraud cases and the highest-scoring false positives with Service and Finance. Capture reason codes and evidence, not just a binary outcome.
5. Reassess after at least 2–3 months of consistently adjudicated outcomes. Report precision@40, fraud rupees stopped per review, genuine-customer delay cost and subgroup performance by partner type/city/tenure.

## Guardrails

The data does **not** support the view that newer partners as a group are the problem. Partner tenure is used only as context, never as a standalone fraud rule. The May 2026 under-₹2,000 auto-approval exception is explicitly represented so missing inspection is not incorrectly treated as a policy breach for those claims. A high score is a queue-priority signal, not proof of fraud. Keep a human decision-maker in the loop and monitor outcomes by partner cohort to avoid unfairly penalising new tier-2/tier-3 outlets.
