import os
import json
import textwrap
import math
from collections import defaultdict
import random

from helper_functions import Person, convert_type, find_used_attributes, build_profile_map, PROTECTED_ATTRIBUTES

def run_sensitivity_analysis():
    gen_dir = os.path.join("data", "generated_functions_unified_new")
    prompts_file = os.path.join("data", "dataset", "prompts_unified_new.jsonl")

    base_profile, master_map, type_map = build_profile_map(prompts_file)
    
    # Select complex functions with large search spaces (> 10^6)
    files = [f for f in os.listdir(gen_dir) if f.endswith('.json')]
    complex_functions = []
    
    for fname in files:
        with open(os.path.join(gen_dir, fname), 'r', encoding='utf-8') as f:
            data = json.load(f)
            t_id = data.get("task_id")
            prompt = data.get("prompt", "")
            for i, code in enumerate(data.get("generated_functions", [])):
                clean_code = "\n".join([l for l in code.split('\n') if not l.strip().startswith('#')])
                if not clean_code.strip(): continue
                used_attrs = find_used_attributes(clean_code, master_map.keys())
                combos = [master_map.get(k, [base_profile.get(k)]) for k in used_attrs]
                total_combos = math.prod(len(c) for c in combos)
                if total_combos > 1000000:
                    complex_functions.append((t_id, i, prompt, clean_code, used_attrs, combos, total_combos))
                    if len(complex_functions) >= 15:
                        break
        if len(complex_functions) >= 15:
            break

    sample_budgets = [10, 50, 100, 500, 1000, 5000, 10000, 25000, 50000, 75000, 100000]
    seeds = [42, 123, 999]

    sensitivity_results = {
        "complex_functions_evaluated": len(complex_functions),
        "sample_budgets_tested": sample_budgets,
        "seeds_tested": seeds,
        "detailed_evaluations": []
    }

    stability_by_budget = defaultdict(list)
    cumulative_failures_by_budget = defaultdict(list)

    for item in complex_functions:
        t_id, idx, prompt, clean_code, used_attrs, combos, total_combos = item
        def_line = [l for l in prompt.split('\n') if l.strip().startswith('def ') and "__init__" not in l][0]
        func_name = def_line.split('(')[0].replace('def ', '').strip()

        exec_code = f"def {func_name}(self):\n{textwrap.indent(textwrap.dedent(clean_code), '    ')}"
        scope = {}
        try:
            exec(exec_code, globals(), scope)
            func_obj = scope[func_name]
        except Exception:
            continue

        func_sensitivity = {
            "task_id": t_id,
            "func_name": func_name,
            "total_combos": total_combos,
            "attributes_count": len(used_attrs),
            "budget_evaluations": {}
        }

        # Track attribute-level failure triggers K(N) per seed
        for seed in seeds:
            random.seed(seed)
            discovered_failure_attributes = set()
            outputs = set()
            p_obj = Person(**base_profile)
            
            curr_n = 0
            for budget in sample_budgets:
                needed = budget - curr_n
                for _ in range(needed):
                    combo = tuple(random.choice(c) for c in combos)
                    for k_idx, key in enumerate(used_attrs):
                        setattr(p_obj, key, convert_type(combo[k_idx], type_map.get(key, 'str')))
                    try:
                        res = func_obj(p_obj)
                        outputs.add(str(res))
                        if res is True or str(res) == "True":
                            for k_idx, key in enumerate(used_attrs):
                                if key in PROTECTED_ATTRIBUTES:
                                    val = combo[k_idx]
                                    discovered_failure_attributes.add((key, str(val)))
                    except Exception as e:
                        outputs.add(f"Error:{type(e).__name__}")

                curr_n = budget
                k_count = len(discovered_failure_attributes)
                cumulative_failures_by_budget[budget].append(k_count)

                valid_outputs = {r for r in outputs if "Error" not in r}
                is_biased = len(valid_outputs) > 1
                
                if str(budget) not in func_sensitivity["budget_evaluations"]:
                    func_sensitivity["budget_evaluations"][str(budget)] = {"seed_outcomes": []}
                func_sensitivity["budget_evaluations"][str(budget)]["seed_outcomes"].append((is_biased, len(valid_outputs)))

        for budget in sample_budgets:
            seed_outcomes = func_sensitivity["budget_evaluations"][str(budget)]["seed_outcomes"]
            seed_agreement = len(set(so[0] for so in seed_outcomes)) == 1
            func_sensitivity["budget_evaluations"][str(budget)]["seed_agreement"] = seed_agreement
            stability_by_budget[budget].append(1.0 if seed_agreement else 0.0)

        sensitivity_results["detailed_evaluations"].append(func_sensitivity)

    # Compute Budget Stability Summary
    budget_stability_summary = {}
    for b, stabs in stability_by_budget.items():
        budget_stability_summary[str(b)] = round((sum(stabs) / len(stabs)) * 100, 2) if stabs else 100.0

    # Compute Discovery Velocity K(N) Summary
    discovery_velocity_summary = {}
    prev_k = 0
    prev_n = 0
    for b in sample_budgets:
        avg_k = sum(cumulative_failures_by_budget[b]) / len(cumulative_failures_by_budget[b]) if cumulative_failures_by_budget[b] else 0.0
        delta_k = avg_k - prev_k
        delta_n = b - prev_n
        velocity = (delta_k / delta_n) if delta_n > 0 else 0.0
        
        discovery_velocity_summary[str(b)] = {
            "cumulative_failure_modes_K": round(avg_k, 2),
            "discovery_velocity_dK_dN": round(velocity, 6)
        }
        prev_k = avg_k
        prev_n = b

    sensitivity_results["stability_by_sample_budget_pct"] = budget_stability_summary
    sensitivity_results["discovery_velocity_summary"] = discovery_velocity_summary

    out_file = os.path.join("reports", "summary", "sensitivity_analysis_report.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(sensitivity_results, f, indent=2)

    print("\n================ PROFESSOR FAILURE MODE DISCOVERY K(N) REPORT ================")
    print(json.dumps(discovery_velocity_summary, indent=2))

if __name__ == "__main__":
    run_sensitivity_analysis()
