import os
import json
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join("reports", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Palatino', 'Times New Roman', 'DejaVu Serif']

def generate_magic_numbers_charts():
    metrics_dir = os.path.join("reports", "feature_metrics")
    
    with open(os.path.join(metrics_dir, "injected_thresholds_gemini_legacy.json")) as f:
        legacy_raw = json.load(f)
    with open(os.path.join(metrics_dir, "injected_thresholds_gemini_expanded.json")) as f:
        expanded_raw = json.load(f)
    with open(os.path.join(metrics_dir, "injected_thresholds_gemini_unified.json")) as f:
        gemini_raw = json.load(f)
    with open(os.path.join(metrics_dir, "injected_thresholds_grok_unified.json")) as f:
        grok_raw = json.load(f)

    def extract_top_attributes(data_raw, top_k=10):
        from collections import Counter
        c = Counter()
        if isinstance(data_raw, list):
            for item in data_raw:
                attr = item.get("attribute", "")
                if attr:
                    c[attr] += 1
        elif isinstance(data_raw, dict):
            for k, v in data_raw.items():
                count = int(v) if isinstance(v, (int, str)) and str(v).isdigit() else len(v) if isinstance(v, list) else 1
                c[k] = count
        return c.most_common(top_k)

    # 2x2 Grid matching exact paper aesthetics and layout
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=300)
    
    conditions = [
        ("Gemini Legacy (Condition 1)", legacy_raw, "#9ecae1", axes[0, 0], 145),
        ("Gemini Expanded (Condition 2)", expanded_raw, "#6baed6", axes[0, 1], 55),
        ("Gemini Unified (Condition 3)", gemini_raw, "#2171b5", axes[1, 0], 33),
        ("Grok Unified (Condition 4)", grok_raw, "#252525", axes[1, 1], 20.5)
    ]
    
    for title, raw_data, color, ax, y_limit in conditions:
        top_items = extract_top_attributes(raw_data, top_k=10)
        if not top_items:
            continue
        
        labels = [item[0].replace('_', ' ').title() for item in top_items]
        counts = [item[1] for item in top_items]
        
        x = np.arange(len(labels))
        bars = ax.bar(x, counts, color=color, alpha=0.9, edgecolor='black', linewidth=0.8, width=0.58)
        
        ax.set_title(title, fontweight='bold', fontsize=12, pad=10)
        ax.set_ylabel('Number of Unprompted Thresholds', fontweight='bold', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.set_ylim(0, y_limit)
        ax.grid(True, linestyle='--', alpha=0.35, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, val in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (y_limit * 0.018), str(val),
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold')
                    
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "magic_numbers_chart_all4.pdf"))
    fig.savefig(os.path.join(OUTPUT_DIR, "magic_numbers_chart_all4.png"), dpi=300)
    
    # Also save to manuscript Assets directory
    ms_assets = os.path.join("MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models", "Assets")
    if os.path.exists(ms_assets):
        fig.savefig(os.path.join(ms_assets, "magic_numbers_chart_all4.pdf"))
        fig.savefig(os.path.join(ms_assets, "magic_numbers_chart_all4.png"), dpi=300)
    plt.close(fig)
    print("Generated magic_numbers_chart_all4 (Unprompted Thresholds) matching paper.")
    individual_maps = [
        ("magic_numbers_chart_gemini", "Gemini Unified Injected Thresholds", gemini_raw, "#2171b5"),
        ("magic_numbers_chart_grok", "Grok Unified Injected Thresholds", grok_raw, "#1a1a1a"),
        ("magic_numbers_chart_legacy", "Gemini Legacy Injected Thresholds", legacy_raw, "#bdd7e7")
    ]
    for filename, title, raw_data, color in individual_maps:
        top_items = extract_top_attributes(raw_data, top_k=10)
        if not top_items: continue
        labels = [item[0].replace('_', ' ').title() for item in top_items][::-1]
        counts = [item[1] for item in top_items][::-1]
        
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
        bars = ax.barh(labels, counts, color=color, alpha=0.9, edgecolor='black', linewidth=0.5, height=0.65)
        ax.set_title(title, fontweight='bold', fontsize=12, pad=10)
        ax.set_xlim(0, max(counts) * 1.18)
        ax.grid(True, linestyle=':', alpha=0.45, axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, val in zip(bars, counts):
            ax.text(val + max(counts)*0.015, bar.get_y() + bar.get_height()/2.0, str(val),
                    va='center', ha='left', fontsize=10, fontweight='bold')
        fig.tight_layout()
        fig.savefig(os.path.join(OUTPUT_DIR, f"{filename}.pdf"))
        fig.savefig(os.path.join(OUTPUT_DIR, f"{filename}.png"), dpi=300)
        plt.close(fig)

    print("Generated all magic numbers and threshold distribution figures.")

def generate_protected_bias_chart_all4():
    metrics_dir = os.path.join("reports", "feature_metrics")
    
    with open(os.path.join(metrics_dir, "protected_bias_rates_gemini_legacy.json")) as f:
        legacy = json.load(f)
    with open(os.path.join(metrics_dir, "protected_bias_rates_gemini_expanded.json")) as f:
        expanded = json.load(f)
    with open(os.path.join(metrics_dir, "protected_bias_rates_gemini_unified.json")) as f:
        gemini = json.load(f)
    with open(os.path.join(metrics_dir, "protected_bias_rates_grok_unified.json")) as f:
        grok = json.load(f)

    # 2x2 Vertical Bar Grid matching the exact paper layout with large, readable fonts
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    conditions = [
        ("Gemini Legacy (Condition 1)", legacy, "#9ecae1", axes[0, 0], 450),
        ("Gemini Expanded (Condition 2)", expanded, "#6baed6", axes[0, 1], 400),
        ("Gemini Unified (Condition 3)", gemini, "#2171b5", axes[1, 0], 450),
        ("Grok Unified (Condition 4)", grok, "#252525", axes[1, 1], 650)
    ]
    
    for title, data, color, ax, y_limit in conditions:
        sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        # Filter out 0 counts
        filtered_items = [item for item in sorted_items if item[1] > 0]
        
        labels = [item[0].replace('_', ' ').title() for item in filtered_items]
        values = [item[1] for item in filtered_items]
        
        x = np.arange(len(labels))
        bars = ax.bar(x, values, color=color, alpha=0.9, edgecolor='black', linewidth=1.0, width=0.62)
        
        ax.set_title(title, fontweight='bold', fontsize=14, pad=12)
        ax.set_ylabel('Utilization Frequency', fontweight='bold', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11, fontweight='semibold')
        ax.tick_params(axis='y', labelsize=11)
        ax.set_ylim(0, y_limit)
        ax.grid(True, linestyle='--', alpha=0.35, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (y_limit * 0.015), str(val),
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
                    
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "protected_bias_chart_all4.pdf"))
    fig.savefig(os.path.join(OUTPUT_DIR, "protected_bias_chart_all4.png"), dpi=300)
    
    ms_assets = os.path.join("MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models", "Assets")
    if os.path.exists(ms_assets):
        fig.savefig(os.path.join(ms_assets, "protected_bias_chart_all4.pdf"))
        fig.savefig(os.path.join(ms_assets, "protected_bias_chart_all4.png"), dpi=300)
        
    plt.close(fig)
    print("Generated vertical protected_bias_chart_all4 matching original paper layout.")

def generate_inconsistency_chart_combined():
    # Structural variance across conditions
    models = ['Gemini Legacy\n(Condition 1)', 'Gemini Expanded\n(Condition 2)', 'Gemini Unified\n(Condition 3)', 'Grok Unified\n(Condition 4)']
    structural_variance = [63.27, 64.14, 92.42, 95.63]
    
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    colors = ['#bdd7e7', '#6baed6', '#2171b5', '#1a1a1a']
    
    bars = ax.bar(models, structural_variance, color=colors, edgecolor='black', alpha=0.88, width=0.55)
    
    for bar, val in zip(bars, structural_variance):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2.0, f'{val:.2f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
                
    ax.set_ylabel('Structural Logic Inconsistency Rate (%)', fontweight='bold', fontsize=11)
    ax.set_title('Internal Structural Logic Inconsistency Across Prompt Conditions', fontweight='bold', pad=15, fontsize=13)
    ax.set_ylim(0, 110)
    ax.grid(True, linestyle='--', alpha=0.45, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "inconsistency_chart_combined.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "inconsistency_chart_combined.pdf"))
    plt.close(fig)
    print("Generated inconsistency_chart_combined figure.")

def generate_domain_breakdown_figure():
    summary_path = os.path.join("reports", "summary", "domain_wise_bias_breakdown_summary.json")
    if not os.path.exists(summary_path):
        return
    with open(summary_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
        
    domains_list = [
        "Social Benefits", "Employee Dev. & Benefits", "Licensing", 
        "Hobbies", "University Admissions", "Health Exams", "Occupations"
    ]
    
    gemini_domain = [results["Gemini Unified"][dom]["bias_pct"] for dom in domains_list]
    grok_domain = [results["Grok Unified"][dom]["bias_pct"] for dom in domains_list]
    
    x = np.arange(len(domains_list))
    width = 0.38
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    rects1 = ax.bar(x - width/2, gemini_domain, width, label='Gemini 2.5 Flash (Unified)', color='#4682b4', edgecolor='black', alpha=0.85)
    rects2 = ax.bar(x + width/2, grok_domain, width, label='Grok-Code-Fast-1 (Unified)', color='#d9534f', edgecolor='black', alpha=0.85)
    
    ax.set_ylabel('Protected Attribute Utilization Rate (%)', fontweight='bold', fontsize=11)
    ax.set_title('Domain-Level Protected Attribute Utilization Comparison', fontweight='bold', pad=15, fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(domains_list, rotation=25, ha='right', fontsize=10)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax.set_ylim(0, 105)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_domain_breakdown.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_domain_breakdown.pdf"))
    
    ms_assets = os.path.join("MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models", "Assets")
    if os.path.exists(ms_assets):
        fig.savefig(os.path.join(ms_assets, "fig3_domain_breakdown.png"), dpi=300)
        fig.savefig(os.path.join(ms_assets, "fig3_domain_breakdown.pdf"))
    plt.close(fig)
    print("Generated fig3_domain_breakdown with Protected Attribute Utilization Rate y-axis.")

def main():
    generate_magic_numbers_charts()
    generate_protected_bias_chart_all4()
    generate_inconsistency_chart_combined()
    generate_domain_breakdown_figure()

if __name__ == "__main__":
    main()
