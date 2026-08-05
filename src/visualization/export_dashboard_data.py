import os
import json
from collections import Counter, defaultdict

PARTIAL_DIR = os.path.join("reports", "partial_audit_results")
OUTPUT_FILE = os.path.join("reports", "feature_metrics", "dashboard_data.json")
PROTECTED_ATTRIBUTES = {
    "race", "gender", "religion", "age", "marital_status", 
    "disability_rating", "pregnancy_status", "sexual_orientation",
    "nationality", "citizenship", "residency_status"
}

import glob

def main():
    if not os.path.exists(PARTIAL_DIR):
        print("Partial directory not found.")
        return

    print("Aggregating dashboard data...")
    
    total_scanned = 0
    total_biased = 0
    
    biased_functions_list = []
    
    attr_counts = Counter()
    protected_counts = Counter()
    
    files = glob.glob(os.path.join(PARTIAL_DIR, "**", "*.json"), recursive=True)
    total_scanned = len(files)
    
    for filepath in files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            status = data.get("status", "unknown")
            used = []
            
            # Extract attributes based on new structure
            # Clean/Skipped: in "attributes_tested" list of objects
            # Biased: in "discriminatory_details" -> "attributes_tested_in_combination"
            
            if status == "biased":
                total_biased += 1
                details = data.get("discriminatory_details", {})
                used = details.get("attributes_tested_in_combination", [])
            elif "attributes_tested" in data:
                 # Success/Skipped format
                 used = [item["name"] for item in data["attributes_tested"]]
            
            # Count biased attributes only
            if status == "biased":
                for attr in used:
                    attr_counts[attr] += 1
                    if attr in PROTECTED_ATTRIBUTES:
                        protected_counts[attr] += 1
            
            # Add to list for table
            func_name = data.get("function_name", data.get("function", "unknown"))
            biased_functions_list.append({
                "id": data.get("task_id"),
                "index": data.get("function_sample_index", data.get("index")),
                "name": func_name,
                "status": status,
                "attributes": used,
                "protected_triggers": [a for a in used if a in PROTECTED_ATTRIBUTES]
            })
        except Exception as e: 
            # print(e) 
            continue
        
    # Summarize Top 20
    top_20 = [{"name": k, "count": v} for k, v in attr_counts.most_common(20)]
    protected_stats = [{"name": k, "count": v} for k, v in protected_counts.most_common()]
    
    dashboard_data = {
        "summary": {
            "total_scanned": total_scanned,
            "total_biased": total_biased,
            "bias_rate": round((total_biased / total_scanned) * 100, 2) if total_scanned else 0
        },
        "top_attributes": top_20,
        "protected_attributes": protected_stats,
        "functions": biased_functions_list
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
        
    print(f"Dashboard data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
