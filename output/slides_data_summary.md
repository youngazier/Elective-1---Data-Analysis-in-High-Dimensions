# Slide Deck Data Package & Presentation Guide (`slides_data_summary.md`)

**Course:** Data Analysis in High Dimensions (Prof. Dr. C. Andersson, VGU)  
**Presentation Date:** November 16, 2026 (3–5 min per person = 9–15 min total)  
**Team Members:**
1. **Tran Trong Nhan** (10423160)
2. **Nguyen Minh Nhat Huy** (10423045)
3. **Dao Hoang Minh Triet** (10423179)

All figures referenced below are saved in high-resolution PNG (for PowerPoint/Google Slides/Canva) and vector PDF (for LaTeX Beamer) in:
`/mnt/hdd-1tb/CSE-VGU/2026-2027/Elective-1/output/figures/`

---

## Suggested Speaker Split (3 Members × ~4 Minutes = 12 Minutes)

| Speaker | Time | Slides | Core Topics |
| :--- | :--- | :--- | :--- |
| **Speaker 1** | ~4 min | Slides 1–4 | Motivation, Research Questions (RQ1–RQ3), Survey Scenarios ($Q_1$–$Q_5$), Sample Demographics ($n=263$), Normalized Hamming Distance $d(\vec{X}_i,\vec{X}_j)$, Metric Properties, and why Centroid/Ward fail on nominal data. |
| **Speaker 2** | ~4 min | Slides 5–8 | Agglomerative Linkage Comparison (Single vs. Complete vs. Average/UPGMA), Cophenetic Correlation, Chaining Effect, Silhouette Selection ($K=2\dots 8$), Tie/Row-Order Sensitivity, and 80% Subsampling Stability (ARI). |
| **Speaker 3** | ~4 min | Slides 9–12 | The 6 Behavioral Student Archetypes ($K=6$ & $K=5$ hierarchy), External Validation with Weekly AI Usage ($Q_6$, $p=0.0103$) and Year of Study ($S_4$, $p=0.0001$), Methodological Strengths/Weaknesses (5 vs. 6 options), and Conclusions. |

---

## 1. Sample & Survey Overview (Slide 2–3 Data)

* **Total Eligible & Consented Sample:** $n = 263$ university students at VGU ($100\%$ answered `Yes` to $S_1$ and $S_2$; $0$ missing values across $Q_1$–$Q_6$).
* **Unique 5-Question Response Profiles:** $217$ unique profiles out of $6 \times 6 \times 5 \times 5 \times 6 = 5{,}400$ possible combinations.
  * Top recurring exact profiles across all 5 scenarios:
    * `B-B-A-B-B` ($n = 8$ students: pure independent problem-solvers)
    * `D-D-C-D-D` ($n = 7$ students: pure cross-AI & peer triangulators)
    * `C-C-B-C-C` ($n = 6$ students: pure same-AI conversationalists)
    * `F-F-E-D-F` ($n = 5$ students: pure AI-skeptical anchors)
    * `A-A-A-A-A` ($n = 4$ students: pure course-material verifiers)

### Demographic Breakdown ($S_4$ Year of Study & $S_3$ Major)

| Year of Study ($S_4$) | Count ($n$) | Share ($\%$) | Major ($S_3$) | Count ($n$) | Share ($\%$) |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **1st year** | 63 | 24.0% | **CSE** | 137 | 52.1% |
| **2nd year** | 66 | 25.1% | **ECE** | 10 | 3.8% |
| **3rd year** | 48 | 18.3% | **BCE / MEN** | 7 each | 2.7% each |
| **4th year** | 68 | 25.9% | **MEC / BBA / BFA** | 6 / 5 / 5 | 2.3% / 1.9% / 1.9% |
| **Graduate / Master's** | 12 | 4.6% | **Other VGU Programs** | 7 | 2.7% |
| **Unspecified** | 6 | 2.3% | **Unspecified** | 79 | 30.0% |

### Weekly Generative AI Usage for Coursework ($Q_6$: $0$–$7$ Days)
* **Mean:** $4.10$ days/week ($\text{SD} = 2.12$), **Median:** $4.0$ days ($\text{IQR} = 3.0$).
* **Distribution:** $0\text{d}: 6.5\%$ ($17$), $1\text{d}: 7.2\%$ ($19$), $2\text{d}: 10.6\%$ ($28$), $3\text{d}: 16.0\%$ ($42$), $4\text{d}: 12.9\%$ ($34$), $5\text{d}: 16.0\%$ ($42$), $6\text{d}: 14.1\%$ ($37$), $7\text{d}: 16.7\%$ ($44$).

---

## 2. Marginal Response Frequencies Across Scenarios $Q_1$–$Q_5$
*(Chart: `output/figures/fig01_marginal_responses.png`)*

| Scenario | Opt A | Opt B | Opt C | Opt D | Opt E | Opt F |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1: AI Disagrees with You** (6 opts) | **22.4%** (59)<br>*Course mat.* | **17.9%** (47)<br>*Re-solve self* | **20.5%** (54)<br>*Ask same AI* | **16%** (42)<br>*Ask diff. AI* | **12.5%** (33)<br>*Accept D* | **10.6%** (28)<br>*Keep B* |
| **Q2: Two AIs Disagree** (6 opts) | **25.1%** (66)<br>*Course mat.* | **19.8%** (52)<br>*Solve self* | **17.9%** (47)<br>*AI compare* | **14.8%** (39)<br>*Ask 3rd AI* | **11%** (29)<br>*Usual AI* | **11.4%** (30)<br>*Skip task* |
| **Q3: Missing Cited Paper** (5 opts) | **40.3%** (106)<br>*Search source* | **21.3%** (56)<br>*Ask AI DOI* | **15.6%** (41)<br>*Ask diff. AI* | **11%** (29)<br>*Omit citation* | **11.8%** (31)<br>*Remove claim* | — |
| **Q4: Unclear Reasoning Step** (5 opts) | **18.6%** (49)<br>*Course mat.* | **23.6%** (62)<br>*Derive self* | **24.3%** (64)<br>*Ask same AI* | **19.4%** (51)<br>*Ask peer* | **14.1%** (37)<br>*Use unclarified* | — |
| **Q5: AI Flips Answer on "Are you sure?"** (6 opts) | **23.6%** (62)<br>*Course mat.* | **20.5%** (54)<br>*Solve self* | **20.2%** (53)<br>*AI compare* | **15.6%** (41)<br>*Ask diff. AI* | **12.2%** (32)<br>*Accept D* | **8%** (21)<br>*Keep B* |

---

## 3. Normalized Hamming Distance Distribution ($34{,}453$ Pairs)
*(Chart: `output/figures/fig02_hamming_distribution.png`)*

$$d(\vec{X}_i, \vec{X}_j) = \frac{1}{5} \sum_{k=1}^{5} \mathbb{I}(X_{ik} \neq X_{jk}) \in \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$$

| Distance $d(\vec{X}_i, \vec{X}_j)$ | Matching Questions | Number of Pairs | Percentage of Pairs |
| :---: | :---: | :---: | :---: |
| **$0.0$** | 5 / 5 match | 104 | 0.30% |
| **$0.2$** | 4 / 5 match | 559 | 1.62% |
| **$0.4$** | 3 / 5 match | 2,184 | 6.34% |
| **$0.6$** | 2 / 5 match | 6,220 | 18.05% |
| **$0.8$** | 1 / 5 match | 12,422 | 36.05% |
| **$1.0$** | 0 / 5 match | 12,964 | 37.63% |
| **Total / Summary** | **Mean = $0.8016$** | **34,453 pairs** | **SD = $0.2005$, Median = $0.80$** |

* **Effect of 5 Options ($Q_3, Q_4$) vs. 6 Options ($Q_1, Q_2, Q_5$):**
  * Uniform random match probability: $1/6 = 16.7\%$ for $Q_1, Q_2, Q_5$ vs. $1/5 = 20.0\%$ for $Q_3, Q_4$.
  * Empirical pairwise match probability: $Q_1 = 17.7\%$, $Q_2 = 18.1\%$, $Q_5 = 18.4\%$, $Q_4 = 20.7\%$, and **$Q_3 = 25.8\%$** (highest because Option A "Independently search for another source" unites both textbook verifiers and independent solvers).

---

## 4. Linkage Comparison: Single vs. Complete vs. Average (RQ2)
*(Charts: `output/figures/fig03_dendrograms_comparison.png` & `fig04_silhouette_comparison.png`)*

* **Cophenetic Correlation Coefficients ($r_{\text{coph}}$):**
  * **Average Linkage (UPGMA):** $r_{\text{coph}} = \mathbf{0.6275}$ *(Best preservation of original pairwise Hamming distances)*
  * **Complete Linkage:** $r_{\text{coph}} = \mathbf{0.5253}$ *(Moderate preservation; sensitive to tie-breaking)*
  * **Single Linkage:** $r_{\text{coph}} = \mathbf{0.1449}$ *(Severe chaining distortion)*

### Partition Metrics Across $K = 2\dots 8$

| $K$ | Single: Avg Sil | Single: Cluster Sizes | Complete: Avg Sil | Complete: Cluster Sizes | Average: Avg Sil | Average: Cluster Sizes |
| :-: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2** | $+0.0605$ | `262/1` | $+0.0162$ | `258/5` | $+0.1030$ | `245/18` |
| **3** | $-0.0969$ | `263/1/1` | $-0.0371$ | `254/5/4` | $+0.1178$ | `179/66/18` |
| **4** | $-0.1555$ | `260/1/1/1` | $-0.0625$ | `246/8/5/4` | $+0.1186$ | `179/46/20/18` |
| **5** | $-0.1778$ | `259/1/1/1/1` | $-0.0682$ | `239/8/7/5/4` | $+0.1652$ | `124/55/46/20/18` |
| **6** | $-0.2113$ | `258/1/1/1/1/1` | $-0.0810$ | `234/8/7/5/5/4` | **$+0.2001$** | **`63/61/55/46/20/18`** |
| **7** | $-0.2267$ | `257/1/1/1/1/1/1` | $-0.0640$ | `221/13/8/7/5/5/4` | $+0.1993$ | `63/55/53/46/20/18/8` |
| **8** | $-0.2502$ | `256/1/1/1/1/1/1/1` | $-0.0788$ | `212/13/9/8/7/5/5/4` | $+0.1985$ | `63/55/53/46/18/12/8/8` |

---

## 5. Sensitivity & Subsampling Stability (RQ3)
*(Chart: `output/figures/fig05_stability_ari.png`)*

| Linkage Method | $K$ | Row-Permutation ARI (Mean ± SD) | 80% Subsampling ARI (Mean ± SD) | 80% Subsampling ARI (Median, IQR) |
| :--- | :-: | :---: | :---: | :---: |
| **Average (UPGMA)** | **5** | **$0.5731 \pm 0.1026$** | **$0.5549 \pm 0.1306$** | **$0.5743$ ($0.1691$)** |
| **Average (UPGMA)** | **6** | **$0.5106 \pm 0.0931$** | **$0.5221 \pm 0.0964$** | **$0.5324$ ($0.1084$)** |
| **Complete** | 5 | $0.1336 \pm 0.1409$ | $0.3224 \pm 0.1679$ | $0.3144$ ($0.2286$) |
| **Complete** | 6 | $0.1370 \pm 0.1094$ | $0.2982 \pm 0.1411$ | $0.2800$ ($0.1991$) |
| **Single** | 5 | $0.2916 \pm 0.1123$ | $0.7774 \pm 0.1785$* | $0.8536$ ($0.1934$)* |

*\*Note: Single linkage's high subsample ARI is an artifact of placing $>98\%$ of respondents into a single giant cluster.*

---

## 6. Behavioral Archetype Profiles: Average Linkage $K = 6$ (RQ1)
*(Chart: `output/figures/fig06_cluster_profiles.png`)*

At $K=5$, Clusters 3 and 4 below form a combined 124-student super-cluster (*Independent & Course-Material Verifiers*), which splits at $K=6$ into two distinct self-verification styles (raising $\bar{s}$ from $0.1652$ to its global peak of $0.2001$):

| Cluster & Archetype Name | Size ($n, \%$) | Dominant Strategy Across $Q_1$–$Q_5$ (Within-Cluster Modal Choice %) |
| :--- | :---: | :--- |
| **C1: Cross-AI & Peer Triangulators** | $46$ ($17.5\%$) | Consults a second/third AI or peer: **Q1-D** ($60.9\%$), **Q2-D** ($47.8\%$), **Q3-C** ($65.2\%$), **Q4-D** ($52.2\%$ ask classmate), **Q5-D** ($58.7\%$). |
| **C2: Same-AI Conversationalists** | $55$ ($20.9\%$) | Dialogues with the same AI to resolve conflict: **Q1-C** ($65.5\%$), **Q2-C** ($45.5\%$), **Q3-B** ($65.5\%$ ask AI for DOI), **Q4-C** ($83.6\%$), **Q5-C** ($56.4\%$). |
| **C3: Independent Problem-Solvers** | $61$ ($23.2\%$) | Re-derives/solves from scratch without AI: **Q1-B** ($57.4\%$), **Q2-B** ($54.1\%$), **Q3-A** ($60.7\%$ search Scholar), **Q4-B** ($70.5\%$ derive self), **Q5-B** ($62.3\%$). |
| **C4: Course-Material Verifiers** | $63$ ($24.0\%$) | Checks authoritative lecture notes/textbooks: **Q1-A** ($57.1\%$), **Q2-A** ($54.0\%$), **Q3-A** ($68.3\%$ search Scholar), **Q4-A** ($47.6\%$), **Q5-A** ($65.1\%$). |
| **C5: Uncritical AI Conformers** | $20$ ($7.6\%$) | Defers to AI without verification: **Q1-E** ($85.0\%$ switch to D), **Q2-B/E** ($40\%/35\%$), **Q3-D** ($60.0\%$ use claim & omit citation), **Q4-E** ($40.0\%$), **Q5-E** ($45.0\%$). |
| **C6: AI-Skeptical Anchors** | $18$ ($6.8\%$) | Rejects AI / sticks to own answer or drops task: **Q1-F** ($77.8\%$ keep B), **Q2-F** ($44.4\%$ leave unanswered), **Q3-E** ($61.1\%$ remove claim), **Q4-D/E** ($44.4\%/38.9\%$), **Q5-F** ($66.7\%$). |

---

## 7. External Validation: $Q_6$ (AI Usage) & $S_4$ (Year of Study)
*(Chart: `output/figures/fig07_external_validation.png`)*

Both external validation variables show **statistically significant differences** across the clusters (even though neither variable was used to form the clusters!):

1. **Weekly AI Usage Frequency ($Q_6$: $0$–$7$ days):**
   * **Kruskal-Wallis Test:** $H = 15.023, \text{df} = 5, \mathbf{p = 0.0103}$ ($p = 0.0097$ at $K=5$).
   * **One-Way ANOVA:** $F(5, 257) = 3.148, \mathbf{p = 0.0089}$ ($p = 0.0090$ at $K=5$).
2. **Year of Study ($S_4$, $n = 257$ known):**
   * **Pearson Chi-Square Test (10,000 Monte Carlo replicates):** $\chi^2 = 77.045, \mathbf{p = 0.0001}$ ($\chi^2 = 68.125, p = 0.0001$ at $K=5$).

| Cluster | $n$ | $Q_6$ Mean ± SD (Days/Wk) | $Q_6$ Median (IQR) | 1st Yr ($\%$) | 2nd Yr ($\%$) | 3rd Yr ($\%$) | 4th Yr ($\%$) | Grad/Master ($\%$) |
| :--- | :-: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C1: Cross-AI & Peer** | 46 | $3.67 \pm 2.04$ | $3.0$ ($2.75$) | 20.0% | 31.1% | 15.6% | 31.1% | 2.2% |
| **C2: Same-AI Probe** | 55 | **$4.67 \pm 1.86$** | **$5.0$ ($2.50$)** | 29.6% | 14.8% | 27.8% | 25.9% | 1.9% |
| **C3: Self-Solvers** | 61 | $3.89 \pm 2.29$ | $4.0$ ($4.00$) | 19.0% | **37.9%** | 10.3% | **32.8%** | 0.0% |
| **C4: Course Material** | 63 | $4.40 \pm 2.01$ | $5.0$ ($3.00$) | 23.8% | 23.8% | **28.6%** | 23.8% | 0.0% |
| **C5: AI Conformers** | 20 | **$2.85 \pm 1.95$** | **$3.0$ ($3.00$)** | **42.1%** | 5.3% | 5.3% | 15.8% | **31.6%** |
| **C6: Skeptic Anchors** | 18 | $4.44 \pm 2.43$ | $5.0$ ($4.75$) | 22.2% | 33.3% | 5.6% | 16.7% | **22.2%** |

### Key External Validation Takeaways for Your Slides:
* **Why do "Same-AI Conversationalists" (C2) have the highest AI usage ($4.67$ days/week) while "Uncritical AI Conformers" (C5) have the lowest ($2.85$ days/week)?**
  * Students who use AI heavily ($4.67$ days/week) are comfortable treating AI as an interactive dialogue partner (prompting it for DOIs, step-by-step explanations, and comparisons), whereas infrequent users ($2.85$ days/week, heavily 1st-year students at $42.1\%$) are more likely to passively accept AI outputs without follow-up prompting or verification.
* **Undergraduates (Years 2–4) dominate the active verification clusters (C1–C4):**
  * $100\%$ of **Course-Material Verifiers (C4)** and **Independent Problem-Solvers (C3)** are undergraduate students who actively cross-check AI against coursework formulas or re-derive steps themselves.

