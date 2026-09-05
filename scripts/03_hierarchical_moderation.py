"""Step 3 - Hierarchical multiple regression with moderation (AI Agency x ALV).

Model 1: ODP ~ ALV
Model 2: ODP ~ ALV + AI_Agency
Model 3: ODP ~ ALV + AI_Agency + ALV*AI_Agency   (predictors mean-centred for
the interaction model; simple slopes at -1 SD, M, +1 SD of the moderator)

Outputs:
  outputs/hierarchical_regression.csv
  outputs/model_comparison.csv          (R2 change, F-change tests)
  outputs/simple_slopes.csv
  outputs/fig_simple_slopes.png
  outputs/fig_path_model.png_simple_slopes.png
  outputs/fig_path_model.png sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import common


def ols(X: np.ndarray, y: np.ndarray):
    """OLS with classic standard errors. X must already include a constant col."""
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df_res = n - k
    sigma2 = resid @ resid / df_res
    cov = sigma2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), df_res)
    r2 = 1 - resid @ resid / ((y - y.mean()) @ (y - y.mean()))
    adj = 1 - (1 - r2) * (n - 1) / df_res
    f = (r2 / (k - 1)) / ((1 - r2) / df_res)
    fp = stats.f.sf(f, k - 1, df_res)
    return dict(beta=beta, se=se, t=t, p=p, r2=r2, adj_r2=adj, f=f, fp=fp,
                df=(k - 1, df_res), resid=resid, n=n)


def run_models(df: pd.DataFrame):
    y = df["ODP"].to_numpy(float)
    alv = common.zscoreALV"]).to_numpy(float)
    aia = common.z common.zscore(df["AI_Agency"]).to_numpy(float)
    inter = alv * aia
    one = np.ones_like(y)
    names_c = ["Constant", "ALV (centred)", "AI Agency (centred)", "ALV x AI Agency"]
    models = [
        ("Model 1", np.column_stack([one, alv]), names_c[:2]),
        ("Model 2", np.column_stack([one, alv, aia]), names_c[:3]),
        ("Model 3", np.column_stack([one, alv, aia, inter]), names_c),
    ]
    results = []
    for name, X, nms in models:
        m = ols(X, y)
        for i, nm in enumerate(nms):
            results.append({
                "Model": name, "Predictor": nm,
                "B": round(float(m["beta"][i]), 3),
                "SE": round(float(m["se"][i]), 3),
                "t": round(float(m["t"][i]), 2),
                "p": common.apa_p(float(m["p"][i])),
                "sig": "***" if m["p"][i] < .001 else ("**" if m["p"][i] < .01 else
                       ("*" if m["p"][i] < .05 else "")),
            })
        results[-len(nms)]["R2"] = round(float(m["r2"]), 3)
        results[-len(nms)]["Adj_R2"] = round(float(m["adj_r2"]), 3)
    return results, models


def r2_change(models):
    rows = []
    for i, (name, _, _) in enumerate(models):
        m = models[i][0] if False else None
    prev = None
    for i, (name, X, nms) in enumerate(models):
        m = ols(X, X[:, 0] * 0 + X[:, 0] * 0)  # placeholder, replaced below
    rows = []
    y_key = None
    return rows


def model_comparison(models, y):
    rows = []
    prev = None
    for name, X, nms in models:
        m = ols(X, y)
        if prev is None:
            rows.append({"Model": name, "R2": round(m["r2"], 3),
                         "Adj_R2": round(m["adj_r2"], 3),
                         "df": f"{m['df'][0]:.0f}, {m['df'][1]:.0f}",
                         "F": round(m["f"], 2), "F_p": common.apa_p(m["fp"]),
                         "dR2": "", "dF": "", "dF_p": ""})
        else:
            dr2 = m["r2"] - prev["r2"]
            df1 = X.shape[1] - prev["X"].shape[1]
            df2 = m["df"][1]
            dF = (dr2 / df1) / ((1 - m["r2"]) / df2)
            dp = stats.f.sf(dF, df1, df2)
            rows.append({"Model": name, "R2": round(m["r2"], 3),
                         "Adj_R2": round(m["adj_r2"], 3),
                         "df": f"{m['df'][0]:.0f}, {m['df'][1]:.0f}",
                         "F": round(m["f"], 2), "F_p": common.apa_p(m["fp"]),
                         "dR2": round(dr2, 3), "dF": round(dF, 2),
                         "dF_p": common.apa_p(dp)})
        m["X"] = X
        prev = m
    return rows


def simple_slopes(df: pd.DataFrame):
    y = df["ODP"].to_numpy(float)
    aia_c = common.zscore(df["AI_Agency"]).to_numpy(float)
    alv_c = common.zscore(df["ALV"]).to_numpy(float)
    sd = df["ALV"].std(ddof=1)
    rows = []
    for label, z in [("Low (-1 SD)", -1.0), ("Mean", 0.0), ("High (+1 SD)", 1.0)]:
        # slope of ALV at aia = z: b1 + b3*z, SE from covariance matrix
        X = np.column_stack([np.ones_like(y), alv_c, aia_c, alv_c * aia_c])
        m = ols(X, y)
        b1, b3 = m["beta"][1], m["beta"][3]
        C = np.array([0, 1, 0, z])
        var = C @ np.linalg.pinv(X.T @ X) @ C * (m["resid"] @ m["resid"]) / m["df"][1]
        se = float(np.sqrt(var))
        t = (b1 + b3 * z) / se
        p = 2 * stats.t.sf(abs(t), m["df"][1])
        rows.append({"Moderator_Level": label,
                     "Slope": round(float(b1 + b3 * z), 3),
                     "SE": round(se, 3), "t": round(float(t), 2),
                     "p": common.apa_p(float(p))})
    return rows


def fig_simple_slopes(df, rows, path):
    y = df["ODP"].to_numpy(float)
    alv_c = common.zscore(df["ALV"]).to_numpy(float)
    aia_mean = df["AI_Agency"].mean()
    aia_sd = df["AI_Agency"].std(ddof=1)
    fig, ax = plt.subplots(figsize=(7, 5))
    xs = np.linspace(alv_c.min(), alv_c.max(), 50)
    X = np.column_stack([np.ones_like(y), alv_c,
                         common.zscore(df["AI_Agency"]).to_numpy(float),
                         alv_c * common.zscore(df["AI_Agency"]).to_numpy(float)])
    m = ols(X, y)
    colors = ["#1f77b4", "#888888", "#d62728"]
    for (label, z), c in zip([(r["Moderator_Level"],
                               -1.0 if "Low" in r["Moderator_Level"] else
                               (1.0 if "High" in r["Moderator_Level"] else 0.0)),
                              for r in rows], colors):
        pass
    for row, c in zip(rows, colors):
        z = -1.0 if "Low" in row["Moderator_Level"] else (
            1.0 if "High" in row["Moderator_Level"] else 0.0)
        ys = (m["beta"][0] + m["beta"][1] * xs + m["beta"][2] * z +
              m["beta"][3] * xs * z)
        ax.plot(xs, ys, color=c, lw=2,
                label=f"AI Agency {row['Moderator_Level']} (b={row['Slope']:.2f}, "
                      f"p={row['p']})")
    ax.set_xlabel("ALV (centred)")
    ax.set_ylabel("Oral Defense Performance (centred scale)")
    ax.axhline(0, color="grey", lw=.5, ls=":")
    ax.axvline(0, color="grey", lw=.5, ls=":")
    ax.legend(fontsize=9)
    ax.set_title("Simple slopes of ALV on ODP by AI")
    plt fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_path_model(coef, path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    b_alv = coef.get("ALV (centred)")
    b_aia = coef.get("AI Agency (centred)")
    b_int = coef.get("ALV x AI Agency")
    box = dict(boxstyle="round,pad=0.4", fc="#eef3f8", ec="#33526b")
    ax.text(0.15, 0.5, "ALV", ha="center", va="center", fontsize=13, bbox=box)
    ax.text(0.5, 0.85, "AI Agency", ha="center", va="center", fontsize=13, bbox=box)
    ax.text(0.85, 0.5, "Oral Defense\nPerformance", ha="center", va="center",
            fontsize=13, bbox=box)
    ax.annotate("", xy=(0.74, 0.5), xytext=(0.26, 0.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="#33526b"))
    ax.text(0.5, 0.55, f"b = {b_alv}", ha="center", fontsize=11)
    ax.annotate("", xy=(0.82, 0.66), xytext=(0.55, 0.8),
                arrowprops=dict(arrowstyle="->", lw=2, color="#33526b"))
    ax.text(0.74, 0.8, f"b = {b_aia}", ha="center", fontsize=11)
    ax.text(0.5, 0.2, f"ALV x AI Agency: b = {b_int} (interaction)",
            ha="center", fontsize=11,
            bbox=dict(boxstyle="round,pad=0.3", fc="#fdf3e7", ec="#b8860b"))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title("Moderation path model (Model 3)")
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    os.makedirs(common.OUT, exist_ok=True)
    df = common.load_clean()
    y = df["ODP"].to_numpy(float)

    results, models = run_models(df)
    reg = pd.DataFrame(results)
    reg.to_csv(os.path.join(common.OUT, "hierarchical_regression.csv"), index=False)
    print("[03] hierarchical regression:\n" + reg.to_string(index=False))

    comp = pd.DataFrame(model pd.DataFrame(model_comparison))
    comp.to_csv(os.path.join(common.OUT, "model_comparison.csv"), index=False)
    print("[03] model comparison:\n" + comp.to_string(index=False))

    ss = pd.DataFrame(simple_slopes(df))
    ss.to_csv(os.path.join(common.OUT, "simple_slopes.csv"), index=False)
    print("[03] simple slopes:\n" + ss.to_string(index=False))

    fig_simple_slopes(df, ss, os.path.join(common.OUT, "fig_simple_slopes.png"))

    coef = {r["Predictor"]: r["B"] for r in results if r["Model"] == "Model 3"}
    fig_path_model(coef, os.path.join(common.OUT, "fig_path_model.png"))

    print("[03] outputs written to", common.OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
