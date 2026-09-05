import pandas as pd, numpy as np, os, pickle
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
import scipy.stats as st

df = pd.read_csv('/mnt/data/cleaned_dataset_alv.csv')
names = {'ALV':'Artificial Linguistic Veneer','AI_Agency':'AI Agency','ODP':'Oral Defense Performance'}
V = ['ALV','AI_Agency','ODP']
N = len(df); y = df['ODP']
base = '/mnt/data/github_alv_study/results'
for r in (base, '/mnt/data/results'):
    os.makedirs(r+'/tables', exist_ok=True); os.makedirs(r+'/figures', exist_ok=True)

def fmt_p(p):
    if p < .001: return '<.001'
    s = f'{p:.3f}'
    return s if p >= .01 else s.replace('0.', '.')

# 1. Descriptives
rows = []
for v in V:
    s = df[v]; sk = st.skew(s, bias=False); ku = st.kurtosis(s, bias=False)
    w, pw = st.shapiro(s)
    rows.append([names[v], N, f'{s.mean():.2f}', f'{s.std(ddof=1):.2f}', f'{s.min():.2f}', f'{s.max():.2f}',
                 f'{sk:.2f}', f'{ku:.2f}', f'{w:.3f}', fmt_p(pw)])
desc = pd.DataFrame(rows, columns=['Variable','N','M','SD','Min','Max','Skewness','Kurtosis','Shapiro-Wilk W','Shapiro-Wilk p'])
desc.to_csv(f'{base}/tables/descriptive_statistics.csv', index=False)

# 2. Correlations with bootstrap CIs
labels = [names[v] for v in V]
r_m = np.zeros((3,3)); p_m = np.zeros((3,3)); ci_lo = np.zeros((3,3)); ci_hi = np.zeros((3,3))
boot = np.zeros((5000,3,3))
for i in range(5000):
    b = df.sample(N, replace=True, random_state=i)
    for a in range(3):
        for c in range(3):
            boot[i,a,c] = np.corrcoef(b[V[a]], b[V[c]])[0,1]
for a in range(3):
    for c in range(3):
        r, p = st.pearsonr(df[V[a]], df[V[c]])
        r_m[a,c], p_m[a,c] = r, p
        ci_lo[a,c], ci_hi[a,c] = np.percentile(boot[:,a,c], [2.5, 97.5])
corr_rows = []
for a in range(3):
    row = {'Variable': labels[a]}
    for c in range(3):
        if c > a: row[labels[c]] = ''
        elif c == a: row[labels[c]] = '1.00'
        else:
            stars = '**' if p_m[a,c] < .01 else ('*' if p_m[a,c] < .05 else '')
            row[labels[c]] = f'{r_m[a,c]:.2f}{stars} [{ci_lo[a,c]:.2f}, {ci_hi[a,c]:.2f}]'
    corr_rows.append(row)
corr = pd.DataFrame(corr_rows)
corr.to_csv(f'{base}/tables/correlation_matrix.csv', index=False)

# 3. Hierarchical regression
df['ALV_c'] = df['ALV'] - df['ALV'].mean()
df['AIA_c'] = df['AI_Agency'] - df['AI_Agency'].mean()
df['inter'] = df['ALV_c']*df['AIA_c']
def fit(X): return sm.OLS(y, sm.add_constant(X)).fit()
m1 = fit(df[['ALV_c']]); m2 = fit(df[['ALV_c','AIA_c']]); m3 = fit(df[['ALV_c','AIA_c','inter']])
sy = y.std()
lab = {'const':'Constant','ALV_c':'ALV (centered)','AIA_c':'AI Agency (centered)','inter':'ALV x AI Agency'}
rows = []; R2 = []
for mn, m in [('Model 1', m1), ('Model 2', m2), ('Model 3', m3)]:
    for var in m.params.index:
        b, se, t, p = m.params[var], m.bse[var], m.tvalues[var], m.pvalues[var]
        be = '' if var == 'const' else f'{b*df[var].std()/sy:.3f}'
        rows.append([mn, lab[var], f'{b:.3f}', f'{se:.3f}', be, f'{t:.3f}', fmt_p(p), f'[{b-1.96*se:.3f}, {b+1.96*se:.3f}]'])
    R2.append(m.rsquared)
    rows.append([mn, 'R2', f'{m.rsquared:.3f}', '', '', '', '', ''])
    rows.append([mn, 'Adjusted R2', f'{m.rsquared_adj:.3f}', '', '', '', '', ''])
    rows.append([mn, f'F({int(m.df_model)},{int(m.df_resid)})', f'{m.fvalue:.2f}', '', '', '', fmt_p(m.f_pvalue), ''])
F_ch12 = ((R2[1]-R2[0])/1)/((1-R2[1])/(N-3))
F_ch = ((R2[2]-R2[1])/1)/((1-R2[2])/(N-4))
rows.append(['Model 2','Delta R2 vs Model 1', f'{R2[1]-R2[0]:.3f}','','','', f'F = {F_ch12:.2f}, p = {fmt_p(1-st.f.sf(F_ch12,1,N-3))}', ''])
rows.append(['Model 3','Delta R2 vs Model 2', f'{R2[2]-R2[1]:.3f}','','','', f'F = {F_ch:.2f}, p = {fmt_p(1-st.f.sf(F_ch,1,N-4))}', ''])
hier = pd.DataFrame(rows, columns=['Model','Term','B','SE','Beta','t','p','95% CI'])
hier.to_csv(f'{base}/tables/hierarchical_regression_models.csv', index=False)

# 4. Simple slopes
sdA = df['AIA_c'].std(); srows = []
cov = m3.cov_params(); dfres = m3.df_resid
tc = st.t.ppf(.975, dfres)
for lbl, z in [('Low (-1 SD)', -1), ('Mean', 0), ('High (+1 SD)', 1)]:
    mod = z*sdA
    slope = m3.params['ALV_c'] + m3.params['inter']*mod
    L = np.array([0,1,0,mod]); se = float(np.sqrt(L @ cov @ L))
    t = slope/se; p = 2*st.t.sf(abs(t), dfres)
    srows.append([lbl, f'{slope:.3f}', f'{se:.3f}', f'{t:.3f}', fmt_p(p), f'[{slope-tc*se:.3f}, {slope+tc*se:.3f}]'])
ss = pd.DataFrame(srows, columns=['Moderator Level','Simple Slope of ALV','SE','t','p','95% CI'])
ss.to_csv(f'{base}/tables/simple_slopes_analysis.csv', index=False)

# 5. Robustness & diagnostics
X3 = sm.add_constant(df[['ALV_c','AIA_c','inter']])
vifs = [variance_inflation_factor(X3, i) for i in [1,2,3]]
bp = het_breuschpagan(m3.resid, m3.model.exog)
dw = durbin_watson(m3.resid)
cook = m3.get_influence().cooks_distance[0]
mx = int(np.argmax(cook))
sw = st.shapiro(m3.resid)
bi = []
for i in range(5000):
    b = df.sample(N, replace=True, random_state=10000+i)
    bi.append(sm.OLS(b['ODP'], sm.add_constant(b[['ALV_c','AIA_c','inter']])).fit().params['inter'])
bi = np.array(bi); blo, bhi = np.percentile(bi, [2.5, 97.5])
rows = [
 ['VIF - ALV', f'{vifs[0]:.2f}', '< 5: no problematic multicollinearity'],
 ['VIF - AI Agency', f'{vifs[1]:.2f}', ''],
 ['VIF - ALV x AI Agency', f'{vifs[2]:.2f}', ''],
 ['Breusch-Pagan LM', f'{bp[0]:.2f}', 'Heteroscedasticity test'],
 ['Breusch-Pagan p', fmt_p(bp[1]), 'Homoscedasticity assumption ' + ('violated' if bp[1] < .05 else 'not violated')],
 ['Durbin-Watson', f'{dw:.2f}', '~2: independent residuals'],
 ['Shapiro-Wilk W (residuals)', f'{sw[0]:.3f}', 'p = ' + fmt_p(sw[1])],
 ["Max Cook's D", f'{cook.max():.3f}', f"Case #{int(df.participant_id[mx])}; 4/N threshold = {4/N:.3f}"],
 ["Cases with Cook's D > 4/N", str(int((cook > 4/N).sum())), 'No influential cases' if (cook > 4/N).sum() == 0 else 'Review flagged cases'],
 ['Bootstrap 95% CI for interaction (5,000 resamples)', f'[{blo:.3f}, {bhi:.3f}]', 'Percentile bootstrap; ' + ('excludes 0' if (blo > 0 or bhi < 0) else 'includes 0')],
]
rob = pd.DataFrame(rows, columns=['Statistic','Value','Interpretation'])
rob.to_csv(f'{base}/tables/robustness_and_diagnostics.csv', index=False)

pickle.dump(dict(m1=m1, m2=m2, m3=m3, R2=R2, desc=desc, corr=corr, hier=hier, ss=ss, rob=rob,
   r_m=r_m, p_m=p_m, ci_lo=ci_lo, ci_hi=ci_hi, labels=labels, vifs=vifs, bp=bp, dw=dw, cook=cook,
   blo=blo, bhi=bhi, sdA=sdA, F_ch12=F_ch12, F_ch=F_ch, sw=sw, mx=mx, df=df),
   open(f'{base}/_state.pkl', 'wb'))
print('R2:', [f'{r:.3f}' for r in R2], 'F12=%.2f F23=%.2f' % (F_ch12, F_ch))
print('VIF', np.round(vifs,2), 'BP LM=%.2f p=%.3f' % (bp[0], bp[1]), 'DW=%.2f' % dw)
print('maxCook=%.3f case %d' % (cook.max(), int(df.participant_id[mx])))
print('boot inter CI [%.3f, %.3f]' % (blo, bhi))
print(m3.summary())
print('OK')
