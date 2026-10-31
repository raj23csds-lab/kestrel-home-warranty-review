from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from catboost import CatBoostClassifier
from app.features import build_features
from app.reasons import explain_record

ROOT=Path(__file__).resolve().parents[1]
PARTNERS=pd.read_csv(ROOT/"data/reference/partners.csv").fillna("")
PRODUCTS=pd.read_csv(ROOT/"data/reference/products.csv").fillna("")
MODEL=CatBoostClassifier()
MODEL.load_model(str(ROOT/"models/fraud_model.cbm"))

def predict_one(record: dict) -> dict:
    required=["claim_id","submitted_at","partner_id","sku","product_serial",
              "days_since_purchase","claim_amount_inr","photo_attached",
              "partner_inspected","claim_description","inspector_note",
              "customer_prior_claims","source"]
    missing=[k for k in required if k not in record]
    if missing:
        raise ValueError("Missing required fields: "+", ".join(missing))
    row=pd.DataFrame([{k:record.get(k) for k in required}])
    features=build_features(row,PARTNERS,PRODUCTS)
    score=float(MODEL.predict_proba(features)[0,1])
    partner=PARTNERS.loc[PARTNERS.partner_id.astype(str)==str(record["partner_id"])]
    product=PRODUCTS.loc[PRODUCTS.sku.astype(str)==str(record["sku"])]
    partner_info=partner.iloc[0].to_dict() if len(partner) else None
    product_info=product.iloc[0].to_dict() if len(product) else None
    # Score bands are descriptive ranking bands, not calibrated fraud probabilities.
    if score>=0.20: band="High model score"
    elif score>=0.05: band="Elevated model score"
    elif score>=0.02: band="Watch"
    else: band="Low model score"
    return {
        "claim_id":str(record["claim_id"]),
        "score":round(score,8),
        "score_interpretation":band,
        "score_is_calibrated_probability":False,
        "recommendation":"Use as a review-priority signal only. Do not automatically reject or withhold payment. Apply the monthly limit of 40 investigations and review the highest-ranked eligible claims.",
        "reasons":explain_record(record,partner_info,product_info),
        "model_version":"kestrel-variant-c-catboost-v1",
    }
