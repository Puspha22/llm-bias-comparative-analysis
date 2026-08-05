import json
import ijson
import os
from collections import Counter

def process_file(filepath, out_comp, out_freq):
    print(f"Processing {filepath}...")
    complexity = []
    frequency = Counter()
    
    with open(filepath, 'rb') as f:
        for entry in ijson.items(f, 'item'):
            if entry.get('task_id') is not None:
                attrs = entry.get('attributes_tested', [])
                # Handle old vs new format
                if attrs and isinstance(attrs[0], dict):
                    attr_names = [a.get('name', '') for a in attrs]
                else:
                    attr_names = attrs
                
                complexity.append(len(attr_names))
                for a in attr_names:
                    frequency[a] += 1
                    
    # Only keep top 10 frequencies
    top_freq = dict(frequency.most_common(10))
    
    with open(out_comp, 'w') as f:
        json.dump(complexity, f)
        
    with open(out_freq, 'w') as f:
        json.dump(top_freq, f)

process_file('reports/audit_report_legacy.json', "reports/feature_metrics/complexity_legacy.json", "reports/feature_metrics/frequency_legacy.json")
process_file('reports/audit_report_unified_new.json', "reports/feature_metrics/complexity_gemini.json", "reports/feature_metrics/frequency_gemini.json")
process_file('reports/audit_report_grok.json', "reports/feature_metrics/complexity_grok.json", "reports/feature_metrics/frequency_grok.json")
print("Done!")
