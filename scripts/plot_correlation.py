import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ۱. بارگذاری داده‌ها
df = pd.read_csv('data/ALV_Study_50_Participants.csv')

# ۲. استخراج گروه از روی Participant_ID (دو حرف اول نام)
df['Group'] = df['Participant_ID'].str[:2]

# ۳. تنظیمات ظاهری و رنگ‌بندی حرفه‌ای
sns.set_context("paper", font_scale=1.2)
plt.figure(figsize=(12, 7))

# ۴. رسم نمودار پراکندگی و خطوط رگرسیون به تفکیک گروه
# گروه‌ها: PM (آبی)، AB (نارنجی)، CH (سبز)
palette = {"PM": "#1f77b4", "AB": "#ff7f0e", "CH": "#2ca02c"}

scatter_plot = sns.lmplot(
    data=df, x='ALV_Score', y='ODP_Score', hue='Group',
    palette=palette, height=6, aspect=1.5,
    scatter_kws={'alpha':0.7, 's':60}, line_kws={'linewidth':2}
)

# ۵. افزودن جزئیات نهایی
plt.title('The Veneer Gap Analysis: Group Comparison (PM vs AB vs CH)', pad=20)
plt.xlabel('Artificial Linguistic Veneer Score (ALV)')
plt.ylabel('Oral Descriptive Proficiency (ODP)')

# ۶. ذخیره برای گیت‌هاب و مقاله
plt.savefig('figures/ALV_ODP_Grouped_Analysis.png', dpi=300, bbox_inches='tight')
print("نمودار تفکیکی با موفقیت در پوشه figures ذخیره شد.")
plt.show()
