from __future__ import annotations

def explain_record(record: dict, partner: dict | None, product: dict | None) -> list[str]:
    """Transparent operational checks; these are not causal explanations or proof of fraud."""
    reasons=[]
    partner = partner or {}
    product = product or {}
    try:
        amount=float(record.get("claim_amount_inr") or 0)
    except Exception:
        amount=0.0
    try:
        days=float(record.get("days_since_purchase") or 0)
    except Exception:
        days=0.0
    try:
        prior=int(float(record.get("customer_prior_claims") or 0))
    except Exception:
        prior=0
    submitted=str(record.get("submitted_at",""))
    try:
        import pandas as pd
        dt=pd.to_datetime(submitted,errors="coerce")
        after_policy=bool(pd.notna(dt) and dt>=pd.Timestamp("2026-05-01"))
    except Exception:
        after_policy=False
    try:
        onboard=pd.to_datetime(partner.get("onboarded_date"),errors="coerce")
        dt=pd.to_datetime(submitted,errors="coerce")
        age=(dt-onboard).days if pd.notna(dt) and pd.notna(onboard) else None
    except Exception:
        age=None
    if age is not None and 0 <= age <= 365:
        reasons.append(f"Partner was onboarded within the last 12 months ({age} days). This is a context flag, not evidence of wrongdoing.")
    price=product.get("list_price_inr")
    try:
        ratio=amount/float(price) if price else None
    except Exception:
        ratio=None
    if ratio is not None and ratio>1.5:
        reasons.append(f"Claim amount is {ratio:.1f}× the listed product price; check the repair estimate and parts.")
    warranty=product.get("warranty_months")
    try:
        warranty_days=float(warranty)*30.44 if warranty else None
    except Exception:
        warranty_days=None
    if warranty_days and days>warranty_days:
        reasons.append("Recorded purchase age is beyond the listed standard warranty duration; verify Shield coverage, purchase proof and eligibility.")
    if prior>=2:
        reasons.append(f"Customer record shows {prior} prior claims; check claim history for duplicates or repeat faults.")
    if str(record.get("photo_attached","")).upper()!="Y":
        reasons.append("No photo is recorded; request supporting evidence where policy and workflow permit.")
    inspected=str(record.get("partner_inspected","")).upper()=="Y"
    if after_policy and amount>=2000 and not inspected:
        reasons.append("A claim of ₹2,000 or more after 1 May 2026 has no partner inspection sign-off, contrary to the stated policy.")
    elif not after_policy and not inspected:
        reasons.append("No partner inspection sign-off is recorded; before 1 May 2026 the policy required sign-off for every claim.")
    if after_policy and amount<2000 and not inspected:
        reasons.append("This is consistent with the post-1 May 2026 auto-approval exception for claims under ₹2,000; do not treat missing inspection alone as suspicious.")
    serial=str(record.get("product_serial","")).strip()
    norm="".join(ch for ch in serial.upper() if ch.isalnum())
    if len(norm)<8:
        reasons.append("Serial number is unusually short after removing punctuation; verify it against the product label.")
    if not reasons:
        reasons.append("No obvious rule-based exception was found in the supplied fields. The model score is a prioritisation signal, not a finding.")
    return reasons[:5]
