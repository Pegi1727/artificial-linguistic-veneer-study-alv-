from pathlib import Path
import os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
np.random.seed(2025)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
CANDIDATES=[ROOT/"reconstructed_raw_data_50.csv", HERE.parent/"reconstructed_raw_data_50.csv", Path.cwd()/"../reconstructed_raw_data_50.csv"]
INPUT=next((p for p in CANDIDATES if p.exists()),None)
if INPUT is None: raise FileNotFoundError("Place reconstructed_raw_data_50.csv in package root (or ../ relative to scripts).")
OUT=ROOT/"replication_outputs"/"script_outputs"; OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(INPUT); required=["participant_id","ALV","AI_Agency","ODP"]
if not set(required).issubset(df.columns): raise ValueError("Required columns: "+str(required))
V=["ALV","AI_Agency","ODP"]; x=df[V].astype(float); y=x.ODP
a=x.ALV-x.ALV.mean(); b=x.AI_Agency-x.AI_Agency.mean(); d=pd.DataFrame({"ALV":a,"AI_Agency":b,"ALV_x_AI_Agency":a*b})
def save(obj,name,index=False): obj.to_csv(OUT/name,index=index)
def fit(cols): return sm.OLS(y,sm.add_constant(d[cols])).fit()
def coef_table(m,label):
 ci=m.conf_int(); return pd.DataFrame({"Predictor":m.params.index,"B":m.params.values,"SE":m.bse.values,"t":m.tvalues.values,"p":m.pvalues.values,"CI_low":ci[0].values,"CI_high":ci[1].values,"Model":label,"R2":m.rsquared,"Adj_R2":m.rsquared_adj,"F":m.fvalue,"F_p":m.f_pvalue})

m=fit(["ALV","AI_Agency","ALV_x_AI_Agency"]); infl=m.get_influence(); r=pd.DataFrame({"participant_id":df.participant_id,"fitted":m.fittedvalues,"residual":m.resid,"standardized_residual":infl.resid_studentized_internal,"leverage":infl.hat_matrix_diag,"cooks_distance":infl.cooks_distance[0]}); print(r.describe()); save(r,"18_regression_diagnostics.csv")
