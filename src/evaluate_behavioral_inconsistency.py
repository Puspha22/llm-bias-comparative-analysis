import os
import json
import textwrap
import re
import math
from collections import defaultdict
import random
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc=""):
        print(f"{desc}...")
        return iterable

class Person:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def convert_type(value, type_str):
    if value is None: return None
    if type_str == 'int':
        try: return int(float(value))
        except: return 0
    if type_str == 'float':
        try: return float(value)
        except: return 0.0
    if type_str == 'bool':
        return str(value).lower() in ['true', '1', 'yes']
    return str(value).strip("'\"")

def build_prompt_schema_map(prompts_file):
    prompt_schemas = {}
    
    with open(prompts_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            t_id = data.get("task_id")
            prompt = data.get("prompt", "")
            
            master_map = defaultdict(set)
            type_map = {}
            
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
                default_val = sorted_vals[0] if sorted_vals else None
                base_profile[key] = convert_type(default_val, attr_type)

            prompt_schemas[t_id] = {
                "base_profile": base_profile,
                "master_map": final_map,
                "type_map": type_map,
                "prompt_text": prompt
            }
            
    return prompt_schemas

def evaluate_behavioral_inconsistency(dataset_name, gen_dir, prompts_file, num_profiles=100, seed=42):
    random.seed(seed)
    prompt_schemas = build_prompt_schema_map(prompts_file)
    
    files = sorted([f for f in os.listdir(gen_dir) if f.endswith('.json')])
    
    task_results = []
    
    full_agreement_tasks = 0
    minor_disagreement_tasks = 0
    major_disagreement_tasks = 0
    total_tasks_evaluated = 0

    for fname in tqdm(files, desc=f"Evaluating Behavioral Inconsistency ({dataset_name})"):
        filepath = os.path.join(gen_dir, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        t_id = data.get("task_id")
        funcs_code = data.get("generated_functions", [])

        if len(funcs_code) < 2:
            continue

        schema_info = prompt_schemas.get(t_id)
        if not schema_info:
            continue

        master_map = schema_info["master_map"]
        type_map = schema_info["type_map"]
        base_profile = schema_info["base_profile"]
        prompt_text = schema_info["prompt_text"]

        try:
            def_line = [l for l in prompt_text.split('\n') if l.strip().startswith('def ') and "__init__" not in l][0]
            func_name = def_line.split('(')[0].replace('def ', '').strip()
        except:
            continue

        # Compile all valid functions
        compiled_funcs = []
        for idx, code in enumerate(funcs_code):
            clean_code = "\n".join([l for l in code.split('\n') if not l.strip().startswith('#')])
            if not clean_code.strip(): continue
            exec_code = f"def {func_name}(self):\n{textwrap.indent(textwrap.dedent(clean_code), '    ')}"
            scope = {}
            try:
                exec(exec_code, globals(), scope)
                if func_name in scope:
                    compiled_funcs.append((idx, scope[func_name]))
            except Exception:
                continue

        if len(compiled_funcs) < 2:
            continue

        total_tasks_evaluated += 1

        # Generate shared test profiles with per-task deterministic seed
        try:
            task_seed = seed + int(t_id)
        except:
            task_seed = seed
        random.seed(task_seed)

        all_keys = list(master_map.keys())
        test_profiles = []
        if all_keys:
            for _ in range(num_profiles):
                prof = base_profile.copy()
                for k in all_keys:
                    domain_vals = master_map.get(k, [])
                    if domain_vals:
                        v = random.choice(domain_vals)
                        prof[k] = convert_type(v, type_map.get(k, 'str'))
                test_profiles.append(Person(**prof))
        else:
            test_profiles.append(Person())


        # Collect output vectors per function
        func_outputs = []
        for idx, func_obj in compiled_funcs:
            out_vec = []
            for p_obj in test_profiles:
                try:
                    res = func_obj(p_obj)
                    out_vec.append(str(res))
                except Exception as e:
                    out_vec.append(f"Error:{type(e).__name__}")
            func_outputs.append((idx, out_vec))

        # Calculate pairwise agreement rates
        pairwise_agreements = []
        n_funcs = len(func_outputs)
        for i in range(n_funcs):
            for j in range(i + 1, n_funcs):
                vec1 = func_outputs[i][1]
                vec2 = func_outputs[j][1]
                matches = sum(1 for a, b in zip(vec1, vec2) if a == b)
                agreement = matches / len(vec1) if vec1 else 1.0
                pairwise_agreements.append(agreement)

        avg_task_agreement = sum(pairwise_agreements) / len(pairwise_agreements) if pairwise_agreements else 1.0

        if avg_task_agreement == 1.0:
            full_agreement_tasks += 1
            category = "full_agreement"
        elif avg_task_agreement >= 0.8:
            minor_disagreement_tasks += 1
            category = "minor_disagreement"
        else:
            major_disagreement_tasks += 1
            category = "major_disagreement"

        task_results.append({
            "task_id": t_id,
            "func_name": func_name,
            "compiled_functions_count": n_funcs,
            "average_pairwise_agreement_pct": round(avg_task_agreement * 100, 2),
            "disagreement_category": category
        })

    summary = {
        "dataset_name": dataset_name,
        "total_tasks_evaluated": total_tasks_evaluated,
        "full_behavioral_agreement_tasks": full_agreement_tasks,
        "minor_disagreement_tasks": minor_disagreement_tasks,
        "major_disagreement_tasks": major_disagreement_tasks,
        "behaviorally_inconsistent_tasks": total_tasks_evaluated - full_agreement_tasks,
        "behavioral_inconsistency_rate_pct": round(((total_tasks_evaluated - full_agreement_tasks) / total_tasks_evaluated) * 100, 2) if total_tasks_evaluated else 0,
        "average_overall_agreement_pct": round(sum(t["average_pairwise_agreement_pct"] for t in task_results) / len(task_results), 2) if task_results else 100.0,
        "task_details": task_results
    }

    return summary

def main():
    os.makedirs("reports", exist_ok=True)
    
    datasets = [
        {
            "name": "Gemini_Unified",
            "gen_dir": os.path.join("data", "generated_functions_unified_new"),
            "prompts_file": os.path.join("data", "dataset", "prompts_unified_new.jsonl"),
            "out_file": os.path.join("reports", "behavioral_inconsistency_gemini.json")
        },
        {
            "name": "Grok_Unified",
            "gen_dir": os.path.join("data", "generated_functions_grok"),
            "prompts_file": os.path.join("data", "dataset", "prompts_unified_new.jsonl"),
            "out_file": os.path.join("reports", "behavioral_inconsistency_grok.json")
        },
        {
            "name": "Gemini_Legacy",
            "gen_dir": os.path.join("data", "generated_functions_old"),
            "prompts_file": os.path.join("data", "dataset", "prompts_old.jsonl"),
            "out_file": os.path.join("reports", "behavioral_inconsistency_legacy.json")
        }
    ]

    all_summaries = {}

    for ds in datasets:
        if os.path.exists(ds["gen_dir"]) and os.path.exists(ds["prompts_file"]):
            res = evaluate_behavioral_inconsistency(
                ds["name"], ds["gen_dir"], ds["prompts_file"]
            )
            with open(ds["out_file"], 'w', encoding='utf-8') as f:
                json.dump(res, f, indent=2)
            
            all_summaries[ds["name"]] = {
                "total_tasks_evaluated": res["total_tasks_evaluated"],
                "full_agreement_tasks": res["full_behavioral_agreement_tasks"],
                "behaviorally_inconsistent_tasks": res["behaviorally_inconsistent_tasks"],
                "behavioral_inconsistency_rate_pct": res["behavioral_inconsistency_rate_pct"],
                "average_overall_agreement_pct": res["average_overall_agreement_pct"],
                "minor_disagreement_tasks": res["minor_disagreement_tasks"],
                "major_disagreement_tasks": res["major_disagreement_tasks"]
            }

    summary_file = os.path.join("reports", "behavioral_inconsistency_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_summaries, f, indent=2)

    print("\n================ BEHAVIORAL INCONSISTENCY SUMMARY ================")
    print(json.dumps(all_summaries, indent=2))

if __name__ == "__main__":
    main()
