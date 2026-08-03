import os
import json
import glob
from run_audit_dynamic import audit_function, build_profile_map, PARTIAL_DIR, GENERATED_DIR

SUCCESS_DIR = os.path.join(PARTIAL_DIR, "success")
FAILED_DIR = os.path.join(PARTIAL_DIR, "failed")

def main():
    print("Loading remaining failed audits for sampling...")
    failed_files = glob.glob(os.path.join(FAILED_DIR, "*.json"))
    
    if not failed_files:
        print("No failed audits found. Nothing to sample!")
        return

    # Load metadata
    tasks_to_retry = []
    for fpath in failed_files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                combos = data.get("total_combinations", 0)
                func_name = data.get("function_name")
                
                # We need the prompt to extract the function name inside audit_function (it re-parses it)
                # But we can just construct a dummy prompt since we have the code and func_name
                dummy_prompt = f"def {func_name}(self):\n    pass"
                
                work_item = (data.get("task_id"), data.get("function_sample_index"), dummy_prompt, data.get("code"))
                
                tasks_to_retry.append({
                    "combinations": combos,
                    "filepath": fpath,
                    "work_item": work_item,
                    "func_name": func_name
                })
        except Exception as e:
            print(f"Error loading {fpath}: {e}")

    # Sort largest to smallest (or smallest to largest, doesn't matter much for sampling as logic is O(N) not O(Combos))
    # Let's do smallest first anyway
    tasks_to_retry.sort(key=lambda x: x["combinations"])
    
    print(f"Found {len(tasks_to_retry)} tasks to sample.")
    
    # Run setup
    base_profile, master_map, type_map = build_profile_map()
    
    # Sampling Config
    SAMPLE_SIZE = 100000 
    
    print(f"Sampling Limit set to: {SAMPLE_SIZE:,} iterations per function.")
    
    count_fixed = 0
    
    for task in tasks_to_retry:
        combos = task["combinations"]
        fpath = task["filepath"]
        func_name = task["func_name"]
        
        print(f"Sampling {func_name} (Space: {combos:,})...")
        try:
            # We pass max_combos=SAMPLE_SIZE. 
            # Since these tasks are known to be > 1M (which is > 100k), 
            # the logic in run_audit_dynamic will trigger "total_combos > MAX_COMBOS" -> Sampling
            res = audit_function(task["work_item"], master_map, type_map, base_profile, max_combos=SAMPLE_SIZE)
            
            if res and res.get("status") != "skipped_overlimit":
                # Success! Save to success folder and delete failed file
                fname = os.path.basename(fpath)
                target_path = os.path.join(SUCCESS_DIR, fname)
                
                with open(target_path, 'w') as f:
                    json.dump(res, f, indent=2)
                    
                os.remove(fpath)
                print(f"  -> Done! Moved to success/")
                count_fixed += 1
            else:
                print(f"  -> Failed (Computed status: {res.get('status')})")
                
        except KeyboardInterrupt:
            print("\nStopping loop.")
            break
        except Exception as e:
            print(f"  -> Exception: {e}")

    print(f"Sampling cycle complete. Processed {count_fixed} tasks.")

if __name__ == "__main__":
    main()
