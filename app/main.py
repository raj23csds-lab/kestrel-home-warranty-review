from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any
from app.model_service import predict_one

app=FastAPI(
    title="Kestrel Home Warranty Claim Review",
    version="1.0.0",
    description="Local, no-paid-key model scoring service. Scores prioritise human review; they do not establish fraud."
)

class ClaimPayload(BaseModel):
    claim_id: str
    submitted_at: str
    partner_id: str
    sku: str
    product_serial: str
    days_since_purchase: float
    claim_amount_inr: float
    photo_attached: str
    partner_inspected: str
    claim_description: str
    inspector_note: str | None = None
    customer_prior_claims: int = 0
    source: str = "crm"

@app.get("/health")
def health():
    return {"status":"ok","model":"kestrel-variant-c-catboost-v1"}

@app.post("/predict")
def predict(payload: ClaimPayload):
    try:
        return predict_one(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422,detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail="Prediction failed. Check the record and reference data.")

@app.get("/")
def home():
    return FileResponse(Path(__file__).parent/"static"/"index.html")
