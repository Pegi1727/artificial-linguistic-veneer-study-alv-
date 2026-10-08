#!/usr/bin/env python3
"""Standalone ALV research analysis; accepts a CSV or generates reproducible demo data."""
import argparse, os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", category=RuntimeWarning)
def get_data(path):
    if path:
        df=pd.read_csv(path)
    else:
        rng=np.random.default_rng(2026); n=180
        x=rng.normal(size=n); w=rng.normal(size=n); e=rng.normal(scale=.8,size=n)
        df=pd.DataFrame({"ALV":x,"AI_Agency":w,"ODP":1.2+.45*x+.30*w+.25*x*w+e,
                         "age":rng.integers(18,45,n),"gender":rng.choice([1,2,3],n)})
        for col in ["ALV","AI_Agency","ODP"]: df[col]=np.round(df[col],3)
    return df
def out(name, df):
    path=os.path.join(OUT,name); df.to_csv(path,index=False); print("Saved:",path)
def model_data(df, cols=("ALV","AI_Agency","ODP")):
    missing=[c for c in cols if c not in df]
    if missing: raise ValueError("Required columns missing: "+", ".join(missing))
    return df[list(cols)].apply(pd.to_numeric,errors="coerce").dropna()
def main():
    global OUT
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--input",help="CSV input; defaults to generated demo dataset")
    ap.add_argument("--outdir",default="analysis_output",help="Output directory")
    a=ap.parse_args(); OUT=a.outdir; os.makedirs(OUT,exist_ok=True); df=get_data(a.input)
    print(f"Rows={len(df)}; columns={list(df.columns)}")
    """Topic 11: simple_regression_model1."""
    d=model_data(df,("ALV","ODP")); m=smf.ols("ODP ~ ALV",data=d).fit(); out("simple_regression_model1.csv",pd.DataFrame({"term":m.params.index,"estimate":m.params.values,"se":m.bse.values,"t":m.tvalues.values,"p":m.pvalues.values})); print(m.summary())

if __name__=="__main__": main()
