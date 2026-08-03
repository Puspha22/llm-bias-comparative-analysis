import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
import itertools
import os

# Create figures directory if it doesn't exist
os.makedirs('reports/figures', exist_ok=True)

print("Loading audit report...")
try:
    with open('reports/audit_report_unified_new.json', 'r') as f:
        audit_data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    audit_data = []

# Extract utilized variables
all_utilized_vars = []
var_counts_per_func = []

for entry in audit_data:
    vars_list = entry.get('utilized_variables', [])
    if isinstance(vars_list, list):
        all_utilized_vars.extend(vars_list)
        var_counts_per_func.append(len(vars_list))

# 1. Input Complexity Histogram
print("Generating Complexity Histogram...")
plt.figure(figsize=(10, 6))
sns.histplot(var_counts_per_func, bins=range(0, 20), color='#1A73E8', kde=True)
plt.title('Distribution of Input Variables Utilized per Function', fontsize=14, fontweight='bold')
plt.xlabel('Number of Variables Evaluated', fontsize=12)
plt.ylabel('Frequency (Number of Functions)', fontsize=12)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('reports/figures/complexity_histogram.png', dpi=300)
plt.close()

# 2. Attribute Frequency (Top 20)
print("Generating Attribute Frequency Chart...")
var_counter = Counter(all_utilized_vars)
top_vars = var_counter.most_common(20)

if top_vars:
    labels = [x[0].replace('_', ' ').title() for x in top_vars]
    values = [x[1] for x in top_vars]

    plt.figure(figsize=(12, 8))
    sns.barplot(x=values, y=labels, palette='viridis')
    plt.title('Top 20 Most Utilized Attributes by LLMs', fontsize=14, fontweight='bold')
    plt.xlabel('Frequency across all generated functions', fontsize=12)
    plt.tight_layout()
    plt.savefig('reports/figures/attribute_frequency_chart.png', dpi=300)
    plt.close()

# 3. Attribute Co-Occurrence Heatmap (Top 15)
print("Generating Co-Occurrence Heatmap...")
if len(top_vars) >= 15:
    top_15_names = [x[0] for x in top_vars[:15]]
    
    co_matrix = pd.DataFrame(0, index=top_15_names, columns=top_15_names)
    
    for entry in audit_data:
        vars_list = entry.get('utilized_variables', [])
        if isinstance(vars_list, list):
            # Only consider variables in top 15
            filtered_vars = [v for v in vars_list if v in top_15_names]
            for v1, v2 in itertools.combinations(filtered_vars, 2):
                co_matrix.loc[v1, v2] += 1
                co_matrix.loc[v2, v1] += 1
                
    # Format labels
    formatted_labels = [name.replace('_', ' ').title() for name in top_15_names]
    co_matrix.index = formatted_labels
    co_matrix.columns = formatted_labels

    plt.figure(figsize=(10, 8))
    sns.heatmap(co_matrix, cmap='YlGnBu', annot=False, linewidths=.5)
    plt.title('Attribute Co-Occurrence Heatmap (Top 15)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('reports/figures/attribute_pairs_heatmap.png', dpi=300)
    plt.close()

# 4. Combinatorial Growth Chart (Mathematical)
print("Generating Combinatorial Growth Chart...")
variables = np.arange(1, 13)
# Assuming an average of 5 possible values per variable
combinations = 5 ** variables

plt.figure(figsize=(10, 6))
plt.plot(variables, combinations, marker='o', color='#D93025', linewidth=2, markersize=8)
plt.yscale('log')
plt.axhline(y=100000, color='black', linestyle='--', label='100k Monte Carlo Cutoff')
plt.title('Exponential Growth of Search Space ($5^n$)', fontsize=14, fontweight='bold')
plt.xlabel('Number of Input Variables (n)', fontsize=12)
plt.ylabel('Total Permutations (Log Scale)', fontsize=12)
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.tight_layout()
plt.savefig('reports/figures/combinatorial_growth.png', dpi=300)
plt.close()

print("All EDA charts generated successfully!")
