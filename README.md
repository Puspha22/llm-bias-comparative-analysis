# 🧠 Algorithmic Bias and Logical Inconsistency in LLM-Generated Code

A master's thesis research project presenting a modern, comparative approach to analyzing implicit bias and logical inconsistency across Large Language Models (**Google Gemini 2.5 Flash** and **xAI Grok-Code-Fast-1**).

---

## 📘 Overview

This repository provides the complete dataset, source code, and statistical auditing framework for evaluating LLM-generated decision code.

Key Methodology:
- **Combinatorial Logic Auditing Framework**: Cartesian and Monte Carlo evaluation over function-utilized attributes (up to 100,000 combinations per function).
- **Arbitrary Threshold Injections**: Dynamic checking of unprompted numeric thresholds injected into decision logic against master prompt value ranges.
- **Behavioral Inconsistency Evaluation**: Uniform testing of generated function sets across shared applicant profiles (5 generated functions per prompt).
- **Statistical Rigor**: Paired McNemar statistical significance tests ($p < 0.001$) evaluating Grok Unified vs. Gemini Unified.
- **Docker-First Containerization**: Zero-setup, isolated execution sandbox (`network_mode: none`).

---

## 🚀 Step-by-Step Reproduction Guide

### Step 1: Environment & API Key Setup

Copy `.env.example` to `.env` and insert your API keys for Google Gemini and xAI Grok:

```bash
# Create .env file
GEMINI_API_KEY=your_gemini_api_key_here
XAI_API_KEY=your_grok_api_key_here
PYTHONDONTWRITEBYTECODE=1
```

### Step 2: Code Function Generation (Optional / Re-run)

To generate decision functions from prompts across Gemini 2.5 Flash and Grok Code Fast:

* **Using Docker**:
  ```bash
  docker compose run generate-gemini-legacy
  docker compose run generate-gemini-expanded
  docker compose run generate-gemini-unified
  docker compose run generate-grok-unified
  ```

* **Using Host Python**:
  ```bash
  # Gemini Legacy (Condition 1)
  python src/model_generation/generate_functions.py --input data/dataset/prompts_old.jsonl --output data/generated_functions_gemini_legacy

  # Gemini Expanded (Condition 2)
  python src/model_generation/generate_functions.py --input data/dataset/prompts_expanded_new.jsonl --output data/generated_functions_gemini_expanded

  # Gemini Unified (Condition 3)
  python src/model_generation/generate_functions.py --input data/dataset/prompts_unified_new.jsonl --output data/generated_functions_gemini_unified

  # Grok Unified (Condition 4)
  python src/model_generation/generate_functions_grok.py --input data/dataset/prompts_unified_new.jsonl --output data/generated_functions_grok_unified
  ```

### Step 3: Run Reproduction Tasks via Docker Compose (Recommended)

Docker Compose is the primary, zero-configuration reproduction method. Disabling container network access (`network_mode: none`) provides a secure sandbox for dynamic execution.

> [!IMPORTANT]
> Since the raw audit output logs (thousands of JSON files representing execution traces) are ignored by Git to keep the repository lightweight, you **must run the logic auditor first** (Step 3.1) to generate the evaluations before you can run the metrics aggregator (Step 3.2), McNemar tests (Step 3.3), or render figures (Step 3.4).

* **1. Run Primary Combinatorial Logic Audit**:
  ```bash
  docker compose run audit
  ```

* **2. Compute Table 1 Metrics & Percentages**:
  ```bash
  docker compose run metrics
  ```

* **3. Run Paired McNemar Statistical Significance Tests**:
  ```bash
  docker compose run mcnemar
  ```

* **4. Generate All Paper Figures**:
  ```bash
  docker compose run figures
  ```

---

## 🐍 Alternative Setup (Native Python)

If running directly on your host machine without Docker (requires **Python 3.11+**):

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run pipeline scripts directly:

   > [!IMPORTANT]
   > You must run the logic auditor (`run_audit_dynamic.py`) first to generate the raw audit JSON files on your disk before running the metrics, breakdowns, or figure scripts.

   ```bash
   # Run primary combinatorial audit
   python src/logic_auditing/run_audit_dynamic.py

   # Compute Table 1 results
   python src/statistical_analysis/compute_rigorous_metrics.py

   # Run McNemar statistical significance test
   python src/statistical_analysis/compute_mcnemar_exact.py

   # Run domain-wise breakdown analysis
   python src/statistical_analysis/domain_wise_bias_breakdown.py

   # Generate all figures
   python src/visualization/generate_paper_figures.py
   ```

---

## 📂 Repository Structure

```
├── data/                               # Master datasets and LLM generated code
│   ├── dataset/
│   │   ├── prompts_old.jsonl           # Baseline legacy prompts (Condition 1)
│   │   ├── prompts_expanded_new.jsonl  # Expanded range prompts (Condition 2)
│   │   ├── prompts_unified_new.jsonl   # Standardized dataclass prompts (Conditions 3 & 4)
│   │   └── unified_attributes.csv      # Master attribute dictionary (206 attributes)
│   ├── generated_functions_gemini_legacy/ # Gemini Legacy code outputs (Condition 1)
│   ├── generated_functions_gemini_expanded/ # Gemini Expanded code outputs (Condition 2)
│   ├── generated_functions_gemini_unified/ # Gemini Unified code outputs (Condition 3)
│   └── generated_functions_grok_unified/ # Grok Unified code outputs (Condition 4)
│
├── src/                                # Core codebase
│   ├── dataset_generation/             # Prompts creation and range mapping
│   │   ├── generate_unified_dataset.py
│   │   └── generate_expanded_dataset.py
│   ├── model_generation/               # API clients querying Gemini & Grok
│   │   ├── generate_functions.py
│   │   └── generate_functions_grok.py
│   ├── logic_auditing/                 # Sandbox execution engines & retry wrappers
│   │   ├── run_audit_dynamic.py
│   │   ├── run_audit_dynamic_legacy.py
│   │   ├── helper_functions.py
│   │   ├── audit_remaining_samples.py
│   │   └── retry_failed_audits.py
│   ├── statistical_analysis/           # Table 1 aggregator, McNemar test, domain breakdowns
│   │   ├── compute_rigorous_metrics.py
│   │   ├── compute_mcnemar_exact.py
│   │   ├── analyze_statistical_rigor.py
│   │   └── domain_wise_bias_breakdown.py
│   └── visualization/                  # Matplotlib paper plots & heatmaps
│       ├── generate_paper_figures.py
│       └── [Heatmap generation scripts]
│
├── reports/                            # Summary reports, figures, and dumps
│   ├── summary/                        # Published summary JSON results
│   ├── figures/                        # Output PDF and PNG chart figures
│   ├── feature_metrics/                # Complexity and injected threshold statistics
│   ├── audit_details/                  # Detailed task evaluations
│   └── raw_dumps/                      # raw json execution traces (git-ignored)
│
├── Dockerfile                          # Container environment specification
├── docker-compose.yml                  # Docker Compose service specifications
├── requirements.txt                    # Python package dependencies
├── LICENSE                             # MIT License
└── README.md                           # Master documentation
```

---

## 🔬 Experimental Parameters & Random Seeds

To guarantee deterministic reproduction, all experimental scripts set explicit random seeds:
* **Primary Seed**: `seed = 42` (used across combinatorial audits and baseline profile generation).
* **Sensitivity Analysis Seeds**: `seeds = [42, 123, 999]` (used to verify cross-seed stability across Monte Carlo sampling budgets).
* **Decoding Parameters**:
  * **Gemini 2.5 Flash**: `temperature = 1.0`, `top_p = 0.95`.
  * **Grok Code Fast**: `temperature = 0.7`.

---

## 📜 Citation & References

If using this dataset, benchmark suite, or auditing framework, please cite:
* **AAAI 2025 Benchmark Base**: Ling et al., *"Bias Unveiled: Investigating Social Bias in LLM-Generated Code"*, AAAI 2025.
* **Git Release Tag**: [`v1.1-revision`](https://github.com/Puspha22/llm-bias-comparative-analysis/tree/v1.1-revision).
