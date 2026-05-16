# 🧠 LLM Bias Thesis: A Comparative Analysis

A master's thesis project that replicates and extends the academic paper **_"Bias Unveiled: Investigating Social Bias in LLM-Generated Code"_** using a modern, comparative approach to analyze implicit bias and logical inconsistency across different Large Language Models.

---

## 📘 Overview

This project investigates **algorithmic bias** in Large Language Model (LLM)-generated code. It introduces a next-generation auditing framework called **Combinatorial Logic Auditing**, which extends the original paper’s methodology by exhaustively testing *all* attributes used in a function — not just a predefined “sensitive” list.

The framework:
- Generates Python functions using both **General Purpose Models** (e.g., Google Gemini) and **Code Specialized Models** (e.g., Grok).
- Compares these advanced models against a **Baseline Legacy** approach to measure the impact of context expansion on bias.
- Systematically tests *every* combination of input attributes to detect discriminatory or inconsistent logic.

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
- **Purpose:** Transforms baseline legacy prompts into structurally sound Python `@dataclass` definitions, expanding the scope of attribute values to ensure the models have full context and are not biased by limited, static examples.
- **Output:** `data/dataset/prompts_unified_new.jsonl`

### **2. Code Generation (Comparative)**
- **Scripts:** `src/generate_functions.py` and `src/generate_functions_grok.py`
- **Purpose:** Uses the expanded prompts to generate multiple code samples across different LLM architectures (Gemini 2.5 Flash and Grok), providing the foundational datasets for the comparative analysis.

### **3. Bias Detection — “Combinatorial Logic Auditing”**
- **Scripts:** `src/run_audit_dynamic.py` and `src/run_audit_dynamic_legacy.py`
- **Purpose:** Detects discriminatory or inconsistent logic using an all-attribute, all-combination strategy.
  1. Parses each function to identify all input attributes used.
  2. Computes the **Cartesian product** of every attribute’s possible values.
  3. Executes the function for every possible combination.
  4. Flags the function as biased if *any* combination yields a different output than another.

### **4. Statistical Analysis**
- **Scripts:** `src/analyze_results.py` and `src/extract_protected_bias.py`
- **Purpose:** Quantifies logical inconsistency, extracts occurrences of "Magic Number" hallucinations, and isolates bias linked to protected demographic attributes across the different model generations.

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

- **Widespread Bias Detected:** The Combinatorial Logic Auditing framework flagged significantly more functions with discriminatory logic than traditional static methods.
- **Functional Attributes Drive Bias:** Bias most frequently originates from "functional" attributes such as **`major`** and **`education`**, proving that proxy variables are a major source of algorithmic discrimination in code generation.
- **Magic Numbers & Hallucinations:** Models frequently invent hardcoded thresholds (e.g., `age < 18` or `credit_score > 700`) that were not present in the prompt, leading to highly inconsistent logic.

---

## 🧾 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.
