import ijson
import json
import os

PROTECTED_ATTRIBUTES = [
    'age', 'gender', 'race', 'religion', 'disability_rating', 
    'pregnancy_status', 'marital_status', 'mental_health_history'
]

def extract_protected_bias(input_file, output_file, json_path):
    print(f"Extracting protected bias instances from {input_file}...")
    extracted_data = []
    try:
        with open(input_file, 'rb') as f:
            for entry in ijson.items(f, json_path):
                if entry.get("status") == "biased":
                    details = entry.get("discriminatory_details", {})
                    used_attrs = details.get("attributes_tested_in_combination", [])
                    
                    # Check if any protected attribute is in the biased combination
                    if any(attr in PROTECTED_ATTRIBUTES for attr in used_attrs):
                        extracted_data.append(entry)
                        
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    print(f"Found {len(extracted_data)} protected bias instances. Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2)
    print("Done.\n")

if __name__ == "__main__":
    # Extract for Gemini
    gemini_in = "reports/audit_report_unified_new.json"
    gemini_out = "reports/protected_bias_audit_gemini.json"
    extract_protected_bias(gemini_in, gemini_out, "item")
    
    # Extract for Grok
    grok_in = "reports/audit_report_grok.json"
    grok_out = "reports/protected_bias_audit_grok.json"
    extract_protected_bias(grok_in, grok_out, "item")
