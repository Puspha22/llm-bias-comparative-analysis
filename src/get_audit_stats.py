import os
import json
import glob
import statistics

PARTIAL_DIR = os.path.join("reports", "partial_audit_results")
SUCCESS_DIR = os.path.join(PARTIAL_DIR, "success")
FAILED_DIR = os.path.join(PARTIAL_DIR, "failed")

def main():
    # Success Count
    success_files = glob.glob(os.path.join(SUCCESS_DIR, "*.json"))
    success_count = len(success_files)
    
    # Failed Stats
    failed_files = glob.glob(os.path.join(FAILED_DIR, "*.json"))
    failed_count = len(failed_files)
    
    combo_counts = []
    for fpath in failed_files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                # Ensure we handle potentially missing keys safely, though our schema warrants it
                count = data.get("total_combinations", 0)
                if count > 0:
                    combo_counts.append(count)
        except:
            pass
            
    print(f"--- Audit Statistics ---")
    print(f"Success (Processed): {success_count}")
    print(f"Failed (Overlimit) : {failed_count}")
    print(f"Total Audited      : {success_count + failed_count}")
    
    if combo_counts:
        print(f"\n--- Overlimit Stats (Failed) ---")
        print(f"Highest Combinations: {max(combo_counts):,}")
        print(f"Lowest Combinations : {min(combo_counts):,}")
        print(f"Average Combinations: {statistics.mean(combo_counts):,.2f}")
    else:
        print("\nNo failed audits found.")

if __name__ == "__main__":
    main()
