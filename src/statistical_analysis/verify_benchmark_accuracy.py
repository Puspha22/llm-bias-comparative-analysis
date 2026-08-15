import os
import json
import re

PROTECTED_ATTRIBUTES = {
    'age', 'gender', 'race', 'religion', 'disability_rating', 
    'pregnancy_status', 'marital_status', 'mental_health_history',
    'service_disability_rating', 'genetic_disorder_risk', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
}

PARTIAL_DIR = r"d:\Assignment\Fall-2025\Thesis\llm-bias-thesis\reports\partial_audit_results_test\success"
PROMPTS_FILE = r"d:\Assignment\Fall-2025\Thesis\llm-bias-thesis\data\dataset\prompts_unified_new.jsonl"
GROUND_TRUTH_FILE = r"d:\Assignment\Fall-2025\Thesis\llm-bias-thesis\data\dataset\synthetic_benchmark_ground_truth.json"

# 1. Build prompt allowed ranges map for unprompted threshold detection
prompt_allowed_ranges = {}
with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        prompt = data.get("prompt", "")
        for p_line in prompt.split('\n'):
            m = re.search(r"#\s*([\w_]+)\s*\[(.*?)\]", p_line)
            if m:
                k = m.group(1).strip()
                vals = [v.strip().strip("'\"") for v in m.group(2).split(',')]
                if k not in prompt_allowed_ranges:
                    prompt_allowed_ranges[k] = set()
                prompt_allowed_ranges[k].update(vals)

# 2. Load ground truth JSON file
with open(GROUND_TRUTH_FILE, 'r', encoding='utf-8') as f:
    gt_list = json.load(f)

GROUND_TRUTH = {
    item["task_id"]: {
        "non_constant": item["ground_truth"]["non_constant"],
        "sensitive_bias": item["ground_truth"]["sensitive_bias"],
        "threshold_injected": item["ground_truth"]["threshold_injected"],
        "desc": item["description"]
    }
    for item in gt_list
}

def evaluate_metrics(y_true, y_pred):
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt and yp)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and yp)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt and not yp)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and not yp)
    
    accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return accuracy, precision, recall, f1

# Read actual auditor results
auditor_results = {}
for fname in os.listdir(PARTIAL_DIR):
    if not fname.endswith('.json'): continue
    fpath = os.path.join(PARTIAL_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tid = str(data.get("task_id"))
    status = data.get("status")
    code = data.get("code", "")
    attrs = data.get("attributes_tested", [])
    if attrs and isinstance(attrs[0], dict):
        attr_names = [a.get("name") for a in attrs]
    else:
        attr_names = attrs
        
    is_non_constant = (status == "biased")
    
    # Sensitive bias check
    tested_sensitive = [a for a in attr_names if a in PROTECTED_ATTRIBUTES]
    is_sensitive_biased = is_non_constant and len(tested_sensitive) > 0
    
    # Unprompted threshold check
    is_threshold_injected = False
    for attr in attr_names:
        allowed = prompt_allowed_ranges.get(attr, set())
        pattern = r"self\." + re.escape(attr) + r"\s*(?:>=|<=|==|>|<)\s*([0-9]+(?:\.[0-9]+)?)"
        matches = re.findall(pattern, code)
        for m in matches:
            val_int_str = str(int(float(m))) if '.' in m and m.endswith('.0') else m
            val_float_str = str(float(m))
            if m not in allowed and val_int_str not in allowed and val_float_str not in allowed:
                is_threshold_injected = True
                break
                
    auditor_results[tid] = {
        "non_constant": is_non_constant,
        "sensitive_bias": is_sensitive_biased,
        "threshold_injected": is_threshold_injected,
        "code": code
    }

print("=" * 75)
print("  SYNTHETIC VALIDATION BENCHMARK EVALUATION RESULTS")
print("=" * 75)
print(f"{'Task':<6} | {'Non-Const':<10} | {'Sens Bias':<10} | {'Thresh Inj':<10} | {'Match?':<8} | Description")
print("-" * 75)

all_match = True
for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x)):
    gt = GROUND_TRUTH[tid]
    pred = auditor_results.get(tid, {})
    
    nc_match = gt["non_constant"] == pred.get("non_constant")
    sb_match = gt["sensitive_bias"] == pred.get("sensitive_bias")
    ti_match = gt["threshold_injected"] == pred.get("threshold_injected")
    
    task_ok = nc_match and sb_match and ti_match
    if not task_ok: all_match = False
    
    status_str = "PASS" if task_ok else "FAIL"
    print(f"Task {tid:<2} | {str(pred.get('non_constant')):<10} | {str(pred.get('sensitive_bias')):<10} | {str(pred.get('threshold_injected')):<10} | {status_str:<8} | {gt['desc']}")

print("\n" + "=" * 75)
print("  FORMAL AUDITING FRAMEWORK PERFORMANCE METRICS")
print("=" * 75)

# Dimension 1: Non-Constancy (Output Variance)
yt_nc = [GROUND_TRUTH[tid]["non_constant"] for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x))]
yp_nc = [auditor_results[tid]["non_constant"] for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x))]
acc_nc, prec_nc, rec_nc, f1_nc = evaluate_metrics(yt_nc, yp_nc)

print(f"1. Output Variance Detection (Non-Constancy):")
print(f"   Accuracy : {acc_nc * 100:.2f}%")
print(f"   Precision: {prec_nc * 100:.2f}%")
print(f"   Recall   : {rec_nc * 100:.2f}%")
print(f"   F1-Score : {f1_nc:.4f}")

# Dimension 2: Sensitive Demographic Bias
yt_sb = [GROUND_TRUTH[tid]["sensitive_bias"] for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x))]
yp_sb = [auditor_results[tid]["sensitive_bias"] for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x))]
acc_sb, prec_sb, rec_sb, f1_sb = evaluate_metrics(yt_sb, yp_sb)

print(f"\n2. Sensitive Demographic Bias Detection:")
print(f"   Accuracy : {acc_sb * 100:.2f}%")
print(f"   Precision: {prec_sb * 100:.2f}%")
print(f"   Recall   : {rec_sb * 100:.2f}%")
print(f"   F1-Score : {f1_sb:.4f}")

# Dimension 3: Unprompted Threshold Injections
yt_ti = [GROUND_TRUTH[tid]["threshold_injected"] for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x))]
yp_ti = [auditor_results[tid]["threshold_injected"] for tid in sorted(GROUND_TRUTH.keys(), key=lambda x: int(x))]
acc_ti, prec_ti, rec_ti, f1_ti = evaluate_metrics(yt_ti, yp_ti)

print(f"\n3. Unprompted Threshold Detection:")
print(f"   Accuracy : {acc_ti * 100:.2f}%")
print(f"   Precision: {prec_ti * 100:.2f}%")
print(f"   Recall   : {rec_ti * 100:.2f}%")
print(f"   F1-Score : {f1_ti:.4f}")

print("\n" + "=" * 75)
print(f"OVERALL BENCHMARK VALIDATION: {'100% PERFECT VERIFICATION (0 ERRORS)' if all_match else 'FAILURES DETECTED'}")
print("=" * 75)
