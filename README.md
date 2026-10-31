# Kestrel Home – Warranty Claim Review (Variant C)

A local-first machine learning solution for identifying and prioritising potentially fraudulent warranty claims at Kestrel Home Appliances.

The project includes a CatBoost fraud-risk model, FastAPI prediction service, interactive web dashboard, model evaluation, business memo and `predictions.csv`.

> **Important:** This system provides fraud-risk prioritisation, not an automated fraud verdict. No warranty claim should be rejected or payment withheld solely based on the model score. Human investigation is mandatory. The investigation desk has a capacity of 40 claims per month.

## 1. Project Structure

```text
kestrel_home_warranty_review/
│
├── app/
│   ├── main.py
│   ├── features.py
│   ├── model_service.py
│   ├── reasons.py
│   └── static/
│       └── index.html
│
├── data/
│   ├── input/
│   │   ├── train.csv
│   │   └── test_unlabelled.csv
│   └── reference/
│       ├── partners.csv
│       └── products.csv
│
├── models/
│   ├── fraud_model.cbm
│   └── metadata.json
│
├── scripts/
│   └── train_and_predict.py
│
├── evidence/
│   ├── validation_summary.md
│   ├── model_evaluation.json
│   ├── monthly_top40_backtest.csv
│   ├── data_quality.md
│   └── smoke_test.txt
│
├── tests/
│   ├── conftest.py
│   └── test_smoke.py
│
├── predictions.csv
├── memo_to_ritu.md
├── submission_form.md
├── recording_script.md
├── requirements.txt
├── README.md
└── .gitignore
```

## 2. Technologies Used

| Component | Technology |
|---|---|
| Programming language | Python 3.11 |
| Machine learning | CatBoost |
| Data processing | Pandas, NumPy |
| Model evaluation | Scikit-learn |
| Backend | FastAPI |
| API server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Testing | Pytest |

The application uses local model inference and does not require a paid API key or hosted AI service.

## 3. Installation and Setup

### Requirements

- Python 3.11
- pip
- Windows, macOS or Linux

### Windows PowerShell

Open the project root directory in VS Code or PowerShell.

Create a virtual environment:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Open the dashboard:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Opens the dashboard |
| GET | `/health` | Checks model and backend status |
| POST | `/predict` | Predicts fraud risk for one claim |

### Example API Request

```json
{
  "claim_id": "DEMO-10001",
  "submitted_at": "2026-09-18 11:30",
  "partner_id": "SP3095",
  "sku": "KH-AF-03",
  "product_serial": "KH123456789",
  "days_since_purchase": 260,
  "claim_amount_inr": 4200,
  "photo_attached": "Y",
  "partner_inspected": "Y",
  "claim_description": "unit not heating",
  "inspector_note": "Unit inspected, fault confirmed",
  "customer_prior_claims": 1,
  "source": "crm"
}
```

The API returns:

- Claim ID
- Fraud-risk score
- Risk interpretation
- Employee-readable operational reasons
- Human-review recommendation
- Model version

**Score interpretation:** Higher scores indicate greater estimated fraud risk. Scores are uncalibrated ranking scores, not verified fraud probabilities.

## 5. Model Training and Prediction Generation

The training script performs the following operations:

1. Loads the supplied training and unlabelled test datasets.
2. Removes rows with undecided fraud labels.
3. Deduplicates repeated labelled claim IDs.
4. Creates a chronological training and validation split.
5. Builds features using claim, partner and product information.
6. Trains and evaluates a CatBoost classifier.
7. Simulates the monthly top-40 investigation queue.
8. Retrains the production model using all available adjudicated claims.
9. Generates `predictions.csv`.

Run the script from the project root:

```powershell
python scripts/train_and_predict.py
```

The generated `predictions.csv` contains:

- `claim_id`
- `score`

Each test claim receives one score. Higher scores indicate higher estimated fraud risk.

The optional `sample_submission.csv` can be placed in `data/input/` to preserve its claim ordering.

## 6. Testing

Run the automated tests:

```powershell
python -m pytest -v
```

The tests check the basic prediction service and response structure.

## 7. Model Evaluation

The model was evaluated using a chronological holdout covering 1 April to 30 June 2026.

| Metric | Observed result |
|---|---:|
| ROC-AUC | 0.6681 |
| PR-AUC | 0.0709 |
| Fraud prevalence | 2.11% |
| Brier score | 0.0215 |
| Model accuracy | 97.70% |
| All-genuine baseline accuracy | 97.89% |

### Monthly top-40 review simulation

- Total claims evaluated: 2,131
- Total monthly reviews simulated: 120
- Fraud cases found: 4
- Review precision: 3.33%
- Gross fraud claim value identified: ₹19,038

The results indicate modest ranking performance. The model does not outperform the all-genuine baseline on accuracy.

### Business recommendation

Use the model only in shadow mode as a review-priority tool. Limit investigations to 40 claims per month, retain human decision-making, improve historical outcome labels and evaluate performance again after collecting more reliable investigation results.

## 8. Limitations and Assumptions

- Fraud cases are rare in the supplied dataset.
- Some unresolved legacy Zoho outcomes may have been recorded as non-fraud.
- Repeated claim IDs are treated as resubmissions and deduplicated for training.
- Inspector notes may contain information recorded after initial claim submission. Their availability at scoring time must be confirmed.
- Partner tenure is a contextual feature and is not proof of wrongdoing.
- The model score is not a calibrated probability.
- The validation period is limited to three months.

## 9. Privacy and Data Handling

The supplied customer and operational data is confidential.

- Do not publish raw claim datasets.
- Do not upload confidential data to public repositories.
- Keep the original data pack within the authorised engagement team.
- Use only permitted local or approved environments for processing.

## 10. Deliverables

- `predictions.csv` – model scores for the unlabelled test claims.
- `models/fraud_model.cbm` – trained CatBoost model.
- `models/metadata.json` – model metadata and evaluation details.
- `evidence/` – validation, data-quality and backtest evidence.
- `memo_to_ritu.md` – business recommendation memo.
- `submission_form.md` – completed working copy of submission responses.
- `recording_script.md` – three-minute demonstration guide.

The actual screen recording must be created locally by the submitter before final submission.

---

**Project:** Kestrel Home – Warranty Claim Review  
**Variant:** C  
**Approach:** Local machine learning, human-reviewed fraud-risk prioritisation  
**Model:** CatBoost Classifier