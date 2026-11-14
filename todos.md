# Project Roadmap & Step-by-Step Progress (`todos.md`)

**Course:** Data Analysis in High Dimensions (Prof. Dr. C. Andersson, VGU)  
**Project Title:** *When AI Disagrees With You: How University Students Respond to Uncertain AI Answers*  
**Team Members:**
1. Tran Trong Nhan (10423160)
2. Nguyen Minh Nhat Huy (10423045)
3. Dao Hoang Minh Triet (10423179)

**Key Deadlines (`Infos.pdf`):**
- **Presentation:** November 16, 2026 (3–5 minutes per person = 9–15 minutes total for 3 members)
- **Final Report Submission:** November 25, 2026 (2–3 pages per person = **6–9 pages main body** + Appendix with R code)

---

## Phase 1: Data Cleaning & Preprocessing
- [x] **1.1 Load raw survey responses** from `When AI Disagrees With You_ How University Students Respond to Uncertain AI Answers (Responses) - Form Responses 1.csv` ($N = 263$ total rows).
- [x] **1.2 Verify eligibility & consent ($S_1, S_2$):** Confirm all respondents answered `Yes` to $S_1$ (currently enrolled university student) and $S_2$ (voluntary consent). Retain $n = 263$ complete responses.
- [x] **1.3 Assign anonymous respondent IDs:** Generate sequential IDs (`R001` to `R263`) and remove timestamps before clustering.
- [x] **1.4 Standardize & harmonize $Q_1$–$Q_5$ categorical labels (`A`–`F` / `A`–`E`):**
  - **Crucial Data Cleaning Fix in $Q_1$:** Harmonize the two wording variants of Option D (`"Ask a different AI the same question again."` [$n=29$] and `"Ask a different AI the original question."` [$n=13$]) into a single category `D` ($n=42$), ensuring $Q_1$ has the exact 6 options (`A`–`F`).
  - Map $Q_1, Q_2, Q_5$ to unordered factor levels `A`–`F` (6 options each) and $Q_3, Q_4$ to unordered factor levels `A`–`E` (5 options each).
- [x] **1.5 Clean external validation & demographic variables ($S_3, S_4, Q_6$):**
  - $S_4$ (Year of Study): Order levels (`1st year`, `2nd year`, `3rd year`, `4th year`, `Graduate / Master's student`, plus `Missing / Prefer not to answer` for the 6 blank entries).
  - $Q_6$ (AI Usage Frequency in past 7 days): Parse as integer/ordinal $0, 1, \dots, 7$ (complete for all $n=263$ respondents).
  - $S_3$ (Major at VGU): Clean blank strings ($78$ blanks) into `Unspecified / Prefer not to answer` for descriptive sample reporting.
- [x] **1.6 Check identical response profiles:** Count unique 5-question response patterns across the $n = 263$ students (keep duplicate profiles in the dataset as real observations representing common student habits).

---

## Phase 2: Exploratory Data Analysis (EDA)
- [x] **2.1 Demographic summary table:** Tabulate frequencies and percentages for $S_3$ (Major) and $S_4$ (Year of Study).
- [x] **2.2 Baseline AI usage ($Q_6$):** Compute mean, SD, median, IQR, and histogram/bar distribution of days using AI in the past week ($0$–$7$ days).
- [x] **2.3 Marginal response distributions ($Q_1$–$Q_5$):** Compute counts and percentages for every option (`A`–`F` / `A`–`E`) across the 5 scenarios and generate a summary stacked bar chart (`fig01_marginal_responses.pdf`).

---

## Phase 3: Dissimilarity Matrix & Agglomerative Hierarchical Clustering
- [x] **3.1 Compute Normalized Hamming / Gower Distance Matrix ($263 \times 263$):**
  - Use `cluster::daisy(df_q, metric = "gower")` in R and `scipy.spatial.distance.pdist(..., metric="hamming")` in Python.
  - Verify that all $\binom{263}{2} = 34{,}453$ pairwise distances lie in $\{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$.
  - Plot the distribution of pairwise Hamming distances (`fig02_hamming_distribution.pdf`).
- [x] **3.2 Build Agglomerative Dendrograms (`stats::hclust` / `scipy.cluster.hierarchy.linkage`):**
  - **Single Linkage** (`method = "single"`): $d_{12} = \min_{i,j} d(\vec{X}_i, \vec{Y}_j)$
  - **Complete Linkage** (`method = "complete"`): $d_{12} = \max_{i,j} d(\vec{X}_i, \vec{Y}_j)$
  - **Average Linkage / UPGMA** (`method = "average"`, primary method): $d_{12} = \frac{1}{kl}\sum_{i=1}^k \sum_{j=1}^l d(\vec{X}_i, \vec{Y}_j)$
- [x] **3.3 Compare Dendrograms & Cophenetic Correlation (RQ2):**
  - Calculate Cophenetic Correlation Coefficients ($r_{\text{coph}}$) for Single, Complete, and Average linkage.
  - Generate side-by-side dendrogram comparison plots (`fig03_dendrograms_comparison.pdf`).

---

## Phase 4: Optimal Number of Clusters & Stability / Sensitivity Checks
- [x] **4.1 Evaluate candidate partitions ($K \in \{2, 3, 4, 5, 6, 7, 8\}$):**
  - Cut each tree at $K = 2\dots 8$ using `cutree`.
  - Compute Average Silhouette Width (`cluster::silhouette`), minimum cluster size, maximum cluster size, and proportion of negative silhouette scores (`fig04_silhouette_comparison.pdf`).
  - Document the **chaining effect** in Single Linkage vs. balanced partitions in Average and Complete Linkage.
- [x] **4.2 Select optimal $K$ for Average Linkage:**
  - Balance average silhouette width, cluster interpretability, and minimum group size to select the primary partition $K^*$.
- [x] **4.3 Sensitivity to Row Order / Distance Ties (RQ3):**
  - Randomly permute respondent row order 100 times, re-run `hclust` + `cutree`, match respondents by ID, and compute Adjusted Rand Index (ARI) against the original row order.
- [x] **4.4 Subsampling Stability Analysis (RQ3):**
  - Draw 100 random subsamples of 80% of respondents ($n_{\text{sub}} = 209$) without replacement, re-run hierarchical clustering with $K^*$, and compute ARI against the full-sample cluster assignments (`fig05_stability_ari.pdf`).

---

## Phase 5: Cluster Profiling & External Validation ($S_4$ and $Q_6$)
- [x] **5.1 Behavioral Archetype Profiling ($Q_1$–$Q_5$, RQ1):**
  - Calculate exact within-cluster option percentages for all 5 scenarios.
  - Generate a visual cluster profile heatmap / distribution chart (`fig06_cluster_profiles.pdf`).
  - Assign descriptive, data-driven names to each cluster based on their dominant verification or reliance strategies.
- [x] **5.2 External Validation 1 — Year of Study ($S_4$):**
  - Cross-tabulate Cluster Membership $\times$ Year of Study ($S_4$, excluding missing responses).
  - Run Chi-square test of independence ($\chi^2$) and simulated/Fisher exact p-value (`fig07_external_validation.pdf`).
- [x] **5.3 External Validation 2 — AI Usage Frequency ($Q_6$):**
  - Compute cluster-wise mean, SD, median, and IQR of $Q_6$ (days per week using AI).
  - Run non-parametric Kruskal-Wallis test and one-way ANOVA ($F$-test) across clusters, and plot violin/boxplots + stacked distributions (`fig07_external_validation.pdf`).

---

## Phase 6: Deliverables & Report Compilation
- [x] **6.1 Reproducible R Code (`code/analysis.R`):** Complete script generating all tables, statistical tests, and figures (also embedded in the LaTeX report Appendix).
- [x] **6.2 Reproducible Python Code (`code/analysis.py`):** Equivalent script cross-checking all distances, silhouette scores, stability metrics, and external validation tests.
- [x] **6.3 Presentation Data Package (`output/slides_data_summary.md` & `output/tables/*.csv`):** Slide-by-slide data tables, exact metrics, and speaker breakdown for the Nov 16 presentation.
- [x] **6.4 LaTeX Report (`report/main.tex` & `report/main.pdf`):**
  - Compiled 6–9 page main report following the Research Proposal outline and Prof. Dr. C. Andersson's lecture notation (`vorlesung-1.pdf`), plus Appendix containing the R code and full tables.

---

## Phase 7: Remaining Action Items for the Team (Human Tasks)
- [ ] **7.1 Review the Behavioral Archetype Names:** Check the data-driven cluster names in `output/slides_data_summary.md` and `report/main.pdf` and adjust wording if the team prefers alternative labels.
- [ ] **7.2 Build Presentation Slides (Deadline: Nov 16, 2026):**
  - Use the figures in `output/figures/` and bullet points/tables in `output/slides_data_summary.md`.
  - Split speaking roles across the 3 members (3–5 minutes per member, ~12 minutes total):
    - **Speaker 1 (3–4 min):** Motivation, Survey Scenarios ($Q_1$–$Q_5$), Hamming Distance & Mathematical Properties (Symmetry, Positivity, Identity, Triangle Inequality), and why Centroid/Ward fail on nominal data.
    - **Speaker 2 (4 min):** Agglomerative Linkage Comparison (Single vs. Complete vs. Average/UPGMA), Chaining Effect, Silhouette Selection of $K$, and Tie/Subsampling Stability (ARI).
    - **Speaker 3 (4 min):** Behavioral Cluster Profiles (RQ1), External Validation with Year of Study ($S_4$) and Weekly AI Usage ($Q_6$), Limitations (including 5-option vs. 6-option baseline match probability), and Conclusions.
- [ ] **7.3 Final Proofread & Moodle Submission (Deadline: Nov 25, 2026):**
  - Proofread `report/main.pdf` as a team and submit the PDF report on Moodle.

