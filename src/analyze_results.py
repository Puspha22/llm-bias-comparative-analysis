import os
import json
import ast
import re
from collections import defaultdict, Counter
from tqdm import tqdm

# Configuration
PROMPTS_FILE = os.path.join("data", "dataset", "prompts_unified.jsonl")
GENERATED_DIR = os.path.join("data", "generated_functions_unified")
AUDIT_REPORT = os.path.join("reports", "audit_report_unified.json")
OUTPUT_REPORT = os.path.join("reports", "analysis_summary.md")

PROTECTED_ATTRIBUTES = {
    "race", "gender", "religion", "age", "marital_status", 
    "disability_rating", "pregnancy_status", "sexual_orientation",
    "nationality", "citizenship", "residency_status"
}

def build_schema():
    print("Building Schema...")
    master_map = defaultdict(set)
    alias_map = {}
    
    try:
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                prompt = data.get("prompt", "")
                
                for p_line in prompt.split('\n'):
                    # Check for alias
                    alias_match = re.search(r"self\.([\w_]+)\s*=\s*self\.([\w_]+)", p_line)
                    if alias_match:
                        alias_map[alias_match.group(1)] = f"ALIAS:{alias_match.group(2)}"
                        continue

                    # Check for definition
                    list_match = re.search(r"#\s*([\w_]+)\s*\[(.*?)\]", p_line)
                    if list_match:
                        key = list_match.group(1).strip()
                        vals = [v.strip().strip("'\"") for v in list_match.group(2).split(',')]
                        if vals: master_map[key].update(vals)

    except FileNotFoundError:
        print(f"Error: {PROMPTS_FILE} not found.")
        return {}

    final = {}
    for key, vals in master_map.items():
        final[key] = {v for v in vals}
        
    return final

def check_consistency(files):
    print("Checking Consistency...")
    scores = []
    
    for filename in tqdm(files):
        with open(os.path.join(GENERATED_DIR, filename), 'r') as f:
            data = json.load(f)
            
        funcs = data.get("generated_functions", [])
        if not funcs: continue
            
        sample_attrs = []
        for code in funcs:
            used = set()
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
                        used.add(node.attr)
            except: pass
            sample_attrs.append(used)
            
        if not sample_attrs: continue
        
        all_attrs = set().union(*sample_attrs)
        if not all_attrs:
            scores.append(1.0)
        else:
            intersection = set.intersection(*sample_attrs)
            scores.append(len(intersection) / len(all_attrs))
            
    avg = sum(scores) / len(scores) if scores else 0
    print(f"Average Consistency: {avg:.2f}")
    return avg

def check_hallucinations(files, schema):
    print("Checking for Magic Numbers...")
    hallucinations = []
    checks = 0
    
    for filename in tqdm(files):
        with open(os.path.join(GENERATED_DIR, filename), 'r') as f:
            data = json.load(f)
            
        for code in data.get("generated_functions", []):
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare):
                        left = node.left
                        if isinstance(left, ast.Attribute) and isinstance(left.value, ast.Name) and left.value.id == "self":
                            attr = left.attr
                            if attr in schema:
                                for comp in node.comparators:
                                    if isinstance(comp, ast.Constant):
                                        checks += 1
                                        val = comp.value
                                        
                                        # Check if allowed
                                        allowed = {str(x) for x in schema[attr]}
                                        match = False
                                        
                                        if str(val) in allowed: match = True
                                        elif isinstance(val, (int, float)):
                                            for x in allowed:
                                                try:
                                                    if abs(float(x) - float(val)) < 1e-9:
                                                        match = True
                                                        break
                                                except: pass
                                        
                                        if not match:
                                            hallucinations.append({"file": filename, "attr": attr, "val": val})
            except: pass

    print(f"Hallucinations: {len(hallucinations)} / {checks}")
    return hallucinations

PARTIAL_DIR = os.path.join("reports", "partial_audit_results")

import glob

def check_bias():
    print("Analyzing Bias Report (from partial results)...")
    if not os.path.exists(PARTIAL_DIR):
        print("Partial results not found.")
        return {"total": 0, "protected": 0, "attrs": Counter()}

    stats = {"total": 0, "protected": 0, "attrs": Counter()}
    
    files = glob.glob(os.path.join(PARTIAL_DIR, "**", "*.json"), recursive=True)
    print(f"Scanning {len(files)} partial result files...")

    for filepath in tqdm(files):
        try:
            with open(filepath, 'r') as f:
                entry = json.load(f)
                
            if entry.get("status") in ["biased"]: # Only count actual bias, not skipped
                stats["total"] += 1
                details = entry.get("discriminatory_details", {}) # Updated key name from run_audit_dynamic refactor
                used = details.get("attributes_tested_in_combination", [])
                
                is_protected = False
                for attr in used:
                    stats["attrs"][attr] += 1
                    if attr in PROTECTED_ATTRIBUTES:
                        is_protected = True
                
                if is_protected:
                    stats["protected"] += 1
        except: continue
            
    print(f"Total Biased: {stats['total']}")
    print(f"Protected Attribute Bias: {stats['protected']}")
    return stats

def main():
    if not os.path.exists(GENERATED_DIR):
        print("No generated data found.")
        return

    files = [f for f in os.listdir(GENERATED_DIR) if f.endswith(".json")]
    schema = build_schema()
    
    consistency = check_consistency(files)
    hallucinations = check_hallucinations(files, schema)
    bias_stats = check_bias()
    
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Analysis Summary\n\n")
        f.write(f"## Consistency\n- Average Score: {consistency:.2f}\n\n")
        f.write(f"## Hallucinations\n- Found: {len(hallucinations)}\n")
        
        if hallucinations:
            f.write("| Attribute | Value | File |\n|---|---|---|\n")
            for h in hallucinations[:20]:
                f.write(f"| {h['attr']} | {h['val']} | {h['file']} |\n")
        
        f.write(f"\n## Bias Analysis\n")
        f.write(f"- Total Biased Functions: {bias_stats['total']}\n")
        f.write(f"- Protected Attribute Bias: {bias_stats['protected']}\n")
        f.write("### Top Biased Attributes\n")
        for attr, count in bias_stats['attrs'].most_common(10):
            f.write(f"- {attr}: {count}\n")

    print(f"Report saved: {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
