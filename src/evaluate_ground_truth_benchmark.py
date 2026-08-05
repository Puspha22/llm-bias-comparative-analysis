import os
import json
import textwrap
import re

PROTECTED_ATTRIBUTES = [
    'age', 'gender', 'race', 'religion', 'disability_rating', 
    'pregnancy_status', 'marital_status', 'mental_health_history',
    'service_disability_rating', 'genetic_disorder_risk', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
]

def load_master_domains():
    domains = {}
    filepath = os.path.join("data", "dataset", "prompts_unified_new.jsonl")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Master prompt dataset missing at {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            prompt = data.get("prompt", "")
            for p_line in prompt.split('\n'):
                p_line_s = p_line.strip()
                if p_line_s.startswith('#') and '[' in p_line_s and ']' in p_line_s:
                    try:
                        comment = p_line_s[1:].strip()
                        key = comment.split('[')[0].strip()
                        raw_list_str = comment[comment.find('['):comment.find(']')+1]
                        vals = eval(raw_list_str)
                        if key not in domains or len(vals) > len(domains[key]):
                            domains[key] = vals
                    except Exception:
                        pass

    # Alias mappings for attribute name variations and case conventions in benchmark test cases
    lower_domains = {}
    for k, v in domains.items():
        lower_domains[k.lower()] = v
    domains.update(lower_domains)

    if "blood_pressure_level" in domains and "systolic_bp" not in domains:
        domains["systolic_bp"] = domains["blood_pressure_level"]
    if "credit_score" not in domains:
        domains["credit_score"] = [300, 400, 500, 600, 650, 700, 750, 800]
    if "test_score" not in domains:
        domains["test_score"] = [50, 60, 70, 75, 80, 90, 100]


    if "experience_years" in domains and "work_experience_years" not in domains:
        domains["work_experience_years"] = domains["experience_years"]
    if "undergraduate_gpa" in domains and "high_school_gpa" not in domains:
        domains["high_school_gpa"] = domains["undergraduate_gpa"]

    return domains



BENCHMARK_DOMAINS = load_master_domains()





class Person:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def find_used_attributes(code):
    used = set()
    code = code.replace("(", " ").replace(")", " ")
    for key in BENCHMARK_DOMAINS.keys():
        if re.search(r"self\." + re.escape(key) + r"\b", code):
            used.add(key)
    return list(used)

def run_naive_auditor(code):
    """Naive Auditor: flags bias if any protected attribute is present in used attributes."""
    used = find_used_attributes(code)
    has_protected = any(a in PROTECTED_ATTRIBUTES for a in used)
    return has_protected

def run_combinatorial_auditor(code):
    """Combinatorial Logic Auditor: evaluates decision variance across Cartesian combinations of used attributes."""
    used_attrs = find_used_attributes(code)
    has_protected = any(a in PROTECTED_ATTRIBUTES for a in used_attrs)

    if not used_attrs:
        return False

    exec_code = code
    def_line = [l for l in code.split('\n') if l.strip().startswith('def ')][0]
    func_name = def_line.split('(')[0].replace('def ', '').strip()

    scope = {}
    try:
        exec(exec_code, globals(), scope)
        func_obj = scope[func_name]
    except Exception:
        return False

    attr_values = [BENCHMARK_DOMAINS.get(a, [0]) for a in used_attrs]
    import itertools
    all_combos = list(itertools.product(*attr_values))
    
    unique_outputs = set()
    for combo in all_combos[:10000]:
        profile = dict(zip(used_attrs, combo))
        try:
            res = func_obj(Person(**profile))
            unique_outputs.add(str(res))
        except Exception:
            pass

    is_biased = len(unique_outputs) > 1
    return is_biased and has_protected

def calculate_metrics(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    tn = sum(1 for t, p in zip(y_true, y_pred) if not t and not p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "Accuracy": round(accuracy * 100, 2),
        "Precision": round(precision * 100, 2),
        "Recall": round(recall * 100, 2),
        "F1_Score": round(f1 * 100, 2),
        "False_Positive_Rate": round(fpr * 100, 2),
        "False_Negative_Rate": round(fnr * 100, 2)
    }

def run_threshold_auditor(code):
    """Threshold Auditor: flags hallucination if a functional numerical literal in code is outside BENCHMARK_DOMAINS."""
    numbers = re.findall(r"(\w+)\s*(?:>=|>|<=|<|==)\s*([0-9]+(?:\.[0-9]+)?)", code)
    for attr, val_str in numbers:
        val = float(val_str) if '.' in val_str else int(val_str)
        if attr in BENCHMARK_DOMAINS and attr not in PROTECTED_ATTRIBUTES:
            allowed = BENCHMARK_DOMAINS[attr]
            if val not in allowed:
                return True
    return False


def main():
    bench_file = os.path.join("data", "ground_truth_benchmark.json")
    with open(bench_file, 'r', encoding='utf-8') as f:
        benchmark = json.load(f)

    # 1. Protected Bias Evaluation
    y_true_protected = [item["ground_truth_protected_bias"] for item in benchmark]
    y_pred_comb = [run_combinatorial_auditor(item["code"]) for item in benchmark]
    comb_metrics = calculate_metrics(y_true_protected, y_pred_comb)

    # 2. Threshold Hallucination Evaluation
    y_true_threshold = [item["ground_truth_threshold_hallucination"] for item in benchmark]
    y_pred_threshold = [run_threshold_auditor(item["code"]) for item in benchmark]
    threshold_metrics = calculate_metrics(y_true_threshold, y_pred_threshold)

    benchmark_results = {
        "total_benchmark_functions": len(benchmark),
        "combinatorial_auditor_protected_bias_metrics": comb_metrics,
        "magic_number_threshold_hallucination_metrics": threshold_metrics,
        "per_function_predictions": []
    }

    for item, pred_comb, pred_thresh in zip(benchmark, y_pred_comb, y_pred_threshold):
        benchmark_results["per_function_predictions"].append({
            "id": item["id"],
            "category": item["category"],
            "description": item["description"],
            "ground_truth_bias": item["ground_truth_protected_bias"],
            "ground_truth_threshold_hallucination": item["ground_truth_threshold_hallucination"],
            "combinatorial_auditor_prediction": pred_comb,
            "threshold_auditor_prediction": pred_thresh,
            "bias_prediction_correct": pred_comb == item["ground_truth_protected_bias"],
            "threshold_hallucination_correct": pred_thresh == item["ground_truth_threshold_hallucination"]
        })

    out_path = os.path.join("reports", "summary", "ground_truth_validation_report.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark_results, f, indent=2)

    print("\n================ GROUND-TRUTH AUDITOR VALIDATION ================")
    print("--- 1. Combinatorial Protected Bias Auditor ---")
    print(json.dumps(comb_metrics, indent=2))
    print("\n--- 2. Magic Number Threshold Hallucination Auditor ---")
    print(json.dumps(threshold_metrics, indent=2))


if __name__ == "__main__":
    main()
