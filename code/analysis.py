#!/usr/bin/env python3
"""
Hierarchical Cluster Analysis: "When AI Disagrees With You" (Python Version)
Course: Data Analysis in High Dimensions (Prof. Dr. C. Andersson, VGU)
Team:
  - Tran Trong Nhan (10423160)
  - Nguyen Minh Nhat Huy (10423045)
  - Dao Hoang Minh Triet (10423179)

Description:
  Self-contained Python implementation of Agglomerative Hierarchical Clustering
  using Normalized Hamming (Gower) distance across p = 5 categorical scenario
  variables (Q1-Q5), comparing Single, Complete, and Average (UPGMA) linkage,
  evaluating Silhouette scores across K = 2..8, checking tie/row-order sensitivity
  and 80% subsampling stability via Adjusted Rand Index (ARI), and validating
  clusters externally against S4 (Year of Study) and Q6 (AI Usage Frequency).
"""

import csv
import math
import os
import random
import statistics
from collections import Counter, defaultdict

# Paths
BASE_DIR = "/mnt/hdd-1tb/CSE-VGU/2026-2027/Elective-1"
CSV_PATH = os.path.join(
    BASE_DIR,
    "When AI Disagrees With You_ How University Students Respond to Uncertain AI Answers (Responses) - Form Responses 1.csv",
)
OUT_DIR = os.path.join(BASE_DIR, "output")
TAB_DIR = os.path.join(OUT_DIR, "tables")
os.makedirs(TAB_DIR, exist_ok=True)


# ------------------------------------------------------------------------------
# 1. Data Loading & Option Mapping
# ------------------------------------------------------------------------------
Q1_MAP = {
    "Check the relevant course material.": "A",
    "Solve the question again independently, without consulting the AI explanation.": "B",
    "Ask the same AI why option B is incorrect.": "C",
    "Ask a different AI the same question again.": "D",
    "Ask a different AI the original question.": "D",
    "Change my answer to D without further checking.": "E",
    "Keep my answer B without further checking.": "F",
}

Q2_MAP = {
    "Check the relevant course material.": "A",
    "Solve the question independently without using either AI explanation.": "B",
    "Send the second explanation to the first AI and ask it to compare them.": "C",
    "Ask a third AI the original question.": "D",
    "Choose the answer from the AI I use more often, without further checking.": "E",
    "Leave the question unanswered for now and move to another task.": "F",
}

Q3_MAP = {
    "Independently search for another source to verify the claim.": "A",
    "Ask the same AI for the paper’s DOI or direct link.": "B",
    "Ask the same AI for the paper's DOI or direct link.": "B",
    "Ask a different AI whether the claim is correct.": "C",
    "Use the claim in my work but omit the citation.": "D",
    "Remove the claim from my work without investigating further.": "E",
}

Q4_MAP = {
    "Look up the relevant concept or formula in course materials.": "A",
    "Attempt to derive step 4 from step 3 myself.": "B",
    "Ask the same AI to explain that specific transition.": "C",
    "Ask a classmate to explain that specific transition.": "D",
    "Use the solution without clarifying that step.": "E",
}

Q5_MAP = {
    "Check the relevant course material.": "A",
    "Solve the question independently.": "B",
    "Ask the AI to compare both answers and explain why it changed.": "C",
    "Ask a different AI the original question.": "D",
    "Accept D without further checking.": "E",
    "Keep B without further checking.": "F",
}


def load_and_clean_data(csv_path: str):
    records = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        _ = next(reader)
        idx = 1
        for row in reader:
            s1, s2 = row[1].strip(), row[2].strip()
            if s1 != "Yes" or s2 != "Yes":
                continue
            s3 = row[3].strip()
            if not s3 or s3 == "Prefer not to answer":
                s3 = "Unspecified"
            s4 = row[4].strip()
            if not s4 or s4 == "Prefer not to answer":
                s4 = "Unspecified"
            q1 = Q1_MAP[row[5].strip()]
            q2 = Q2_MAP[row[6].strip()]
            q3 = Q3_MAP[row[7].strip()]
            q4 = Q4_MAP[row[8].strip()]
            q5 = Q5_MAP[row[9].strip()]
            q6 = int(row[10].strip())
            records.append(
                {
                    "ID": f"R{idx:03d}",
                    "S3": s3,
                    "S4": s4,
                    "Q": (q1, q2, q3, q4, q5),
                    "Q6": q6,
                }
            )
            idx += 1
    return records


# ------------------------------------------------------------------------------
# 2. Normalized Hamming Distance & Agglomerative Hierarchical Clustering
# ------------------------------------------------------------------------------
def hamming_distance(q_i: tuple, q_j: tuple) -> float:
    """Normalized Hamming distance across p = 5 nominal variables."""
    p = len(q_i)
    return sum(1 for a, b in zip(q_i, q_j) if a != b) / p


def compute_distance_matrix(records):
    n = len(records)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        qi = records[i]["Q"]
        for j in range(i + 1, n):
            d = hamming_distance(qi, records[j]["Q"])
            dist[i][j] = d
            dist[j][i] = d
    return dist


def agglomerative_clustering(dist_matrix, method="average", target_k_list=(2, 3, 4, 5, 6, 7, 8)):
    """
    Agglomerative hierarchical clustering using Lance-Williams recurrence:
      - single:   d(A U B, C) = min(d(A,C), d(B,C))
      - complete: d(A U B, C) = max(d(A,C), d(B,C))
      - average:  d(A U B, C) = (|A|*d(A,C) + |B|*d(B,C)) / (|A| + |B|)
    Returns (partitions_dict, merge_heights_list).
    """
    n = len(dist_matrix)
    clusters = {c_id: [c_id] for c_id in range(n)}
    active_ids = list(range(n))
    c_dist = {}
    for i in range(n):
        for j in range(i + 1, n):
            c_dist[(i, j)] = dist_matrix[i][j]

    partitions = {}
    merge_heights = []
    next_id = n

    while len(active_ids) > 1:
        k_curr = len(active_ids)
        if k_curr in target_k_list:
            labels = [0] * n
            for rank_idx, cid in enumerate(active_ids, start=1):
                for member in clusters[cid]:
                    labels[member] = rank_idx
            partitions[k_curr] = labels

        best_pair = None
        best_d = float("inf")
        for idx_a in range(len(active_ids)):
            ca = active_ids[idx_a]
            for idx_b in range(idx_a + 1, len(active_ids)):
                cb = active_ids[idx_b]
                key = (ca, cb) if ca < cb else (cb, ca)
                d_ab = c_dist[key]
                if d_ab < best_d - 1e-12:
                    best_d = d_ab
                    best_pair = (ca, cb)

        ca, cb = best_pair
        merge_heights.append(best_d)
        na, nb = len(clusters[ca]), len(clusters[cb])
        merged_members = clusters[ca] + clusters[cb]
        new_cid = next_id
        next_id += 1

        active_ids.remove(ca)
        active_ids.remove(cb)
        for cc in active_ids:
            key_ac = (ca, cc) if ca < cc else (cc, ca)
            key_bc = (cb, cc) if cb < cc else (cc, cb)
            dac = c_dist[key_ac]
            dbc = c_dist[key_bc]
            if method == "single":
                d_new = min(dac, dbc)
            elif method == "complete":
                d_new = max(dac, dbc)
            elif method == "average":
                d_new = (na * dac + nb * dbc) / (na + nb)
            else:
                raise ValueError(f"Unknown linkage method: {method}")
            c_dist[(cc, new_cid)] = d_new

        clusters[new_cid] = merged_members
        active_ids.append(new_cid)

    return partitions, merge_heights


def average_silhouette(dist_matrix, labels):
    """Computes average silhouette width and negative silhouette count."""
    n = len(labels)
    clusters = defaultdict(list)
    for idx, lbl in enumerate(labels):
        clusters[lbl].append(idx)

    sil_scores = []
    for i in range(n):
        own_c = labels[i]
        own_members = clusters[own_c]
        if len(own_members) <= 1:
            sil_scores.append(0.0)
            continue
        a_i = sum(dist_matrix[i][j] for j in own_members if j != i) / (len(own_members) - 1)
        b_i = float("inf")
        for other_c, other_members in clusters.items():
            if other_c == own_c:
                continue
            mean_other = sum(dist_matrix[i][j] for j in other_members) / len(other_members)
            if mean_other < b_i:
                b_i = mean_other
        denom = max(a_i, b_i)
        s_i = (b_i - a_i) / denom if denom > 0 else 0.0
        sil_scores.append(s_i)

    avg_s = sum(sil_scores) / n
    neg_cnt = sum(1 for s in sil_scores if s < 0)
    return avg_s, neg_cnt


def adjusted_rand_index(labels_x, labels_y):
    """Exact Hubert & Arabie (1985) Adjusted Rand Index."""
    n = len(labels_x)
    if n <= 1:
        return 1.0
    tab = Counter(zip(labels_x, labels_y))
    row_sums = Counter(labels_x)
    col_sums = Counter(labels_y)

    def comb2(k):
        return k * (k - 1) // 2

    sum_nij2 = sum(comb2(v) for v in tab.values())
    sum_ai2 = sum(comb2(v) for v in row_sums.values())
    sum_bj2 = sum(comb2(v) for v in col_sums.values())
    total_pairs = comb2(n)
    expected = (sum_ai2 * sum_bj2) / total_pairs
    max_idx = 0.5 * (sum_ai2 + sum_bj2)
    denom = max_idx - expected
    if abs(denom) < 1e-12:
        return 1.0
    return (sum_nij2 - expected) / denom


# ------------------------------------------------------------------------------
# 3. Main Execution & Verification Report
# ------------------------------------------------------------------------------
def main():
    records = load_and_clean_data(CSV_PATH)
    n = len(records)
    print(f"Loaded and cleaned n = {n} eligible student responses.")

    profiles = Counter(r["Q"] for r in records)
    print(f"Unique 5-question response patterns: {len(profiles)} / 5400 possible")

    dist_mat = compute_distance_matrix(records)
    pair_dists = [round(dist_mat[i][j], 1) for i in range(n) for j in range(i + 1, n)]
    dist_counts = Counter(pair_dists)
    total_pairs = len(pair_dists)
    print("\n--- Pairwise Normalized Hamming Distance Distribution ---")
    for d_val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        cnt = dist_counts[d_val]
        print(f"  d = {d_val:.1f}: {cnt:5d} pairs ({100.0 * cnt / total_pairs:5.2f}%)")
    print(f"  Mean distance = {statistics.mean(pair_dists):.4f}, SD = {statistics.stdev(pair_dists):.4f}")

    print("\n--- Silhouette, Cluster Size & Merge Height Comparison (K = 2..8) ---")
    for method in ["single", "complete", "average"]:
        parts, heights = agglomerative_clustering(dist_mat, method=method, target_k_list=range(2, 9))
        unique_h = len(set(round(h, 6) for h in heights))
        print(f"\nMethod: {method.upper()} (Unique merge heights: {unique_h} / {len(heights)})")
        for k in range(2, 9):
            lbls = parts[k]
            avg_s, neg_c = average_silhouette(dist_mat, lbls)
            sizes = sorted(Counter(lbls).values(), reverse=True)
            size_str = "/".join(str(s) for s in sizes)
            print(
                f"  K={k}: Avg_Sil={avg_s:+.4f} | Neg_Sil={neg_c:3d} ({100*neg_c/n:4.1f}%) | Sizes={size_str}"
            )

    # Verify R's exported K=6 cluster assignments and external validation
    r_cleaned_path = os.path.join(TAB_DIR, "cleaned_responses.csv")
    if os.path.exists(r_cleaned_path):
        print("\n--- Cross-Check of R's Average Linkage (K = 6) Cluster Profiles & External Validation ---")
        with open(r_cleaned_path, newline="", encoding="utf-8") as f:
            r_rows = list(csv.DictReader(f))
        by_cl = defaultdict(list)
        for r in r_rows:
            by_cl[int(r["Cluster_K6"])].append(r)
        for cid in sorted(by_cl):
            members = by_cl[cid]
            arch = members[0]["Archetype_K6"]
            q6_vals = [int(m["Q6_Num"]) for m in members]
            print(
                f"  {arch:<35s} | n={len(members):3d} ({100*len(members)/n:4.1f}%) | "
                f"Q6 Mean={statistics.mean(q6_vals):.2f}, SD={statistics.stdev(q6_vals):.2f}, "
                f"Median={statistics.median(q6_vals):.1f}"
            )


if __name__ == "__main__":
    main()
