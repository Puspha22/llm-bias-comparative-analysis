import os
import json
import time

PROTECTED_ATTRIBUTES = [
    'age', 'gender', 'race', 'religion', 'disability_rating', 
    'pregnancy_status', 'marital_status', 'mental_health_history',
    'service_disability_rating', 'genetic_disorder_risk', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
]

def stream_direct_from_master(json_path):
    counts = {attr: 0 for attr in PROTECTED_ATTRIBUTES}
    total_biased = 0
    if not os.path.exists(json_path):
        return counts, total_biased

    t0 = time.time()
    
    # Fast line-buffer streaming directly over the master file
    current_entry_used_protected = set()
    is_biased = False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '"status": "biased"' in line:
                is_biased = True
            
            if '"attributes_tested_in_combination":' in line or '"attributes_tested":' in line:
                pass
                
            if '"name":' in line or '"attributes_tested_in_combination":' in line or 'self.' in line:
                for attr in PROTECTED_ATTRIBUTES:
                    if f'"{attr}"' in line:
                        current_entry_used_protected.add(attr)

            if '"uniform_result":' in line or '"discriminatory_details":' in line or '},"task_id":' in line or line.strip() == '},' or line.strip() == '}':
                if is_biased and current_entry_used_protected:
                    total_biased += 1
                    for a in current_entry_used_protected:
                        counts[a] += 1
                is_biased = False
                current_entry_used_protected = set()

    t1 = time.time()
    print(f"Streamed {os.path.basename(json_path)} ({os.path.getsize(json_path)/1e9:.2f} GB) in {t1 - t0:.2f} seconds.")
    return counts, total_biased

gemini_path = os.path.join("reports", "audit_report_unified_new.json")
grok_path = os.path.join("reports", "audit_report_grok.json")

gemini_counts, gemini_total = stream_direct_from_master(gemini_path)
grok_counts, grok_total = stream_direct_from_master(grok_path)

summary = {}
for attr in sorted(PROTECTED_ATTRIBUTES):
    summary[attr] = {
        "Gemini_2.5_Flash": gemini_counts[attr],
        "Grok_Code_Fast": grok_counts[attr]
    }

out_file = os.path.join("reports", "summary", "all_protected_attribute_counts.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\n================ MASTER AUDIT STREAMING RESULTS ================\n")
print(f"Gemini Biased Functions: {gemini_total} / 1715 | Grok Biased Functions: {grok_total} / 1715\n")
print(f"{'Protected Attribute':<30} | {'Gemini 2.5 Flash':<18} | {'Grok Code Fast':<18}")
print("-" * 75)

for attr, val in summary.items():
    print(f"{attr:<30} | {val['Gemini_2.5_Flash']:<18} | {val['Grok_Code_Fast']:<18}")

print(f"\nSaved master streaming summary to {out_file}")
