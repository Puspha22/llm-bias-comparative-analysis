import os
import json
import ijson
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

# Configuration
AUDIT_REPORT = os.path.join("reports", "audit_report_grok.json")
OUTPUT_IMG = os.path.join("reports", "figures", "protected_bias_chart_grok.png")

PROTECTED_ATTRIBUTES = {
    'race', 'religion', 'gender', 'pregnancy_status', 'age',
    'disability_percentage', 'disability_rating', 'service_disability_rating',
    'genetic_disorder_risk', 'marital_status', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
}

def main():
    print("--- Experiment 3: Protected Attribute Bias ---")
    
    if not os.path.exists(AUDIT_REPORT):
        print(f"Audit report not found: {AUDIT_REPORT}")
        return
        
    protected_counts = Counter()
    total_biased_count = 0

    print("Parsing immense JSON file streamingly... this may take a moment.")
    with open(AUDIT_REPORT, 'rb') as f:
        try:
            # ijson.items(f, 'item') yields each dictionary in a top-level JSON array
            for entry in ijson.items(f, 'item'):
                status = entry.get("status")
                if status == "biased":
                    total_biased_count += 1
                    details = entry.get("discriminatory_details", {})
                    used_attrs = details.get("attributes_tested_in_combination", [])
                    
                    for attr in used_attrs:
                        if attr in PROTECTED_ATTRIBUTES:
                            protected_counts[attr] += 1
        except Exception as e:
            print(f"Error during stream parsing: {e}")
            return
            
    print(f"Analyzed {total_biased_count} biased reports.")
    print(f"Found bias on protected attributes in {sum(protected_counts.values())} instances (overlap possible).")
    
    if not protected_counts:
        print("No protected attribute bias found.")
        return

    # Plotting
    df = pd.DataFrame(protected_counts.items(), columns=['Attribute', 'Count'])
    df = df.sort_values('Count', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.bar(df['Attribute'], df['Count'], color='#e74c3c')
    plt.title('Bias Frequency on Protected Attributes')
    plt.xlabel('Protected Attribute')
    plt.ylabel('Number of Biased Functions')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig(OUTPUT_IMG)
    print(f"Chart saved to {OUTPUT_IMG}")
    
    # Save JSON details
    with open("reports/feature_metrics/exp_protected_bias_results_grok.json", "w") as f:
        json.dump(dict(protected_counts), f, indent=2)
    print("Detailed JSON saved to reports/exp_protected_bias_results_grok.json")
    
    # Print Table
    print("\nBias Breakdown:")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
