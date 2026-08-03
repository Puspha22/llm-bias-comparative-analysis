import json
import ijson
import itertools
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.size": 18,
    "axes.titlesize": 24,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18
})

def calculate_cooccurrence(report_path):
    print(f"Reading {report_path} for co-occurrences...")
    pair_counts = Counter()
    attribute_counts = Counter()
    
    with open(report_path, 'rb') as f:
        for entry in ijson.items(f, 'item'):
            if entry.get('task_id') is not None:
                attrs = entry.get('attributes_tested', [])
                if attrs and isinstance(attrs[0], dict):
                    attr_names = [a.get('name', '') for a in attrs]
                else:
                    attr_names = attrs
                
                for attr in attr_names:
                    attribute_counts[attr] += 1
                
                attr_names = sorted(attr_names)
                for pair in itertools.combinations(attr_names, 2):
                    pair_counts[pair] += 1
            
    return pair_counts, attribute_counts

def plot_heatmap(pair_counts, attribute_counts, title, output_path, top_n=8):
    # Collect top attributes by analyzing the most common pairs
    top_attrs_set = set()
    for pair, count in pair_counts.most_common():
        for attr in pair:
            if attr not in top_attrs_set and len(top_attrs_set) < top_n:
                top_attrs_set.add(attr)
        if len(top_attrs_set) >= top_n:
            break
            
    # If we somehow didn't get enough attributes from pairs, fill with individual top attributes
    if len(top_attrs_set) < top_n:
        for attr, _ in attribute_counts.most_common():
            if attr not in top_attrs_set:
                top_attrs_set.add(attr)
            if len(top_attrs_set) >= top_n:
                break
                
    # Sort them by their individual frequency to keep the heatmap layout logical
    top_attrs = sorted(list(top_attrs_set), key=lambda x: attribute_counts[x], reverse=True)
    
    # Initialize matrix
    matrix = np.zeros((top_n, top_n))
    
    # Fill matrix
    for i, attr1 in enumerate(top_attrs):
        for j, attr2 in enumerate(top_attrs):
            if i == j:
                matrix[i, j] = attribute_counts[attr1]
            else:
                pair1 = tuple(sorted([attr1, attr2]))
                matrix[i, j] = pair_counts.get(pair1, 0)
                
    # Normalize by the individual frequencies or just show raw counts
    # The heatmap usually looks best if we clear the diagonal or make it max
    np.fill_diagonal(matrix, 0)
    
    # Clean labels
    clean_labels = [a.replace('_', ' ').title() for a in top_attrs]
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(matrix, xticklabels=clean_labels, yticklabels=clean_labels, 
                cmap='Blues', annot=False, fmt='g', cbar_kws={"shrink": .8})
    plt.title(title, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved {output_path}")

legacy_file = "reports/audit_report_legacy.json"
gemini_file = "reports/audit_report_unified_new.json"
grok_file = "reports/audit_report_grok.json"

l_pairs, l_attrs = calculate_cooccurrence(legacy_file)
plot_heatmap(l_pairs, l_attrs, "Legacy Prompts", "siuethesis/Assets/attribute_pairs_heatmap_legacy.png")

g_pairs, g_attrs = calculate_cooccurrence(gemini_file)
plot_heatmap(g_pairs, g_attrs, "Gemini 2.5 Flash", "siuethesis/Assets/attribute_pairs_heatmap.png")

gr_pairs, gr_attrs = calculate_cooccurrence(grok_file)
plot_heatmap(gr_pairs, gr_attrs, "Grok-Code-Fast-1", "siuethesis/Assets/attribute_pairs_heatmap_grok.png")
