import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# ۱. بارگذاری داده‌ها
df = pd.read_csv('data/ALV_Study_50_Participants.csv')

# ۲. محاسبه ضریب همبستگی پیرسون
corr, _ = pearsonr(df['ALV_Score'], df['ODP_Score'])

# ۳. تنظیمات ظاهری نمودار
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

# ۴. ترسیم نمودار پراکندگی همراه با خط رگرسیون (Regression Line)
sns.regplot(data=df, x='ALV_Score', y='ODP_Score', 
            scatter_kws={'alpha':0.6, 'color': 'blue'}, 
            line_kws={'color':'red', 'label': f'Correlation r={corr:.2f}'})

# ۵. افزودن جزئیات علمی
plt.title('The Veneer Gap: Correlation between ALV and ODP Scores')
plt.xlabel('Artificial Linguistic Veneer Score (ALV)')
plt.ylabel('Oral Descriptive Proficiency (ODP)')
plt.legend()

# ۶. ذخیره نمودار با کیفیت بالا برای پایان‌نامه و README
plt.savefig('figures/ALV_ODP_Correlation_Final.png', dpi=300)
print(f"نمودار با موفقیت ذخیره شد. ضریب همبستگی مشاهده شده: {corr:.2f}")
plt.show()

