# 🧠 LLM Bias Thesis: Replicating and Extending *"Bias Unveiled"*

A master's thesis project that replicates and extends the academic paper **_"Bias Unveiled: Investigating Social Bias in LLM-Generated Code"_** using a modern and robust Python implementation.

---

## 📘 Overview

This project investigates **algorithmic bias** in Large Language Model (LLM)-generated code. It introduces a next-generation auditing framework called **Smart Combination Testing**, which extends the original paper’s methodology by testing *all* attributes used in a function — not just a predefined “sensitive” list.

The framework:
- Generates Python functions using Google’s **Gemini API**.
- Systematically tests *every* combination of input attributes.
- Detects discriminatory or inconsistent logic across generated functions.

> [!NOTE]
> For a detailed history of the project's evolution, methodology changes, and legacy comparisons, see [project_log.md](project_log.md).

---

## 📂 Project Structure

```
├── src/                           # Source code
│   ├── generate_functions.py      # Code generation script (V2)
│   ├── run_audit_dynamic.py       # Smart Combination Testing audit script (V2)
│   ├── expand_prompts.py          # Standalone attribute expansion script (V3 Fix)
│   └── scan_attributes.py         # Utility to analyze attribute usage in datasets
│
├── data/                          # Data files
│   ├── dataset/
│   │   ├── prompts_old.jsonl          # 343 original bias testing prompts
│   │   └── prompts_expanded.jsonl # (V2) Expanded prompts (Legacy/Corrupted)
│   │   └── prompts_expanded_new.jsonl # (V3) Cleaned expanded prompts
│   ├── generated_functions_expanded/ # LLM-generated code samples
│   └── generated_functions_old/   # Legacy generated code
│
├── notebooks/                     # Jupyter notebooks
│   └── analysis.ipynb             # Data analysis notebook
│
├── reports/                       # Generated reports
│   ├── audit_report.json          # Full audit results (V2)
│   └── attribute_statistics.md    # Attribute frequency report (V3)
│
├── docs/                          # Documentation assets
│   └── img/
│
├── project_log.md                 # Record of the project's evolution
├── README.md                      # Project documentation
└── .env                           # Local file for API keys
```

---

## ⚙️ Methodology

### **1. Prompt Expansion (Data Prep)**
- **Script:** `src/expand_prompts.py`
- **Purpose:** The original dataset contained constrained value lists (e.g., `age` might only show `[25]`). This script scans the entire dataset to aggregate *all* possible values for every attribute and injects this comprehensive list into every prompt. This ensures the model has full context and isn't biased by limited examples.
- **Output:** `data/dataset/prompts_expanded_new.jsonl`

---

### **2. Code Generation**
- **Script:** `src/generate_functions.py`  
- **Input:** `data/dataset/prompts_expanded.jsonl`  
- **Purpose:** Uses **Google Gemini 2.5 Flash API** to generate 5 code samples for each of the 343 prompts  
  → **1,715 total functions.**

---

### **3. Bias Detection — “Smart Combination Testing”**
- **Script:** `src/run_audit_dynamic.py`  
- **Purpose:** Detects discriminatory or inconsistent logic using an all-attribute, all-combination strategy.

#### Process:
1. **Finds Used Attributes:**  
   Parses each function to identify all input attributes it actually uses (e.g., `major`, `age`, `income`).
2. **Generates Combinations:**  
   Computes the **Cartesian product** of every attribute’s possible values.
3. **Tests All Combinations:**  
   Executes the function for every possible input combination.
4. **Flags Bias:**  
   Marks the function as biased if *any* combination yields a different output than another.

---

### **4. Analysis**
- **Script:** `notebooks/analysis.ipynb`  
- **Input:** `reports/audit_report.json`  
- **Purpose:** Loads all audit results (1,400 flagged functions) into a pandas DataFrame for analysis.  
  Provides:
  - Deep-dive exploration tools  
  - Attribute-level bias visualizations  
  - Pattern detection for complex logic bias

---

## 🚀 Usage

### **Prerequisites**

You’ll need **Python 3.8+** and the following dependencies:
```bash
pip install pandas matplotlib seaborn tqdm requests python-dotenv
```

---

### **Setup**

1. Create a `.env` file in the project root.  
2. Add your **Gemini API key**:
   ```
   GEMINI_API_KEY="YOUR_API_KEY_HERE"
   ```

---

### **Step 1 – Run Prompt Expansion**
Run the expansion script to scan the original dataset and generate the comprehensive prompts:
```bash
python src/expand_prompts.py
```
This generates `data/dataset/prompts_expanded_new.jsonl` (used for code generation).

---

### **Step 2 – Generate Code Samples**
Use the expanded prompts to generate new LLM functions:
```bash
python src/generate_functions.py
```

---

### **Step 3 – Run the Bias Audit**
Execute the dynamic audit across all generated functions:
```bash
python src/run_audit_dynamic.py
```
This will produce a comprehensive `reports/audit_report.json` file.

---

### **Step 4 – Analyze Results**
Open `notebooks/analysis.ipynb` again and run the remaining cells to:
- Load `reports/audit_report.json`
- Explore flagged functions
- Visualize and interpret findings

---

## 📊 Key Findings

- **Widespread Bias Detected**
  The Smart Combination Testing framework flagged **1,400+ functions** with discriminatory logic, significantly more than traditional methods.

- **Functional Attributes Drive Bias**
  Bias most frequently originates from "functional" attributes such as **`major`** and **`education`**, not just demographic ones.

- **Religious Bias Detected**
  The framework detected instances of **religious bias** (e.g., Task 181: `eligible_for_diversity_award`). The generated code explicitly listed `islam`, `hinduism`, `buddhism`, and `atheist` as qualifying, while **excluding `christianity`**.

- **Magic Numbers & Inconsistency**
  Analysis reveals that the model often hallucinates thresholds (e.g., hardcoding `age < 18`) and applies inconsistent logic across different samples for the same prompt.

---

## 🧾 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## ✨ Acknowledgments

Inspired by: **"Bias Unveiled: Investigating Social Bias in LLM-Generated Code"** and extended through a novel, data-driven auditing framework.

