import os
import json
import glob
from run_audit_dynamic import audit_function, build_profile_map, PARTIAL_DIR

SUCCESS_DIR = os.path.join(PARTIAL_DIR, "success")
FAILED_DIR = os.path.join(PARTIAL_DIR, "failed")

def main():
    print("Loading failed audits...")
    failed_files = glob.glob(os.path.join(FAILED_DIR, "*.json"))
    
    if not failed_files:
        print("No failed audits found.")
        return

    # Load metadata to sort
    tasks_to_retry = []
    for fpath in failed_files:
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
                combos = data.get("total_combinations", 0)
                # Reconstruct work_item tuple expected by audit_function
                # (task_id, idx, prompt, code)
                # Note: 'prompt' is not saved in the result json, but we only need it for function name extraction
                # which we can hack or we actually need to reload prompts.
                # Actually, audit_function uses prompt to get func_name. 
                # Let's see if we can just pass a dummy prompt that has "def func_name"
                func_name = data.get("function_name")
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

    # Sort small -> large
    tasks_to_retry.sort(key=lambda x: x["combinations"])
    
    print(f"Found {len(tasks_to_retry)} failed tasks.")
    print(f"Smallest: {tasks_to_retry[0]['combinations']} combos")
    print(f"Largest:  {tasks_to_retry[-1]['combinations']} combos")
    
    # Run setup
    base_profile, master_map, type_map = build_profile_map()
    
    # Retry Loop
    NEW_LIMIT = 100000000 # 100 Million Limit for retries
    
    print(f"Retrying with higher limit: {NEW_LIMIT:,}")
    
    count_fixed = 0
    
    for task in tasks_to_retry:
        combos = task["combinations"]
        fpath = task["filepath"]
        func_name = task["func_name"]
        
        if combos > NEW_LIMIT:
             print(f"Skipping {func_name} (Still too huge: {combos:,})")
             continue
             
        print(f"Retrying {func_name} ({combos:,} combos)...")
        try:
            res = audit_function(task["work_item"], master_map, type_map, base_profile, max_combos=NEW_LIMIT)
            
            if res and res.get("status") != "skipped_overlimit":
                # Success! Save to success folder and delete failed file
                fname = os.path.basename(fpath)
                target_path = os.path.join(SUCCESS_DIR, fname)
                
                with open(target_path, 'w') as f:
                    json.dump(res, f, indent=2)
                    
                os.remove(fpath)
                print(f"  -> Success! Moved to success/")
                count_fixed += 1
            else:
                print(f"  -> Failed again (Skipped or Error)")
                
        except KeyboardInterrupt:
            print("\nStopping retry loop.")
            break
        except Exception as e:
            print(f"  -> Exception: {e}")

    print(f"Retry cycle complete. Fixed {count_fixed} tasks.")

if __name__ == "__main__":
    main()
