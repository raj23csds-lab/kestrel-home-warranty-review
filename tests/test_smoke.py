from app.model_service import predict_one

def test_single_claim_prediction_shape():
    record = {
        "claim_id":"TEST-1",
        "submitted_at":"2026-09-18 11:30",
        "partner_id":"SP3095",
        "sku":"KH-AF-03",
        "product_serial":"KH123456789",
        "days_since_purchase":260,
        "claim_amount_inr":4200,
        "photo_attached":"Y",
        "partner_inspected":"Y",
        "claim_description":"unit not heating",
        "inspector_note":"Unit inspected, fault confirmed",
        "customer_prior_claims":1,
        "source":"crm"
    }
    result=predict_one(record)
    assert result["claim_id"]=="TEST-1"
    assert 0 <= result["score"] <= 1
    assert result["score_is_calibrated_probability"] is False
    assert isinstance(result["reasons"],list) and result["reasons"]
    assert "recommendation" in result
