# 🧠 Algorithmic Bias and Logical Inconsistency in LLM-Generated Code

A master's thesis research project presenting a modern, comparative approach to analyzing implicit bias and logical inconsistency across Large Language Models (**Google Gemini 2.5 Flash** and **xAI Grok-Code-Fast-1**).

---

## 📘 Overview

This repository provides the complete dataset, source code, ground-truth benchmark suite, and statistical auditing framework for evaluating LLM-generated decision code.

Key Methodology:
- **Combinatorial Logic Auditing Framework**: Cartesian and Monte Carlo evaluation over function-utilized attributes (up to 100,000 combinations per function).
- **Magic Number Threshold Hallucination Detection**: Dynamic checking of numeric thresholds against master prompt value ranges.
- **Behavioral Inconsistency Evaluation**: Uniform testing of generated function sets across shared applicant profiles (5 generated functions per prompt).
- **Ground-Truth Benchmark Suite**: Validation against 30 synthetic functions with known ground truth.
- **Statistical Rigor**: Clustered bootstrap 95% Confidence Intervals and paired McNemar statistical significance tests ($p < 0.001$).
- **Docker-First Containerization**: Zero-setup, isolated execution environment (`network_mode: none`).

---

## 🚀 Step-by-Step Reproduction Guide (From Scratch)

### Step 1: Environment & API Key Setup

Copy `.env.example` to `.env` and insert your API keys for Google Gemini and xAI Grok:

```bash
# Create .env file
GEMINI_API_KEY=your_gemini_api_key_here
XAI_API_KEY=your_grok_api_key_here
PYTHONDONTWRITEBYTECODE=1
```

### Step 2: Code Function Generation (Optional / Optional Re-run)

To generate 1,715 Python decision functions from prompts across Gemini 2.5 Flash and Grok Code Fast:

* **Using Docker**:
  ```bash
  docker compose run auditor python src/generate_functions.py
  docker compose run auditor python src/generate_functions_grok.py
  ```

* **Using Host Python**:
  ```bash
  python src/generate_functions.py
  python src/generate_functions_grok.py
  ```

### Step 3: Run Full Pipeline via Docker Compose (Recommended)

Docker Compose is the primary, zero-configuration reproduction method.

* **1. Run Unit Tests**:
  ```bash
  docker compose run test
  ```

* **2. Run Primary Combinatorial Logic Audit**:
  ```bash
  docker compose run auditor
  ```

* **3. Run Ground-Truth Benchmark Validation**:
  ```bash
  docker compose run benchmark
  ```

* **4. Run Behavioral Inconsistency Evaluation**:
  ```bash
  docker compose run inconsistency
  ```

* **5. Run Statistical Rigor & McNemar Significance Tests**:
  ```bash
  docker compose run statistical
  ```

* **6. Run Sampling Budget & Seed Sensitivity Analysis**:
  ```bash
  docker compose run sensitivity
  ```

---

## 🐍 Alternative Setup (Native Python)

If running directly on your host machine without Docker:

1. Requires **Python 3.11+**. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run pipeline scripts directly:
   ```bash
   # Run unit tests
   python -m unittest tests/test_auditor.py

   # Run primary combinatorial audit
   python src/run_audit_dynamic.py

   # Extract all 15 protected attribute counts
   python src/extract_all_protected_counts.py

   # Run ground-truth benchmark validation
   python src/evaluate_ground_truth_benchmark.py

   # Run behavioral inconsistency evaluation
   python src/evaluate_behavioral_inconsistency.py

   # Run statistical rigor analysis
   python src/analyze_statistical_rigor.py

   # Run sensitivity analysis
   python src/run_sensitivity_analysis.py
   ```

---

## 📂 Repository Structure

```
├── data/                               # Master prompt datasets and generated code
│   ├── dataset/
│   │   ├── prompts_old.jsonl           # Baseline legacy prompts
│   │   ├── prompts_unified_new.jsonl   # Standardized dataclass prompts (343 tasks, 206 master attributes)
│   │   ├── auto_canonical_map.json     # Attribute canonical mapping
│   │   ├── attribute_clusters.csv      # Cluster mapping
│   │   └── unified_attributes.csv      # Master attribute dictionary
│   ├── generated_functions_unified_new/# 1,715 Python code samples (Gemini 2.5 Flash)
│   ├── generated_functions_grok/       # 1,715 Python code samples (Grok-Code-Fast-1)
│   └── ground_truth_benchmark.json     # 30 synthetic functions with known ground truth
│
├── src/                                # Core auditing and analysis scripts
│   ├── helper_functions.py             # Shared Person, type conversion, and prompt parser module
│   ├── run_audit_dynamic.py            # Primary Combinatorial Logic Auditor
│   ├── extract_all_protected_counts.py # 15 Protected Attribute counter
│   ├── evaluate_ground_truth_benchmark.py # Validation against 30 ground-truth functions
│   ├── evaluate_behavioral_inconsistency.py # Behavioral decision disagreement evaluator
│   ├── evaluate_code_compilation_metrics.py # Syntax extraction & compilation success rate evaluator
│   ├── analyze_statistical_rigor.py    # McNemar test, 95% CIs, and 7-domain breakdown
│   ├── run_sensitivity_analysis.py     # Sampling budget (1k–200k) & random seed stability
│   ├── experiments/                    # Exploratory feature & attribute variance experiments
│   └── visualization/                  # Plotting, PDF/PNG chart generation, & dashboard scripts
│
├── tests/
│   └── test_auditor.py                 # Automated unit tests for auditor components
│
├── reports/                            # Summary JSON reports, audit details, and figures
│   ├── summary/                        # Published summary JSON reports
│   ├── audit_details/                  # Detailed per-model JSON audit logs
│   ├── feature_metrics/                # Feature variance and complexity metrics
│   ├── figures/                        # Output PDF and PNG chart figures
│   └── manuscript_notes/               # Response letters and methodology notes
│
├── Dockerfile                          # Container environment specification
├── docker-compose.yml                  # Docker Compose service specifications
├── requirements.txt                    # Pinned Python package dependencies
├── LICENSE                             # Open-source MIT License
└── README.md                           # Master repository documentation
```

---

## 🔬 Experimental Parameters & Random Seeds

To guarantee deterministic reproduction, all experimental scripts set explicit random seeds:
* **Primary Seed**: `seed = 42` (used across combinatorial audits, baseline profile generation, and ground-truth benchmark runs).
* **Sensitivity Analysis Seeds**: `seeds = [42, 123, 999]` (used to verify cross-seed stability across Monte Carlo sampling budgets).
* **Clustered Bootstrap**: `n_bootstraps = 1000` resamples clustered by prompt task (`seed = 42`).
* **Decoding Parameters**:
  * **Gemini 2.5 Flash**: `temperature = 1.0`, `top_p = 0.95`.
  * **Grok Code Fast**: `temperature = 0.7`.

---

## 📜 Citation & References

If using this dataset, benchmark suite, or auditing framework, please cite:
* **AAAI 2025 Benchmark Base**: Ling et al., *"Bias Unveiled: Investigating Social Bias in LLM-Generated Code"*, AAAI 2025.
* **Git Release Tag**: [`v1.1-revision`](https://github.com/Puspha22/llm-bias-comparative-analysis/tree/v1.1-revision).
