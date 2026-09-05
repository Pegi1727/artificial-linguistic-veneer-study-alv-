"""Step 2 - Descriptive statistics, normality, and correlation matrix (with p-values).

Outputs:
  outputs/descriptives.csv
  outputs/correlation_matrix.csv          (r matrix, 3 decimals)
  outputs/correlation_pvalues.csv         (p-value matrix, APA formatted)
  outputs/fig_descriptives_distributions.png
 (p-value matrix, APA formatted)
  outputs/fig_descriptives_distributions.png

import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import common

V = common.VARS
LAB = common.LABELS


def descriptives(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for v in V:
        x = df[v].astype(float)
        sh_w, sh_p =        sh_w, sh_p =.append({
            "Variable": LAB[v],
            "N": int(x.notna().sum()),
            "M": round(float(x.mean()), 3),
            "SD": round(float(x.std(ddof=1)), 3),
            "Min": round(float(x.min()), 2),
            "Max": round(float(x.max()), 2),
            "Skewness": round(float(stats.skew(x, bias=False)), 3),
            "Kurtosis": round(float(stats.kurtosis(x, bias=False)), 3),
            "Shapiro_W": round(float(sh_w), 3),
            "Shapiro_p": common.apa_p(float(sh_p)),
        })
    return pd.DataFrame(rows)


def corr_with_p(df: pd.DataFrame):
    k = len(V)
    r = np.eye(k)
    p = np.zeros((k, k))
    for i in range(k):
        for j in range(i + 1, k):
            rval, pval = stats.pearsonr(df[V[i]], df[V[j]])
            r[i, j] = r[j, i] = rval
            p[i, j] = p[j, i] = pval
    return r, p


def star(p: float) -> str:
    return "***" if p < .001 else ("**" if p < .01 else ("*" if p < .05 else ""))


def main() -> int:
    os.makedirs(common.OUT, exist_ok=True)
    df = common.load_clean()

    desc = descriptives(df)
    desc.to_csv(os.path.join(common.OUT, "descriptives.csv"), index=False)
    print("[02] descriptives:\n" + desc.to_string(index=False))

    r, p = corr_with_p(df)
    labels = [LAB[v] for v in V]
    rmat = pd.DataFrame(np.round(r, 3), index=labels, columns=labels)
    pmat = pd.DataFrame(
        [["\u2014" if i == j else common.apa_p(p[i, j]) for j in range(len(V))]
         for i in range(len(V))],
        index=labels, columns=labels)
    rmat.to_csv(os.path.join(common.OUT, "correlation_matrix.csv"))
    pmat.to_csv(os.path.join(common.OUT, "correlation_pvalues.csv"))
    print("[02] correlations:\n" + rmat.to_string())
    print("[02] p-values:\n" + pmat.to_string())

    # Figure: distributions
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, v in zip(axes, V):
        ax.hist(df[v], bins=12, color="#7aa6c2", edgecolor="white")
        ax.set_title(LAB[v], fontsize=11)
        ax.set_xlabel("Score (1-5)")
        ax.set_ylabel("Frequency")
    fig.suptitle("Distributions of Study Variables (clean data)", fontsize=13)
    fig.tight_layout()
    common.save_fig(fig, "fig_descriptives_distributions.png")
    plt.close(fig)

    # Figure: correlation heatmap
    fig, ax = plt.subplots(figsize=(7, 5.5))
    im = ax.imshow(r, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(V)))
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_yticks(range(len(V)))
    ax.set_yticklabels(labels, fontsize=9)
    for i in range(len(V)):
        for j in range(len(V)):
            ax.text(j, i, f"{r[i, j]:.2f}{'' if i == j else star(p[i, j])}",
                    ha="center", va="center",
                    color="white" if abs(r[i, j]) > 0.6 else "black", fontsize=11)
    fig.colorbar(im, ax=ax, label="Pearson r")
    ax.set_title(f"Correlation matrix (N = {len(df)})\n* p<.05, ** p<.01, *** p<.001",
                 fontsize=11)
    fig.tight_layout()
    common.save_fig(fig, "fig_correlation_matrix.png")
    plt.close(fig)

    print("[02] outputs written to", common.OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
