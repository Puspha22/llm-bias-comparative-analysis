import json
import ijson
from collections import defaultdict

def calc(p):
    tasks = defaultdict(list)
    with open(p, 'rb') as f:
        for entry in ijson.items(f, 'item'):
            if entry.get('task_id') is not None:
                attrs = entry.get('attributes_tested', [])
                if attrs and isinstance(attrs[0], dict):
                    attr_names = [a.get('name', '') for a in attrs]
                else:
                    attr_names = attrs
                tasks[entry['task_id']].append(tuple(sorted(attr_names)))
    counts = {1:0, 2:0, 3:0, 4:0, 5:0}
    for s in tasks.values():
        val = min(5, len(set(s)))
        counts[val] += 1
    return counts

json.dump(calc('reports/audit_report_unified_new.json'), open('reports/consistency_gemini.json', 'w'))
json.dump(calc('reports/audit_report_grok.json'), open('reports/consistency_grok.json', 'w'))
