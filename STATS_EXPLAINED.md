# Statistics in `main.pdf`, Explained for Beginners

This guide walks through every statistical idea in the report, in the same order the report uses them. Each one comes with an everyday analogy and the actual numbers from the study.

> You said you already understand **the clustering variables (p = 5), raw/normalized Hamming distance, and Gower dissimilarity**, so those get only a short recap in §1. Everything else is explained in full.

---

## 0. The big picture in one paragraph

We asked 261 students 5 multiple-choice "what would you do first?" questions (Q1–Q5). We wanted to know whether students **naturally fall into groups** of similar behaviour. We didn't label anyone ourselves. We measured how different every pair of students is, then let an algorithm build the groups. Next we checked three things: (a) whether the groups are any good, (b) whether they are stable, and (c) whether they also differ on things the algorithm never saw, namely weekly AI usage (Q6) and year of study (S4). The answer to all three was yes. The result is 6 groups ("archetypes").

---

## 1. Quick recap (things you already know)

| Term | Meaning in our study |
|---|---|
| n = 261 | number of students (rows) |
| p = 5 | number of clustering variables (Q1–Q5) |
| Normalized Hamming / Gower distance | share of the 5 questions where two students answered differently. It can only be 0, 0.2, 0.4, 0.6, 0.8 or 1.0 |
| Distance matrix D | 261 × 261 table holding the distance between every pair of students (33,930 unique pairs) |

**Nominal variable**: answers are labels with no order (A, B, C… are not "1, 2, 3"). That's why we can't use Euclidean distance or means. "A" isn't smaller than "F".

**Discrete lattice**: a fancy way of saying "the distance can only take those 6 values". This matters a lot later (§4).

---

## 2. Basic descriptive statistics

| Term | Plain meaning | Example from report |
|---|---|---|
| **Mean** | the average | students used AI 4.09 days/week on average |
| **SD (standard deviation)**, written `±` | how spread out values are around the mean. Small SD means most people are close to the average | 4.09 **± 2.13** → most students fall roughly between 2 and 6 days |
| **Median** | the middle value when sorted. Extreme values don't pull it around | median = 4.0 days |
| **IQR (interquartile range)** | width of the middle 50% of the data (75th percentile − 25th percentile) | IQR = 3.0 → the middle half of students differ by about 3 days |
| **Marginal distribution** | the % choosing each option for **one question at a time**, ignoring the other questions | Figure 1 |
| **Modal response** | the most common answer | bold entries in Table 2 |
| **Empirical match rate**, $\sum_m \hat p_{km}^2$ | chance that two random students pick the **same** option on question k. $\hat p_{km}$ is the share choosing option m | Q3 = 25.7% (many chose A), Q1 = 17.7% |

---

## 3. Clustering vocabulary

### Cluster analysis / unsupervised learning
Grouping things so that items in the same group are similar and items in different groups are different. "Unsupervised" means **nobody tells the algorithm the right answer**. It discovers the groups by itself.

### Hierarchical vs. non-hierarchical
- **Non-hierarchical (e.g. K-means)**: you say "give me K groups" up front.
- **Hierarchical**: builds a whole **family tree** of groupings, from "everyone alone" to "everyone together". You decide afterwards where to cut it.

### Agglomerative (bottom-up)
Start with 261 groups of 1 student each. At each step, **merge the two closest groups**. Repeat 260 times until one group remains. (*Divisive* does the opposite, top-down. It's rarely used because it is computationally expensive.)

### Dendrogram
The tree diagram of those merges (Figure 3). The **height** where two branches join is the distance at which they were merged. Low joins mean very similar students. High joins mean very different groups.

### Cutting the tree / K
Draw a horizontal line across the dendrogram. The number of branches it crosses is **K**, the number of clusters. R does this with `cutree`. We chose **K = 6**.

### Merge height
The distance value at which a merge happens (the y-axis of the dendrogram).

---

## 4. Linkage methods: "how far apart are two *groups*?"

We know the distance between two **students**. But once students are grouped, we need a rule for the distance between two **groups**. That rule is the *linkage*.

| Linkage | Rule | Analogy | Problem in our data |
|---|---|---|---|
| **Single** (nearest neighbour) | distance of the **closest** pair across the two groups | two towns are "close" if *any* two houses are close | **Chaining**: groups get linked through a chain of in-between people, so everyone ends up in one giant blob (256 of 261 students in one cluster) |
| **Complete** (furthest neighbour) | distance of the **farthest** pair | two towns are close only if *every* house is close | the final 15 merges all happen at height 1.0 (a **tie**), so the result depends on the order of rows in the file |
| **Average (UPGMA)** | **average** of all pairwise distances between the two groups | the typical distance between towns | ✅ the averages give many distinct values (67 different heights), so ties are rare. **This is the method we used** |
| Centroid / Ward | use group **means** / variance | – | ❌ can't be used, because A–F labels have no mean |

### Why ties matter ("quantization" / "tie degeneracy")
Single and Complete linkage only take a min or max of existing distances. So **every merge height must be one of 0, 0.2, …, 1.0**. Thousands of pairs share the same height. When several merges tie, the computer picks one based on **row order in the dataset**, which is arbitrary. Average linkage divides by group sizes, so it produces values like 0.6941 or 0.7065 and ties disappear.

- **Order statistic**: the min, the max, or another ranked value from a list. Single and Complete use order statistics.
- **Rational merge heights**: fractions, produced by averaging.
- **Row order / tie-breaking**: the algorithm's arbitrary choice when several options are equally good.

---

## 5. How good is the tree? Cophenetic correlation

- **Cophenetic distance** between two students: the dendrogram height where they first end up in the same branch.
- **Cophenetic correlation** $r_{coph}$: the **correlation** between the real distances and the tree's cophenetic distances. It answers: "Does the tree faithfully represent the original distances?"
- **Correlation** in general: a number from −1 to 1 measuring how strongly two quantities move together. 1 means perfect agreement and 0 means no relation.

| Method | r_coph | Interpretation |
|---|---|---|
| Average | **0.62** | best: reasonably faithful |
| Complete | 0.53 | OK |
| Single | 0.14 | poor: the tree distorts the real distances |

---

## 6. How many clusters? Silhouette width

For each student *i*:
- **a(i)** = average distance to the students in **their own** cluster (how well they fit at home)
- **b(i)** = average distance to the students in the **nearest other** cluster (how close the neighbours are)

$$
s(i) = \frac{b(i) - a(i)}{\max\{a(i),\, b(i)\}}
$$

| s(i) value | Meaning |
|---|---|
| close to +1 | clearly in the right cluster |
| around 0 | on the border between two clusters |
| negative | probably in the wrong cluster |

- **Average silhouette width** $\bar s$: the mean of s(i) over all students. **Higher is better.** We tried K = 2…8 and chose the K with the highest value: **K = 6, s̄ = 0.195**.
- **Negative silhouette %**: share of students who seem misplaced. At K = 6 it is lowest (16.5%).
- **Max cluster %**: size of the biggest cluster. A huge value (98%) signals chaining. At K = 6 it is 26.1%, which is balanced.

> Is 0.195 low? Yes, by textbook standards (above 0.5 counts as "strong"). But survey answers from humans are noisy and only 5 questions are available, so weak-but-real structure is expected. That's why the stability checks and external validation below matter.

---

## 7. Are the clusters stable? Adjusted Rand Index (ARI)

### Rand Index / ARI
A score for **how similar two groupings of the same people are**. It looks at every pair of students and asks: "Are these two together in both groupings, or apart in both?"
- **Adjusted** means it is corrected for agreement that would happen by pure chance.
- ARI = 1: identical groupings. ARI ≈ 0: no better than random. Negative: worse than random.
- Rough guide: above 0.5 is moderate–good, below 0.2 is poor.

### Two stability experiments
1. **Row-order permutation (100 shuffles)**: shuffle the order of students in the file, re-cluster, and compare with the original using ARI. This tests the tie-breaking problem from §4.
   Complete: 0.135 (collapses). Average K = 6: **0.50**.
2. **80% subsampling (100 times)**: randomly keep 209 of 261 students (**without replacement** = nobody is picked twice), re-cluster, and compare. This tests whether the groups depend on a few particular people.
   Average K = 6: **ARI ≈ 0.52** (moderate stability).

`± value` here is again the SD across the 100 repetitions.

---

## 8. Do the clusters mean something outside the data? External validation

The clusters were built from Q1–Q5 only, so of course they differ on Q1–Q5. That's circular. The real test is whether they also differ on variables the algorithm **never saw**: **Q6** (AI days/week) and **S4** (year of study).

### Hypothesis test, p-value, significance
- **Null hypothesis (H₀)**: "there is no difference between clusters" (e.g. all clusters use AI equally often).
- **p-value**: *if H₀ were true*, how likely it would be to see differences at least this large purely by chance.
- Convention: **p < 0.05 counts as "statistically significant"**, meaning we reject H₀ and conclude the difference is probably real.
- A p-value says *whether* a difference exists. It does **not** say how big or important the difference is.

### One-way ANOVA (for Q6)
Compares the **means** of a numeric variable across 3+ groups.
- **F statistic** = (variation *between* group means) ÷ (variation *within* groups). A big F means the groups differ more than random noise would explain.
- **F(5, 255)**: the two **degrees of freedom**, 5 = (6 clusters − 1) and 255 = (261 − 6).
- Result: F = 2.96, **p = 0.013** → AI usage differs between clusters.
- Assumes roughly normal (bell-shaped) data. Q6 is a 0–7 count, so we also ran ↓

### Kruskal–Wallis H test (for Q6)
The **non-parametric** version of ANOVA. It ranks all values and compares **ranks** (roughly, medians) instead of means, so it makes no bell-curve assumption.
- **Non-parametric**: doesn't assume a particular distribution shape.
- **df = 5** (degrees of freedom = groups − 1).
- Result: H = 14.14, **p = 0.015**. Same conclusion, which makes the finding more robust.

### Pearson's chi-square (χ²) test (for S4)
Used when **both** variables are categories (cluster × year of study). It builds a **contingency table** (rows = clusters, columns = years) and compares the **observed** counts with the counts **expected** if cluster and year were unrelated.

$$
\chi^2 = \sum \frac{(\text{observed} - \text{expected})^2}{\text{expected}}
$$

A big χ² means the observed table is far from "no relationship".

- **Monte Carlo simulated p-value (10,000 replicates)**: some cells are tiny (e.g. only 12 grad students), so the usual chi-square formula is unreliable. Instead, the computer generates 10,000 random tables under "no relationship" and counts how often they look as extreme as ours. None of them did, so **p ≈ 0.0001** (the smallest value possible with 10,000 runs).
- Result: χ² = 76.66, **p = 0.0001** → year of study is strongly related to cluster membership.
- **Row %**: percentages computed within each cluster's row (each row adds up to 100%).

---

## 9. Other terms you might trip over

| Term | Meaning |
|---|---|
| **Metric axioms** (symmetry, positivity, identity, triangle inequality) | rules a "proper" distance must follow: A→B equals B→A; the distance is never negative; it is 0 for identical items; a detour can't be shorter than the direct route. Hamming satisfies all four |
| **Profile** | one student's 5 answers, e.g. `B-B-A-B-B` |
| **Archetype** | a named cluster, i.e. a typical behaviour pattern |
| **Within-cluster %** | inside one cluster, the % choosing each option (Table 2 / Figure 6) |
| **Singleton** | a cluster containing just 1 person |
| **Partition** | one way of dividing everyone into non-overlapping groups |
| **Binomial coefficient** $\binom{261}{2}$ | number of possible pairs = 261 × 260 / 2 = 33,930 |
| **SSE / SST / R²** (Ward section) | error / total sum of squares. R² = share of the variation explained by the grouping. Mentioned only to explain why Ward can't be used |
| **One-hot / dummy coding** | turning A–F into six 0/1 columns. An alternative we deliberately avoided |

---

## 10. The whole study in one table

| Step | Tool | Result |
|---|---|---|
| Measure student differences | Normalized Hamming (Gower) | mean distance 0.80 (students are quite diverse) |
| Build groups | Average linkage hierarchical clustering | 67 distinct merge heights, no tie problem |
| Check the tree | Cophenetic correlation | 0.62 (best of the 3 linkages) |
| Choose K | Average silhouette width | K = 6, s̄ = 0.195 |
| Check stability | ARI (shuffle and subsample) | ≈ 0.50–0.52, moderately stable |
| Check external meaning | ANOVA, Kruskal–Wallis, χ² | p = 0.013, 0.015, 0.0001 → all significant |
| Interpret | Within-cluster % | 6 archetypes (Course-Material Verifiers 26%, Independent Solvers 23%, Same-AI 19%, Cross-AI/Peer 18%, Uncritical Conformers 8%, Skeptical Anchors 7%) |

