import json
import matplotlib.pyplot as plt
import os
from collections import defaultdict
import matplotlib

# Use LaTeX for text rendering
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"]
})

import ijson

def calculate_consistency(report_path):
    # Group by task_id
    tasks = defaultdict(list)
    print(f"Parsing {report_path} streamingly...")
    with open(report_path, 'rb') as f:
        try:
            for entry in ijson.items(f, 'item'):
                task_id = entry.get('task_id')
                if task_id is None:
                    continue
                attrs = tuple(sorted(entry.get('attributes_tested', [])))
                tasks[task_id].append(attrs)
        except Exception as e:
            print(f"Error during parsing {report_path}: {e}")
            
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for task_id, samples in tasks.items():
        unique_sets = len(set(samples))
        if unique_sets > 5:
            unique_sets = 5
        counts[unique_sets] += 1
        
    return counts

gemini_file = "reports/audit_report_unified_new.json"
grok_file = "reports/audit_report_grok.json"

if not os.path.exists(gemini_file):
    gemini_file = "reports/audit_report_unified.json"

gemini_counts = calculate_consistency(gemini_file)
grok_counts = calculate_consistency(grok_file)

# Plotting
labels = ['1', '2', '3', '4', '5']
gemini_values = [gemini_counts[i] for i in range(1, 6)]
grok_values = [grok_counts[i] for i in range(1, 6)]

x = range(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
rects1 = ax.bar([p - width/2 for p in x], gemini_values, width, label='Gemini 2.5 Flash', color='#1A73E8')
rects2 = ax.bar([p + width/2 for p in x], grok_values, width, label='Grok-Code-Fast-1', color='#F9AB00')

ax.set_ylabel('Number of Tasks')
ax.set_xlabel('Unique Logical Variations Generated (Out of 5)')
ax.set_title('Internal Consistency: Logical Variance Across Samples')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)

fig.tight_layout()
os.makedirs("reports/figures", exist_ok=True)
plt.savefig('reports/figures/inconsistency_chart.pdf', format='pdf', bbox_inches='tight')
plt.savefig('reports/figures/inconsistency_chart.png', dpi=300, bbox_inches='tight')
print("Consistency chart saved to reports/figures/inconsistency_chart.pdf")

