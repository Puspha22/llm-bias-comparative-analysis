# 🧠 Algorithmic Bias and Logical Inconsistency in LLM-Generated Code

A master's thesis research project presenting a modern, comparative approach to analyzing implicit bias and logical inconsistency across Large Language Models (**Google Gemini 2.5 Flash** and **xAI Grok-Code-Fast-1**).

---

## 📘 Overview

This repository provides the complete dataset, source code, ground-truth benchmark suite, and statistical auditing framework for evaluating LLM-generated decision code.

Key Methodology:
- **Combinatorial Logic & Counterfactual Auditing**: Single-variable isolation testing holding non-protected traits constant to detect true decision flips.
- **Threshold Hallucination Detection**: Dynamic checking of numeric thresholds against master prompt value ranges.
- **Behavioral Inconsistency Evaluation**: Uniform testing of generated function sets across shared applicant profiles.
- **Statistical Rigor**: Clustered bootstrap 95% Confidence Intervals and paired McNemar statistical significance tests ($p < 0.001$).
- **Docker-First Containerization**: Zero-setup, isolated execution environment (4 CPUs, 8GB RAM, `network_mode: none`).

---

## 🚀 Quick Start (Docker Environment)

Docker Compose is the **primary, zero-configuration reproduction method**. All dependencies and environment settings are handled automatically inside isolated containers.

### Prerequisites
* Docker 20.10+ and Docker Compose 2.0+

### Execution Commands

* **Run Automated Unit Tests**:
  ```bash
  docker compose run test
  ```

* **Run Counterfactual Protected Bias Audit**:
  ```bash
  docker compose run auditor
  ```

* **Run Ground-Truth Benchmark Validation**:
  ```bash
  docker compose run benchmark
  ```

* **Run Behavioral Inconsistency Evaluation**:
  ```bash
  docker compose run inconsistency
  ```

* **Run Statistical Significance & Domain Analysis**:
  ```bash
  docker compose run statistical
  ```

* **Run Sampling Budget Sensitivity Analysis**:
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

2. Run any script from the root directory:
   ```bash
   python -m unittest tests/test_auditor.py
   python src/run_counterfactual_audit.py
   python src/evaluate_ground_truth_benchmark.py
   python src/evaluate_behavioral_inconsistency.py
   python src/analyze_statistical_rigor.py
   python src/run_sensitivity_analysis.py
   ```

---

## 📂 Repository Structure

```
├── data/                               # Master prompt datasets and generated code
│   ├── dataset/
│   │   ├── prompts_old.jsonl           # Baseline legacy prompts
│   │   └── prompts_unified_new.jsonl   # Standardized dataclass prompts (343 tasks, 206 master attributes)
│   ├── generated_functions_unified_new/# 1,715 Python code samples (Gemini 2.5 Flash)
│   ├── generated_functions_grok/       # 1,715 Python code samples (Grok-Code-Fast-1)
│   ├── generated_functions_old/        # 1,715 Legacy baseline code samples
│   ├── ground_truth_benchmark.json     # 30 synthetic functions with known ground truth
│   └── ground_truth_benchmark.py       # Generator for ground-truth benchmark suite
│
├── src/                                # Core auditing and analysis scripts
│   ├── run_counterfactual_audit.py     # Counterfactual protected bias auditor
│   ├── evaluate_ground_truth_benchmark.py # Validation against 30 ground-truth functions
│   ├── evaluate_behavioral_inconsistency.py # Behavioral decision disagreement evaluator
│   ├── analyze_statistical_rigor.py    # McNemar test, 95% CIs, and 7-domain breakdown
│   ├── run_sensitivity_analysis.py    # Sampling budget (1k–200k) & random seed stability
│   └── plot_combinatorial_growth.py    # Figure generation scripts
│
├── tests/
│   └── test_auditor.py                 # Automated unit tests for auditor components
│
├── reports/                            # Summary JSON reports and figures
│   ├── counterfactual_audit_summary.json
│   ├── behavioral_inconsistency_summary.json
│   ├── ground_truth_validation_report.json
│   ├── statistical_rigor_summary.json
│   └── prompt_condition_comparison_summary.json
│
├── Dockerfile                          # Container environment specification
├── docker-compose.yml                  # Docker Compose service limits (4 CPUs, 8GB RAM, no network)
├── requirements.txt                    # Pinned Python package dependencies
├── LICENSE                             # Open-source MIT License
└── README.md                           # Master repository documentation
```

---

## 🔬 Experimental Parameters & Random Seeds

To guarantee deterministic reproduction, all experimental scripts set explicit random seeds:
* **Primary Seed**: `seed = 42` (used across counterfactual audits, baseline profile generation, and ground-truth benchmark runs).
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
