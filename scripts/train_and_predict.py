"""Rebuild model, temporal holdout evidence and root predictions.csv from the supplied pack."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss,
    confusion_matrix, precision_score, recall_score, roc_auc_score
)
from app.features import build_features, CAT_FEATURES, MODEL_FEATURES


def deduplicate_and_label(train: pd.DataFrame) -> pd.DataFrame:
    df=train.copy()
    df["submitted_at"]=pd.to_datetime(df["submitted_at"],errors="coerce")
    df=df.dropna(subset=["is_fraud"]).sort_values("submitted_at")
    # The email thread confirms re-submissions can repeat claim_id. Keep the first event
    # so repeated copies do not overweight a single investigation outcome.
    df=df.drop_duplicates("claim_id",keep="first").copy()
    df["is_fraud"]=df["is_fraud"].astype(int)
    return df

def make_model(iterations=250):
    return CatBoostClassifier(
        iterations=iterations, depth=4, learning_rate=0.03,
        loss_function="Logloss", eval_metric="AUC", l2_leaf_reg=10,
        random_seed=17, verbose=False, allow_writing_files=False,
        thread_count=4
    )

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--train",default=str(ROOT/"data/input/train.csv"))
    parser.add_argument("--test",default=str(ROOT/"data/input/test_unlabelled.csv"))
    parser.add_argument("--sample",default=str(ROOT/"data/input/sample_submission.csv"))
    args=parser.parse_args()
    for p in [args.train,args.test]:
        if not Path(p).exists():
            raise SystemExit(f"Missing {p}. Put the supplied claim CSVs in data/input/; see README.")
    train_raw=pd.read_csv(args.train)
    test=pd.read_csv(args.test)
    partners=pd.read_csv(ROOT/"data/reference/partners.csv")
    products=pd.read_csv(ROOT/"data/reference/products.csv")
    train=deduplicate_and_label(train_raw)
    train["dt"]=pd.to_datetime(train["submitted_at"])
    cutoff=pd.Timestamp("2026-04-01")
    fit=train[train.dt<cutoff].copy()
    valid=train[train.dt>=cutoff].copy()
    Xfit=build_features(fit,partners,products)
    Xvalid=build_features(valid,partners,products)
    validation_model=make_model(500)
    validation_model.fit(
        Xfit,fit.is_fraud,cat_features=CAT_FEATURES,
        eval_set=(Xvalid,valid.is_fraud),early_stopping_rounds=80,
        use_best_model=True,verbose=False
    )
    vp=validation_model.predict_proba(Xvalid)[:,1]
    threshold_pred=(vp>=0.5).astype(int)
    prevalence=float(valid.is_fraud.mean())
    cm=confusion_matrix(valid.is_fraud,threshold_pred,labels=[0,1]).tolist()
    metrics={
        "validation_period_start":"2026-04-01",
        "validation_period_end":"2026-06-30",
        "validation_rows":int(len(valid)),
        "validation_fraud":int(valid.is_fraud.sum()),
        "validation_fraud_rate":prevalence,
        "roc_auc":float(roc_auc_score(valid.is_fraud,vp)),
        "average_precision_pr_auc":float(average_precision_score(valid.is_fraud,vp)),
        "brier_score":float(brier_score_loss(valid.is_fraud,vp)),
        "accuracy_at_0_5":float(accuracy_score(valid.is_fraud,threshold_pred)),
        "majority_class_baseline_accuracy":float(accuracy_score(valid.is_fraud,np.zeros(len(valid),dtype=int))),
        "precision_at_0_5":float(precision_score(valid.is_fraud,threshold_pred,zero_division=0)),
        "recall_at_0_5":float(recall_score(valid.is_fraud,threshold_pred,zero_division=0)),
        "confusion_matrix_labels_0_1":cm,
        "best_iteration":int(validation_model.best_iteration_),
        "review_capacity_per_month":40,
    }
    val=valid.copy()
    val["score"]=vp
    val["month"]=val.dt.dt.to_period("M").astype(str)
    monthly=[]
    for month,g in val.groupby("month"):
        top=g.nlargest(40,"score")
        fraud_value=float(top.loc[top.is_fraud==1,"claim_amount_inr"].sum())
        monthly.append({
            "month":month,"claims":int(len(g)),"fraud_in_month":int(g.is_fraud.sum()),
            "reviews":int(min(40,len(g))),"fraud_found_top40":int(top.is_fraud.sum()),
            "precision_top40":float(top.is_fraud.mean()),
            "random_expected_fraud_in_40":float(40*g.is_fraud.mean()),
            "fraud_claim_value_found_inr":fraud_value,
            "false_positive_reviews":int((top.is_fraud==0).sum()),
        })
    metrics["monthly_top40_backtest"]=monthly
    metrics["total_top40_reviews"]=int(sum(x["reviews"] for x in monthly))
    metrics["fraud_found_top40_total"]=int(sum(x["fraud_found_top40"] for x in monthly))
    metrics["fraud_claim_value_found_inr_total"]=float(sum(x["fraud_claim_value_found_inr"] for x in monthly))
    metrics["false_positive_reviews_total"]=int(sum(x["false_positive_reviews"] for x in monthly))
    metrics["top40_precision_overall"]=(
        metrics["fraud_found_top40_total"]/metrics["total_top40_reviews"]
        if metrics["total_top40_reviews"] else 0.0
    )
    # Production model is retrained on all available adjudicated unique claims.
    Xall=build_features(train,partners,products)
    production_model=make_model(250)
    production_model.fit(Xall,train.is_fraud,cat_features=CAT_FEATURES,verbose=False)
    model_path=ROOT/"models/fraud_model.cbm"
    production_model.save_model(str(model_path))
    # Preserve sample-submission ordering and schema when supplied.
    Xt=build_features(test,partners,products)
    scores=production_model.predict_proba(Xt)[:,1]
    pred=pd.DataFrame({"claim_id":test.claim_id.astype(str),"score":scores})
    if Path(args.sample).exists():
        sample=pd.read_csv(args.sample)
        if {"claim_id","score"}.issubset(sample.columns):
            pred=sample[["claim_id"]].merge(pred,on="claim_id",how="left",validate="one_to_one")
    pred.to_csv(ROOT/"predictions.csv",index=False,float_format="%.8f")
    metadata={
        "model_version":"kestrel-variant-c-catboost-v1",
        "algorithm":"CatBoostClassifier",
        "training_unique_labelled_claims":int(len(train)),
        "training_fraud_claims":int(train.is_fraud.sum()),
        "training_nonfraud_claims":int((train.is_fraud==0).sum()),
        "excluded_undecided_rows":int(train_raw.is_fraud.isna().sum()),
        "duplicate_claim_ids_removed":int(train_raw.dropna(subset=["is_fraud"]).claim_id.duplicated().sum()),
        "feature_columns":MODEL_FEATURES,
        "categorical_features":CAT_FEATURES,
        "validation":metrics,
        "score_semantics":"Uncalibrated model ranking score in [0,1]; higher means higher estimated fraud risk. Not a verified probability."
    }
    (ROOT/"models/metadata.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    (ROOT/"evidence/model_evaluation.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    pd.DataFrame(monthly).to_csv(ROOT/"evidence/monthly_top40_backtest.csv",index=False)
    print(json.dumps({
        "predictions":str(ROOT/"predictions.csv"),
        "model":str(model_path),
        "training_rows":len(train),
        "test_rows":len(pred),
        "validation_roc_auc":metrics["roc_auc"],
        "validation_pr_auc":metrics["average_precision_pr_auc"],
        "top40_fraud_found":metrics["fraud_found_top40_total"],
        "top40_reviews":metrics["total_top40_reviews"]
    },indent=2))

if __name__=="__main__":
    main()
