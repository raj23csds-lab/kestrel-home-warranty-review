# 3-minute screen-recording plan (record locally; no slides)

**0:00–0:25 — Brief and data decision**
- Show the repository and README.
- Say: “I treated this as a rare-event prioritisation problem, not a binary auto-reject system. I removed undecided labels, deduplicated repeated claim IDs, and held out the latest three labelled months.”

**0:25–1:05 — Evidence**
- Open `evidence/validation_summary.md` and `evidence/monthly_top40_backtest.csv`.
- Say: “The holdout has a 2.11% fraud rate. The 97.7% model accuracy is below the 97.89% all-genuine baseline. At 40 reviews per month, the ranking found 4 frauds across 120 reviews. This is not yet a safe automated decision system.”

**1:05–2:15 — Working product**
- In a terminal, show the server running with `uvicorn app.main:app --reload`.
- Open `http://127.0.0.1:8000`.
- Submit the demo claim, show score and operational reasons.
- Say: “The API accepts one claim as JSON and returns a score plus checks an employee can read. It needs no paid API key. The score is not calibrated probability and does not automatically reject a claim.”

**2:15–2:45 — What changed / what was discarded**
- Show `submission_form.md` and `memo_to_ritu.md`.
- Say: “I rejected accuracy-only success, automatic blocking, and blanket suspicion of new partners. The economics in the backtest are negative under the stated cost assumptions, so I recommend shadow mode and label cleanup.”

**2:45–3:00 — Close**
- Show `predictions.csv` header and row count.
- Say: “The predictions file has one score for every test claim. The next step is a controlled shadow pilot with no more than 40 human investigations per month.”
