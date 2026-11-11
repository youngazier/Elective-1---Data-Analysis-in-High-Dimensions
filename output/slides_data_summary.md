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
| **Speaker 1** | ~4 min | Slides 1–4 | Motivation, Research Questions (RQ1–RQ3), Survey Scenarios ($Q_1$–$Q_5$), Sample Demographics ($n=261$), Normalized Hamming Distance $d(\vec{X}_i,\vec{X}_j)$, Metric Properties, and why Centroid/Ward fail on nominal data. |
| **Speaker 2** | ~4 min | Slides 5–8 | Agglomerative Linkage Comparison (Single vs. Complete vs. Average/UPGMA), Cophenetic Correlation, Chaining Effect, Silhouette Selection ($K=2\dots 8$), Tie/Row-Order Sensitivity, and 80% Subsampling Stability (ARI). |
| **Speaker 3** | ~4 min | Slides 9–12 | The 6 Behavioral Student Archetypes ($K=6$ & $K=5$ hierarchy), External Validation with Weekly AI Usage ($Q_6$, $p=0.0147$) and Year of Study ($S_4$, $p=0.0001$), Methodological Strengths/Weaknesses (5 vs. 6 options), and Conclusions. |

---

## 1. Sample & Survey Overview (Slide 2–3 Data)

* **Total Eligible & Consented Sample:** $n = 261$ university students at VGU ($100\%$ answered `Yes` to $S_1$ and $S_2$; $0$ missing values across $Q_1$–$Q_6$).
* **Unique 5-Question Response Profiles:** $215$ unique profiles out of $6 \times 6 \times 5 \times 5 \times 6 = 5{,}400$ possible combinations.
  * Top recurring exact profiles across all 5 scenarios:
    * `B-B-A-B-B` ($n = 8$ students: pure independent problem-solvers)
    * `D-D-C-D-D` ($n = 7$ students: pure cross-AI & peer triangulators)
    * `C-C-B-C-C` ($n = 6$ students: pure same-AI conversationalists)
    * `F-F-E-D-F` ($n = 5$ students: pure AI-skeptical anchors)
    * `A-A-A-A-A` ($n = 4$ students: pure course-material verifiers)

### Demographic Breakdown ($S_4$ Year of Study & $S_3$ Major)

| Year of Study ($S_4$) | Count ($n$) | Share ($\%$) | Major ($S_3$) | Count ($n$) | Share ($\%$) |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **1st year** | 63 | 24.1% | **CSE** | 136 | 52.1% |
| **2nd year** | 65 | 24.9% | **ECE** | 10 | 3.8% |
| **3rd year** | 48 | 18.4% | **BCE / MEN** | 7 each | 2.7% each |
| **4th year** | 67 | 25.7% | **MEC / BBA / BFA** | 6 / 5 / 4 | 2.3% / 1.9% / 1.5% |
| **Graduate / Master's** | 12 | 4.6% | **Other VGU Programs** | 7 | 2.7% |
| **Unspecified** | 6 | 2.3% | **Unspecified** | 79 | 30.3% |

### Weekly Generative AI Usage for Coursework ($Q_6$: $0$–$7$ Days)
* **Mean:** $4.09$ days/week ($\text{SD} = 2.13$), **Median:** $4.0$ days ($\text{IQR} = 3.0$).
* **Distribution:** $0\text{d}: 6.5\%$ ($17$), $1\text{d}: 7.3\%$ ($19$), $2\text{d}: 10.7\%$ ($28$), $3\text{d}: 16.1\%$ ($42$), $4\text{d}: 13.0\%$ ($34$), $5\text{d}: 15.3\%$ ($40$), $6\text{d}: 14.2\%$ ($37$), $7\text{d}: 16.9\%$ ($44$).

---

## 2. Marginal Response Frequencies Across Scenarios $Q_1$–$Q_5$
*(Chart: `output/figures/fig01_marginal_responses.png`)*

| Scenario | Opt A | Opt B | Opt C | Opt D | Opt E | Opt F |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1: AI Disagrees with You** (6 opts) | **22.6%** (59)<br>*Course mat.* | **18.0%** (47)<br>*Re-solve self* | **20.3%** (53)<br>*Ask same AI* | **15.7%** (41)<br>*Ask diff. AI* | **12.6%** (33)<br>*Accept D* | **10.7%** (28)<br>*Keep B* |
| **Q2: Two AIs Disagree** (6 opts) | **24.9%** (65)<br>*Course mat.* | **19.9%** (52)<br>*Solve self* | **18.0%** (47)<br>*AI compare* | **14.6%** (38)<br>*Ask 3rd AI* | **11.1%** (29)<br>*Usual AI* | **11.5%** (30)<br>*Skip task* |
| **Q3: Missing Cited Paper** (5 opts) | **40.2%** (105)<br>*Search source* | **21.1%** (55)<br>*Ask AI DOI* | **15.7%** (41)<br>*Ask diff. AI* | **11.1%** (29)<br>*Omit citation* | **11.9%** (31)<br>*Remove claim* | — |
| **Q4: Unclear Reasoning Step** (5 opts) | **18.8%** (49)<br>*Course mat.* | **23.8%** (62)<br>*Derive self* | **23.8%** (62)<br>*Ask same AI* | **19.5%** (51)<br>*Ask peer* | **14.2%** (37)<br>*Use unclarified* | — |
| **Q5: AI Flips Answer on "Are you sure?"** (6 opts) | **23.4%** (61)<br>*Course mat.* | **20.7%** (54)<br>*Solve self* | **19.9%** (52)<br>*AI compare* | **15.7%** (41)<br>*Ask diff. AI* | **12.3%** (32)<br>*Accept D* | **8.0%** (21)<br>*Keep B* |

---

## 3. Normalized Hamming Distance Distribution ($33{,}930$ Pairs)
*(Chart: `output/figures/fig02_hamming_distribution.png`)*

$$d(\vec{X}_i, \vec{X}_j) = \frac{1}{5} \sum_{k=1}^{5} \mathbb{I}(X_{ik} \neq X_{jk}) \in \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$$

| Distance $d(\vec{X}_i, \vec{X}_j)$ | Matching Questions | Number of Pairs | Percentage of Pairs |
| :---: | :---: | :---: | :---: |
| **$0.0$** | 5 / 5 match | 104 | 0.31% |
| **$0.2$** | 4 / 5 match | 549 | 1.62% |
| **$0.4$** | 3 / 5 match | 2,145 | 6.32% |
| **$0.6$** | 2 / 5 match | 6,097 | 17.97% |
| **$0.8$** | 1 / 5 match | 12,230 | 36.04% |
| **$1.0$** | 0 / 5 match | 12,805 | 37.74% |
| **Total / Summary** | **Mean = $0.8021$** | **33,930 pairs** | **SD = $0.2005$, Median = $0.80$** |

* **Effect of 5 Options ($Q_3, Q_4$) vs. 6 Options ($Q_1, Q_2, Q_5$):**
  * Uniform random match probability: $1/6 = 16.7\%$ for $Q_1, Q_2, Q_5$ vs. $1/5 = 20.0\%$ for $Q_3, Q_4$.
  * Empirical pairwise match probability: $Q_1 = 17.7\%$, $Q_2 = 18.1\%$, $Q_5 = 18.3\%$, $Q_4 = 20.6\%$, and **$Q_3 = 25.7\%$** (highest because Option A "Independently search for another source" unites both textbook verifiers and independent solvers).

---

## 4. Linkage Comparison: Single vs. Complete vs. Average (RQ2)
*(Charts: `output/figures/fig03_dendrograms_comparison.png` & `fig04_silhouette_comparison.png`)*

* **Cophenetic Correlation Coefficients ($r_{\text{coph}}$):**
  * **Average Linkage (UPGMA):** $r_{\text{coph}} = \mathbf{0.6221}$ *(Best preservation of original pairwise Hamming distances)*
  * **Complete Linkage:** $r_{\text{coph}} = \mathbf{0.5290}$ *(Moderate preservation; sensitive to tie-breaking)*
  * **Single Linkage:** $r_{\text{coph}} = \mathbf{0.1409}$ *(Severe chaining distortion)*

### Partition Metrics Across $K = 2\dots 8$

| $K$ | Single: Avg Sil | Single: Cluster Sizes | Complete: Avg Sil | Complete: Cluster Sizes | Average: Avg Sil | Average: Cluster Sizes |
| :-: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2** | $+0.0598$ | `260/1` | $+0.0167$ | `256/5` | $+0.1023$ | `243/18` |
| **3** | $-0.0982$ | `259/1/1` | $-0.0367$ | `252/5/4` | $+0.1176$ | `177/66/18` |
| **4** | $-0.1562$ | `258/1/1/1` | $-0.0619$ | `244/8/5/4` | $+0.1189$ | `177/46/20/18` |
| **5** | $-0.1777$ | `257/1/1/1/1` | $-0.0677$ | `237/8/7/5/4` | $+0.1562$ | `128/49/46/20/18` |
| **6** | $-0.2114$ | `256/1/1/1/1/1` | $-0.0806$ | `232/8/7/5/5/4` | **$+0.1952$** | **`68/60/49/46/20/18`** |
| **7** | $-0.2269$ | `255/1/1/1/1/1/1` | $-0.0636$ | `219/13/8/7/5/5/4` | $+0.1944$ | `68/52/49/46/20/18/8` |
| **8** | $-0.2507$ | `254/1/1/1/1/1/1/1` | $-0.0807$ | `211/13/8/8/7/5/5/4` | $+0.1943$ | `68/52/49/46/18/12/8/8` |

---

## 5. Sensitivity & Subsampling Stability (RQ3)
*(Chart: `output/figures/fig05_stability_ari.png`)*

| Linkage Method | $K$ | Row-Permutation ARI (Mean ± SD) | 80% Subsampling ARI (Mean ± SD) | 80% Subsampling ARI (Median, IQR) |
| :--- | :-: | :---: | :---: | :---: |
| **Average (UPGMA)** | **5** | **$0.5721 \pm 0.0890$** | **$0.5679 \pm 0.1334$** | **$0.5912$ ($0.1277$)** |
| **Average (UPGMA)** | **6** | **$0.4980 \pm 0.0895$** | **$0.5228 \pm 0.0969$** | **$0.5327$ ($0.1456$)** |
| **Complete** | 5 | $0.1351 \pm 0.1474$ | $0.3032 \pm 0.1641$ | $0.2953$ ($0.2242$) |
| **Complete** | 6 | $0.1346 \pm 0.1265$ | $0.3009 \pm 0.1520$ | $0.2853$ ($0.2214$) |
| **Single** | 5 | $0.2788 \pm 0.0964$ | $0.8490 \pm 0.1404$* | $0.8535$ ($0.2568$)* |

*\*Note: Single linkage's high subsample ARI is an artifact of placing $>98\%$ of respondents into a single giant cluster.*

---

## 6. Behavioral Archetype Profiles: Average Linkage $K = 6$ (RQ1)
*(Chart: `output/figures/fig06_cluster_profiles.png`)*

At $K=5$, Clusters 3 and 4 below form a combined 128-student super-cluster (*Independent & Course-Material Verifiers*), which splits at $K=6$ into two distinct self-verification styles (raising $\bar{s}$ from $0.1562$ to its global peak of $0.1952$):

| Cluster & Archetype Name | Size ($n, \%$) | Dominant Strategy Across $Q_1$–$Q_5$ (Within-Cluster Modal Choice %) |
| :--- | :---: | :--- |
| **C1: Cross-AI & Peer Triangulators** | $46$ ($17.6\%$) | Consults a second/third AI or peer: **Q1-D** ($60.9\%$), **Q2-D** ($47.8\%$), **Q3-C** ($65.2\%$), **Q4-D** ($52.2\%$ ask classmate), **Q5-D** ($58.7\%$). |
| **C2: Same-AI Conversationalists** | $49$ ($18.8\%$) | Dialogues with the same AI to resolve conflict: **Q1-C** ($71.4\%$), **Q2-C** ($46.9\%$), **Q3-B** ($71.4\%$ ask AI for DOI), **Q4-C** ($77.6\%$), **Q5-C** ($59.2\%$). |
| **C3: Independent Problem-Solvers** | $60$ ($23.0\%$) | Re-derives/solves from scratch without AI: **Q1-B** ($60.0\%$), **Q2-B** ($51.7\%$), **Q3-A** ($60.0\%$ search Scholar), **Q4-B** ($70.0\%$ derive self), **Q5-B** ($60.0\%$). |
| **C4: Course-Material Verifiers** | $68$ ($26.1\%$) | Checks authoritative lecture notes/textbooks: **Q1-A** ($52.9\%$), **Q2-A** ($55.9\%$), **Q3-A** ($67.6\%$ search Scholar), **Q4-A** ($44.1\%$), **Q5-A** ($67.6\%$). |
| **C5: Uncritical AI Conformers** | $20$ ($7.7\%$) | Defers to AI without verification: **Q1-E** ($85.0\%$ switch to D), **Q2-B/E** ($40\%/35\%$), **Q3-D** ($60.0\%$ use claim & omit citation), **Q4-E** ($40.0\%$), **Q5-E** ($45.0\%$). |
| **C6: AI-Skeptical Anchors** | $18$ ($6.9\%$) | Rejects AI / sticks to own answer or drops task: **Q1-F** ($77.8\%$ keep B), **Q2-F** ($44.4\%$ leave unanswered), **Q3-E** ($61.1\%$ remove claim), **Q4-D/E** ($44.4\%/38.9\%$), **Q5-F** ($66.7\%$). |

---

## 7. External Validation: $Q_6$ (AI Usage) & $S_4$ (Year of Study)
*(Chart: `output/figures/fig07_external_validation.png`)*

Both external validation variables show **statistically significant differences** across the clusters (even though neither variable was used to form the clusters!):

1. **Weekly AI Usage Frequency ($Q_6$: $0$–$7$ days):**
   * **Kruskal-Wallis Test:** $H = 14.144, \text{df} = 5, \mathbf{p = 0.0147}$ ($p = 0.0140$ at $K=5$).
   * **One-Way ANOVA:** $F(5, 255) = 2.957, \mathbf{p = 0.0130}$ ($p = 0.0136$ at $K=5$).
2. **Year of Study ($S_4$, $n = 255$ known):**
   * **Pearson Chi-Square Test (10,000 Monte Carlo replicates):** $\chi^2 = 76.659, \mathbf{p = 0.0001}$ ($\chi^2 = 66.284, p = 0.0001$ at $K=5$).

| Cluster | $n$ | $Q_6$ Mean ± SD (Days/Wk) | $Q_6$ Median (IQR) | 1st Yr ($\%$) | 2nd Yr ($\%$) | 3rd Yr ($\%$) | 4th Yr ($\%$) | Grad/Master ($\%$) |
| :--- | :-: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C1: Cross-AI & Peer** | 46 | $3.67 \pm 2.04$ | $3.0$ ($2.75$) | 20.0% | 31.1% | 15.6% | 31.1% | 2.2% |
| **C2: Same-AI Probe** | 49 | **$4.63 \pm 1.95$** | **$5.0$ ($3.00$)** | 29.2% | 14.6% | 27.1% | 27.1% | 2.1% |
| **C3: Self-Solvers** | 60 | $3.90 \pm 2.30$ | $4.0$ ($4.00$) | 19.3% | **38.6%** | 10.5% | **31.6%** | 0.0% |
| **C4: Course Material** | 68 | $4.41 \pm 1.96$ | $5.0$ ($3.00$) | 25.0% | 22.1% | **29.4%** | 23.5% | 0.0% |
| **C5: AI Conformers** | 20 | **$2.85 \pm 1.95$** | **$3.0$ ($3.00$)** | **42.1%** | 5.3% | 5.3% | 15.8% | **31.6%** |
| **C6: Skeptic Anchors** | 18 | $4.44 \pm 2.43$ | $5.0$ ($4.75$) | 22.2% | 33.3% | 5.6% | 16.7% | **22.2%** |

### Key External Validation Takeaways for Your Slides:
* **Why do "Same-AI Conversationalists" (C2) have the highest AI usage ($4.63$ days/week) while "Uncritical AI Conformers" (C5) have the lowest ($2.85$ days/week)?**
  * Students who use AI heavily ($4.63$ days/week) are comfortable treating AI as an interactive dialogue partner (prompting it for DOIs, step-by-step explanations, and comparisons), whereas infrequent users ($2.85$ days/week, heavily 1st-year students at $42.1\%$) are more likely to passively accept AI outputs without follow-up prompting or verification.
* **Undergraduates (Years 2–4) dominate the active verification clusters (C1–C4):**
  * Over $98\%$ of **Course-Material Verifiers (C4)** and **Independent Problem-Solvers (C3)** are undergraduate students who actively cross-check AI against coursework formulas or re-derive steps themselves.

