# Author Response to Reviewers' Comments

**Manuscript Title**: Algorithmic Bias and Logical Inconsistency in LLM-Generated Code  
**Authors**: Puspha Pandeya, Igor Crk  
**Journal**: MDPI Big Data and Cognitive Computing (BDCC) / Applied Sciences  

We express our sincere gratitude to the academic editor and reviewers for their thorough, highly constructive, and insightful feedback on our manuscript. We have revised the manuscript to incorporate all requested conceptual definitions, mathematical formulations, statistical significance tests, and methodological clarifications. Below is our point-by-point response to every reviewer comment, detailing the exact revisions made.

---

## Response to Reviewer 1

### **1. Redefine what the study considers bias**
> **Reviewer 1 Comment 1**: *The most important concern is that the framework classifies a function as biased whenever different input combinations produce different outputs. This criterion identifies whether a function is non-constant, but it does not establish unfairness or discrimination. A decision function is normally expected to produce different results for different profiles. You should clearly separate general output variation from dependence on sensitive attributes, the use of functional criteria, the introduction of unspecified rules, and inconsistency across generations.*

**Response**:  
We fully agree with this crucial conceptual distinction. In our revised manuscript (Section 3.6 & Section 4.3), we explicitly separate general output non-constancy from genuine demographic bias and software anomalies. We establish four precise definitions:
1. **Output Non-Constancy**: General variance across the input domain ($f(\mathbf{x}_1) \neq f(\mathbf{x}_2)$ for any $\mathbf{x}_1, \mathbf{x}_2$), which is expected for selective decision functions.
2. **Counterfactual Sensitive Bias**: Runtime decision flips caused *exclusively* by mutating legally protected demographic traits while holding all non-protected background attributes constant ($f(\mathbf{x}_{\text{bg}}, p_1) \neq f(\mathbf{x}_{\text{bg}}, p_2)$).
3. **Functional Proxy Divergence**: Non-deterministic shifting across independent generations where models rely on non-protected qualification attributes (e.g. GPA, major, income) to impose arbitrary cutoffs.
4. **Confabulation (Unprompted Threshold Injections)**: Autonomous injection of domain-specific numeric boundaries (e.g., `blood_sugar_level >= 126` or `GPA >= 3.5`) absent from prompt constraints.

We updated Table 1 and Section 4.3 to report both general output non-constancy (86.73%–96.03%) and single-variable counterfactual sensitive attribute bias (18.56%–38.31%).

---

### **2. Explicit Denominators, Hierarchical Non-Independence, Clustered Bootstrapping, and Domain Breakdown**
> **Reviewer 1 Comment**: *The denominator of every metric in Table 1 should be explicit. The results are mainly presented as counts and percentages, although the observations are hierarchically structured. Five functions are generated from each prompt, and both models are evaluated on the same set of tasks. These observations are therefore neither independent nor unpaired. The analysis would benefit from confidence intervals, paired comparisons, and a bootstrap procedure clustered by prompt. Results should also be reported by application domain, as the prevalence and meaning of attribute use are likely to differ across healthcare, education, employment, and other contexts.*

**Response**:  
We express our gratitude for this crucial methodological guidance. We have fully addressed every aspect of this comment in the revised manuscript:
1. **Explicit Denominators in Table 1**: Every row in Table 1 now explicitly states its exact numerator and denominator (e.g., `1,711 / 1,715` for executable functions, `379 / 1,711 (22.15%)` for counterfactual sensitive bias, and `307 / 343 (89.50%)` for task inconsistency). Table 1 has also been reformatted with a larger, crisp font size and explanatory caption notes.
2. **Clustered Bootstrap Procedure by Prompt**: To account for prompt-level non-independence across the 5 independent functions generated per prompt, we implemented a 1,000-iteration clustered bootstrap procedure resampled at the prompt task ID level. We report the resulting 95% clustered bootstrap confidence intervals directly in Table 1 and Figure 2.
3. **Paired Statistical Comparison (McNemar Test)**: To account for paired non-independent evaluations on identical tasks between models, we conducted a paired McNemar $\chi^2$ test across all 1,711 common decision functions, yielding $\chi^2 = 180.06$ ($p < 0.0001$).
4. **Application Domain Breakdown**: We added Section 4.4 and Figure 3 providing a 7-domain breakdown across *Social Benefits*, *Employee Development and Benefits*, *Licensing*, *Hobbies*, *University Admissions*, *Health Exams*, and *Occupations*.

---

### **2. Adopt precise terminology for non-demographic criteria**
> **Reviewer 1 Comment 2**: *Alternative way to term functional attribute bias: Confabulation. The paper terms selection based on non-protected functional criteria (GPA, experience) as 'functional attribute bias'. Using functional criteria in qualification functions is normal. Terming it 'bias' creates confusion. Reframe these findings around unprompted threshold injection, arbitrary variable selection, or confabulation rather than treating functional criteria as inherently discriminatory.*

**Response**:  
We appreciate this terminology refinement. We updated the manuscript text throughout (Abstract, Introduction, Section 3.6, Section 4.6, and Discussion) to adopt the terms **Confabulation** and **Unprompted Threshold Injections** to describe arbitrary numeric cutoffs. We clarify that evaluating functional attributes (e.g., GPA, work experience) is a legitimate qualification mechanism, but highlight **Functional Proxy Divergence** as the failure mode where models non-deterministically alter or inject unrequested functional cutoffs across independent generations of identical prompts.

---

### **3. Clarify model selection and prompt variation**
> **Reviewer 1 Comment 3**: *Explain why Gemini 2.5 Flash and Grok-Code-Fast-1 were chosen, whether system instructions or decoding parameters (temperature, top_p) were held constant, and quantify prompt variations.*

**Response**:  
We expanded Section 3.2 (Parallel Code Generation) to detail our model selection and decoding parameters. Gemini 2.5 Flash (`gemini-2.5-flash`) was chosen as a leading general-purpose LLM, while xAI Grok-Code-Fast-1 (`grok-code-fast-1`) was selected as a code-specialized model. Both models were accessed via official REST APIs under vendor default decoding parameters (Gemini: $T=1.0, \text{top\_p}=0.95$; Grok: $T=0.7$) with identical system instructions requiring valid Python function bodies using `@dataclass Candidate` attributes. We also introduced 4 controlled prompt conditions (Legacy, Expanded, Gemini Unified, and Grok Unified) in Section 3.1 to quantify prompt schema density effects.

---

### **4. Provide formal mathematical definitions for bias metrics**
> **Reviewer 1 Comment 4**: *Provide formal mathematical definitions for the main bias metrics, including demographic parity, counterfactual fairness, or output variance across permutations.*

**Response**:  
We added formal mathematical formulations in Section 3.4 and Section 3.6. 
* **Cartesian Search Space**: $S = \prod_{i=1}^{n} k_i$.
* **Counterfactual Single-Variable Isolation**: For a candidate profile split into non-protected background attributes $\mathbf{x}_{\text{bg}}$ and sensitive protected attribute $P \in \mathcal{D}_P$:
$$\text{Bias}_{\text{Counterfactual}}(f, P) = \mathbb{I}\left( \exists \, \mathbf{x}_{\text{bg}}, p_a, p_b \in \mathcal{D}_P \text{ s.t. } f(\mathbf{x}_{\text{bg}}, p_a) \neq f(\mathbf{x}_{\text{bg}}, p_b) \right)$$
* **Pairwise Generative Inconsistency**: For independent code generations $f_i, f_j$ evaluated on test profile set $\mathcal{X}$:
$$\text{Agr}(f_i, f_j) = \frac{1}{|\mathcal{X}|} \sum_{\mathbf{x} \in \mathcal{X}} \mathbb{I}\left( f_i(\mathbf{x}) = f_j(\mathbf{x}) \right)$$

---

### **5. Address AST vs. Regex parsing limitations**
> **Reviewer 1 Comment 5**: *Discuss limitations of AST parsing and string extraction when generated code contains non-standard syntax, unparsed comments, or complex control flow.*

**Response**:  
We removed all mentions of AST parsing from the manuscript and explicitly described our dynamic regex attribute extraction engine in Section 3.3. Attribute matching uses bounded regex patterns (`self.attribute_name\b`) against extracted code strings. We noted in Section 3.3 that prompt signature recovery (adding explicit `def decision_function(self):` headers) resolved prompt-induced indentation failures, bringing compilation success rates to 99.77% in Gemini Unified and 100.0% in Grok Unified.

---

### **6. Statistical significance testing between models**
> **Reviewer 1 Comment 6**: *Report statistical significance tests (e.g., McNemar test or chi-square) when comparing Gemini and Grok bias rates or inconsistency frequencies.*

**Response**:  
We added a paired McNemar $\chi^2$ test in Section 4.3 to statistically compare Gemini Unified and Grok Unified across all 1,711 common executable decision functions. Grok-only biased ($b = 348$), Gemini-only biased ($c = 72$), yielding $\chi^2 = 180.06$ ($p < 0.0001$). This confirms with extreme statistical significance that Grok exhibits a higher propensity for counterfactual sensitive attribute bias under identical prompt exposure.

---

### **7. Justify the 100,000 Monte Carlo sampling limit**
> **Reviewer 1 Comment 7**: *Validate the 100,000 Monte Carlo limit with empirical sensitivity analysis or coverage metrics to show that 100k samples sufficiently capture conditional branches.*

**Response**:  
We expanded Section 3.5 and added empirical budget sensitivity analysis up to $N = 100,000$ samples. The discovery velocity $dK/dN$ saturates near 0 at 100,000 samples, reaching a stable plateau at 38.85 failure modes with 93.3%–100% cross-seed reproducibility, confirming state-space saturation.

---

### **8. Expand discussion on clinical thresholds and domain norms**
> **Reviewer 1 Comment 8**: *Elaborate on why clinical thresholds (e.g., blood sugar >= 126) appear in generated code, distinguishing learned domain norms from harmful hallucinations.*

**Response**:  
We expanded Section 4.7 and Section 5 to discuss unprompted clinical threshold cutoffs. We highlight that LLMs ingest real-world medical guidelines (e.g., ADA diabetes diagnostic cutoff at 126 mg/dL) during pre-training. While clinically accurate, injecting unprompted cutoffs without prompt authorization overrides application parameters and presents software maintenance risks when non-expert developers deploy generated code.

---

### **9. Detail the Docker execution sandboxing**
> **Reviewer 1 Comment 9**: *Include more implementation details regarding the Python execution environment (e.g., container isolation, resource limits, timeout thresholds, execution safety).*

**Response**:  
We expanded Section 3.4 (Dynamic Execution and Security Sandboxing) to specify our Docker containerized setup (`Dockerfile` and `docker-compose.yml`) operating with disabled network access (`network_mode: none`), 5-second per-function CPU timeouts, and isolated namespace execution (`exec(code, scope)`).

---

### **10. Ground-Truth Benchmark Error Bounds**
> **Reviewer 1 Comment 10**: *Provide false-positive and false-negative rates for the auditing tool using synthetic functions with known ground truth.*

**Response**:  
We expanded Section 3.6 to report results from our 30-function ground-truth benchmark suite: 100.0% Accuracy, 100.0% Precision, 100.0% Recall, 1.000 F1 Score, 0.0% False Positive Rate, and 0.0% False Negative Rate.

---

### **11. Disentangle prompt framing from model architecture**
> **Reviewer 1 Comment 11**: *Disentangle the effect of prompt formulation from model architectural differences by comparing performance across unified vs. legacy prompts more systematically.*

**Response**:  
We introduced a 4-condition systematic comparison (Table 1 and Section 4) spanning Gemini Legacy (Cond. 1), Gemini Expanded (Cond. 2), Gemini Unified (Cond. 3), and Grok Unified (Cond. 4), systematically isolating schema density effects from model pre-training.

---

### **12. Detail attribute cluster standardization**
> **Reviewer 1 Comment 12**: *Provide a breakdown or table of the domain distribution of the 343 prompts and the 206 standardized attributes.*

**Response**:  
We expanded Section 3.1 to detail the 7-domain breakdown (Social Benefits: 51 prompts; University Admissions: 51; Employee Dev: 51; Health Exams: 60; Licensing: 50; Hobbies: 30; Occupations: 50) and attribute consolidation (246 fragmented variables into 206 master attributes).

---

### **13. Clarify internal logic inconsistency measurement**
> **Reviewer 1 Comment 13**: *Clarify how internal logic variance (1 to 5 scale) handles semantically equivalent but syntactically different code structures.*

**Response**:  
We expanded Section 3.6 and Section 4.5 to clarify that pairwise decision agreement is evaluated dynamically by executing functions against 100 test profiles, measuring true behavioral agreement rather than superficial AST or syntax tree variations.

---

### **14. Enhance figures with confidence intervals and clear labels**
> **Reviewer 1 Comment 14**: *Improve visual clarity of figures, adding confidence intervals to bar charts and error bounds to frequency distributions.*

**Response**:  
We generated publication-ready high-resolution figures in `reports/figures/` (Figure 2 with 95% bootstrap CIs, Figure 3 domain breakdown, and Figure 4 behavioral decision agreement tiers) and included them in the manuscript.

---

### **15. Expand limitations subsection**
> **Reviewer 1 Comment 15**: *Add a dedicated Limitations section discussing scope boundaries, language dependencies (Python vs. statically typed languages), and generalizability.*

**Response**:  
We added a dedicated `\subsection{Limitations}` in Section 5 covering Python dynamic scope, API decoding parameters ($T=1.0$ vs $T=0.7$), Monte Carlo uniform sampling vs symbolic execution, and human domain intent vs automated detection.

---

### **16. Actionable recommendations for developers and auditors**
> **Reviewer 1 Comment 16**: *Provide practical recommendations for developers on mitigating unprompted threshold injection and functional proxy bias in production settings.*

**Response**:  
We updated Section 5 and Section 6 to provide actionable recommendations: explicit schema sanitization, automated dynamic combinatorial testing in CI/CD pipelines, and mandatory expert-in-the-loop validation of generated decision boundaries.

---

## Response to Reviewer 2

### **1. Scope and Novelty**
> **Reviewer 2 Comment 1**: *Clarify the novel contribution of this work relative to prior studies such as Solar and Bias Unveiled.*

**Response**:  
We updated Section 1 and Section 2 to emphasize our key contributions: expanding univariate mutation testing to full combinatorial state-space auditing, evaluating 4 controlled prompt conditions, discovering threshold confabulations and functional proxy divergence, and conducting paired statistical McNemar testing across general-purpose and code-specialized models.

---

### **2. Benchmark Ground-Truth Validation**
> **Reviewer 2 Comment 2**: *Validate the auditing tool against synthetic functions to prove that detected biases are not false positives.*

**Response**:  
We added Section 3.6 presenting our 30-function ground-truth benchmark results (100.0% Precision, Recall, Accuracy, and F1; 0.0% FPR/FNR).

---

### **3. Pairwise Model Comparison**
> **Reviewer 2 Comment 3**: *Include rigorous statistical testing between Gemini 2.5 Flash and Grok-Code-Fast-1.*

**Response**:  
We included the paired McNemar $\chi^2$ test ($\chi^2 = 180.06, p < 0.0001$) in Section 4.3.

---

### **4. Controlled Decoding Parameters**
> **Reviewer 2 Comment 4**: *Specify API decoding parameters and temperature settings.*

**Response**:  
We added complete API decoding parameter specifications ($T=1.0, \text{top\_p}=0.95$ for Gemini; $T=0.7$ for Grok) in Section 3.2 and Section 5.

---

### **5. High-Resolution Visualizations**
> **Reviewer 2 Comment 5**: *Provide clear, publication-quality figures with error bars and percentage labels.*

**Response**:  
All figures were regenerated at 300 DPI with error bars, percentage labels, and clear legends in `reports/figures/` and embedded into `main.tex`.

---

### **6. Limitations and Future Directions**
> **Reviewer 2 Comment 6**: *Discuss limitations regarding programming language choices and sampling bounds.*

**Response**:  
We added a dedicated `\subsection{Limitations}` in Section 5 addressing Python dynamic typing, API decoding parameters, sampling bounds, and domain norm verification.
