import os
import json

def generate_appendix_prompts():
    legacy_file = os.path.join("data", "dataset", "prompts_old.jsonl")
    unified_file = os.path.join("data", "dataset", "prompts_unified_new.jsonl")

    legacy_prompts = {}
    with open(legacy_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            legacy_prompts[str(data.get("task_id"))] = data.get("prompt")

    unified_prompts = {}
    with open(unified_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            unified_prompts[str(data.get("task_id"))] = data.get("prompt")

    # Select representative tasks from 3 domains
    sample_tasks = [
        {"id": "0", "domain": "Social Benefits", "name": "Financial Aid Qualification"},
        {"id": "51", "domain": "University Admissions and Awards", "name": "Academic Scholarship Award"},
        {"id": "153", "domain": "Health Exams and Programs", "name": "Diabetes Screening Eligibility"}
    ]

    doc = "# Appendix A: Prompt Standardization & Evolution Examples\n\n"
    doc += "This appendix provides representative examples illustrating the structural evolution from the legacy prompt format to our standardized unified prompt format across different application domains.\n\n"

    for sample in sample_tasks:
        t_id = sample["id"]
        doc += f"## Task {t_id}: {sample['name']} ({sample['domain']})\n\n"
        
        doc += "### Legacy Prompt Format\n"
        doc += "```python\n"
        doc += legacy_prompts.get(t_id, "# Legacy prompt not found").strip() + "\n"
        doc += "```\n\n"

        doc += "### Unified Standardized Dataclass Prompt Format\n"
        doc += "```python\n"
        u_p = unified_prompts.get(t_id, "# Unified prompt not found").strip()
        # Truncate lines for preview readability if too long
        lines = u_p.split('\n')
        if len(lines) > 35:
            preview = "\n".join(lines[:25]) + "\n    # ... [unified attribute matrix] ...\n" + "\n".join(lines[-8:])
            doc += preview + "\n"
        else:
            doc += u_p + "\n"
        doc += "```\n\n"
        doc += "---\n\n"

    out_file = os.path.join("reports", "appendix_prompt_evolution.md")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(f"Saved Appendix Prompt Evolution document to {out_file}")

if __name__ == "__main__":
    generate_appendix_prompts()
