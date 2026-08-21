import os, sys, json
from collections import defaultdict
from scipy.stats import chi2 as chi2_dist

# Support running directly or from project root
sys.path.append(os.path.dirname(__file__))
try:
    from compute_rigorous_metrics import analyze_dir
except ImportError:
    from src.statistical_analysis.compute_rigorous_metrics import analyze_dir

def main():
    gemini_dir = os.path.join("reports", "partial_audit_results_gemini_unified")
    grok_dir = os.path.join("reports", "partial_audit_results_grok_unified")

    if not os.path.exists(gemini_dir) or not os.path.exists(grok_dir):
        print("Missing partial audit directories.")
        return

    gemini_res = analyze_dir(gemini_dir)
    grok_res = analyze_dir(grok_dir)

    if not gemini_res or not grok_res:
        print("Failed to analyze audit directories.")
        return

    # =========================================================================
    # 1. FUNCTION-LEVEL MCNEMAR TEST (N ~ 1,711 Paired Functions)
    # =========================================================================
    common_func_keys = set(gemini_res["function_results"].keys()).intersection(set(grok_res["function_results"].keys()))
    
    b_func_grok_only = 0
    c_func_gemini_only = 0
    both_func_biased = 0
    neither_func_biased = 0

    for k in common_func_keys:
        v1 = gemini_res["function_results"][k]["biased"]
        v2 = grok_res["function_results"][k]["biased"]
        if not v1 and v2:
            b_func_grok_only += 1
        elif v1 and not v2:
            c_func_gemini_only += 1
        elif v1 and v2:
            both_func_biased += 1
        else:
            neither_func_biased += 1

    total_func_pairs = len(common_func_keys)
    chi2_func = (abs(b_func_grok_only - c_func_gemini_only) - 1)**2 / (b_func_grok_only + c_func_gemini_only) if (b_func_grok_only + c_func_gemini_only) > 0 else 0.0
    p_val_func = float(1.0 - chi2_dist.cdf(chi2_func, df=1))

    # =========================================================================
    # 2. PROMPT-LEVEL MCNEMAR TEST (N = 343 Paired Tasks / Prompts)
    # =========================================================================
    # Group runs by task_id: a prompt is flagged if >=1 generated sample is biased
    gemini_task_runs = defaultdict(list)
    grok_task_runs = defaultdict(list)

    for (tid, sidx), v in gemini_res["function_results"].items():
        gemini_task_runs[tid].append(v["biased"])

    for (tid, sidx), v in grok_res["function_results"].items():
        grok_task_runs[tid].append(v["biased"])

    common_tasks = sorted(list(set(gemini_task_runs.keys()).intersection(set(grok_task_runs.keys()))), key=lambda x: int(x) if x.isdigit() else x)

    b_prompt_grok_only = 0
    c_prompt_gemini_only = 0
    both_prompt_biased = 0
    neither_prompt_biased = 0

    for tid in common_tasks:
        gemini_prompt_biased = any(gemini_task_runs[tid])
        grok_prompt_biased = any(grok_task_runs[tid])

        if not gemini_prompt_biased and grok_prompt_biased:
            b_prompt_grok_only += 1
        elif gemini_prompt_biased and not grok_prompt_biased:
            c_prompt_gemini_only += 1
        elif gemini_prompt_biased and grok_prompt_biased:
            both_prompt_biased += 1
        else:
            neither_prompt_biased += 1

    total_prompt_pairs = len(common_tasks)
    disc_prompt_total = b_prompt_grok_only + c_prompt_gemini_only
    chi2_prompt = (abs(b_prompt_grok_only - c_prompt_gemini_only) - 1)**2 / disc_prompt_total if disc_prompt_total > 0 else 0.0
    p_val_prompt = float(1.0 - chi2_dist.cdf(chi2_prompt, df=1))

    mcnemar_results = {
        "function_level_test": {
            "description": "Unclustered paired test across individual function generations",
            "common_pairs_evaluated": total_func_pairs,
            "b_grok_only_biased": b_func_grok_only,
            "c_gemini_only_biased": c_func_gemini_only,
            "both_biased": both_func_biased,
            "neither_biased": neither_func_biased,
            "chi2_statistic": round(float(chi2_func), 4),
            "p_value": float(p_val_func),
            "statistically_significant": p_val_func < 0.05
        },
        "prompt_level_test": {
            "description": "Cluster-adjusted paired test across 343 base prompts (task flagged if >=1 generation exhibits bias)",
            "common_prompts_evaluated": total_prompt_pairs,
            "gemini_total_biased_prompts": both_prompt_biased + c_prompt_gemini_only,
            "grok_total_biased_prompts": both_prompt_biased + b_prompt_grok_only,
            "both_biased_prompts (a)": both_prompt_biased,
            "b_grok_only_biased_prompts (b)": b_prompt_grok_only,
            "c_gemini_only_biased_prompts (c)": c_prompt_gemini_only,
            "neither_biased_prompts (d)": neither_prompt_biased,
            "chi2_statistic": round(float(chi2_prompt), 4),
            "p_value": float(p_val_prompt),
            "statistically_significant": p_val_prompt < 0.05
        }
    }

    out_dir = os.path.join("reports", "summary")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "mcnemar_significance_test_results.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(mcnemar_results, f, indent=2)

    print("\n================ MCNEMAR TEST RESULTS (GEMINI UNIFIED VS GROK UNIFIED) ================")
    print(json.dumps(mcnemar_results, indent=2))

if __name__ == "__main__":
    main()

