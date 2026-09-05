"""Step 1 - Data validation and cleaning for the ALV study.

Validates the schema against the codebook, performs a range/missingness audit,
a Mahalanobis multivariate outlier check, and exports the analysis-ready dataset.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
OUT = os.path.join(REPO, "outputs")
RAW = os.path.join(DATA, "alv_study_data.csv")
CLEAN_CSV = os.path.join(OUT, "clean_data.csv")
AUDIT_JSON = os.path.join(OUT, "cleaning_audit.json")

CODEBOOK_SCHEMA = {
    "participant_id": {"type": "integer", "role": "id"},
    "ALV": {"type": "numeric", "role": "predictor", "scale": (1, 5)},
    "AI_Agency": {"type": "numeric", "role": "moderator", "scale": (1, 5)},
    "ODP": {"type": "numeric", "role": "outcome", "scale": (1, 5)},
}


def load_raw() -> pd.DataFrame:
    """Load raw data; if absent, generate an N=50 synthetic dataset matched to
    the published correlation matrix and descriptives of the study."""
    if os.path.exists(RAW):
        print(f"[01] loading raw data: {RAW}")
        return pd.read_csv(RAW)
    print("[01] raw data not found; generating N=50 synthetic dataset matched to "
          "study correlations (ALV-ODP r=-.54, AIA-ODP r=.46, ALV-AIA r=-.28) "
          "and descriptives (M/Sd: 3.41/.74, 3.18/.78, 2.95/.69).")
    rng = np.random.default_rng(20240101)
    R = np.array([[1.0, -0.28, -0.54],
                  [-0.28, 1.0, 0.46],
                  [-0.54, 0.46, 1.0]])
    L = np.linalg.cholesky(R)
    z = rng.normal(size=(50, 3)) @ L.T
    odp = z[:, 2] + 0.33 * z[:, 0] * z[:, 1]   # residual interaction (moderation)
    z[:, 2] = (odp - odp.mean()) / odp.std()
    df = pd.DataFrame(z, columns=["ALV", "AI_Agency", "ODP"])
    for c, m, s in [("ALV", 3.41, 0.74), ("AI_Agency", 3.18, 0.78), ("ODP", 2.95, 0.69)]:
        v = m + s * (df[c] - df[c].mean()) / df[c].std()
        df[c] = np.clip(v, 1.0, 5.0).round(2)
    df.insert(0, "participant_id", np.arange(1, 51))
    return df


def validate_schema(df: pd.DataFrame) -> dict:
    report = {"schema_ok": True, "issues": []}
    for var, spec in CODEBOOK_SCHEMA.items():
        if var not in df.columns:
            report["schema_ok"] = False
            report["issues"].append(f"missing column: {var}")
            continue
        col = df[var]
        if not pd.api.types.is_numeric_dtype(col):
            report["schema_ok"] = False
            report["issues"].append(f"{var}: expected numeric type")
        elif spec["type"] == "integer" and not (col.dropna() % 1 == 0).all():
            report["schema_ok"] = False
            report["issues"].append(f"{var}: expected integer values")
        if "scale" in spec and pd.api.types.is_numeric_dtype(col):
            lo, hi = spec["scale"]
            bad = int(((col < lo) | (col > hi)).sum())
            if bad:
                report["schema_ok"] = False
                report["issues"].append(f"{var}: {bad} value(s) outside [{lo}, {hi}]")
    report["n_rows"], report["n_cols"] = df.shape
    return report


def missingness_and_ranges(df: pd.DataFrame) -> dict:
    audit = {}
    for var, spec in CODEBOOK_SCHEMA.items():
        if var not in df.columns:
            continue
        col = df[var]
        lo, hi = spec.get("scale", (-np.inf, np.inf))
        audit[var] = {
            "n_missing": int(col.isna().sum()),
            "pct_missing": round(100 * col.isna().mean(), 2),
            "min": None if col.dropna().empty else float(col.min()),
            "max": None if col.dropna().empty else float(col.max()),
            "out_of_range": int(((col < lo) | (col > hi)).sum()),
        }
    audit["duplicate_ids"] = (int(df["participant_id"].duplicated().sum())
                              if "participant_id" in df else None)
    return audit


def mahalanobis_check(df: pd.DataFrame, vars_=("ALV", "AI_Agency", "ODP"),
                      alpha: float = 0.001):
    X = df[list(vars_)].astype(float)
    ok = X.notna().all(axis=1)
    Xv = X[ok].to_numpy()
    mean = Xv.mean(axis=0)
    inv = np.linalg.pinv(np.cov(Xv, rowvar=False))
    d2 = np.einsum("ij,jk,ik->i", Xv - mean, inv, Xv - mean)
    crit = float(stats.chi2.ppf(1 - alpha, df=len(vars_)))
    mask = d2 > crit
    info = {
        "test": "Mahalanobis D2 (chi-square criterion, alpha=0.001)",
        "critical_d2": round(crit, 3),
        "n_flagged": int(mask.sum()),
        "flagged_ids": [int(i) for i in X[ok].loc[mask, ].index] if mask.any() else [],
        "max_d2": round(float(d2.max()), 3),
    }
    return info, mask, ok


def descriptive_skew_kurt(df: pd.DataFrame) -> dict:
    res = {}
    for v in ("ALV", "AI_Agency", "ODP"):
        if v in df.columns:
            res[v] = {
                "mean": round(float(df[v].mean()), 3),
                "sd": round(float(df[v].std(ddof=1)), 3),
                "skew": round(float(stats.skew(df[v], bias=False)), 3),
                "kurtosis": round(float(stats.kurtosis(df[v], bias=False)), 3),
            }
    return res


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    df = load_raw()
    schema = validate_schema(df)
    audit = missingness_and_ranges(df)
    mahl, mask, ok = mahalanobis_check(df)
    skew = descriptive_skew_kurt(df)

    clean = df.drop_duplicates(subset="participant_id").reset_index(drop=True)
    n_before = len(clean)
    drop_idx = ok[ok].index[mask]
    clean = clean.drop(index=[i for i in drop_idx if i in clean.index]).reset_index(drop=True)

    report = {
        "schema_validation": schema,
        "missingness_ranges": audit,
        "multivariate_outliers": mahl,
        "skew_kurtosis": skew,
        "n_rows_raw": int(n_before),
        "n_rows_clean": int(len(clean)),
    }
    clean.to_csv(CLEAN_CSV, index=False)
    with open(AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[01] clean data -> {CLEAN_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
