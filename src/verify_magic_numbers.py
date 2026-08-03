import json
import os
import re
from collections import defaultdict

GENERATED_FUNCTIONS_DIR = os.path.join("data", "generated_functions_unified")
PROMPTS_FILE = os.path.join("data", "dataset", "prompts_unified.jsonl")

# 1. Attributes to specificly verify
TARGET_ATTRS = ['hemoglobin_a1c_level', 'cholesterol_level', 'flight_hours_completed']

# 2. Build Master Map for TARGET attributes only
master_map = defaultdict(set)
list_pattern = re.compile(r"#\s*([\w_]+)\s*\[(.*?)\]")

print(f"Loading '{PROMPTS_FILE}'...")
with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        prompt = data.get("prompt", "")
        
        for p_line in prompt.split('\n'):
            list_match = list_pattern.search(p_line)
            if list_match:
                key = list_match.group(1).strip()
                if key in TARGET_ATTRS:
                    # Parse values
                    raw_vals = list_match.group(2).split(',')
                    vals = [v.strip().strip("'\"") for v in raw_vals]
                    master_map[key].update(vals)

print(f"\n--- Allowed Values ---")
for key, vals in master_map.items():
    # Only show first 10 for brevity if too many
    sorted_vals = sorted(list(vals))
    display_vals = sorted_vals[:10]
    display_vals_str = ", ".join(display_vals)
    if len(vals) > 10:
        display_vals_str += f" ... (+{len(vals)-10} more)"
    print(f"{key}: [{display_vals_str}]")


# 3. Check Magic Values in Generated Code
print(f"\n--- Checking Generated Code for TARGET attributes ---")
comparison_pattern = re.compile(r"self\.([\w_]+)\s*(?:>=|<=|>|<|==|!=)\s*([\"']?[\w\.]+[\"']?)")

flagged_instances = defaultdict(list)

if os.path.exists(GENERATED_FUNCTIONS_DIR):
    for file_name in os.listdir(GENERATED_FUNCTIONS_DIR):
        if file_name.endswith('.json'):
            with open(os.path.join(GENERATED_FUNCTIONS_DIR, file_name), 'r') as f:
                data = json.load(f)
                functions = data.get('generated_functions', [])
                for code in functions:
                    lines = code.split('\n')
                    for line in lines:
                        if line.strip().startswith('#'): continue
                        matches = comparison_pattern.findall(line)
                        for attr, value in matches:
                            if attr not in TARGET_ATTRS: continue
                            
                            val_clean = value.strip().strip('"\'')
                            
                            # Same filter logic as generation script
                            if not val_clean: continue
                            if val_clean.lower() in ['yes', 'no', 'true', 'false', 'none']: continue
                            try:
                                if float(val_clean) == 0.0: continue
                            except: pass
                            
                            # Ignore variables
                            if not (value.strip().startswith('"') or value.strip().startswith("'")) and re.search(r'[a-zA-Z]', val_clean):
                                continue

                            # Check validity
                            allowed_values = master_map[attr]
                            is_allowed = False
                            if val_clean in allowed_values:
                                is_allowed = True
                            else:
                                try:
                                    val_float = float(val_clean)
                                    for allowed in allowed_values:
                                        try:
                                            if float(allowed) == val_float:
                                                is_allowed = True
                                                break
                                        except: pass
                                except: pass
                            
                            if not is_allowed:
                                flagged_instances[attr].append(f"Value: {val_clean} | Line: {line.strip()}")

print("\n--- Results ---")
for attr in TARGET_ATTRS:
    instances = flagged_instances[attr]
    print(f"\nAttribute: {attr} | Flagged Count: {len(instances)}")
    # Print unique values flagged
    unique_vals = set()
    for inst in instances:
        val = inst.split('|')[0].replace("Value: ", "").strip()
        unique_vals.add(val)
    print(f"Unique Hallucinated Values: {sorted(list(unique_vals))}")
    print("Examples:")
    for ex in instances[:5]:
        print(f"  {ex}")
