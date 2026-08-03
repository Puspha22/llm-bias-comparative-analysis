import json
from collections import defaultdict

PROTECTED = {
    'race', 'religion', 'gender', 'pregnancy_status', 'age',
    'disability_percentage', 'disability_rating', 'service_disability_rating',
    'genetic_disorder_risk', 'marital_status', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
}

data = json.load(open('reports/audit_report_legacy.json', 'r'))
tasks = defaultdict(list)
protected_count = 0

for entry in data:
    attrs = entry.get('attributes_tested', [])
    attr_names = [a.get('name', '') for a in attrs]
    tasks[entry['task_id']].append(tuple(sorted(attr_names)))
    
    details = entry.get('discriminatory_details', {})
    if details:
        attrs_tested = details.get('attributes_tested_in_combination', [])
        if any(a in PROTECTED for a in attrs_tested):
            protected_count += 1

inconsistency = sum(1 for s in tasks.values() if len(set(s)) > 1) / len(tasks) * 100

print(f'Legacy Highly Inconsistent Tasks: {inconsistency:.1f}%')
print(f'Legacy Functions with Protected Bias: {protected_count} ({protected_count/1715*100:.1f}%)')
