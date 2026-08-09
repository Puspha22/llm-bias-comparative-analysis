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

    def extract_top(data_raw, top_k=10):
        # Data format can be dict of counts or list
        if isinstance(data_raw, dict):
            # Sort by frequency
            sorted_items = sorted(data_raw.items(), key=lambda x: int(x[1]) if isinstance(x[1], (int, str)) and str(x[1]).isdigit() else len(x[1]) if isinstance(x[1], list) else 1, reverse=True)
            return sorted_items[:top_k]
        elif isinstance(data_raw, list):
            from collections import Counter
            c = Counter()
            for item in data_raw:
                val = item.get("threshold") or item.get("value") or item.get("condition") or str(item)
                c[str(val)] += 1
            return c.most_common(top_k)
        return []

    # 1. 4-Condition Combined Magic Numbers
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), dpi=300)
    conditions = [
        ("Gemini Legacy (Condition 1)", legacy_raw, "#bdd7e7", axes[0, 0]),
        ("Gemini Expanded (Condition 2)", expanded_raw, "#6baed6", axes[0, 1]),
        ("Gemini Unified (Condition 3)", gemini_raw, "#2171b5", axes[1, 0]),
        ("Grok Unified (Condition 4)", grok_raw, "#1a1a1a", axes[1, 1])
    ]
    
    for title, raw_data, color, ax in conditions:
        top_items = extract_top(raw_data, top_k=8)
        if not top_items:
            continue
        labels = [str(item[0])[:20] for item in top_items][::-1]
        counts = [item[1] if isinstance(item[1], int) else len(item[1]) if isinstance(item[1], list) else 1 for item in top_items][::-1]
        
        bars = ax.barh(labels, counts, color=color, alpha=0.9, edgecolor='black', linewidth=0.5, height=0.65)
        ax.set_title(title, fontweight='bold', fontsize=11, pad=8)
        ax.set_xlim(0, max(counts) * 1.2 if counts else 10)
        ax.grid(True, linestyle=':', alpha=0.45, axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, val in zip(bars, counts):
            ax.text(val + max(counts)*0.015, bar.get_y() + bar.get_height()/2.0, str(val),
                    va='center', ha='left', fontsize=9, fontweight='bold')
                    
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "magic_numbers_chart_all4.pdf"))
    fig.savefig(os.path.join(OUTPUT_DIR, "magic_numbers_chart_all4.png"), dpi=300)
    plt.close(fig)

    # 2. Standalone Charts for Gemini, Grok, Legacy
    individual_maps = [
        ("magic_numbers_chart_gemini", "Gemini Unified Injected Thresholds", gemini_raw, "#2171b5"),
        ("magic_numbers_chart_grok", "Grok Unified Injected Thresholds", grok_raw, "#1a1a1a"),
        ("magic_numbers_chart_legacy", "Gemini Legacy Injected Thresholds", legacy_raw, "#bdd7e7")
    ]
    for filename, title, raw_data, color in individual_maps:
        top_items = extract_top(raw_data, top_k=10)
        if not top_items: continue
        labels = [str(item[0])[:25] for item in top_items][::-1]
        counts = [item[1] if isinstance(item[1], int) else len(item[1]) if isinstance(item[1], list) else 1 for item in top_items][::-1]
        
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

    fig, axes = plt.subplots(2, 2, figsize=(13, 10), dpi=300)
    conditions = [
        ("Gemini Legacy (Condition 1)", legacy, "#bdd7e7", axes[0, 0]),
        ("Gemini Expanded (Condition 2)", expanded, "#6baed6", axes[0, 1]),
        ("Gemini Unified (Condition 3)", gemini, "#2171b5", axes[1, 0]),
        ("Grok Unified (Condition 4)", grok, "#1a1a1a", axes[1, 1])
    ]
    
    for title, data, color, ax in conditions:
        items = list(data.items())[:8][::-1]
        labels = [item[0].replace('_', ' ').title() for item in items]
        values = [item[1] for item in items]
        
        bars = ax.barh(labels, values, color=color, alpha=0.9, edgecolor='black', linewidth=0.5, height=0.65)
        ax.set_title(title, fontweight='bold', fontsize=11, pad=8)
        ax.set_xlim(0, max(values) * 1.2 if values else 10)
        ax.grid(True, linestyle=':', alpha=0.45, axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, val in zip(bars, values):
            ax.text(val + max(values)*0.015, bar.get_y() + bar.get_height()/2.0, str(val),
                    va='center', ha='left', fontsize=9, fontweight='bold')
                    
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "protected_bias_chart_all4.pdf"))
    fig.savefig(os.path.join(OUTPUT_DIR, "protected_bias_chart_all4.png"), dpi=300)
    plt.close(fig)
    print("Generated protected demographic bias distribution figures.")

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

def main():
    generate_magic_numbers_charts()
    generate_protected_bias_chart_all4()
    generate_inconsistency_chart_combined()

if __name__ == "__main__":
    main()
