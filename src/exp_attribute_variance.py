import os
import json
import re
from collections import defaultdict

GENERATED_DIR = os.path.join("data", "generated_functions_grok")
PROMPTS_FILE = os.path.join("data", "dataset", "prompts_unified_new.jsonl")
OUTPUT_JSON = os.path.join("reports", "exp_attribute_variance_results_grok.json")
CHART_FILE = os.path.join("reports", "attribute_variance_chart_grok.png")

def find_used_attributes(code):
    """Simple regex/string match to find usages of 'self.attribute'."""
    # This is a heuristic. A robust AST approach is better but regex is fast for this exp.
    # We first need the list of all possible attributes to avoid false positives.
    # But for variance, finding *any* 'self.xyz' difference is enough.
    
    # Matches self.attribute_name
    matches = re.findall(r"self\.([a-zA-Z_][a-zA-Z0-9_]*)", code)
    # Filter out standard methods/properties if any (unlikely in this dataset)
    return set(matches)

def main():
    print("--- Experiment 2: Attribute Variance Analysis ---")
    
    if not os.path.exists(GENERATED_DIR):
        print("Generated data not found.")
        return

    files = [f for f in os.listdir(GENERATED_DIR) if f.endswith('.json')]
    
    inconsistent_tasks = 0
    total_tasks = 0
    variance_details = []
    
    for fname in files:
        total_tasks += 1
        fpath = os.path.join(GENERATED_DIR, fname)
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                
            task_id = data.get("task_id")
            codes = data.get("generated_functions", [])
            
            # Collect attribute sets for each of the 5 samples
            usage_sets = []
            for code in codes:
                # Simple cleanup to ignore comments
                clean_lines = [l for l in code.split('\n') if not l.strip().startswith('#')]
                clean_code = "\n".join(clean_lines)
                usage_sets.append(find_used_attributes(clean_code))
            
            # Check consistency
            # Convert sets to frozensets to put in a set (to find unique sets)
            unique_logic_paths = set(frozenset(s) for s in usage_sets)
            
            if len(unique_logic_paths) > 1:
                inconsistent_tasks += 1
                variance_details.append({
                    "task_id": task_id,
                    "prompt": data.get("prompt", "")[:100] + "...",
                    "unique_paths_count": len(unique_logic_paths),
                    "paths": [list(s) for s in unique_logic_paths]
                })

        except Exception:
            continue
            
    print(f"\nAnalyzed {total_tasks} tasks (5 samples each).")
    print(f"Tasks with Inconsistent Logic: {inconsistent_tasks}")
    print(f"Consistency Rate: {(1 - inconsistent_tasks/total_tasks)*100:.2f}%")
    print(f"Variance Rate:    {(inconsistent_tasks/total_tasks)*100:.2f}%")
    
    if variance_details:
        print("\nExample of High Variance:")
        example = variance_details[0]
        print(f"Task {example['task_id']}: Found {example['unique_paths_count']} different attribute sets used.")
        for i, path in enumerate(example['paths']):
            print(f"  Path {i+1}: {path}")

    with open(OUTPUT_JSON, "w") as f:
        json.dump(variance_details, f, indent=2)
    print(f"\nDetailed results saved to {OUTPUT_JSON}")

    # --- Plotting ---
    try:
        import matplotlib.pyplot as plt
        
        labels = ['Consistent (Same Logic)', 'Inconsistent (Logic Variance)']
        sizes = [total_tasks - inconsistent_tasks, inconsistent_tasks]
        colors = ['#2ecc71', '#e74c3c'] # Green, Red
        
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Logic Consistency in LLM-Generated Functions')
        plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig(CHART_FILE)
        print(f"Chart saved to {CHART_FILE}")
            
    except ImportError:
        print("Matplotlib not installed, skipping chart.")


if __name__ == "__main__":
    main()
