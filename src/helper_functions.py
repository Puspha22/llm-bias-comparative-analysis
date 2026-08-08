import os
import json
import re

PROTECTED_ATTRIBUTES = [
    'age', 'gender', 'race', 'religion', 'disability_rating', 
    'pregnancy_status', 'marital_status', 'mental_health_history',
    'service_disability_rating', 'genetic_disorder_risk', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
]

class Person:
    """Flexible profile object for dynamic function execution."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def __repr__(self):
        return f"Person({self.__dict__})"

def convert_type(value, type_str):
    """Safely converts string values into specified primitive types."""
    if value is None: return None
    val_str = str(value).strip("'\"")
    if type_str == 'int':
        try: return int(float(val_str))
        except: return 0
    if type_str == 'float':
        try: return float(val_str)
        except: return 0.0
    if type_str == 'bool':
        return val_str.lower() in ['true', '1', 'yes']
    
    # Auto-convert numeric strings if type_str is unspecified/str
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        pass
        
    return val_str

def find_used_attributes(code, all_keys):
    """Extracts all self.<attribute> references from Python code text."""
    used = set()
    code_clean = code.replace("(", " ").replace(")", " ")
    for key in all_keys:
        if re.search(r"self\." + re.escape(key) + r"\b", code_clean):
            used.add(key)
    return sorted(list(used))

def build_profile_map(prompts_file):
    """Parses prompt JSONL file to build base profiles and attribute domain maps."""
    from collections import defaultdict
    master_map = defaultdict(set)
    type_map = {} 
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            prompt = data.get("prompt", "")
            
            for p_line in prompt.split('\n'):
                list_match = re.search(r"#\s*([\w_]+)\s*\[(.*?)\]", p_line)
                if list_match:
                    key = list_match.group(1).strip()
                    vals = [v.strip().strip("'\"") for v in list_match.group(2).split(',')]
                    if vals: master_map[key].update(vals)
                
                type_match = re.search(r"^\s*([\w_]+)\s*:\s*(\w+)", p_line)
                if type_match:
                    type_map[type_match.group(1)] = type_match.group(2)

    base_profile = {}
    final_map = {}

    for key, vals in master_map.items():
        sorted_vals = sorted(list(vals))
        final_map[key] = sorted_vals
        attr_type = type_map.get(key, 'str')
        if attr_type == 'int' and any('.' in str(v) for v in sorted_vals):
            attr_type = 'float'
            type_map[key] = 'float'
        default_val = sorted_vals[0] if sorted_vals else None
        base_profile[key] = convert_type(default_val, attr_type)

    return base_profile, final_map, type_map
