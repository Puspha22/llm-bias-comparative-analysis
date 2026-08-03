import json
from collections import defaultdict

data = json.load(open('reports/audit_report_legacy.json', 'r'))
tasks = defaultdict(list)

for entry in data:
    attrs = entry.get('attributes_tested', [])
    attr_names = [a.get('name', '') for a in attrs]
    tasks[entry['task_id']].append(tuple(sorted(attr_names)))

print("--- Sample of 5 Tasks from Legacy Prompts ---")
for t in list(tasks.keys())[:5]:
    variations = set(tasks[t])
    print(f"\nTask {t}: {len(variations)} unique logical variations out of 5 samples:")
    for v in variations:
        print(f"  - {list(v)}")
