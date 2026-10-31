"""Feature engineering shared by offline training and online inference."""
from __future__ import annotations
import numpy as np
import pandas as pd

CAT_FEATURES = [
    "partner_id", "sku", "family", "city", "partner_type",
    "photo_attached", "partner_inspected", "claim_description",
    "inspector_note", "source", "month", "hour", "weekday", "quarter",
]
NUM_FEATURES = [
    "days_since_purchase", "claim_amount_inr", "customer_prior_claims",
    "warranty_months", "list_price_inr", "partner_age_days",
    "partner_new_90d", "partner_new_365d", "amount_to_list_ratio",
    "within_warranty", "days_beyond_warranty", "policy_small_autoapprove",
    "inspection_policy_mismatch", "days_from_policy_change", "serial_len",
    "serial_alpha_count", "serial_digit_count", "serial_has_letters",
    "serial_has_hyphen", "description_len", "note_len", "note_missing",
    "claim_amount_log", "days_since_purchase_log",
]
MODEL_FEATURES = CAT_FEATURES + NUM_FEATURES

def build_features(records: pd.DataFrame, partners: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Join reference data and build only fields available in the supplied claim export."""
    x = records.copy()
    # Accept one record or a batch. Keep original rows/order.
    x["submitted_at"] = pd.to_datetime(x["submitted_at"], errors="coerce")
    x = x.merge(partners, on="partner_id", how="left", validate="many_to_one")
    x = x.merge(products, on="sku", how="left", validate="many_to_one")
    x["partner_onboarded"] = pd.to_datetime(x["onboarded_date"], errors="coerce")
    x["partner_age_days"] = (x["submitted_at"] - x["partner_onboarded"]).dt.days
    x["partner_new_90d"] = ((x["partner_age_days"] >= 0) & (x["partner_age_days"] <= 90)).astype(int)
    x["partner_new_365d"] = ((x["partner_age_days"] >= 0) & (x["partner_age_days"] <= 365)).astype(int)
    x["amount_to_list_ratio"] = x["claim_amount_inr"] / x["list_price_inr"].replace(0, np.nan)
    x["within_warranty"] = (x["days_since_purchase"] <= x["warranty_months"] * 30.44).astype(int)
    x["days_beyond_warranty"] = np.maximum(0, x["days_since_purchase"] - x["warranty_months"] * 30.44)
    x["policy_small_autoapprove"] = (
        (x["submitted_at"] >= pd.Timestamp("2026-05-01")) & (x["claim_amount_inr"] < 2000)
    ).astype(int)
    x["inspection_policy_mismatch"] = (
        ((x["submitted_at"] >= pd.Timestamp("2026-05-01")) &
         (x["claim_amount_inr"] >= 2000) & (x["partner_inspected"].fillna("").str.upper() != "Y")) |
        ((x["submitted_at"] < pd.Timestamp("2026-05-01")) &
         (x["partner_inspected"].fillna("").str.upper() != "Y"))
    ).astype(int)
    x["month"] = x["submitted_at"].dt.month.astype("Int64").astype(str)
    x["hour"] = x["submitted_at"].dt.hour.astype("Int64").astype(str)
    x["weekday"] = x["submitted_at"].dt.dayofweek.astype("Int64").astype(str)
    x["quarter"] = x["submitted_at"].dt.quarter.astype("Int64").astype(str)
    x["days_from_policy_change"] = (x["submitted_at"] - pd.Timestamp("2026-05-01")).dt.days
    serial = x["product_serial"].fillna("").astype(str)
    x["serial_norm"] = serial.str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    x["serial_len"] = x["serial_norm"].str.len()
    x["serial_alpha_count"] = x["serial_norm"].str.count(r"[A-Z]")
    x["serial_digit_count"] = x["serial_norm"].str.count(r"\d")
    x["serial_has_letters"] = (x["serial_alpha_count"] > 0).astype(int)
    x["serial_has_hyphen"] = serial.str.contains("-", regex=False).astype(int)
    x["description_len"] = x["claim_description"].fillna("").astype(str).str.len()
    x["note_len"] = x["inspector_note"].fillna("").astype(str).str.len()
    x["note_missing"] = x["inspector_note"].isna().astype(int)
    x["claim_amount_log"] = np.log1p(pd.to_numeric(x["claim_amount_inr"], errors="coerce").clip(lower=0))
    x["days_since_purchase_log"] = np.log1p(pd.to_numeric(x["days_since_purchase"], errors="coerce").clip(lower=0))
    for col in CAT_FEATURES:
        x[col] = x[col].fillna("__MISSING__").astype(str)
    for col in NUM_FEATURES:
        x[col] = pd.to_numeric(x[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return x[MODEL_FEATURES]
