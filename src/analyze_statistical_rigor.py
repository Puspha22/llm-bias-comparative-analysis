import os
import json
import numpy as np

# Mapping of task IDs to the 7 application domains
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
        t_num = int(task_id)
        for domain, (start_idx, end_idx) in DOMAIN_RANGES.items():
            if start_idx <= t_num <= end_idx:
                return domain
    except:
        pass
    return "Other"

def compute_bootstrap_ci(data_by_task, n_bootstraps=1000, ci=95, seed=42):
    """Clustered bootstrap resampling by prompt task."""
    np.random.seed(seed)
    task_ids = list(data_by_task.keys())
    n_tasks = len(task_ids)
    
    bootstrap_means = []
    for _ in range(n_bootstraps):
        sampled_tasks = np.random.choice(task_ids, size=n_tasks, replace=True)
        sampled_vals = [data_by_task[t] for t in sampled_tasks]
        bootstrap_means.append(np.mean(sampled_vals))
        
    lower_p = (100 - ci) / 2.0
    upper_p = 100 - lower_p
    
    mean_val = float(np.mean([data_by_task[t] for t in task_ids]))
    ci_lower = float(np.percentile(bootstrap_means, lower_p))
    ci_upper = float(np.percentile(bootstrap_means, upper_p))
    
    return {
        "mean_pct": round(mean_val * 100, 2),
        "ci_95_lower_pct": round(ci_lower * 100, 2),
        "ci_95_upper_pct": round(ci_upper * 100, 2)
    }

def mcnemar_test(b_gemini_task, b_grok_task):
    """Paired McNemar test comparing Gemini vs Grok task-level outcomes."""
    # Contingency table:
    # n00: both false, n01: gemini false & grok true, n10: gemini true & grok false, n11: both true
    n01 = 0
    n10 = 0
    
    common_tasks = set(b_gemini_task.keys()).intersection(set(b_grok_task.keys()))
    for t in common_tasks:
        g1 = b_gemini_task[t]
        g2 = b_grok_task[t]
        if not g1 and g2:
            n01 += 1
        elif g1 and not g2:
            n10 += 1
            
    b = n01
    c = n10
    if (b + c) > 0:
        chi2 = ((abs(b - c) - 1) ** 2) / (b + c)
        from scipy.stats import chi2 as chi2_dist
        p_val = float(1 - chi2_dist.cdf(chi2, df=1))
    else:
        chi2 = 0.0
        p_val = 1.0
        
    return {
        "b_grok_only": b,
        "c_gemini_only": c,
        "chi2_statistic": round(chi2, 4),
        "p_value": p_val,
        "statistically_significant": p_val < 0.05
    }

def main():
    os.makedirs("reports", exist_ok=True)
    
    # Load Counterfactual Results
    with open(os.path.join("reports", "counterfactual_audit_gemini.json"), 'r') as f:
        cf_gemini = json.load(f)
    with open(os.path.join("reports", "counterfactual_audit_grok.json"), 'r') as f:
        cf_grok = json.load(f)

    # Load Behavioral Inconsistency Results
    with open(os.path.join("reports", "behavioral_inconsistency_gemini.json"), 'r') as f:
        bi_gemini = json.load(f)
    with open(os.path.join("reports", "behavioral_inconsistency_grok.json"), 'r') as f:
        bi_grok = json.load(f)

    # Build Task-level binary flags for Counterfactual Protected Bias
    # Task is biased if any of its 5 samples has counterfactual protected bias
    cf_task_gemini = {}
    for item in cf_gemini.get("detailed_function_results", []):
        cf_task_gemini[str(item["task_id"])] = 1.0
    for t in range(343):
        if str(t) not in cf_task_gemini:
            cf_task_gemini[str(t)] = 0.0

    cf_task_grok = {}
    for item in cf_grok.get("detailed_function_results", []):
        cf_task_grok[str(item["task_id"])] = 1.0
    for t in range(343):
        if str(t) not in cf_task_grok:
            cf_task_grok[str(t)] = 0.0

    # Build Task-level binary flags for Behavioral Inconsistency
    bi_task_gemini = {}
    for item in bi_gemini.get("task_details", []):
        bi_task_gemini[str(item["task_id"])] = 1.0 if item["disagreement_category"] != "full_agreement" else 0.0

    bi_task_grok = {}
    for item in bi_grok.get("task_details", []):
        bi_task_grok[str(item["task_id"])] = 1.0 if item["disagreement_category"] != "full_agreement" else 0.0

    # Compute Clustered Bootstrap 95% Confidence Intervals
    cf_ci_gemini = compute_bootstrap_ci(cf_task_gemini)
    cf_ci_grok = compute_bootstrap_ci(cf_task_grok)

    bi_ci_gemini = compute_bootstrap_ci(bi_task_gemini)
    bi_ci_grok = compute_bootstrap_ci(bi_task_grok)

    # McNemar Paired Tests
    mcnemar_cf = mcnemar_test(cf_task_gemini, cf_task_grok)
    mcnemar_bi = mcnemar_test(bi_task_gemini, bi_task_grok)

    # Domain Breakdown
    domain_breakdown = {}
    for domain in DOMAIN_RANGES.keys():
        g_cf_domain = [v for t, v in cf_task_gemini.items() if get_domain_for_task(t) == domain]
        gr_cf_domain = [v for t, v in cf_task_grok.items() if get_domain_for_task(t) == domain]
        
        g_bi_domain = [v for t, v in bi_task_gemini.items() if get_domain_for_task(t) == domain]
        gr_bi_domain = [v for t, v in bi_task_grok.items() if get_domain_for_task(t) == domain]

        domain_breakdown[domain] = {
            "task_count": len(g_cf_domain),
            "counterfactual_protected_bias_pct": {
                "Gemini": round(np.mean(g_cf_domain) * 100, 2) if g_cf_domain else 0,
                "Grok": round(np.mean(gr_cf_domain) * 100, 2) if gr_cf_domain else 0
            },
            "behavioral_inconsistency_pct": {
                "Gemini": round(np.mean(g_bi_domain) * 100, 2) if g_bi_domain else 0,
                "Grok": round(np.mean(gr_bi_domain) * 100, 2) if gr_bi_domain else 0
            }
        }

    statistical_report = {
        "counterfactual_protected_bias_bootstrap_ci": {
            "Gemini_Unified": cf_ci_gemini,
            "Grok_Unified": cf_ci_grok
        },
        "behavioral_inconsistency_bootstrap_ci": {
            "Gemini_Unified": bi_ci_gemini,
            "Grok_Unified": bi_ci_grok
        },
        "paired_mcnemar_tests": {
            "counterfactual_bias_gemini_vs_grok": mcnemar_cf,
            "behavioral_inconsistency_gemini_vs_grok": mcnemar_bi
        },
        "domain_level_breakdown": domain_breakdown
    }

    out_file = os.path.join("reports", "statistical_rigor_and_domain_analysis.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(statistical_report, f, indent=2)

    print("\n================ STATISTICAL RIGOR & DOMAIN ANALYSIS ================")
    print(json.dumps(statistical_report, indent=2))

if __name__ == "__main__":
    main()
