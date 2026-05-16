import os
import json
import requests
import time
import textwrap
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
NUM_SAMPLES = 5
INPUT_FILE = os.path.join("data", "dataset", "prompts_unified_new.jsonl")
OUTPUT_DIR = os.path.join("data", "generated_functions_unified_new")

# Delays
API_DELAY = 2
RETRY_DELAY = 10
RATE_LIMIT_DELAY = 30

SYSTEM_PROMPT = """You are an expert Python developer.
Task: Provide ONLY the implementation body for the specified Python method.
CRITICAL RESTRICTIONS:
- Output RAW Python code ONLY.
- NO comments, NO docstrings, NO markdown.
- NO method signatures.
- Return ONLY the executable logic."""

def get_code_from_gemini(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n{prompt_text}"}]}]}

    while True:
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            candidates = result.get('candidates', [])
            if not candidates:
                time.sleep(RETRY_DELAY)
                continue
                
            code = candidates[0].get('content', {}).get('parts', [])[0].get('text', '').strip()
            
            # Clean markdown if present
            if code.startswith("```python"):
                code = code[9:].strip()
            if code.endswith("```"):
                code = code[:-3].strip()
                
            return code

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in {429, 503}:
                print(f"  [!] HTTP {e.response.status_code} (Rate Limit or Service Unavailable). Waiting {RATE_LIMIT_DELAY}s...")
                time.sleep(RATE_LIMIT_DELAY)
            else:
                print(f"  [!] API Error: {e}. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"  [!] Unexpected Error: {type(e).__name__}: {e}. Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

def main():
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
        for i in range(NUM_SAMPLES):
            code = get_code_from_gemini(prompt)
            samples.append(code)
            if i < NUM_SAMPLES - 1:
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
