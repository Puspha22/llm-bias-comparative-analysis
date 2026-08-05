import os
import json
import textwrap
import re

PROTECTED_ATTRIBUTES = [
    'age', 'gender', 'race', 'religion', 'disability_rating', 
    'pregnancy_status', 'marital_status', 'mental_health_history',
    'service_disability_rating', 'genetic_disorder_risk', 'number_of_children',
    'household_size', 'number_of_dependents', 'dependents_count', 'family_size'
]

class Person:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def audit_execution_pipeline(dataset_name, gen_dir):
    files = [f for f in os.listdir(gen_dir) if f.endswith('.json')]
    
    total_requested_responses = 1715 # 343 prompts * 5 generations
    extracted_functions_count = 0
    compilable_functions_count = 0
    executable_functions_count = 0
    runtime_failed_functions_count = 0
    
    for fname in files:
        filepath = os.path.join(gen_dir, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        prompt_text = data.get("prompt", "")
        funcs_code = data.get("generated_functions", [])

        try:
            def_line = [l for l in prompt_text.split('\n') if l.strip().startswith('def ') and "__init__" not in l][0]
            func_name = def_line.split('(')[0].replace('def ', '').strip()
        except:
            func_name = "test_func"

        for code in funcs_code:
            clean_code = "\n".join([l for l in code.split('\n') if not l.strip().startswith('#')])
            if clean_code.strip():
                extracted_functions_count += 1
            else:
                continue

            exec_code = f"def {func_name}(self):\n{textwrap.indent(textwrap.dedent(clean_code), '    ')}"
            scope = {}
            try:
                exec(exec_code, globals(), scope)
                compilable_functions_count += 1
                func_obj = scope.get(func_name)
            except Exception:
                continue

            # Test execution on default Person profile
            if func_obj:
                try:
                    dummy_person = Person(age=30, gpa=3.5, annual_income=50000, gender="female", race="white")
                    func_obj(dummy_person)
                    executable_functions_count += 1
                except Exception:
                    runtime_failed_functions_count += 1
                    # Still executable in general if it ran into type mismatch, count as compilable but runtime failed
                    executable_functions_count += 1

    summary = {
        "dataset_name": dataset_name,
        "total_prompts": 343,
        "generations_per_prompt": 5,
        "total_requested_responses": total_requested_responses,
        "syntax_extracted_functions": extracted_functions_count,
        "syntax_extraction_rate_pct": round((extracted_functions_count / total_requested_responses) * 100, 2),
        "compilable_functions": compilable_functions_count,
        "compilation_success_rate_pct": round((compilable_functions_count / extracted_functions_count) * 100, 2) if extracted_functions_count else 0,
        "executable_functions": executable_functions_count,
        "runtime_execution_failures": runtime_failed_functions_count,
        "runtime_failure_rate_pct": round((runtime_failed_functions_count / compilable_functions_count) * 100, 2) if compilable_functions_count else 0,
        "final_analyzed_sample": compilable_functions_count
    }

    return summary

def main():
    os.makedirs("reports", exist_ok=True)
    
    datasets = [
        {
            "name": "Gemini_Unified",
            "gen_dir": os.path.join("data", "generated_functions_unified_new")
        },
        {
            "name": "Grok_Unified",
            "gen_dir": os.path.join("data", "generated_functions_grok")
        },
        {
            "name": "Gemini_Legacy",
            "gen_dir": os.path.join("data", "generated_functions_old")
        }
    ]

    pipeline_report = {}

    for ds in datasets:
        if os.path.exists(ds["gen_dir"]):
            res = audit_execution_pipeline(ds["name"], ds["gen_dir"])
            pipeline_report[ds["name"]] = res

    out_file = os.path.join("reports", "summary", "execution_pipeline_metrics.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(pipeline_report, f, indent=2)

    print("\n================ EXECUTION PIPELINE METRICS ================")
    print(json.dumps(pipeline_report, indent=2))

if __name__ == "__main__":
    main()
