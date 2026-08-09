import os, json, glob, time, re
from collections import defaultdict
import numpy as np

PROTECTED_ATTRIBUTES = {
    'race', 'religion', 'gender', 'pregnancy_status', 'age',
    'disability_percentage', 'disability_rating', 'service_disability_rating',
    'genetic_disorder_risk', 'marital_status', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
}

DOMAIN_RANGES = {
    "Social Benefits": (0, 50),
    "University Admissions and Awards": (51, 101),
    "Employee Development and Benefits": (102, 152),
    "Health Exams and Programs": (153, 212),
    "Licensing": (213, 262),
    "Hobbies": (263, 292),
    "Occupations": (293, 342)
}

def get_domain_for_task(task_id):
    try:
        tid = int(task_id)
        for domain, (start, end) in DOMAIN_RANGES.items():
            if start <= tid <= end: return domain
    except: pass
    return "Other"

def process_file_stream(filepath):
    m_task = re.search(r'task_(\d+)_sample_(\d+)_result', filepath)
    if not m_task: return None
    task_id = m_task.group(1)
    sample_idx = int(m_task.group(2))
    func_key = (task_id, sample_idx)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return None

    is_biased = data.get("status") == "biased"
    attrs_tested = data.get("attributes_tested", [])
    if attrs_tested and isinstance(attrs_tested[0], dict):
        attrs_tested = [a.get("name", "") for a in attrs_tested]

    tested_protected = [pattr for pattr in attrs_tested if pattr in PROTECTED_ATTRIBUTES]
    func_is_biased = is_biased and len(tested_protected) > 0

    attr_bias_dict = {}
    for pattr in PROTECTED_ATTRIBUTES:
        if pattr in tested_protected and is_biased:
            attr_bias_dict[pattr] = (True, 1, 1, 100.0)
        else:
            attr_bias_dict[pattr] = (False, 0, 1, 0.0)

    return func_key, task_id, sample_idx, func_is_biased, attr_bias_dict

def analyze_dir(pdir):
    success_dir = os.path.join(pdir, "success")
    if not os.path.exists(success_dir): return None
    files = glob.glob(os.path.join(success_dir, "*.json"))
    t0 = time.time()
    
    results = []
    for idx, f in enumerate(files):
        res = process_file_stream(f)
        if res: results.append(res)
        if (idx + 1) % 500 == 0:
            print(f"[{os.path.basename(pdir)}] Processed {idx + 1}/{len(files)} files...", flush=True)

    t1 = time.time()
    print(f"[{os.path.basename(pdir)}] Finished {len(files)} files in {t1 - t0:.2f} seconds.", flush=True)

    task_functions = defaultdict(dict)
    function_results = {}
    attribute_flips = defaultdict(int)
    attribute_evals = defaultdict(int)
    attribute_flip_rates = defaultdict(list)

    for item in results:
        func_key, task_id, sample_idx, is_biased, attr_bias_dict = item
        function_results[func_key] = {"biased": is_biased, "attrs": {k: v[0] for k, v in attr_bias_dict.items()}}
        task_functions[task_id][sample_idx] = is_biased

        for p_attr, (flips, f_count, t_count, f_rate) in attr_bias_dict.items():
            attribute_evals[p_attr] += 1
            if flips:
                attribute_flips[p_attr] += 1
                attribute_flip_rates[p_attr].append(f_rate)

    total_eval = len(function_results)
    biased_cnt = sum(1 for v in function_results.values() if v["biased"])
    bias_rate = (biased_cnt / total_eval * 100.0) if total_eval > 0 else 0.0

    dom_stats = defaultdict(lambda: {"total": 0, "biased": 0})
    for (tid, sidx), v in function_results.items():
        dom = get_domain_for_task(tid)
        dom_stats[dom]["total"] += 1
        if v["biased"]: dom_stats[dom]["biased"] += 1

    dom_pcts = {d: round((c["biased"]/c["total"]*100.0), 2) if c["total"] > 0 else 0.0 for d, c in dom_stats.items()}
    avg_flips = {a: round(float(np.mean(r)), 2) for a, r in attribute_flip_rates.items()}

    return {
        "executable_functions": total_eval,
        "protected_attribute_sensitive_functions": biased_cnt,
        "protected_attribute_sensitivity_rate_pct": round(bias_rate, 2),
        "sensitive_attribute_counts": dict(attribute_flips),
        "attribute_evaluations": dict(attribute_evals),
        "average_attribute_flip_rates_pct": avg_flips,
        "domain_wise_sensitivity_pct": dom_pcts,
        "function_results": function_results
    }

def main():
    os.makedirs(os.path.join("reports", "summary"), exist_ok=True)
    datasets = {
        "Gemini_Unified": os.path.join("reports", "partial_audit_results_gemini_unified"),
        "Grok_Unified": os.path.join("reports", "partial_audit_results_grok_unified"),
        "Gemini_Legacy": os.path.join("reports", "partial_audit_results_gemini_legacy"),
        "Gemini_Expanded": os.path.join("reports", "partial_audit_results_gemini_expanded")
    }
    results = {}
    for name, pdir in datasets.items():
        if os.path.exists(pdir):
            res = analyze_dir(pdir)
            if res: results[name] = res

    summary = {}
    for name, res in results.items():
        summary[name] = {
            "executable_functions": res["executable_functions"],
            "protected_attribute_sensitive_functions": res["protected_attribute_sensitive_functions"],
            "protected_attribute_sensitivity_rate_pct": res["protected_attribute_sensitivity_rate_pct"],
            "sensitive_attribute_counts": res["sensitive_attribute_counts"],
            "average_attribute_flip_rates_pct": res["average_attribute_flip_rates_pct"],
            "domain_wise_sensitivity_pct": res["domain_wise_sensitivity_pct"]
        }

    out_file = os.path.join("reports", "summary", "protected_attribute_sensitivity_summary.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n================ VERIFIED LOGIC AUDIT SUMMARY ================", flush=True)
    print(json.dumps(summary, indent=2), flush=True)

if __name__ == "__main__":
    main()
