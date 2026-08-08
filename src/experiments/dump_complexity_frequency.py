import json
import os
from collections import Counter

def process_location(path, out_comp, out_freq):
    print(f"Processing {path}...")
    complexity = []
    frequency = Counter()
    
    files_to_process = []
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.json'):
                    files_to_process.append(os.path.join(root, file))
    else:
        files_to_process.append(path)
        
    for filepath in files_to_process:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                entries = data if isinstance(data, list) else [data]
                for entry in entries:
                    if isinstance(entry, dict) and entry.get('task_id') is not None:
                        attrs = entry.get('attributes_tested', [])
                        if attrs and isinstance(attrs[0], dict):
                            attr_names = [a.get('name', '') for a in attrs]
                        else:
                            attr_names = attrs
                        
                        complexity.append(len(attr_names))
                        for a in attr_names:
                            frequency[a] += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                    
    top_freq = dict(frequency.most_common(10))
    
    os.makedirs(os.path.dirname(out_comp), exist_ok=True)
    with open(out_comp, 'w', encoding='utf-8') as f:
        json.dump(complexity, f)
        
    with open(out_freq, 'w', encoding='utf-8') as f:
        json.dump(top_freq, f)

process_location('reports/audit_report_legacy.json', "reports/feature_metrics/complexity_legacy.json", "reports/feature_metrics/frequency_legacy.json")
process_location('reports/partial_audit_results_expanded/success', "reports/feature_metrics/complexity_expanded.json", "reports/feature_metrics/frequency_expanded.json")
process_location('reports/audit_report_unified_new.json', "reports/feature_metrics/complexity_gemini.json", "reports/feature_metrics/frequency_gemini.json")
process_location('reports/audit_report_grok.json', "reports/feature_metrics/complexity_grok.json", "reports/feature_metrics/frequency_grok.json")
print("Done!")


