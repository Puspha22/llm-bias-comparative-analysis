import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import re
import textwrap
import math

# Configuration
AUDIT_REPORT_FILE = os.path.join("reports", "raw_dumps", "audit_report_gemini_unified.json")
GENERATED_FUNCTIONS_DIR = os.path.join("data", "generated_functions_unified")
# PROMPTS_FILE = os.path.join("data", "dataset", "prompts_unified.jsonl") # Original
# The user wants to "parse the prompts" to be 100% sure. 
# We will use the same prompts_unified.jsonl file but with improved parsing logic.
PROMPTS_FILE = os.path.join("data", "dataset", "prompts_unified.jsonl")
OUTPUT_DIR = os.path.join("reports", "figures")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Helper Functions ---
def find_used_attributes(code_string, all_keys):
    """Scans the code and returns a set of attributes it actually uses."""
    used_attributes = set()
    for key in all_keys:
        if f"self.{key}" in code_string:
            used_attributes.add(key)
    return used_attributes

def is_valid_numeric_match(val_clean, allowed_values):
    """
    Checks if val_clean (string) numerically matches any value in allowed_values.
    Example: val_clean="100.0", allowed_values=["100"] -> True
    """
    try:
        val_float = float(val_clean)
        for allowed in allowed_values:
            try:
                if math.isclose(float(allowed), val_float, rel_tol=1e-9):
                    return True
            except:
                pass
    except:
        pass
    return False

def extract_magic_values(code_string, master_map, alias_map):
    """
    Extracts potential 'magic values' from code.
    A value is MAGIC if it is NOT in the master_map's allowed values for that attribute.
    """
    magic_values = []
    
    # Regex to capture: self.attr OP value
    comparison_pattern = re.compile(r"self\.([\w_]+)\s*(?:>=|<=|>|<|==|!=)\s*([\"']?[\w\.]+[\"']?)")
    
    lines = code_string.split('\n')
    for line in lines:
        if line.strip().startswith('#'): continue
        
        matches = comparison_pattern.findall(line)
        for attr, value in matches:
            # Clean value
            val_clean = value.strip().strip('"\'')
            
            # FILTERS -----------------------------------------------------------------
            # 1. Ignore booleans/None/empty
            if not val_clean: continue
            if val_clean.lower() in ['yes', 'no', 'true', 'false', 'none']: continue
            
            # 2. Ignore 0 or 0.0
            try:
                if float(val_clean) == 0.0: continue
            except:
                pass

            # 3. Ignore unquoted variable names (e.g. 'income_limit')
            if not (value.strip().startswith('"') or value.strip().startswith("'")) and re.search(r'[a-zA-Z]', val_clean):
                 continue

            # 4. Resolve Aliases
            check_attr = attr
            if attr in alias_map:
                check_attr = alias_map[attr]

            # 5. Check Against Master Map
            if check_attr in master_map:
                allowed_values = master_map[check_attr]
                is_allowed = False
                
                # Direct string match (handles quoted values)
                if val_clean in allowed_values:
                    is_allowed = True
                # Numeric comparison (Robust)
                elif is_valid_numeric_match(val_clean, allowed_values):
                    is_allowed = True
                
                if is_allowed:
                    continue 

            magic_values.append({
                "attribute": attr,
                "value": val_clean,
                "line": line.strip()
            })
            
    return magic_values

def main():
    print("Starting Comprehensive Analysis (Robust Parsing)...")
    
    # --- 1. Load Data ---
    print(f"Loading '{AUDIT_REPORT_FILE}'...")
    try:
        with open(AUDIT_REPORT_FILE, 'r') as f:
            report_data = json.load(f)
        discriminatory_functions = report_data.get("biased_functions", [])
        if not discriminatory_functions:
             if isinstance(report_data, list):
                 discriminatory_functions = report_data
        print(f" > Found {len(discriminatory_functions)} discriminatory functions.")
    except Exception as e:
        print(f"Error loading report: {e}")
        discriminatory_functions = []

    print(f"Loading generated functions...")
    all_generated_functions = {}
    if os.path.exists(GENERATED_FUNCTIONS_DIR):
        g_files = [f for f in os.listdir(GENERATED_FUNCTIONS_DIR) if f.endswith('.json')]
        for file_name in g_files:
            parts = file_name.split('_')
            if len(parts) >= 2 and parts[0] == 'task':
                 task_id = parts[1]
                 filepath = os.path.join(GENERATED_FUNCTIONS_DIR, file_name)
                 with open(filepath, 'r') as f:
                    all_generated_functions[task_id] = json.load(f)
    print(f" > Loaded function samples for {len(all_generated_functions)} tasks.")

    # --- ROBUST PROMPT PARSING ---
    print(f"Building attribute map from '{PROMPTS_FILE}'...")
    all_attribute_keys = set()
    master_map = defaultdict(set)
    alias_map = {} 
    
    # These regexes need to match the prompts_unified.jsonl structure precisely
    list_pattern = re.compile(r"#\s*([\w_]+)\s*\[(.*?)\]")
    type_pattern = re.compile(r"^\s*([\w_]+)\s*:\s*(\w+)")
    alias_pattern = re.compile(r"self\.([\w_]+)\s*=\s*self\.([\w_]+)") 
    
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                prompt = data.get("prompt", "")
                
                for p_line in prompt.split('\n'):
                    # 1. Attribute Lists
                    list_match = list_pattern.search(p_line)
                    if list_match:
                         key = list_match.group(1).strip()
                         val_str = list_match.group(2)
                         # Handle mixed quoting: 'a', "b", c
                         # Split by comma, strip whitespace and quotes
                         vals = [v.strip().strip("'\"") for v in val_str.split(',')]
                         if vals:
                            master_map[key].update(vals)
                            all_attribute_keys.add(key)
                    
                    # 2. Type Hints
                    type_match = type_pattern.search(p_line)
                    if type_match:
                        all_attribute_keys.add(type_match.group(1).strip())
                    
                    # 3. None Defaults: self.age = None # int
                    alt_match = re.search(r"self\.([\w_]+)\s*=\s*None\s*#\s*(\w+)", p_line)
                    if alt_match:
                         all_attribute_keys.add(alt_match.group(1).strip())

                    # 4. Aliases
                    al_match = alias_pattern.search(p_line)
                    if al_match:
                        alias = al_match.group(1).strip()
                        source = al_match.group(2).strip()
                        if alias != source:
                            alias_map[alias] = source
                            all_attribute_keys.add(alias)

    # Validate Propagations
    for alias, source in alias_map.items():
        if source in master_map:
            master_map[alias].update(master_map[source])
            
    # Also need to make sure 'blood_sugar_level' etc are actually in the map
    # You mentioned blood_sugar_level was missed. Let's verify.
    # The parsing logic relies on # attr [list]. 
    
    print(f" > Found {len(all_attribute_keys)} unique attributes.")
    print(f" > Found value lists for {len(master_map)} attributes.")
    if 'blood_sugar_level' in master_map:
        print(f" > verified: blood_sugar_level has {len(master_map['blood_sugar_level'])} values.")
    else:
        print(" > WARNING: blood_sugar_level NOT found in master_map!")

    # --- Analysis 1: Attribute Consistency ---
    print("\n--- Analysis 1: Attribute Consistency ---")
    inconsistent_tasks = []
    for task_id, task_data in all_generated_functions.items():
        samples = task_data.get('generated_functions', [])
        seen_attr_sets = set()
        for code in samples:
            clean_code = "\n".join([l for l in code.split('\n') if not l.strip().startswith('#')])
            used = find_used_attributes(clean_code, all_attribute_keys)
            seen_attr_sets.add(frozenset(used))
        if len(seen_attr_sets) > 1:
            inconsistent_tasks.append(task_id)

    total_tasks = len(all_generated_functions)
    inc_count = len(inconsistent_tasks)
    con_count = total_tasks - inc_count
    
    plt.figure(figsize=(8, 6))
    plt.pie([con_count, inc_count], labels=['Consistent', 'Inconsistent'], 
            autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'], startangle=90)
    plt.title('Logic Consistency Across Samples')
    plt.savefig(os.path.join(OUTPUT_DIR, 'consistency_chart.png'))
    plt.close()
    print(f"Saved consistency_chart.png. Consistent: {con_count}, Inconsistent: {inc_count}")

    # --- Analysis 2: Magic Numbers (FIXED) ---
    print("\n--- Analysis 2: Magic Numbers ---")
    all_magic = []
    
    for task_id, task_data in all_generated_functions.items():
        samples = task_data.get('generated_functions', [])
        for code in samples:
            clean_code = "\n".join([l for l in code.split('\n') if not l.strip().startswith('#')])
            # PASS MASTER_MAP & ALIAS_MAP HERE
            magics = extract_magic_values(clean_code, master_map, alias_map)
            for m in magics:
                m['task_id'] = task_id
                all_magic.append(m)
                
    magic_df = pd.DataFrame(all_magic)
    if not magic_df.empty:
        top_values = magic_df['value'].value_counts().head(10)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_values.index, y=top_values.values, palette="viridis")
        plt.title('Top 10 "Magic Values" Injected')
        plt.xlabel('Value')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'magic_values_chart.png'))
        plt.close()
        print(f"Saved magic_values_chart.png. Total magic instances: {len(magic_df)}")
        
        top_attrs = magic_df['attribute'].value_counts().head(10)
        print("Top attributes with magic numbers:")
        print(top_attrs)
    else:
        print("No magic values found after filter!")

    # --- Analysis 3: Bias Types ---
    print("\n--- Analysis 3: Bias Types ---")
    biased_attrs_count = Counter()
    for entry in discriminatory_functions:
        if "details" in entry and "attributes" in entry["details"]:
            attrs = entry["details"]["attributes"]
            biased_attrs_count.update(attrs)
            
    if biased_attrs_count:
        SENSITIVE = {'age', 'gender', 'race', 'religion', 'disability', 'sexual_orientation', 'political_orientation', 'marital_status', 'nationality'}
        found_sensitive = {k: v for k, v in biased_attrs_count.items() if k in SENSITIVE}
        print("Sensitive Attributes causing bias:")
        print(found_sensitive)
        
        common_biased = biased_attrs_count.most_common(15)
        lbls, vals = zip(*common_biased)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x=list(vals), y=list(lbls), palette="magma")
        plt.title('Top Attributes Leading to Biased Outcomes')
        plt.xlabel('Frequency in Biased Functions')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'biased_attributes_chart.png'))
        plt.close()
        print("Saved biased_attributes_chart.png")

    print("\nAnalysis Complete.")

if __name__ == "__main__":
    main()
