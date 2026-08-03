import json
import re
import sys
from collections import defaultdict
from pathlib import Path

def scan_attributes(file_path):
    if not file_path.exists():
        print(f"Error: {file_path} not found.")
        return

    attributes = defaultdict(set)
    counts = defaultdict(int)
    values = defaultdict(set)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                prompt = data.get('prompt', '')
                
                for prompt_line in prompt.split('\n'):
                    # Definition: gender: str
                    match = re.search(r'^\s+(\w+):\s+(\w+)', prompt_line)
                    if match:
                        name, type_ = match.groups()
                        attributes[name].add(type_)
                        counts[name] += 1
                    
                    # Values: # gender ['female', 'male']
                    val_match = re.search(r'^\s+#\s+(\w+)\s+\[(.*?)\]', prompt_line)
                    if val_match:
                        name, val_str = val_match.groups()
                        vals = [v.strip().strip("'\"") for v in val_str.split(',') if v.strip()]
                        for v in vals: values[name].add(v)
                        
            except: continue

    # Report
    print(f"# Attribute Statistics")
    print(f"Total Unique: {len(attributes)}\n")
    print("| Attribute | Type | Count | Values |")
    print("| :--- | :--- | :--- | :--- |")
    
    sorted_attrs = sorted(attributes.keys(), key=lambda x: (-counts[x], x))
    
    for attr in sorted_attrs:
        types = ", ".join(sorted(list(attributes[attr])))
        vals = ", ".join(sorted(list(values[attr])))
        print(f"| {attr} | {types} | {counts[attr]} | {vals} |")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    path = base_dir / "data" / "dataset" / "prompts_expanded_new.jsonl"
    scan_attributes(path)
