"""Shared utilities for the ALV analysis pipeline."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy import stats

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
OUT = os.path.join(REPO, "outputs")

LABELS = {
    "ALV": "Artificial Linguistic Veneer",
    "AI_Agency": "AI Agency",
    "ODP": "Oral Defense Performance",
}

VARS = ["ALV", "AI_Agency", "ODP"]


def load_clean() -> pd.DataFrame:
    path = os.path.join(OUT, "clean_data.csv")
    if not os.path.exists(path):
        raise FileNotFoundError("clean_data.csv not found - run 01_clean_data.py first")
    return pd.read_csv(path)


def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=1)


def apa_p(p: float) -> str:
    if p < .001:
        return "<.001"
    s = f"{p:.3f}" if p < .01 else f"{p:.2f}"
    return s.lstrip("0")


def fmt_coef(b: float, se: float, t: float, p: float) -> dict:
    star = "***" if p < .001 else ("**" if p < .01 else ("*" if p < .05 else ""))
    return {"B": round(float(b), 3), "SE": round(float(se), 3),
            "t": round(float(t), 2), "p": apa_p(p), "sig": star}


def save_fig(fig, name: str) -> str:
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    return path


def mean_sd(df: pd.DataFrame, var: str):
    return float(df[var].mean()), float(df[var].std(ddof=1))
