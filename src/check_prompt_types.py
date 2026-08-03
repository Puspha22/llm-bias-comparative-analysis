import sys
import json
import re
import ast

def check_types(file_path):
    issues = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            prompt = data['prompt']
            
            # Find all attribute comments and their corresponding type hints
            # Example: 
            #     # GPA [1.5, 2.0, 2.5]
            #     GPA: float
            
            pattern = re.compile(r'#\s*(\w+)\s*\[(.*?)\]\n\s*\w+:\s*(\w+)')
            matches = pattern.findall(prompt)
            
            for attr_name, list_str, type_hint in matches:
                if list_str.strip() == '':
                    continue
                    
                # parse the list
                try:
                    # handle string arrays might be ['a', 'b'] or 'a', 'b' ... but usually they are valid python reprs
                    list_str_clean = list_str.replace('"', "'")
                    values = ast.literal_eval(f"[{list_str_clean}]")
                    
                    for v in values:
                        v_type = type(v)
                        expected_type = type_hint.lower()
                        
                        if expected_type == 'int' and v_type is float:
                            issues.add(f"Attribute '{attr_name}' has float value ({v}) but is typed as 'int'")
                        elif expected_type == 'int' and v_type is str:
                            issues.add(f"Attribute '{attr_name}' has str value ({v}) but is typed as 'int'")
                        elif expected_type == 'str' and v_type is not str:
                            issues.add(f"Attribute '{attr_name}' has {v_type.__name__} value ({v}) but is typed as 'str'")
                        elif expected_type == 'float' and v_type is str:
                           issues.add(f"Attribute '{attr_name}' has string value ({v}) but is typed as 'float'")
                        elif expected_type == 'list' or expected_type == 'dict':
                           pass # ignoring complex types for now
                except SyntaxError:
                     # Some values might not be valid python literals if unquoted
                     issues.add(f"Parse error for '{attr_name}': values [{list_str}] couldn't be evaluated.")
                except Exception as e:
                     pass

    if issues:
        for issue in sorted(list(issues)):
            print(issue)
    else:
        print("No type mismatches found.")

if __name__ == "__main__":
    check_types(sys.argv[1])


