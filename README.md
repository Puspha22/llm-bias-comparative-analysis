# 🧠 Algorithmic Bias and Logical Inconsistency in LLM-Generated Code

A master's thesis project presenting a modern, comparative approach to analyzing implicit bias and logical inconsistency across different Large Language Models.

---

## 📘 Overview

This project investigates **algorithmic bias** in Large Language Model (LLM)-generated code. It introduces a novel, next-generation evaluation methodology called the **Combinatorial Logic Auditing** framework, designed to dynamically test *all* attributes utilized in an LLM-generated function — not just a predefined list of demographic traits.

The framework:
- Generates Python functions using both **General Purpose Models** (Google Gemini 2.5 Flash) and **Code Specialized Models** (Grok-Code-Fast-1).
- Systematically calculates and executes the **Cartesian product** of all input attributes (using Monte Carlo sampling for massive combinatorial spaces).
- Automatically detects discriminatory decision boundaries, arbitrary numeric hallucinations, and severe logical inconsistencies across the models.

---

## 📂 Core Project Structure

The repository has been streamlined to contain only the core datasets and the scripts necessary to run the comparative pipeline:

```
├── src/                           # Source code
│   ├── generate_unified_dataset.py  # Data Prep: Unifies and expands prompts into dataclass format
│   ├── generate_functions.py        # Code Generation: Gemini (General Purpose)
│   ├── generate_functions_grok.py   # Code Generation: Grok (Code Specialized)
│   ├── run_audit_dynamic_legacy.py  # Audit: Baseline comparison testing
│   ├── run_audit_dynamic.py         # Audit: Combinatorial Logic Auditing
│   ├── analyze_results.py           # Analysis: Consistency and Hallucination stats
│   └── extract_protected_bias.py    # Analysis: Protected attribute extraction
│
├── data/                          # Data files
│   ├── dataset/
│   │   ├── prompts_old.jsonl            # Baseline legacy prompts
│   │   └── prompts_unified_new.jsonl    # Expanded, clean unified prompts
│   ├── generated_functions_old/         # Baseline generated code
│   ├── generated_functions_unified_new/ # Gemini generated code
│   └── generated_functions_grok/        # Grok generated code
│
├── README.md                      # Project documentation
└── requirements.txt               # Dependencies
```

---

## ⚙️ Methodology & Pipeline

### **1. Prompt Expansion (Data Prep)**
- **Script:** `src/generate_unified_dataset.py`
- **Purpose:** To ensure the models have full context and are not biased by limited, static examples, this script transforms an initial set of 343 human-centered tasks (originally sourced from the *Bias Unveiled* study) into structurally sound Python `@dataclass` definitions. It dramatically expands the scope and standardizes the typing of all available attributes.
- **Output:** `data/dataset/prompts_unified_new.jsonl`

### **2. Code Generation (Comparative)**
- **Scripts:** `src/generate_functions.py` and `src/generate_functions_grok.py`
- **Purpose:** Uses the expanded, unified prompts to generate independent code samples across different LLM architectures (Gemini 2.5 Flash and Grok), providing the foundational datasets for the comparative analysis.

### **3. Bias Detection — “Combinatorial Logic Auditing”**
- **Scripts:** `src/run_audit_dynamic.py` and `src/run_audit_dynamic_legacy.py`
- **Purpose:** Detects discriminatory or inconsistent logic using an all-attribute, all-combination strategy.
  1. Parses each function to dynamically identify all input attributes actually used by the LLM.
  2. Computes the **Cartesian product** of every attribute’s possible values (applying Monte Carlo limits at 100,000 combinations).
  3. Executes the function for every possible combination within an isolated namespace.
  4. Flags the function as biased or hallucinated if *any* combination yields an unexplained discriminatory output.

### **4. Statistical Analysis**
- **Scripts:** `src/analyze_results.py` and `src/extract_protected_bias.py`
- **Purpose:** Quantifies logical inconsistency, extracts occurrences of "Magic Number" hallucinations, and isolates bias linked to both legally protected demographics and non-demographic "functional" attributes.

---

## 🚀 Usage

### **Prerequisites**

You’ll need **Python 3.8+** and the following dependencies:
```bash
pip install -r requirements.txt
```

*(Note: API Keys for Gemini and Grok must be configured in your environment to re-run the code generation phases).*

---

## 📊 Key Findings

- **Widespread Bias Detected:** The Combinatorial Logic Auditing framework flagged significantly more functions with discriminatory logic than traditional static testing methods.
- **Functional Attributes Drive Bias:** Bias most frequently originates from "functional" attributes such as **`major`** and **`education`**, proving that seemingly neutral proxy variables are a major source of algorithmic discrimination in code generation.
- **Magic Numbers & Hallucinations:** Models frequently invent hardcoded numerical thresholds (e.g., arbitrarily restricting `GPA > 3.5` or `blood_sugar >= 126`) that were not present in the prompt, silently embedding rigid rules into software.
- **High Inconsistency:** The models exhibit extreme logical variance (often >93% inconsistency) when asked to evaluate the identical prompt multiple times, proving they do not rely on structured logical processes.

---

## 🧾 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.
