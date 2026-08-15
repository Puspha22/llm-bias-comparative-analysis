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

To generate decision functions from prompts across Google Gemini and xAI Grok:

> [!NOTE]
> All 6,700+ pre-generated Python functions analyzed in the paper are already tracked and included in the `data/` folder. **You can skip this step** and proceed directly to Step 3 unless you wish to perform a fresh API generation from scratch (which requires API keys).

* **Using Docker**:
  ```bash
  docker compose run generate-gemini-legacy
  docker compose run generate-gemini-expanded
  docker compose run generate-gemini-unified
  docker compose run generate-grok-unified
  ```

* **Using Host Python**:
  ```bash
  # Gemini Legacy
  python src/model_generation/generate_functions.py --input data/dataset/prompts_old.jsonl --output data/generated_functions_gemini_legacy

  # Gemini Expanded
  python src/model_generation/generate_functions.py --input data/dataset/prompts_expanded_new.jsonl --output data/generated_functions_gemini_expanded

  # Gemini Unified
  python src/model_generation/generate_functions.py --input data/dataset/prompts_unified_new.jsonl --output data/generated_functions_gemini_unified

  # Grok Unified
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
  * **Files Created:** Generates thousands of individual JSON task-run evaluation files under:
    * `reports/partial_audit_results_gemini_legacy/success/`
    * `reports/partial_audit_results_gemini_expanded/success/`
    * `reports/partial_audit_results_gemini_unified/success/`
    * `reports/partial_audit_results_grok_unified/success/`
  * **What it contains:** Execution traces for each task run mapping mutated attribute combinations to program decisions.

* **2. Compute Table 1 Metrics & Sensitivity Summaries**:
  ```bash
  docker compose run metrics
  ```
  * **Files Created:**
    * `reports/summary/protected_attribute_sensitivity_summary.json`
  * **What it contains:** Summarizes the overall Protected Attribute Sensitivity rates (Table 1 main results) for all four model configurations:
    * **Gemini Legacy:** 475 / 1,688 biased functions (28.14%)
    * **Gemini Expanded:** 427 / 1,627 biased functions (26.24%)
    * **Gemini Unified:** 499 / 1,711 biased functions (29.16%)
    * **Grok Unified:** 656 / 1,715 biased functions (38.25%)
    * Also outputs attribute-specific flip frequencies and domain-level bias percentages.

* **3. Run Paired McNemar Statistical Significance Tests**:
  ```bash
  docker compose run mcnemar
  ```
  * **Files Created:**
    * `reports/summary/mcnemar_significance_test_results.json`
  * **What it contains:** Formats the paired hypothesis test results evaluating Grok Unified vs Gemini Unified (manuscript Section 3.2):
    * **Both biased:** 400 functions
    * **Both clean:** 958 functions
    * **Grok Unified biased exclusively ($b$):** 254 functions
    * **Gemini Unified biased exclusively ($c$):** 99 functions
    * **Chi-square statistic ($\chi^2$):** 67.18 (exact p-value < 0.0001, confirming statistical significance).

* **4. Generate All Paper Figures**:
  ```bash
  docker compose run figures
  ```
  * **Files Created:** Generates high-res PNG and vector PDF charts under `reports/figures/`:
    * **Architecture & Theory:**
      * `EndToEndProcess.png` (End-to-end framework architecture)
      * `combinatorial_growth.png` (Exponential search space growth)
      * `discovery_velocity_plateau.pdf/.png` (Monte Carlo failure discovery velocity $dK/dN$)
    * **Sensitivity & Consistency:**
      * `fig2_protected_attribute_sensitivity_rates.pdf/.png` (Overall sensitivity rates across conditions)
      * `fig3_domain_breakdown.pdf/.png` (Domain-level sensitivity breakdown comparison)
      * `fig4_behavioral_inconsistency.pdf/.png` (Generative decision inconsistency across seeds)
      * `complexity_combined.pdf/.png` (Input variable count density histogram)
      * `attribute_frequency_combined.pdf/.png` (Top-10 utilized sensitive demographics $2 \times 2$ grid)
    * **Heatmaps & Injected Thresholds:**
      * `attribute_pairs_heatmap_*.pdf/.png` (Pairwise co-occurrence heatmaps for Legacy, Expanded, Gemini, Grok, and Combined $2 \times 2$ grid)
      * `magic_numbers_chart_*.pdf/.png` (Arbitrary injected numeric thresholds for All4, Gemini, Grok, and Legacy)
      * `protected_bias_chart_all4.pdf/.png` (Top protected demographic classes across 4 conditions)
      * `inconsistency_chart_combined.pdf/.png` (Internal structural logic variance across conditions)
  * **What it contains:** Visual assets and plots corresponding to the figures in the manuscript.

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

   # Run synthetic ground-truth validation benchmark (Review Round 2)
   python src/statistical_analysis/verify_benchmark_accuracy.py

   # Generate all paper figures and diagrams
   python src/visualization/plot_primary_paper_figures.py
   python src/visualization/plot_process_flowchart.py
   python src/visualization/plot_combinatorial_space_growth.py
   python src/visualization/plot_monte_carlo_velocity.py
   python src/visualization/plot_attribute_cooccurrence_heatmaps.py
   python src/visualization/plot_threshold_and_bias_distributions.py
   ```

### Step 4: Synthetic Ground-Truth Benchmark Validation

To independently verify the classification precision, recall, and F1-score of the auditing pipeline against known ground truth (as detailed in Section 3):

```bash
# 1. Execute dynamic auditing on the 20-function benchmark suite
python src/logic_auditing/run_audit_dynamic.py \
  --generated-dir data/generated_functions_test \
  --partial-dir reports/partial_audit_results_test \
  --audit-report reports/raw_dumps/audit_report_test.json \
  --prompts-file data/dataset/prompts_unified_new.jsonl

# 2. Evaluate performance against established ground truth
python src/statistical_analysis/verify_benchmark_accuracy.py
```
* **Performance Result:** **100.00% Precision, 100.00% Recall, 1.0000 F1-Score (0 Errors)** across Output Variance, Sensitive Demographic Bias, and Unprompted Threshold Injections.

---

## 📂 Repository Structure

```
├── data/                               # Master datasets and LLM generated code
│   ├── dataset/
│   │   ├── prompts_old.jsonl           # Baseline legacy prompts
│   │   ├── prompts_expanded_new.jsonl  # Expanded range prompts
│   │   ├── prompts_unified_new.jsonl   # Standardized dataclass prompts
│   │   ├── synthetic_benchmark_ground_truth.json # 20 ground-truth validation records
│   │   └── unified_attributes.csv      # Master attribute dictionary (206 attributes)
│   ├── generated_functions_test/       # 20 hand-crafted benchmark test tasks
│   ├── generated_functions_gemini_legacy/ # Gemini Legacy code outputs
│   ├── generated_functions_gemini_expanded/ # Gemini Expanded code outputs
│   ├── generated_functions_gemini_unified/ # Gemini Unified code outputs
│   └── generated_functions_grok_unified/ # Grok Unified code outputs
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
│   ├── statistical_analysis/           # Table 1 aggregator, McNemar test, benchmark verifier
│   │   ├── compute_rigorous_metrics.py
│   │   ├── compute_mcnemar_exact.py
│   │   ├── domain_wise_bias_breakdown.py
│   │   └── verify_benchmark_accuracy.py # Synthetic benchmark precision/recall evaluation
│   └── visualization/                  # Matplotlib paper plots, R charts, & heatmaps
│       ├── plot_primary_paper_figures.py
│       ├── plot_process_flowchart.py
│       ├── plot_combinatorial_space_growth.py
│       ├── plot_monte_carlo_velocity.py
│       ├── plot_code_complexity_density.R
│       ├── plot_attribute_frequency.R
│       ├── plot_attribute_cooccurrence_heatmaps.py
│       └── export_appendix_prompts_latex.py
│
├── reports/                            # Summary reports, figures, and dumps
│   ├── summary/                        # Published summary JSON results
│   │   ├── protected_attribute_sensitivity_summary.json # Table 1 main results
│   │   ├── mcnemar_significance_test_results.json       # Paired hypothesis test results
│   │   ├── domain_wise_bias_breakdown_summary.json     # Figure 3 domain bias rates
│   │   └── monte_carlo_sampling_sensitivity_report.json # Monte Carlo budget stats
│   ├── figures/                        # Output PDF and PNG chart figures
│   ├── feature_metrics/                # Structured complexity, frequency, and threshold JSONs
│   │   ├── code_complexity_*.json      # Input variable complexity counts
│   │   ├── attribute_frequency_*.json  # Attribute usage frequencies per model
│   │   ├── injected_thresholds_*.json  # Arbitrary threshold injection metrics
│   │   └── protected_bias_rates_*.json # Protected attribute-wise bias rates
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

## 🔬 Experimental Parameters & Decoding Settings

To ensure controlled comparative conditions and reproducibility across API providers, the models were evaluated under the following settings (as described in the paper):
* **Decoding Parameters**:
  * **Google Gemini 2.5 Flash**: accessed using default API decoding parameters (`temperature = 1.0`, `top_p = 0.95`).
  * **xAI Grok-Code-Fast-1**: accessed using standard code generation settings (`temperature = 0.7`).

---

## 📜 Citation & References

If using this dataset, benchmark suite, or auditing framework, please cite:
* **AAAI 2025 Benchmark Base**: Ling et al., *"Bias Unveiled: Investigating Social Bias in LLM-Generated Code"*, AAAI 2025.
* **Git Release Tag**: [`v2.0.0`](https://github.com/Puspha22/llm-bias-comparative-analysis/releases/tag/v2.0.0).
