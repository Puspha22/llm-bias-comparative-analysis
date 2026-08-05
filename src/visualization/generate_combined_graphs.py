import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"]
})

def create_grouped_bar_chart(gemini_json, grok_json, title, ylabel, output_path):
    with open(gemini_json, 'r') as f:
        gemini_data_raw = json.load(f)
    with open(grok_json, 'r') as f:
        grok_data_raw = json.load(f)
        
    def to_counts(data):
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            counts = {}
            for item in data:
                attr = item.get('attribute')
                if attr:
                    counts[attr] = counts.get(attr, 0) + 1
            return counts
        return {}
        
    gemini_data = to_counts(gemini_data_raw)
    grok_data = to_counts(grok_data_raw)
        
    all_keys = set(gemini_data.keys()).union(set(grok_data.keys()))
    
    # Sort keys by highest combined value
    combined_counts = {k: gemini_data.get(k, 0) + grok_data.get(k, 0) for k in all_keys}
    sorted_keys = sorted(all_keys, key=lambda k: combined_counts[k], reverse=True)
    
    # Limit to top 15 for readability
    sorted_keys = sorted_keys[:15]
    
    gemini_vals = [gemini_data.get(k, 0) for k in sorted_keys]
    grok_vals = [grok_data.get(k, 0) for k in sorted_keys]
    
    x = np.arange(len(sorted_keys))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, gemini_vals, width, label='Gemini 2.5 Flash', color='#1A73E8')
    rects2 = ax.bar(x + width/2, grok_vals, width, label='Grok-Code-Fast-1', color='#F9AB00')
    
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    
    # Clean up labels (replace underscores)
    clean_labels = [k.replace('_', ' ').title() for k in sorted_keys]
    ax.set_xticklabels(clean_labels, rotation=45, ha='right')
    ax.legend()
    
    fig.tight_layout()
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    # Also save as png for easy preview
    plt.savefig(output_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
    print(f"Saved {output_path}")

# Protected Bias
create_grouped_bar_chart(
    "reports/feature_metrics/exp_protected_bias_results_new.json",
    "reports/feature_metrics/exp_protected_bias_results_grok.json",
    'Bias Frequency on Protected Attributes (Gemini vs Grok)',
    'Number of Biased Functions',
    'siuethesis/Assets/protected_bias_chart_combined.pdf'
)

# Magic Numbers
create_grouped_bar_chart(
    "reports/feature_metrics/exp_magic_numbers_results_new.json",
    "reports/feature_metrics/exp_magic_numbers_results_grok.json",
    'Arbitrary Numeric Threshold Hallucinations (Gemini vs Grok)',
    'Number of Hallucinated Thresholds',
    'siuethesis/Assets/magic_numbers_chart_combined.pdf'
)
