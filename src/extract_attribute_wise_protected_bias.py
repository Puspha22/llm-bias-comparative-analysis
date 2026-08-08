import os
import glob
import json
import sys
from collections import Counter

# Define the 15 protected attributes
PROTECTED_ATTRIBUTES = {
    'race', 'religion', 'gender', 'pregnancy_status', 'age',
    'disability_percentage', 'disability_rating', 'service_disability_rating',
    'genetic_disorder_risk', 'marital_status', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
}

def analyze_directory(success_dir):
    if not os.path.exists(success_dir):
        print(f"Directory not found: {success_dir}")
        return Counter(), 0, 0
        
    print(f"Scanning directory: {success_dir}")
    files = glob.glob(os.path.join(success_dir, "*.json"))
    total_files = len(files)
    print(f"Found {total_files} files to audit.")
    
    total_biased = 0
    protected_biased = 0  # Count of unique functions with protected attribute bias
    attribute_counts = Counter()
    
    for idx, fpath in enumerate(files):
        # Print progress log every 100 files
        if (idx + 1) % 100 == 0 or (idx + 1) == total_files:
            sys.stdout.write(f"\r  Progress: Processed {idx + 1}/{total_files} files...")
            sys.stdout.flush()

        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
            
        if data.get("status") == "biased":
            total_biased += 1
            
            details = data.get("discriminatory_details", {})
            used_attrs = details.get("attributes_tested_in_combination", [])
            if not used_attrs:
                used_attrs = data.get("attributes_tested", [])
                if used_attrs and isinstance(used_attrs[0], dict):
                    used_attrs = [a.get("name", "") for a in used_attrs]
            
            protected_used = [a for a in used_attrs if a in PROTECTED_ATTRIBUTES]
            
            if protected_used:
                protected_biased += 1
            
            for attr in protected_used:
                attribute_counts[attr] += 1
                
    # Clear the progress line and print final stats
    print("\n\n--- Results ---")
    print(f"Total Biased Functions (Any Bias): {total_biased}")
    print(f"Functions with Protected Bias    : {protected_biased}")  # Output the unique function count
    print("Bias Counts per Attribute:")
    print(f"{'Attribute':<30} | {'Count':<10}")
    print("-" * 45)
    for attr, count in attribute_counts.most_common():
        print(f"{attr:<30} | {count:<10}")
    print("=" * 45)
    
    return attribute_counts, protected_biased, total_biased

def main():
    conditions = {
        "Gemini Legacy": "reports/partial_audit_results_legacy/success",
        "Gemini Expanded": "reports/partial_audit_results_expanded/success",
        "Gemini Unified": "reports/partial_audit_results_new/success",
        "Grok Unified": "reports/partial_audit_results_grok/success"
    }
    
    results = {}
    for name, path in conditions.items():
        print(f"\n=== Running Audit Stats for {name} ===")
        counts, protected_b, total_b = analyze_directory(path)
        results[name] = counts

    # Keep original output saving format to reports/summary/all_protected_attribute_counts.json
    # mapping Gemini Unified (Gemini_2.5_Flash) and Grok Unified (Grok_Code_Fast)
    summary = {}
    gemini_counts = results.get("Gemini Unified", Counter())
    grok_counts = results.get("Grok Unified", Counter())
    
    for attr in sorted(PROTECTED_ATTRIBUTES):
        summary[attr] = {
            "Gemini_2.5_Flash": gemini_counts[attr],
            "Grok_Code_Fast": grok_counts[attr]
        }

    out_file = os.path.join("reports", "summary", "all_protected_attribute_counts.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print(f"\nSaved master streaming summary to {out_file}")

if __name__ == "__main__":
    main()
