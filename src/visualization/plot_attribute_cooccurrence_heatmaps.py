import os
import json
import itertools
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join("reports", "figures")

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Palatino', 'Times New Roman', 'DejaVu Serif']

def load_pairs_data(model_name):
    pairs_file = os.path.join("reports", "feature_metrics", f"attribute_pairs_{model_name}.json")
    freq_file = os.path.join("reports", "feature_metrics", f"attribute_frequency_{model_name}.json")
    
    with open(freq_file, 'r', encoding='utf-8') as f:
        top_attrs = list(json.load(f).keys())[:8]
        
    with open(pairs_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    attr_counts = data.get("attribute_counts", {})
    pair_counts_raw = data.get("pair_counts", {})
    
    pair_counts = {}
    for k, v in pair_counts_raw.items():
        parts = k.split("||")
        if len(parts) == 2:
            pair_counts[(parts[0], parts[1])] = v
            
    return top_attrs, pair_counts, attr_counts

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
    print("Loading precomputed attribute co-occurrence matrices...")
    l_top8, l_pairs, l_attrs = load_pairs_data("gemini_legacy")
    e_top8, e_pairs, e_attrs = load_pairs_data("gemini_expanded")
    g_top8, g_pairs, g_attrs = load_pairs_data("gemini_unified")
    gr_top8, gr_pairs, gr_attrs = load_pairs_data("grok_unified")

    fig, axes = plt.subplots(2, 2, figsize=(13, 11), dpi=300)

    datasets = [
        ("Gemini Legacy (Condition 1)", l_top8, l_pairs, l_attrs, axes[0, 0]),
        ("Gemini Expanded (Condition 2)", e_top8, e_pairs, e_attrs, axes[0, 1]),
        ("Gemini Unified (Condition 3)", g_top8, g_pairs, g_attrs, axes[1, 0]),
        ("Grok Unified (Condition 4)", gr_top8, gr_pairs, gr_attrs, axes[1, 1])
    ]

    top_n = 8

    filenames_map = {
        "Gemini Legacy (Condition 1)": "attribute_pairs_heatmap_legacy",
        "Gemini Expanded (Condition 2)": "attribute_pairs_heatmap_expanded",
        "Gemini Unified (Condition 3)": "attribute_pairs_heatmap",
        "Grok Unified (Condition 4)": "attribute_pairs_heatmap_grok"
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)

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

        # Generate individual standalone heatmap
        single_name = filenames_map.get(title)
        if single_name:
            single_fig, single_ax = plt.subplots(figsize=(7, 6), dpi=300)
            single_im = single_ax.imshow(matrix, cmap='Blues', aspect='auto')
            single_ax.set_xticks(np.arange(top_n))
            single_ax.set_yticks(np.arange(top_n))
            single_ax.set_xticklabels(clean_labels, rotation=35, ha='right', fontsize=10)
            single_ax.set_yticklabels(clean_labels, fontsize=10)
            single_ax.set_title(title, fontweight='bold', fontsize=13, pad=12)
            single_fig.colorbar(single_im, ax=single_ax, shrink=0.8)
            single_fig.tight_layout()
            single_fig.savefig(os.path.join(OUTPUT_DIR, f"{single_name}.png"), dpi=300)
            single_fig.savefig(os.path.join(OUTPUT_DIR, f"{single_name}.pdf"))
            plt.close(single_fig)

    fig.tight_layout()

    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_pairs_heatmap_combined.png"), dpi=300)
    fig.savefig(os.path.join(OUTPUT_DIR, "attribute_pairs_heatmap_combined.pdf"))

    plt.close(fig)
    print("Generated all individual heatmaps and 4-condition combined heatmap grid!")

if __name__ == "__main__":
    main()
