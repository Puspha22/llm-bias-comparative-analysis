import os, json
from scipy.stats import chi2 as chi2_dist

def main():
    verified_file = os.path.join("reports", "summary", "verified_counterfactual_audit_summary.json")
    if not os.path.exists(verified_file):
        print("Missing verified summary file.")
        return

    # Load function results from task-275 script output
    # Let's run a quick paired lookup between Gemini Unified and Grok Unified results
    from compute_rigorous_metrics import analyze_dir

    gemini_res = analyze_dir(os.path.join("reports", "partial_audit_results_gemini_unified"))
    grok_res = analyze_dir(os.path.join("reports", "partial_audit_results_grok_unified"))

    common_keys = set(gemini_res["function_results"].keys()).intersection(set(grok_res["function_results"].keys()))
    
    b_grok_only = 0 # Gemini False, Grok True
    c_gemini_only = 0 # Gemini True, Grok False
    both_true = 0
    both_false = 0

    for k in common_keys:
        v1 = gemini_res["function_results"][k]["biased"]
        v2 = grok_res["function_results"][k]["biased"]
        if not v1 and v2:
            b_grok_only += 1
        elif v1 and not v2:
            c_gemini_only += 1
        elif v1 and v2:
            both_true += 1
        else:
            both_false += 1

    total_pairs = len(common_keys)
    chi2_stat = (abs(b_grok_only - c_gemini_only) - 1)**2 / (b_grok_only + c_gemini_only)
    p_val = float(1.0 - chi2_dist.cdf(chi2_stat, df=1))

    mcnemar_results = {
        "common_pairs_evaluated": total_pairs,
        "b_grok_only_biased": b_grok_only,
        "c_gemini_only_biased": c_gemini_only,
        "both_biased": both_true,
        "neither_biased": both_false,
        "chi2_statistic": round(float(chi2_stat), 4),
        "p_value": float(p_val),
        "statistically_significant": p_val < 0.05
    }

    out_path = os.path.join("reports", "summary", "verified_mcnemar_test_results.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(mcnemar_results, f, indent=2)

    print("\n================ VERIFIED MCNEMAR TEST (GEMINI UNIFIED VS GROK UNIFIED) ================")
    print(json.dumps(mcnemar_results, indent=2))

if __name__ == "__main__":
    main()
