import os
import json
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

OUTPUT_DIR = os.path.join("reports", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_figure2_counterfactual_bias():
    models = ['Gemini Legacy\n(Condition 1)', 'Gemini Expanded\n(Condition 2)', 'Gemini Unified\n(Condition 3)', 'Grok Unified\n(Condition 4)']
    rates = [19.31, 18.56, 22.15, 38.31]
    ci_lower = [15.71, 14.99, 18.60, 33.99]
    ci_upper = [22.87, 22.20, 25.75, 42.74]

    yerr_lower = [r - l for r, l in zip(rates, ci_lower)]
    yerr_upper = [u - r for r, u in zip(rates, ci_upper)]
    yerr = [yerr_lower, yerr_upper]

    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    colors = ['#2b5c8f', '#337ab7', '#4682b4', '#d9534f']
    
    bars = ax.bar(models, rates, yerr=yerr, capsize=6, color=colors, edgecolor='black', alpha=0.85, width=0.55)

    for bar, r in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 3.0, f'{r:.2f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_ylabel('Counterfactual Sensitive Bias Rate (%)', fontweight='bold')
    ax.set_title('Counterfactual Protected Attribute Bias Across Controlled Prompt Conditions\n(With 95% Clustered Bootstrap CIs)', fontweight='bold', pad=15)
    ax.set_ylim(0, 50)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_counterfactual_bias_rates.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_counterfactual_bias_rates.pdf"))
    plt.close()
    print("Generated Figure 2.")

def generate_figure3_domain_breakdown():
    domains = [
        "Social Benefits", "Employee Dev. & Benefits", "Licensing", 
        "Hobbies", "University Admissions", "Health Exams", "Occupations"
    ]
    gemini_domain = [54.51, 44.31, 24.19, 18.00, 10.63, 2.67, 2.01]
    grok_domain = [64.71, 83.14, 55.60, 42.67, 16.08, 8.33, 4.40]

    x = np.arange(len(domains))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    rects1 = ax.bar(x - width/2, gemini_domain, width, label='Gemini 2.5 Flash (Unified)', color='#4682b4', edgecolor='black', alpha=0.85)
    rects2 = ax.bar(x + width/2, grok_domain, width, label='Grok-Code-Fast-1 (Unified)', color='#d9534f', edgecolor='black', alpha=0.85)

    ax.set_ylabel('Counterfactual Sensitive Bias Rate (%)', fontweight='bold')
    ax.set_title('Domain-Level Counterfactual Sensitive Attribute Bias Comparison', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(domains, rotation=25, ha='right')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.set_ylim(0, 95)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_domain_breakdown.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_domain_breakdown.pdf"))
    plt.close()
    print("Generated Figure 3.")

def generate_figure4_behavioral_inconsistency():
    models = ['Gemini Legacy\n(Condition 1)', 'Gemini Expanded\n(Condition 2)', 'Gemini Unified\n(Condition 3)', 'Grok Unified\n(Condition 4)']
    full_agreement = [98, 83, 36, 23]
    minor_disagreement = [146, 142, 160, 239]
    major_disagreement = [99, 118, 147, 81]

    fig, ax = plt.subplots(figsize=(9.5, 5), dpi=300)
    x = np.arange(len(models))
    width = 0.55

    p1 = ax.bar(x, full_agreement, width, label='Full Agreement (100%)', color='#1B365D', edgecolor='white', linewidth=0.5)
    p2 = ax.bar(x, minor_disagreement, width, bottom=full_agreement, label='Minor Disagreement (80%–99%)', color='#7895A2', edgecolor='white', linewidth=0.5)
    
    bottom_major = [i + j for i, j in zip(full_agreement, minor_disagreement)]
    p3 = ax.bar(x, major_disagreement, width, bottom=bottom_major, label='Major Disagreement (<80%)', color='#8B2626', edgecolor='white', linewidth=0.5)

    ax.set_ylabel('Number of Evaluated Decision Tasks (out of 343)', fontweight='bold')
    ax.set_title('Generative Behavioral Inconsistency Across Independent Executions', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.set_ylim(0, 370)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_behavioral_inconsistency.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_behavioral_inconsistency.pdf"))
    plt.close()
    print("Generated Figure 4.")

def generate_complexity_combined():
    metrics_dir = os.path.join("reports", "feature_metrics")
    with open(os.path.join(metrics_dir, "code_complexity_gemini_legacy.json")) as f:
        legacy = json.load(f)
    with open(os.path.join(metrics_dir, "code_complexity_gemini_expanded.json")) as f:
        expanded = json.load(f)
    with open(os.path.join(metrics_dir, "code_complexity_gemini_unified.json")) as f:
        gemini = json.load(f)
    with open(os.path.join(metrics_dir, "code_complexity_grok_unified.json")) as f:
        grok = json.load(f)

    max_vars = 12
    bins = np.arange(0, max_vars + 2) - 0.5
    
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Palatino', 'Times New Roman', 'DejaVu Serif']

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    
    counts_legacy, _ = np.histogram(legacy, bins=bins)
    counts_expanded, _ = np.histogram(expanded, bins=bins)
    counts_gemini, _ = np.histogram(gemini, bins=bins)
    counts_grok, _ = np.histogram(grok, bins=bins)

    x = np.arange(0, max_vars + 1)
    width = 0.19

    # Curated Nature/MDPI Journal Palette: 3 progressive ColorBrewer blues for Gemini + Onyx Black for Grok
    c_legacy   = '#bdd7e7'  # Soft light blue
    c_expanded = '#6baed6'  # Mid blue
    c_gemini   = '#2171b5'  # Deep royal blue
    c_grok     = '#1a1a1a'  # Onyx black

    ax.bar(x - 1.5*width, counts_legacy, width, label='Gemini Legacy (Cond. 1)', color=c_legacy, alpha=0.92, edgecolor='black', linewidth=0.5)
    ax.bar(x - 0.5*width, counts_expanded, width, label='Gemini Expanded (Cond. 2)', color=c_expanded, alpha=0.92, edgecolor='black', linewidth=0.5)
    ax.bar(x + 0.5*width, counts_gemini, width, label='Gemini Unified (Cond. 3)', color=c_gemini, alpha=0.92, edgecolor='black', linewidth=0.5)
    ax.bar(x + 1.5*width, counts_grok, width, label='Grok Unified (Cond. 4)', color=c_grok, alpha=0.92, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Number of Input Variables Utilized Per Function', fontweight='bold', fontsize=12)
    ax.set_ylabel('Number of Generated Functions', fontweight='bold', fontsize=12)
    ax.set_title('Distribution of Utilized Input Variables Across Controlled Prompt Conditions', fontweight='bold', fontsize=13, pad=12)
    ax.set_xticks(x)
    ax.set_xlim(-0.6, 12.6)
    ax.set_ylim(0, max(max(counts_legacy), max(counts_expanded), max(counts_gemini), max(counts_grok)) * 1.15)
    
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#d0d0d0', framealpha=0.95, fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.45, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "complexity_combined.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "complexity_combined.pdf"))
    
    # Also save to MDPI Assets
    assets_dir = os.path.join("MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models", "Assets")
    if os.path.exists(assets_dir):
        fig.savefig(os.path.join(assets_dir, "complexity_combined.png"), dpi=300)
        fig.savefig(os.path.join(assets_dir, "complexity_combined.pdf"))
        
    plt.close()
    print("Generated 4-condition complexity_combined figure with ColorBrewer journal palette.")

def generate_frequency_combined():
    metrics_dir = os.path.join("reports", "feature_metrics")
    with open(os.path.join(metrics_dir, "attribute_frequency_gemini_legacy.json")) as f:
        legacy = json.load(f)
    with open(os.path.join(metrics_dir, "attribute_frequency_gemini_expanded.json")) as f:
        expanded = json.load(f)
    with open(os.path.join(metrics_dir, "attribute_frequency_gemini_unified.json")) as f:
        gemini = json.load(f)
    with open(os.path.join(metrics_dir, "attribute_frequency_grok_unified.json")) as f:
        grok = json.load(f)

    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Palatino', 'Times New Roman', 'DejaVu Serif']

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=300)
    
    conditions = [
        ('Gemini Legacy (Condition 1)', legacy, '#bdd7e7', axes[0, 0]),
        ('Gemini Expanded (Condition 2)', expanded, '#6baed6', axes[0, 1]),
        ('Gemini Unified (Condition 3)', gemini, '#2171b5', axes[1, 0]),
        ('Grok Unified (Condition 4)', grok, '#1a1a1a', axes[1, 1])
    ]

    for title, data, color, ax in conditions:
        # Sort ascending for horizontal bar plot
        items = list(data.items())[:10][::-1]
        labels = [item[0].replace('_', ' ').title() for item in items]
        values = [item[1] for item in items]
        
        bars = ax.barh(labels, values, color=color, alpha=0.92, edgecolor='black', linewidth=0.5, height=0.65)
        ax.set_title(title, fontweight='bold', fontsize=11, pad=8)
        ax.set_xlim(0, max(values) * 1.18)
        ax.grid(True, linestyle=':', alpha=0.45, axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for bar, val in zip(bars, values):
            ax.text(val + max(values)*0.015, bar.get_y() + bar.get_height()/2.0, str(val),
                    va='center', ha='left', fontsize=9, fontweight='bold')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_frequency_combined.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_frequency_combined.pdf"))
    
    # Save to MDPI Assets
    assets_dir = os.path.join("MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models", "Assets")
    if os.path.exists(assets_dir):
        fig.savefig(os.path.join(assets_dir, "attribute_frequency_combined.png"), dpi=300)
        fig.savefig(os.path.join(assets_dir, "attribute_frequency_combined.pdf"))
        
    plt.close()
    print("Generated 4-condition attribute_frequency_combined 2x2 grid.")

def main():
    generate_figure2_counterfactual_bias()
    generate_figure3_domain_breakdown()
    generate_figure4_behavioral_inconsistency()
    generate_complexity_combined()
    generate_frequency_combined()
    print("All paper figures successfully updated in reports/figures!")

if __name__ == "__main__":
    main()
