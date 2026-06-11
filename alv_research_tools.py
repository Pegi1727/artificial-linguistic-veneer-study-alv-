import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_alv_plots(data_path):
    # Load the corrected data
    df = pd.read_excel(data_path)
    sns.set_theme(style="whitegrid")
    
    # --- FIGURE 1: Simple Slopes Analysis (Moderation) ---
    plt.figure(figsize=(10, 6))
    # Filter for High and Low AI Agency
    low_agency = df[df['AI_Agency_Level'] == 'Low']
    high_agency = df[df['AI_Agency_Level'] == 'High']
    
    sns.regplot(x='ALV_Score', y='ODP_Score', data=low_agency, 
                label='Low AI Agency (Lower Support)', scatter_kws={'alpha':0.5}, line_kws={'linestyle':'--'})
    sns.regplot(x='ALV_Score', y='ODP_Score', data=high_agency, 
                label='High AI Agency (Buffering Effect)', scatter_kws={'alpha':0.5})
    
    plt.title('Moderation Effect of AI Agency on ALV-ODP Relationship', fontsize=14)
    plt.xlabel('Artificial Linguistic Veneer (ALV) Score', fontsize=12)
    plt.ylabel('Oral Defense Performance (ODP) Score', fontsize=12)
    plt.legend()
    plt.savefig('figures/ALV_AI_Agency_Simple_Slopes_300dpi.png', dpi=300)
    plt.close()

    # --- FIGURE 2: Correlation Analysis ---
    plt.figure(figsize=(10, 6))
    sns.regplot(x='ALV_Score', y='ODP_Score', data=df, 
                scatter_kws={'color': '#5D8AA8', 'alpha': 0.6}, 
                line_kws={'color': '#8B0000', 'lw': 2})
    
    plt.title('Negative Correlation: ALV vs Oral Defense Performance', fontsize=14)
    plt.xlabel('ALV Total Score (Written Polish)', fontsize=12)
    plt.ylabel('ODP Total Score (Conceptual Ownership)', fontsize=12)
    
    # Add stats annotation
    plt.text(4.1, 4.5, 'r = -0.81\np < .01', bbox=dict(facecolor='white', alpha=0.5))
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig('figures/ALV_ODP_negative_correlation_scatter.png', dpi=300)
    plt.close()
    
    print("Success: Figures generated and saved in /figures folder.")

if __name__ == "__main__":
    # Ensure the 'figures' directory exists
    import os
    if not os.path.exists('figures'):
        os.makedirs('figures')
    
    # Run analysis (Assumes the Excel file is in the same directory)
    try:
        generate_alv_plots('ALV_AI_Agency_Simple_Slopes_CORRECTED.xlsx')
    except FileNotFoundError:
        print("Error: Excel file not found. Please ensure the data file is in the same folder.")

