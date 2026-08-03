import ijson
import sys

def get_tasks(file, max_tasks=2):
    print(f"Parsing {file}...")
    gender, race, age = [], [], []
    try:
        with open(file, 'rb') as f:
            for entry in ijson.items(f, 'item'):
                if entry.get("status") == "biased":
                    details = entry.get("discriminatory_details", {})
                    attrs = details.get("attributes_tested_in_combination", [])
                    tid = entry.get('task_id')
                    
                    if 'gender' in attrs and len(gender) < max_tasks: 
                        gender.append(tid)
                    if 'race' in attrs and len(race) < max_tasks: 
                        race.append(tid)
                    if 'age' in attrs and len(age) < max_tasks: 
                        age.append(tid)
                        
                    if len(gender) == max_tasks and len(race) == max_tasks and len(age) == max_tasks:
                        break
    except Exception as e:
        print(f"Error: {e}")
        
    print(f"Gender: {list(set(gender))}")
    print(f"Race  : {list(set(race))}")
    print(f"Age   : {list(set(age))}")
    return gender, race, age

print("--- GEMINI ---")
get_tasks('reports/audit_report_unified_new.json')
print("\n--- GROK ---")
get_tasks('reports/audit_report_grok.json')
