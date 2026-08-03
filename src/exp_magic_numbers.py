import os
import json
import ast
import re
from collections import Counter, defaultdict
import textwrap

# Configuration
PROMPTS_FILE = os.path.join("data", "dataset", "prompts_unified_new.jsonl")
GENERATED_DIR = os.path.join("data", "generated_functions_unified_new")

def load_prompt_values():
    """Builds a map of {attribute: set(values)} from the prompts."""
    master_map = defaultdict(set)
    # Regex to find lists in comments: # age ['18', '20']
    list_pattern = re.compile(r"#\s*([\w_]+)\s*\[(.*?)\]")
    
    try:
        with open(PROMPTS_FILE, 'r') as f:
            for line in f:
                data = json.loads(line)
                prompt = data.get("prompt", "")
                
                # Scan prompt for attribute definitions
                for p_line in prompt.split('\n'):
                    match = list_pattern.search(p_line)
                    if match:
                        key = match.group(1).strip()
                        # Parse values: 'a', "b", 10
                        raw_vals = match.group(2).split(',')
                        clean_vals = [v.strip().strip("'\"") for v in raw_vals if v.strip()]
                        
                        # Convert numbers to strings for comparison
                        final_vals = []
                        for v in clean_vals:
                            try:
                                # Try converting to float/int to normalize (e.g. "18.0" == 18)
                                val_num = float(v)
                                if val_num.is_integer():
                                    final_vals.append(str(int(val_num)))
                                else:
                                    final_vals.append(str(val_num))
                                    
                                # Fix for GPA int type issue
                                if 'gpa' in key.lower():
                                    final_vals.append(str(int(val_num * 10)))
                            except:
                                final_vals.append(v)
                        
                        master_map[key].update(final_vals)
    except Exception as e:
        print(f"Error loading prompts: {e}")
        
    return master_map

class MagicNumberVisitor(ast.NodeVisitor):
    def __init__(self, known_values_map):
        self.magic_numbers = []
        self.known_values_map = known_values_map
        self.current_attr = None

    def visit_Attribute(self, node):
        # unexpected, but tracking attribute access: self.age
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            self.current_attr = node.attr
        self.generic_visit(node)

    def visit_Compare(self, node):
        # Check comparisons: self.age >= 18
        
        # Reset current attribute before visiting children
        self.current_attr = None
        
        # Visit left side to find attribute (e.g. self.age)
        self.visit(node.left)
        left_attr = self.current_attr
        
        # Visit comparators (the values being compared to)
        for comparator in node.comparators:
            val = None
            if isinstance(comparator, ast.Constant):
                val = comparator.value
                
            if val is not None and left_attr:
                # Normalization
                val_str = str(val)
                known_vals = self.known_values_map.get(left_attr, set())
                
                # Check 1: Direct String Match
                if val_str in known_vals:
                    continue
                    
                # Check 2: Numeric Match (if applicable)
                is_magic = True
                try:
                    val_float = float(val)
                    # Check against all known values by trying to convert them to float too
                    for k_val in known_vals:
                        try:
                            if k_val and float(k_val) == val_float:
                                is_magic = False
                                break
                        except:
                            continue
                except:
                    pass
                
                # If value is NOT in known values, it's a MAGIC NUMBER
                if is_magic:
                    # Filter out obvious non-magic numbers like 0, 1, empty string
                    if val_str not in ['0', '1', '0.0', '1.0', '']:
                        self.magic_numbers.append({
                            "attribute": left_attr,
                            "magic_value": val,
                            "line": getattr(node, 'lineno', '?')
                        })
        
        # Reset
        self.current_attr = None

def main():
    print("--- Experiment 1: Magic Number Analysis ---")
    
    # 1. Load Known Values
    print("Loading valid attribute values from prompts...")
    master_map = load_prompt_values()
    print(f"Loaded valid value sets for {len(master_map)} attributes.")
    
    # 2. Scan Functions
    print("Scanning generated functions for hardcoded constants...")
    files = [f for f in os.listdir(GENERATED_DIR) if f.endswith('.json')]
    
    magic_counts = Counter()
    magic_details = []
    
    for fname in files:
        fpath = os.path.join(GENERATED_DIR, fname)
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                
            task_id = data.get("task_id")
            codes = data.get("generated_functions", [])
            
            for idx, code in enumerate(codes):
                try:
                    tree = ast.parse(code)
                    visitor = MagicNumberVisitor(master_map)
                    visitor.visit(tree)
                    
                    for magic in visitor.magic_numbers:
                        magic_val = magic['magic_value']
                        attr = magic['attribute']
                        
                        magic_counts[magic_val] += 1
                        magic_details.append({
                            "task_id": task_id,
                            "sample": idx,
                            "attribute": attr,
                            "value": magic_val
                        })
                except SyntaxError:
                    pass # Skip unparseable code
                    
        except Exception:
            continue
            
    # 3. Report
    print(f"\nFound {len(magic_details)} instances of potential magic numbers/strings.\n")
    
    print("Top 10 Most Common Magic Values:")
    print(f"{'Value':<15} | {'Count':<5}")
    print("-" * 25)
    for val, count in magic_counts.most_common(10):
        print(f"{str(val):<15} | {count:<5}")
        
    print("\nMost Frequent Attributes with Magic Numbers:")
    attr_counts = Counter(d['attribute'] for d in magic_details)
    for attr, count in attr_counts.most_common(5):
        print(f" - {attr}: {count} times")

    # Save details
    with open("reports/exp_magic_numbers_results_new.json", "w") as f:
        json.dump(magic_details, f, indent=2)
    print("\nDetailed results saved to reports/exp_magic_numbers_results_new.json")

    # --- Plotting ---
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        
        # Plot top 10 magic values
        top_magic = magic_counts.most_common(10)
        if top_magic:
            df = pd.DataFrame(top_magic, columns=['Value', 'Count'])
            df['Value'] = df['Value'].astype(str) # ensure categorical plotting
            
            plt.figure(figsize=(10, 6))
            plt.bar(df['Value'], df['Count'], color='#3498db')
            plt.title('Top 10 "Magic Values" Found in Generated Code')
            plt.xlabel('Hardcoded Value')
            plt.ylabel('Frequency')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('reports/magic_numbers_chart_new.png')
            print("Chart saved to reports/magic_numbers_chart_new.png")
    except ImportError:
        print("Matplotlib/Pandas not installed. skipping chart.")


if __name__ == "__main__":
    main()
