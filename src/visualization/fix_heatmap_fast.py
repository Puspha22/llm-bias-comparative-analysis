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
    # Reads only attributes_tested section from json file, ignoring huge detailed_results
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
                        current_attrs.append(match.group(1))
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

def main():
    legacy_dir = "reports/partial_audit_results_legacy/success"
    expanded_dir = "reports/partial_audit_results_expanded/success"
    gemini_dir = "reports/partial_audit_results_new/success"
    grok_dir = "reports/partial_audit_results_grok/success"

    print("Computing 100% full dataset co-occurrences fast...")
    l_pairs, l_attrs = calculate_cooccurrence_fast(legacy_dir)
    e_pairs, e_attrs = calculate_cooccurrence_fast(expanded_dir)
    g_pairs, g_attrs = calculate_cooccurrence_fast(gemini_dir)
    gr_pairs, gr_attrs = calculate_cooccurrence_fast(grok_dir)

    fig, axes = plt.subplots(2, 2, figsize=(13, 11), dpi=300)

    datasets = [
        ("Gemini Legacy (Condition 1)", l_pairs, l_attrs, axes[0, 0]),
        ("Gemini Expanded (Condition 2)", e_pairs, e_attrs, axes[0, 1]),
        ("Gemini Unified (Condition 3)", g_pairs, g_attrs, axes[1, 0]),
        ("Grok Unified (Condition 4)", gr_pairs, gr_attrs, axes[1, 1])
    ]

    top_n = 8

    for title, pair_counts, attribute_counts, ax in datasets:
        top_attrs_set = set()
        for pair, _ in pair_counts.most_common():
            for attr in pair:
                if attr not in top_attrs_set and len(top_attrs_set) < top_n:
                    top_attrs_set.add(attr)
            if len(top_attrs_set) >= top_n:
                break
                
        if len(top_attrs_set) < top_n:
            for attr, _ in attribute_counts.most_common():
                if attr not in top_attrs_set:
                    top_attrs_set.add(attr)
                if len(top_attrs_set) >= top_n:
                    break

        top_attrs = sorted(list(top_attrs_set), key=lambda x: attribute_counts[x], reverse=True)
        matrix = np.zeros((top_n, top_n))

        for i, attr1 in enumerate(top_attrs):
            for j, attr2 in enumerate(top_attrs):
                if i == j:
                    matrix[i, j] = attribute_counts[attr1]
                else:
                    pair1 = tuple(sorted([attr1, attr2]))
                    matrix[i, j] = pair_counts.get(pair1, 0)

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

    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_pairs_heatmap_combined.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_pairs_heatmap_combined.pdf"))
    fig.savefig(os.path.join(ASSETS_DIR, "attribute_pairs_heatmap_combined.png"), dpi=300)
    fig.savefig(os.path.join(ASSETS_DIR, "attribute_pairs_heatmap_combined.pdf"))

    plt.close()
    print("Successfully generated true 100% dataset heatmap combined grid in ASSETS_DIR.")

if __name__ == "__main__":
    main()
