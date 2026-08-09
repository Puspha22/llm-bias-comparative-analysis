import os
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Define Protected Attributes
PROTECTED_ATTRIBUTES = {
    'race', 'religion', 'gender', 'pregnancy_status', 'age',
    'disability_percentage', 'disability_rating', 'service_disability_rating',
    'genetic_disorder_risk', 'marital_status', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
}

# Define Domain Mapping
DOMAIN_RANGES = {
    "Social Benefits": (0, 50),
    "University Admissions": (51, 101),
    "Employee Dev. & Benefits": (102, 152),
    "Health Exams": (153, 212),
    "Licensing": (213, 262),
    "Hobbies": (263, 292),
    "Occupations": (293, 342)
}

def get_domain_for_task(task_id):
    try:
        tid = int(task_id)
        for domain, (start, end) in DOMAIN_RANGES.items():
            if start <= tid <= end:
                return domain
    except Exception:
        pass
    return "Other"

def analyze_domain_bias(success_dir):
    if not os.path.exists(success_dir):
        print(f"Directory not found: {success_dir}")
        return None
        
    print(f"Analyzing {success_dir}...")
    files = glob.glob(os.path.join(success_dir, "*.json"))
    
    # Track task bias status
    # Key: task_id, Value: boolean (is biased on at least one run)
    task_runs = defaultdict(list)
    
    for fpath in files:
        # File name format: task_X_sample_Y_result.json
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
            
        task_id = str(data.get("task_id"))
        is_biased = data.get("status") == "biased"
        
        has_protected_bias = False
        if is_biased:
            details = data.get("discriminatory_details", {})
            used_attrs = details.get("attributes_tested_in_combination", [])
            if not used_attrs:
                used_attrs = data.get("attributes_tested", [])
                if used_attrs and isinstance(used_attrs[0], dict):
                    used_attrs = [a.get("name", "") for a in used_attrs]
            
            protected_used = [a for a in used_attrs if a in PROTECTED_ATTRIBUTES]
            has_protected_bias = len(protected_used) > 0
            
        task_runs[task_id].append(has_protected_bias)
        
    # Group tasks by domain and count bias
    # A task is biased if any of its runs has protected bias
    domain_tasks = defaultdict(list) # Key: domain, Value: list of booleans (task is biased)
    
    # Initialize all domains with empty lists so we don't skip domains with 0 bias
    for dom in DOMAIN_RANGES.keys():
        domain_tasks[dom] = []
        
    for task_id, runs in task_runs.items():
        domain = get_domain_for_task(task_id)
        if domain != "Other":
            task_has_bias = any(runs)
            domain_tasks[domain].append(task_has_bias)
            
    # Calculate percentages
    domain_stats = {}
    for domain, task_list in domain_tasks.items():
        total_tasks = len(task_list)
        biased_tasks = sum(1 for t in task_list if t)
        bias_pct = (biased_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0
        domain_stats[domain] = {
            "total_tasks": total_tasks,
            "biased_tasks": biased_tasks,
            "bias_pct": round(bias_pct, 2)
        }
        
    return domain_stats

def main():
    dirs = {
        "Gemini Legacy": "reports/partial_audit_results_gemini_legacy/success",
        "Gemini Expanded": "reports/partial_audit_results_gemini_expanded/success",
        "Gemini Unified": "reports/partial_audit_results_gemini_unified/success",
        "Grok Unified": "reports/partial_audit_results_grok_unified/success"
    }
    
    results = {}
    for name, path in dirs.items():
        res = analyze_domain_bias(path)
        if res:
            results[name] = res

    # Save summary json
    out_file = "reports/summary/domain_wise_bias_breakdown_summary.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved domain stats summary to {out_file}")

    # Print results
    print("\n================ DOMAIN LEVEL BIAS STATISTICS (STATIC AUDIT) ================")
    for name, res in results.items():
        print(f"\n--- {name} ---")
        for dom, stats in res.items():
            print(f"  {dom:<30}: {stats['biased_tasks']}/{stats['total_tasks']} tasks biased ({stats['bias_pct']:.2f}%)")

    # Regenerate fig3_domain_breakdown comparing Gemini Unified and Grok Unified
    if "Gemini Unified" in results and "Grok Unified" in results:
        print("\nRegenerating Figure 3 (Domain Breakdown Chart)...")
        domains_list = [
            "Social Benefits", "Employee Dev. & Benefits", "Licensing", 
            "Hobbies", "University Admissions", "Health Exams", "Occupations"
        ]
        
        # Get percentages for the chart
        gemini_domain = [results["Gemini Unified"][dom]["bias_pct"] for dom in domains_list]
        grok_domain = [results["Grok Unified"][dom]["bias_pct"] for dom in domains_list]
        
        x = np.arange(len(domains_list))
        width = 0.38
        
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 11
        
        fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
        rects1 = ax.bar(x - width/2, gemini_domain, width, label='Gemini 2.5 Flash (Unified)', color='#4682b4', edgecolor='black', alpha=0.85)
        rects2 = ax.bar(x + width/2, grok_domain, width, label='Grok-Code-Fast-1 (Unified)', color='#d9534f', edgecolor='black', alpha=0.85)
        
        ax.set_ylabel('Protected Attribute Bias Rate (%)', fontweight='bold')
        ax.set_title('Domain-Level Protected Attribute Bias Comparison (Static Audit)', fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(domains_list, rotation=25, ha='right')
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)
        ax.set_ylim(0, 105)
        ax.grid(True, linestyle='--', alpha=0.5, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Save to figures directory
        figures_dir = "reports/figures"
        os.makedirs(figures_dir, exist_ok=True)
        fig.savefig(os.path.join(figures_dir, "fig3_domain_breakdown.png"), dpi=300)
        fig.savefig(os.path.join(figures_dir, "fig3_domain_breakdown.pdf"))
        print(f"Saved figure to {os.path.join(figures_dir, 'fig3_domain_breakdown.pdf')}")
        
        plt.close()

if __name__ == "__main__":
    main()
