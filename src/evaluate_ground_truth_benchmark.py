import os
import json
import re
import subprocess
from collections import defaultdict

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
    return domains

BENCHMARK_DOMAINS = load_master_domains()

def prepare_benchmark_inputs(benchmark):
    gen_dir = os.path.join("data", "generated_functions_benchmark")
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir)

    for item in benchmark:
        filepath = os.path.join(gen_dir, f"task_{item['id']}.json")
        data = {
            "task_id": item["id"],
            "prompt": item["code"],
            "generated_functions": [item["code"]],
            "category": item["category"],
            "description": item["description"],
            "ground_truth_protected_bias": item["ground_truth_protected_bias"],
            "ground_truth_threshold_hallucination": item["ground_truth_threshold_hallucination"]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    return gen_dir

def run_production_auditor():
    gen_dir = os.path.join("data", "generated_functions_benchmark")
    partial_dir = os.path.join("reports", "partial_audit_results_benchmark")
    audit_report = os.path.join("reports", "audit_report_benchmark.json")

    cmd = [
        "python", "src/run_audit_dynamic.py",
        "--generated-dir", gen_dir,
        "--partial-dir", partial_dir,
        "--audit-report", audit_report
    ]
    subprocess.run(cmd, check=True)
    return partial_dir

def parse_benchmark_predictions(partial_dir, benchmark):
    predictions = {}
    success_dir = os.path.join(partial_dir, "success")
    
    for item in benchmark:
        task_id = item["id"]
        result_file = os.path.join(success_dir, f"task_{task_id}_sample_0_result.json")
        if not os.path.exists(result_file):
            predictions[task_id] = False
            continue

        with open(result_file, 'r', encoding='utf-8') as f:
            res = json.load(f)

        if res and res.get("status") == "biased":
            details = res.get("discriminatory_details", {})
            tested_attrs = details.get("attributes_tested_in_combination", [])
            prot_attrs = [a for a in tested_attrs if a in PROTECTED_ATTRIBUTES]
            if not prot_attrs:
                predictions[task_id] = False
                continue

            outcomes = details.get("outcomes", {})
            non_prot_groups = defaultdict(set)
            for key_str, outcome in outcomes.items():
                pairs = dict(p.split('=') for p in key_str.split(', '))
                non_prot_key = tuple(sorted((k, v) for k, v in pairs.items() if k not in PROTECTED_ATTRIBUTES))
                non_prot_groups[non_prot_key].add(str(outcome))

            is_causal_bias = any(len(out_set) > 1 for out_set in non_prot_groups.values())
            predictions[task_id] = is_causal_bias
        else:
            predictions[task_id] = False

    return predictions

def run_threshold_auditor(code):
    numbers = re.findall(r"(\w+)\s*(?:>=|>|<=|<|==)\s*([0-9]+(?:\.[0-9]+)?)", code)
    for attr, val_str in numbers:
        val = float(val_str) if '.' in val_str else int(val_str)
        if attr in BENCHMARK_DOMAINS and attr not in PROTECTED_ATTRIBUTES:
            allowed = BENCHMARK_DOMAINS[attr]
            if val not in allowed:
                return True
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

def main():
    bench_file = os.path.join("data", "ground_truth_benchmark.json")
    with open(bench_file, 'r', encoding='utf-8') as f:
        benchmark = json.load(f)

    # 1. Prepare benchmark input files
    prepare_benchmark_inputs(benchmark)

    # 2. Run production auditor engine
    partial_dir = run_production_auditor()

    # 3. Parse predictions & calculate protected bias metrics
    predictions = parse_benchmark_predictions(partial_dir, benchmark)
    y_true_protected = [item["ground_truth_protected_bias"] for item in benchmark]
    y_pred_comb = [predictions.get(item["id"], False) for item in benchmark]
    comb_metrics = calculate_metrics(y_true_protected, y_pred_comb)

    # 4. Threshold Hallucination Evaluation
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
