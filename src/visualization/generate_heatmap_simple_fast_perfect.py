import os
import json
import itertools
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join("reports", "figures")
ASSETS_DIR = os.path.join("MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models", "Assets")

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Palatino', 'Times New Roman', 'DejaVu Serif']

def extract_attributes_fast(file_path):
    sample_attributes = []
    current_attrs = []
    in_attrs = False
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '"attributes_tested"' in line:
                in_attrs = True
                current_attrs = []
                continue
            if in_attrs:
                if '"name"' in line:
                    match = re.search(r'"name":\s*"([^"]+)"', line)
                    if match:
                        current_attrs.append(match.group(1).strip())
                elif ']' in line and in_attrs:
                    in_attrs = False
                    if current_attrs:
                        sample_attributes.append(current_attrs)
                        current_attrs = []
    return sample_attributes

def calculate_cooccurrence_fast(folder_path):
    pair_counts = Counter()
    attribute_counts = Counter()
    
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.name.endswith('.json'):
                samples = extract_attributes_fast(entry.path)
                for attrs in samples:
                    unique_attrs = sorted(set(attrs))
                    for attr in unique_attrs:
                        attribute_counts[attr] += 1
                    for pair in itertools.combinations(unique_attrs, 2):
                        pair_counts[pair] += 1
    return pair_counts, attribute_counts

def match_count(counts, target_name):
    t = target_name.lower().replace(' ', '_')
    for k, v in counts.items():
        if k.lower().replace(' ', '_') == t:
            return v
    return 0

def match_pair_count(pair_counts, target_a, target_b):
    ta = target_a.lower().replace(' ', '_')
    tb = target_b.lower().replace(' ', '_')
    for (ka, kb), v in pair_counts.items():
        ka_clean = ka.lower().replace(' ', '_')
        kb_clean = kb.lower().replace(' ', '_')
        if (ka_clean == ta and kb_clean == tb) or (ka_clean == tb and kb_clean == ta):
            return v
    return 0

def main():
    legacy_dir = "reports/partial_audit_results_legacy/success"
    expanded_dir = "reports/partial_audit_results_expanded/success"
    gemini_dir = "reports/partial_audit_results_new/success"
    grok_dir = "reports/partial_audit_results_grok/success"

    print("Computing simple top 8 heatmap co-occurrences instantly...")
    l_pairs, l_attrs = calculate_cooccurrence_fast(legacy_dir)
    e_pairs, e_attrs = calculate_cooccurrence_fast(expanded_dir)
    g_pairs, g_attrs = calculate_cooccurrence_fast(gemini_dir)
    gr_pairs, gr_attrs = calculate_cooccurrence_fast(grok_dir)

    with open("reports/feature_metrics/frequency_legacy.json") as f:
        l_top8 = list(json.load(f).keys())[:8]
    with open("reports/feature_metrics/frequency_expanded.json") as f:
        e_top8 = list(json.load(f).keys())[:8]
    with open("reports/feature_metrics/frequency_gemini.json") as f:
        g_top8 = list(json.load(f).keys())[:8]
    with open("reports/feature_metrics/frequency_grok.json") as f:
        gr_top8 = list(json.load(f).keys())[:8]

    fig, axes = plt.subplots(2, 2, figsize=(13, 11), dpi=300)

    datasets = [
        ("Gemini Legacy (Condition 1)", l_top8, l_pairs, l_attrs, axes[0, 0]),
        ("Gemini Expanded (Condition 2)", e_top8, e_pairs, e_attrs, axes[0, 1]),
        ("Gemini Unified (Condition 3)", g_top8, g_pairs, g_attrs, axes[1, 0]),
        ("Grok Unified (Condition 4)", gr_top8, gr_pairs, gr_attrs, axes[1, 1])
    ]

    top_n = 8

    for title, top_attrs, pair_counts, attribute_counts, ax in datasets:
        matrix = np.zeros((top_n, top_n))

        for i, attr1 in enumerate(top_attrs):
            for j, attr2 in enumerate(top_attrs):
                if i == j:
                    matrix[i, j] = match_count(attribute_counts, attr1)
                else:
                    matrix[i, j] = match_pair_count(pair_counts, attr1, attr2)

        np.fill_diagonal(matrix, 0)
        clean_labels = [a.replace('_', ' ').title() for a in top_attrs]

        im = ax.imshow(matrix, cmap='Blues', aspect='auto')
        ax.set_xticks(np.arange(top_n))
        ax.set_yticks(np.arange(top_n))
        ax.set_xticklabels(clean_labels, rotation=35, ha='right', fontsize=9.5)
        ax.set_yticklabels(clean_labels, fontsize=9.5)
        ax.set_title(title, fontweight='bold', fontsize=12, pad=10)
        fig.colorbar(im, ax=ax, shrink=0.8)

    plt.tight_layout()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_pairs_heatmap_combined_simple.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_pairs_heatmap_combined_simple.pdf"))
    fig.savefig(os.path.join(ASSETS_DIR, "attribute_pairs_heatmap_combined_simple.png"), dpi=300)
    fig.savefig(os.path.join(ASSETS_DIR, "attribute_pairs_heatmap_combined_simple.pdf"))

    fig.savefig(os.path.join(ASSETS_DIR, "attribute_pairs_heatmap_combined.png"), dpi=300)
    fig.savefig(os.path.join(ASSETS_DIR, "attribute_pairs_heatmap_combined.pdf"))

    plt.close()
    print("INSTANTLY generated simple frequency-based 4-condition attribute_pairs_heatmap_combined grid!")

if __name__ == "__main__":
    main()
