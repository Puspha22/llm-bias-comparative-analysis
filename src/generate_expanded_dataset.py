import json
import re
import sys
from collections import defaultdict
from pathlib import Path

def parse_attribute_comment(line):
    """Extracts attribute key and values from a comment line."""
    match = re.search(r"#\s*([\w_]+)\s*\[(.*?)\]", line)
    if match:
        key = match.group(1).strip()
        content = match.group(2).strip()
        if content:
            values = [v.strip().strip("'").strip('"') for v in content.split(',') if v.strip()]
            return key, values
        return key, []
    return None, []

def main():
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "data" / "dataset" / "prompts_old.jsonl"
    output_path = base_dir / "data" / "dataset" / "prompts_expanded_new.jsonl"

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Reading from: {input_path}")
    
    # 1. Collect all attribute values
    functional_values = defaultdict(set)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                prompt = data.get('prompt', '')
                for prompt_line in prompt.split('\n'):
                    key, values = parse_attribute_comment(prompt_line)
                    if key:
                        functional_values[key].update(values)
            except json.JSONDecodeError:
                continue

    # Sort for deterministic output
    sorted_values = {k: sorted(list(v)) for k, v in functional_values.items()}

    # 2. Rewrite file with expanded lists
    print(f"Writing to: {output_path}")
    count = 0
    
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            try:
                data = json.loads(line)
                prompt = data.get('prompt', '')
                new_lines = []
                
                for prompt_line in prompt.split('\n'):
                    key, _ = parse_attribute_comment(prompt_line)
                    if key and key in sorted_values:
                        indent = re.match(r"^\s*", prompt_line).group(0)
                        all_vals = sorted_values[key]
                        
                        # Format values (keep numbers as numbers, quote strings)
                        formatted = []
                        for v in all_vals:
                            # Simple heuristic: if it looks like a number, keep it as is
                            if v.replace('.', '', 1).isdigit():
                                formatted.append(v)
                            else:
                                formatted.append(f"'{v}'")

                        vals_str = ", ".join(formatted)
                        new_lines.append(f"{indent}# {key} [{vals_str}]")
                    else:
                        new_lines.append(prompt_line)
                
                data['prompt'] = "\n".join(new_lines)
                f_out.write(json.dumps(data) + "\n")
                count += 1
                
            except json.JSONDecodeError:
                continue

    print(f"Processed {count} prompts.")

if __name__ == "__main__":
    main()
