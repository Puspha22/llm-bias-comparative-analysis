# 🧠 Algorithmic Bias and Logical Inconsistency in LLM-Generated Code

A master's thesis project presenting a modern, comparative approach to analyzing implicit bias and logical inconsistency across different Large Language Models.

---

## 📘 Overview

This project investigates **algorithmic bias** in Large Language Model (LLM)-generated code. It introduces a novel evaluation methodology called the **Combinatorial Logic Auditing** framework, designed to dynamically test *all* attributes utilized in an LLM-generated function — not just a predefined list of demographic traits.

The framework:
- Generates Python functions using both **General Purpose Models** (Google Gemini 2.5 Flash) and **Code Specialized Models** (Grok-Code-Fast-1).
- Systematically executes the **Cartesian product** of all input attributes (using Monte Carlo sampling for massive combinatorial spaces).
- Automatically detects discriminatory decision boundaries, arbitrary numeric hallucinations, and logical inconsistencies across the models.

---

## 📂 Repository Structure

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
- **Purpose:** Unifies fragmented variables from the base dataset and systematically expands their valid data arrays to ensure the LLMs are evaluated against a comprehensive, standardized schema.
- **Output:** `data/dataset/prompts_unified_new.jsonl`

### **2. Code Generation (Comparative)**
- **Scripts:** `src/generate_functions.py` and `src/generate_functions_grok.py`
- **Purpose:** Generates independent code samples across different LLM architectures (Gemini 2.5 Flash and Grok) to provide the foundational datasets for comparative analysis.

### **3. Bias Detection — “Combinatorial Logic Auditing”**
- **Scripts:** `src/run_audit_dynamic.py` and `src/run_audit_dynamic_legacy.py`
- **Purpose:** Detects discriminatory or inconsistent logic using an all-attribute, all-combination strategy.
  1. Parses each function to dynamically identify all utilized input attributes.
  2. Computes the **Cartesian product** of every attribute’s possible values (applying Monte Carlo limits at 100,000 combinations).
  3. Executes the function for every possible combination within an isolated namespace.
  4. Flags the function as biased if the code returns different outputs (e.g., returning `True` for one combination of traits but `False` for another) solely based on changing input attributes.

### **4. Statistical Analysis**
- **Scripts:** `src/analyze_results.py` and `src/extract_protected_bias.py`
- **Purpose:** Quantifies logical inconsistency, extracts occurrences of "Magic Number" hallucinations, and isolates bias linked to legally protected demographics and non-demographic "functional" attributes.

---

## 🚀 Usage

### **Prerequisites**

Requires **Python 3.8+** and the following dependencies:
```bash
pip install -r requirements.txt
```

### **Environment Setup**

To re-run the code generation phases, you must provide your API keys. Create a `.env` file in the root directory and add the following:

```env
GEMINI_API_KEY="your_google_gemini_key_here"
GROK_API_KEY="your_xai_grok_key_here"
```

### **Execution Pipeline**

To reproduce the study from scratch, run the scripts from the root directory in the following order:

**1. Data Preparation**
```bash
python src/generate_unified_dataset.py
```

**2. Code Generation**
```bash
python src/generate_functions.py
python src/generate_functions_grok.py
```

**3. Combinatorial Logic Auditing**
```bash
python src/run_audit_dynamic_legacy.py
python src/run_audit_dynamic.py
```

**4. Statistical Analysis**
```bash
python src/analyze_results.py
python src/extract_protected_bias.py
```

---

## 📊 Key Findings

- **Widespread Bias Detected:** The Combinatorial Logic Auditing framework flagged significantly more functions with discriminatory logic than traditional static testing methods.
- **Functional Attributes Drive Bias:** Bias most frequently originates from "functional" attributes such as **`major`** and **`education`**, proving that seemingly neutral proxy variables are a major source of algorithmic discrimination in code generation.
- **Magic Numbers & Hallucinations:** Models frequently invent hardcoded numerical thresholds (e.g., hallucinating clinical cutoffs like `blood_sugar >= 126`) that were not requested in the prompt.
- **High Inconsistency:** The models exhibit extreme logical variance (often >93% inconsistency) when asked to evaluate the identical prompt multiple times, proving they do not rely on structured logical processes.

---

## 🧾 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.
