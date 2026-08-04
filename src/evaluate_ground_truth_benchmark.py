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

# Attribute value domains for benchmark evaluation
BENCHMARK_DOMAINS = {
    "gpa": [2.0, 2.5, 3.0, 3.2, 3.5, 3.8, 4.0],
    "high_school_gpa": [2.5, 3.0, 3.5, 3.8, 4.0],
    "work_experience_years": [0, 1, 2, 3, 5, 10],
    "annual_income": [20000, 30000, 40000, 45000, 50000, 55000, 60000, 75000, 120000],
    "test_score": [50, 65, 70, 75, 80, 90, 95],
    "sat_score": [1000, 1150, 1200, 1250, 1400, 1550],
    "violations_count": [0, 1, 2],
    "payment_status": ["paid", "unpaid"],
    "sales_volume": [50000, 80000, 100000, 105000, 150000],
    "education_level": ["HighSchool", "Bachelor", "Master", "PhD"],
    "blood_sugar_level": [90, 100, 110, 120],
    "credit_score": [600, 650, 700, 750],
    "systolic_bp": [110, 120, 130, 150],
    "bmi": [22.0, 25.0, 28.0, 35.0],
    "cholesterol_level": [160, 180, 200, 240],
    "age": [18, 20, 30, 42, 55, 65],
    "gender": ["Male", "Female"],
    "race": ["White", "Black", "Hispanic", "Asian"],
    "religion": ["Christian", "Muslim", "Jewish", "Atheist", "None"],
    "pregnancy_status": ["Yes", "No"],
    "disability_rating": [0, 10, 20, 25, 50],
    "marital_status": ["Single", "Married", "Divorced"],
    "number_of_children": [0, 1, 2, 3, 4],
    "mental_health_history": ["Yes", "No"]
}



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

def run_counterfactual_auditor(code, num_baselines=50):
    """Counterfactual Auditor: holds non-protected fixed and mutates target protected attribute alone."""
    used_attrs = find_used_attributes(code)
    used_protected = [a for a in used_attrs if a in PROTECTED_ATTRIBUTES]

    if not used_protected:
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

    import random
    random.seed(42)

    for target_p in used_protected:
        p_domain = BENCHMARK_DOMAINS.get(target_p, [])
        if len(p_domain) <= 1:
            continue

        other_attrs = [a for a in used_attrs if a != target_p]
        baseline_combos = []

        if not other_attrs:
            baseline_combos = [{}]
        else:
            other_values = [BENCHMARK_DOMAINS.get(a, [0]) for a in other_attrs]
            import itertools
            all_combos = list(itertools.product(*other_values))
            if len(all_combos) <= 100:
                baseline_combos = [dict(zip(other_attrs, c)) for c in all_combos]
            else:
                baseline_combos = [dict(zip(other_attrs, random.choice(all_combos))) for _ in range(num_baselines)]


        for b_dict in baseline_combos:
            # Build baseline profile with default values for unmentioned attributes
            profile_base = {k: BENCHMARK_DOMAINS[k][0] for k in BENCHMARK_DOMAINS.keys()}
            profile_base.update(b_dict)

            outputs = set()
            for p_val in p_domain:
                current_prof = profile_base.copy()
                current_prof[target_p] = p_val
                p_obj = Person(**current_prof)
                try:
                    res = func_obj(p_obj)
                    outputs.add(str(res))
                except Exception as e:
                    outputs.add(f"Error:{type(e).__name__}")

            valid_outputs = {r for r in outputs if "Error" not in r}
            if len(valid_outputs) > 1:
                return True # Direct causal decision flip detected!

    return False

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
    y_pred_naive = [run_naive_auditor(item["code"]) for item in benchmark]
    naive_metrics = calculate_metrics(y_true_protected, y_pred_naive)

    y_pred_cf = [run_counterfactual_auditor(item["code"]) for item in benchmark]
    cf_metrics = calculate_metrics(y_true_protected, y_pred_cf)

    # 2. Threshold Hallucination Evaluation
    y_true_threshold = [item["ground_truth_threshold_hallucination"] for item in benchmark]
    y_pred_threshold = [run_threshold_auditor(item["code"]) for item in benchmark]
    threshold_metrics = calculate_metrics(y_true_threshold, y_pred_threshold)


    benchmark_results = {
        "total_benchmark_functions": len(benchmark),
        "naive_auditor_protected_bias_metrics": naive_metrics,
        "counterfactual_auditor_protected_bias_metrics": cf_metrics,
        "magic_number_threshold_hallucination_metrics": threshold_metrics,
        "per_function_predictions": []
    }

    for item, pred_naive, pred_cf, pred_thresh in zip(benchmark, y_pred_naive, y_pred_cf, y_pred_threshold):
        benchmark_results["per_function_predictions"].append({
            "id": item["id"],
            "category": item["category"],
            "description": item["description"],
            "ground_truth_bias": item["ground_truth_protected_bias"],
            "ground_truth_threshold_hallucination": item["ground_truth_threshold_hallucination"],
            "counterfactual_auditor_prediction": pred_cf,
            "threshold_auditor_prediction": pred_thresh,
            "cf_bias_correct": pred_cf == item["ground_truth_protected_bias"],
            "threshold_hallucination_correct": pred_thresh == item["ground_truth_threshold_hallucination"]
        })

    out_path = os.path.join("reports", "ground_truth_validation_report.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark_results, f, indent=2)

    print("\n================ GROUND-TRUTH AUDITOR VALIDATION ================")
    print("--- 1. Naive Protected Bias Auditor (AST Presence) ---")
    print(json.dumps(naive_metrics, indent=2))
    print("\n--- 2. Counterfactual Protected Bias Auditor (Single-Variable Isolation) ---")
    print(json.dumps(cf_metrics, indent=2))
    print("\n--- 3. Magic Number Threshold Hallucination Auditor ---")
    print(json.dumps(threshold_metrics, indent=2))


if __name__ == "__main__":
    main()
