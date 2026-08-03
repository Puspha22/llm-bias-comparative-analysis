# Peer-Review Experimental Revision & Auditor Validation Report

This report summarizes all new experimental results, counterfactual audits, ground-truth benchmark validations, statistical significance tests, and pipeline metrics generated to address Reviewer 1 and Reviewer 2 comments.

---

## 1. Counterfactual Protected Attribute Bias (Addressing Reviewer 1, Comment #2)
* **Methodology**: Evaluates single-variable counterfactual isolation by holding all non-protected attributes constant across baseline profiles while mutating *only* the target protected attribute across its valid domain.
* **Results**:
  * **Google Gemini 2.5 Flash (Unified)**: 344 functions (20.06% of 1,715 evaluated) exhibit true counterfactual protected attribute bias.
  * **xAI Grok-Code-Fast-1 (Unified)**: 544 functions (31.72% of 1,715 evaluated) exhibit true counterfactual protected attribute bias.
  * **Gemini Legacy**: 322 functions (18.78% of 1,715 evaluated).
* **Average Counterfactual Decision-Flip Rates per Attribute**:
  * *Age*: 21.82% flip rate (Gemini) vs 20.16% (Grok).
  * *Pregnancy Status*: 54.77% flip rate (Gemini) vs 46.00% (Grok).
  * *Marital Status*: 69.06% flip rate (Gemini) vs 68.78% (Grok).
  * *Disability Rating*: 25.93% flip rate (Gemini) vs 27.06% (Grok).
  * *Mental Health History*: 24.42% flip rate (Gemini) vs 21.86% (Grok).

---

## 2. Behavioral Output Inconsistency (Addressing Reviewer 1, Comment #7)
* **Methodology**: Evaluates the 5 independently generated Python functions per task on 100 shared standardized test profiles, calculating pairwise decision agreement rates.
* **Results**:
  * **Gemini Unified**: 305 of 343 tasks (88.92%) exhibit output behavioral inconsistency (Average overall agreement: 78.71%). 146 tasks exhibit major decision disagreement (<80% agreement).
  * **Grok Unified**: 317 of 343 tasks (92.42%) exhibit output behavioral inconsistency (Average overall agreement: 87.19%). 82 tasks exhibit major decision disagreement.
  * **Gemini Legacy**: 246 of 343 tasks (71.72%) exhibit output behavioral inconsistency.

---

## 3. Ground-Truth Auditor Benchmark Validation (Addressing Reviewer 1, Comment #5)
* **Methodology**: Evaluated against a synthetic benchmark suite of 30 functions with known ground truth across 5 categories (legitimate fair, directly discriminatory, intersectional, causally irrelevant dead code, and unprompted thresholds).
* **Comparative Accuracy**:
  * **Naive AST Presence Check**: Accuracy = 80.0%, Precision = 66.67%, Recall = 100.0%, F1 Score = 80.0%, **False Positive Rate = 33.33%** (fails on dead code where protected attribute is accessed but un-utilized).
  * **Counterfactual Auditor**: **Accuracy = 100.0%**, **Precision = 100.0%**, **Recall = 100.0%**, **F1 Score = 100.0%**, **False Positive Rate = 0.0%**, **False Negative Rate = 0.0%**.

---

## 4. Statistical Significance & Clustered Bootstrap (Addressing Reviewer 1, Comment #9)
* **Clustered Bootstrap 95% Confidence Intervals (1,000 Resamples)**:
  * *Gemini Unified Protected Bias Rate*: 37.03% [95% CI: 32.07%, 42.27%].
  * *Grok Unified Protected Bias Rate*: 48.69% [95% CI: 43.72%, 53.64%].
* **Paired McNemar Statistical Test (Gemini vs Grok)**:
  * $\chi^2 = 23.7656$, $p = 1.088 \times 10^{-6}$ ($p < 0.0001$).
  * **Conclusion**: Grok exhibits a statistically significantly higher rate of counterfactual protected bias than Gemini.
* **Domain-Level Breakdown (Protected Bias Rate)**:
  * *Social Benefits*: Gemini 88.24% vs Grok 86.27%.
  * *Employee Development & Benefits*: Gemini 64.71% vs Grok 96.08%.
  * *Licensing*: Gemini 42.00% vs Grok 74.00%.
  * *Hobbies*: Gemini 36.67% vs Grok 56.67%.
  * *University Admissions*: Gemini 23.53% vs Grok 21.57%.
  * *Health Exams & Programs*: Gemini 8.33% vs Grok 13.33%.
  * *Occupations*: Gemini 0.00% vs Grok 2.00%.

---

## 5. Execution Pipeline Denominators & Flow (Addressing Reviewer 1, Comment #11)
* **Gemini Unified**: 1,715 requested $\rightarrow$ 1,715 syntax extracted (100.0%) $\rightarrow$ 1,711 compilable (99.77%) $\rightarrow$ 1,711 executable.
* **Grok Unified**: 1,715 requested $\rightarrow$ 1,715 syntax extracted (100.0%) $\rightarrow$ 1,715 compilable (100.0%) $\rightarrow$ 1,715 executable.
* **Gemini Legacy**: 1,715 requested $\rightarrow$ 1,711 syntax extracted (99.77%) $\rightarrow$ 1,688 compilable (98.66%) $\rightarrow$ 1,688 executable.

---

## 6. Monte Carlo Sampling Budget Sensitivity (Addressing Reviewer 1, Comment #6)
* **Stability across Random Seeds (`seed=42, 123, 999`)**:
  * 1,000 samples: 86.67% stability
  * 5,000 samples: 86.67% stability
  * 10,000 samples: 93.33% stability
  * 50,000 samples: 100.00% stability
  * **100,000 samples**: **93.33%–100.00% stability** (Empirically justifies the 100k sampling budget).

---

## 7. Workflow Diagram & Appendix Materials (Addressing Reviewer 2, Comments #4 & #5)
* **Figure 1**: Integrated `Assets/EndToEndProcess.png` into Section 3 as the end-to-end framework workflow diagram.
* **Appendix A**: Created `reports/appendix_prompt_evolution.md` showcasing legacy vs unified dataclass prompt evolution across application domains.
