import os
import json
import time
import textwrap
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("XAI_API_KEY")

# For Grok, we use the OpenAI SDK with the xAI base URL
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.x.ai/v1",
)

MODEL_NAME = "grok-code-fast-1"
NUM_SAMPLES = 5
INPUT_FILE = os.path.join("data", "dataset", "prompts_unified_new.jsonl")
OUTPUT_DIR = os.path.join("data", "generated_functions_grok")

# Delays
API_DELAY = 1
RETRY_DELAY = 10
RATE_LIMIT_DELAY = 30

SYSTEM_PROMPT = """You are an expert Python developer.
Task: Provide ONLY the implementation body for the specified Python method.
CRITICAL RESTRICTIONS:
- Output RAW Python code ONLY.
- NO comments, NO docstrings, NO markdown.
- NO method signatures.
- Return ONLY the executable logic."""

def get_code_from_grok(prompt_text):
    while True:
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0.7, # Same default logic as typical generation
            )
            
            code = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if code.startswith("```python"):
                code = code[9:].strip()
            if code.endswith("```"):
                code = code[:-3].strip()
                
            return code

        except Exception as e:
            err_msg = str(e).lower()
            if "rate limit" in err_msg or "429" in err_msg or "503" in err_msg:
                print(f"  [!] Rate Limit or Service Unavailable. Waiting {RATE_LIMIT_DELAY}s...")
                time.sleep(RATE_LIMIT_DELAY)
            else:
                print(f"  [!] API Error: {type(e).__name__}: {e}. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)

def main():
    if not API_KEY:
        print("CRITICAL ERROR: XAI_API_KEY not found in .env file.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        tasks = [json.loads(line) for line in f]

    print(f"Loaded {len(tasks)} tasks. Starting generation into {OUTPUT_DIR}")

    for i, task in enumerate(tasks):
        task_id = task.get("task_id")
        prompt = task.get("prompt")
        
        output_file = os.path.join(OUTPUT_DIR, f"task_{task_id}_generated.json")
        if os.path.exists(output_file):
            print(f"[{i+1}/{len(tasks)}] Skipping task {task_id} - already exists.")
            continue

        print(f"[{i+1}/{len(tasks)}] Processing task {task_id}...")
        samples = []
        for _ in range(NUM_SAMPLES):
            code = get_code_from_grok(prompt)
            samples.append(code)
            time.sleep(API_DELAY)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "task_id": task_id,
                "prompt": prompt,
                "generated_functions": samples
            }, f, indent=2)

    print("Generation complete.")

if __name__ == "__main__":
    main()
