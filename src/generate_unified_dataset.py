import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "reports" / "unified_attributes.csv"
INPUT_JSONL = BASE_DIR / "data" / "dataset" / "prompts_old.jsonl"
OUTPUT_JSONL = BASE_DIR / "data" / "dataset" / "prompts_unified_new.jsonl"

def parse_vals(val_str):
    return [v.strip().strip("'\"") for v in val_str.split(',') if v.strip()]

def get_type_hint(vals):
    if not vals: return 'str'
    try:
        if all(v.replace('.', '', 1).isdigit() for v in vals):
            return 'int' # simplification, could be float
    except: pass
    return 'str'

def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        sys.exit(1)

    print("Building index...")
    master = defaultdict(lambda: {'vals': set()})
    aliases = {}

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            old = row['Old_Attribute'].strip()
            new_ = row['Modified_Attribute'].strip()
            vals = parse_vals(row['Modified_Values'])
            
            if old: aliases[old] = new_
            master[new_]['vals'].update(vals)

    # Fields Construction
    attr_lines = []
    
    sorted_keys = sorted(master.keys())
    for k in sorted_keys:
        vals = sorted(list(master[k]['vals']))
        t = get_type_hint(vals)
        
        # Format string
        val_str = ", ".join(vals) if t != 'str' else ", ".join([f"'{v}'" for v in vals])
        attr_lines.append(f"    # {k} [{val_str}]")
        attr_lines.append(f"    {k}: {t}")
            
    fields_block = "\n".join(attr_lines)

    # Process Prompts
    print("Processing prompts...")
    count = 0
    with open(INPUT_JSONL, 'r', encoding='utf-8') as f_in, \
         open(OUTPUT_JSONL, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            try:
                data = json.loads(line)
                orig = data.get('prompt', '')
                
                # Replace top part with new header
                if 'def ' in orig and 'class ' in orig:
                    class_idx = orig.find('class ')
                    colon_idx = orig.find(':', class_idx)
                    class_name = orig[class_idx + 6:colon_idx].strip()

                    new_header = f"from dataclasses import dataclass\n\n\n@dataclass\nclass {class_name}:\n{fields_block}\n\n"

                    idx = orig.find('    def ')
                    new_p = new_header + orig[idx:]
                    data['prompt'] = new_p
                    f_out.write(json.dumps(data) + '\n')
                    count += 1
            except: continue
            
    print(f"Generated {count} unified prompts.")

if __name__ == "__main__":
    main()
