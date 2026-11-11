#!/usr/bin/env Rscript
# ==============================================================================
# Hierarchical Cluster Analysis: "When AI Disagrees With You"
# Course: Data Analysis in High Dimensions (Prof. Dr. C. Andersson, VGU)
# Team: Tran Trong Nhan (10423160), Nguyen Minh Nhat Huy (10423045),
#       Dao Hoang Minh Triet (10423179)
# ==============================================================================

options(stringsAsFactors = FALSE, width = 120)
library(cluster)
library(stats)
library(graphics)
library(grDevices)

# Set reproducible random seed
set.seed(20261111)

# Paths
base_dir <- "/mnt/hdd-1tb/CSE-VGU/2026-2027/Elective-1"
csv_path <- file.path(
  base_dir,
  "When AI Disagrees With You_ How University Students Respond to Uncertain AI Answers (Responses) - Form Responses 1.csv"
)
out_dir  <- file.path(base_dir, "output")
fig_dir  <- file.path(out_dir, "figures")
tab_dir  <- file.path(out_dir, "tables")

dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(tab_dir, recursive = TRUE, showWarnings = FALSE)

# ------------------------------------------------------------------------------
# Helper: Adjusted Rand Index (Hubert & Arabie 1985)
# ------------------------------------------------------------------------------
adjusted_rand_index <- function(x, y) {
  tab <- table(x, y)
  n <- sum(tab)
  if (n <= 1) return(1.0)
  sum_nij2 <- sum(choose(tab, 2))
  sum_ai2  <- sum(choose(rowSums(tab), 2))
  sum_bj2  <- sum(choose(colSums(tab), 2))
  total_pairs <- choose(n, 2)
  expected_index <- (sum_ai2 * sum_bj2) / total_pairs
  max_index <- 0.5 * (sum_ai2 + sum_bj2)
  denom <- max_index - expected_index
  if (abs(denom) < 1e-12) return(1.0)
  (sum_nij2 - expected_index) / denom
}

# Helper to save plots as both PDF (for LaTeX) and PNG (for Slides)
save_dual_plot <- function(filename_stem, width_in, height_in, plot_fn) {
  pdf_file <- file.path(fig_dir, paste0(filename_stem, ".pdf"))
  png_file <- file.path(fig_dir, paste0(filename_stem, ".png"))
  pdf(pdf_file, width = width_in, height = height_in, useDingbats = FALSE)
  plot_fn()
  dev.off()
  png(png_file, width = width_in * 150, height = height_in * 150, res = 150)
  plot_fn()
  dev.off()
}

# ------------------------------------------------------------------------------
# 1. Load & Preprocess Data
# ------------------------------------------------------------------------------
raw_df <- read.csv(csv_path, check.names = FALSE, encoding = "UTF-8")
colnames(raw_df) <- c(
  "Timestamp", "S1_Enrolled", "S2_Consent", "S3_Major", "S4_Year",
  "Q1_Raw", "Q2_Raw", "Q3_Raw", "Q4_Raw", "Q5_Raw", "Q6_Days"
)

# Filter for eligibility (S1 == "Yes" & S2 == "Yes")
df <- raw_df[trimws(raw_df$S1_Enrolled) == "Yes" & trimws(raw_df$S2_Consent) == "Yes", ]
df$ID <- sprintf("R%03d", seq_len(nrow(df)))

# Map Q1-Q5 text responses to option codes A-F / A-E
map_q1 <- function(x) {
  x <- trimws(x)
  ifelse(x == "Check the relevant course material.", "A",
  ifelse(x == "Solve the question again independently, without consulting the AI explanation.", "B",
  ifelse(x == "Ask the same AI why option B is incorrect.", "C",
  ifelse(x %in% c("Ask a different AI the same question again.",
                  "Ask a different AI the original question."), "D",
  ifelse(x == "Change my answer to D without further checking.", "E",
  ifelse(x == "Keep my answer B without further checking.", "F", NA_character_))))))
}

map_q2 <- function(x) {
  x <- trimws(x)
  ifelse(x == "Check the relevant course material.", "A",
  ifelse(x == "Solve the question independently without using either AI explanation.", "B",
  ifelse(x == "Send the second explanation to the first AI and ask it to compare them.", "C",
  ifelse(x == "Ask a third AI the original question.", "D",
  ifelse(x == "Choose the answer from the AI I use more often, without further checking.", "E",
  ifelse(x == "Leave the question unanswered for now and move to another task.", "F", NA_character_))))))
}

map_q3 <- function(x) {
  x <- trimws(x)
  ifelse(x == "Independently search for another source to verify the claim.", "A",
  ifelse(grepl("^Ask the same AI for the paper", x), "B",
  ifelse(x == "Ask a different AI whether the claim is correct.", "C",
  ifelse(x == "Use the claim in my work but omit the citation.", "D",
  ifelse(x == "Remove the claim from my work without investigating further.", "E", NA_character_)))))
}

map_q4 <- function(x) {
  x <- trimws(x)
  ifelse(x == "Look up the relevant concept or formula in course materials.", "A",
  ifelse(x == "Attempt to derive step 4 from step 3 myself.", "B",
  ifelse(x == "Ask the same AI to explain that specific transition.", "C",
  ifelse(x == "Ask a classmate to explain that specific transition.", "D",
  ifelse(x == "Use the solution without clarifying that step.", "E", NA_character_)))))
}

map_q5 <- function(x) {
  x <- trimws(x)
  ifelse(x == "Check the relevant course material.", "A",
  ifelse(x == "Solve the question independently.", "B",
  ifelse(x == "Ask the AI to compare both answers and explain why it changed.", "C",
  ifelse(x == "Ask a different AI the original question.", "D",
  ifelse(x == "Accept D without further checking.", "E",
  ifelse(x == "Keep B without further checking.", "F", NA_character_))))))
}

df$Q1 <- factor(map_q1(df$Q1_Raw), levels = c("A", "B", "C", "D", "E", "F"))
df$Q2 <- factor(map_q2(df$Q2_Raw), levels = c("A", "B", "C", "D", "E", "F"))
df$Q3 <- factor(map_q3(df$Q3_Raw), levels = c("A", "B", "C", "D", "E"))
df$Q4 <- factor(map_q4(df$Q4_Raw), levels = c("A", "B", "C", "D", "E"))
df$Q5 <- factor(map_q5(df$Q5_Raw), levels = c("A", "B", "C", "D", "E", "F"))

stopifnot(all(colSums(is.na(df[, c("Q1", "Q2", "Q3", "Q4", "Q5")])) == 0))

df$S3_Clean <- ifelse(trimws(df$S3_Major) == "" | trimws(df$S3_Major) == "Prefer not to answer",
                      "Unspecified", trimws(df$S3_Major))
df$S4_Clean <- ifelse(trimws(df$S4_Year) == "" | trimws(df$S4_Year) == "Prefer not to answer",
                      "Unspecified", trimws(df$S4_Year))
df$S4_Clean <- factor(
  df$S4_Clean,
  levels = c("1st year", "2nd year", "3rd year", "4th year", "Graduate / Master's student", "Unspecified")
)
df$Q6_Num <- as.integer(trimws(df$Q6_Days))
df$Profile <- paste(df$Q1, df$Q2, df$Q3, df$Q4, df$Q5, sep = "-")

# ------------------------------------------------------------------------------
# 2. Marginal Distributions & Distance Matrix
# ------------------------------------------------------------------------------
q_cols <- c("Q1", "Q2", "Q3", "Q4", "Q5")
marginal_list <- list()
for (q in q_cols) {
  tb <- table(df[[q]])
  pct <- round(100 * prop.table(tb), 1)
  marginal_list[[q]] <- data.frame(
    Question = q,
    Option = names(tb),
    Count = as.integer(tb),
    Percentage = as.numeric(pct)
  )
}
marginal_df <- do.call(rbind, marginal_list)
write.csv(marginal_df, file.path(tab_dir, "marginal_q1_q5.csv"), row.names = FALSE)

df_q <- df[, q_cols]
rownames(df_q) <- df$ID

dist_hamming <- daisy(df_q, metric = "gower")
dist_vec <- as.numeric(dist_hamming)

hc_single   <- hclust(dist_hamming, method = "single")
hc_complete <- hclust(dist_hamming, method = "complete")
hc_average  <- hclust(dist_hamming, method = "average")

coph_single   <- cor(dist_hamming, cophenetic(hc_single))
coph_complete <- cor(dist_hamming, cophenetic(hc_complete))
coph_average  <- cor(dist_hamming, cophenetic(hc_average))

# ------------------------------------------------------------------------------
# 3. Partition Evaluation (K = 2..8) & Stability Analysis
# ------------------------------------------------------------------------------
k_range <- 2:8
eval_rows <- list()
for (m_name in c("Single", "Complete", "Average")) {
  hc_obj <- switch(m_name, Single = hc_single, Complete = hc_complete, Average = hc_average)
  for (k in k_range) {
    cl <- cutree(hc_obj, k = k)
    sil <- silhouette(cl, dist_hamming)
    sil_vals <- sil[, "sil_width"]
    sz <- sort(as.integer(table(cl)), decreasing = TRUE)
    eval_rows[[length(eval_rows) + 1]] <- data.frame(
      Method = m_name,
      K = k,
      Avg_Silhouette = round(mean(sil_vals), 4),
      Neg_Sil_Count = sum(sil_vals < 0),
      Neg_Sil_Pct = round(100 * mean(sil_vals < 0), 1),
      Max_Cluster_Size = max(sz),
      Max_Cluster_Pct = round(100 * max(sz) / nrow(df_q), 1),
      Min_Cluster_Size = min(sz),
      Singletons = sum(sz == 1),
      Cluster_Sizes = paste(sz, collapse = "/")
    )
  }
}
eval_df <- do.call(rbind, eval_rows)
write.csv(eval_df, file.path(tab_dir, "linkage_k_evaluation.csv"), row.names = FALSE)

# Sensitivity & Subsampling Stability (K = 2..6)
set.seed(20261111)
n_perm <- 100
n_sub  <- 100
sub_size <- floor(0.80 * nrow(df_q))

stability_rows <- list()
sub_ari_store <- list()

for (m_name in c("Single", "Complete", "Average")) {
  m_code <- tolower(m_name)
  hc_full <- switch(m_name, Single = hc_single, Complete = hc_complete, Average = hc_average)
  for (k in 2:6) {
    cl_full <- cutree(hc_full, k = k)
    names(cl_full) <- rownames(df_q)
    
    perm_aris <- numeric(n_perm)
    for (b in seq_len(n_perm)) {
      perm_idx <- sample(seq_len(nrow(df_q)))
      df_perm <- df_q[perm_idx, , drop = FALSE]
      d_perm <- daisy(df_perm, metric = "gower")
      hc_perm <- hclust(d_perm, method = m_code)
      cl_perm <- cutree(hc_perm, k = k)
      perm_aris[b] <- adjusted_rand_index(cl_full, cl_perm[names(cl_full)])
    }
    
    sub_aris <- numeric(n_sub)
    for (b in seq_len(n_sub)) {
      sub_idx <- sort(sample(seq_len(nrow(df_q)), size = sub_size, replace = FALSE))
      df_sub <- df_q[sub_idx, , drop = FALSE]
      d_sub <- daisy(df_sub, metric = "gower")
      hc_sub <- hclust(d_sub, method = m_code)
      cl_sub <- cutree(hc_sub, k = k)
      sub_aris[b] <- adjusted_rand_index(cl_full[rownames(df_sub)], cl_sub)
    }
    if (m_name == "Average") {
      sub_ari_store[[paste0("K=", k)]] <- sub_aris
    }
    
    stability_rows[[length(stability_rows) + 1]] <- data.frame(
      Method = m_name,
      K = k,
      Perm_ARI_Mean = round(mean(perm_aris), 4),
      Perm_ARI_SD   = round(sd(perm_aris), 4),
      Perm_ARI_Min  = round(min(perm_aris), 4),
      Sub80_ARI_Mean = round(mean(sub_aris), 4),
      Sub80_ARI_SD   = round(sd(sub_aris), 4),
      Sub80_ARI_Median = round(median(sub_aris), 4),
      Sub80_ARI_IQR  = round(IQR(sub_aris), 4)
    )
  }
}
stability_df <- do.call(rbind, stability_rows)
write.csv(stability_df, file.path(tab_dir, "stability_sensitivity_ari.csv"), row.names = FALSE)

# ------------------------------------------------------------------------------
# 4. Cluster Assignments & Profiling (Average Linkage K = 5 and K = 6)
# ------------------------------------------------------------------------------
df$Cluster_K5 <- cutree(hc_average, k = 5)
df$Cluster_K6 <- cutree(hc_average, k = 6)

# Descriptive archetype labels for K = 6
archetype_k6 <- c(
  "1" = "C1: Cross-AI & Peer Triangulators",
  "2" = "C2: Same-AI Conversationalists",
  "3" = "C3: Independent Problem-Solvers",
  "4" = "C4: Course-Material Verifiers",
  "5" = "C5: Uncritical AI Conformers",
  "6" = "C6: AI-Skeptical Anchors"
)
df$Archetype_K6 <- archetype_k6[as.character(df$Cluster_K6)]

write.csv(
  df[, c("ID", "S3_Clean", "S4_Clean", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6_Num",
         "Profile", "Cluster_K5", "Cluster_K6", "Archetype_K6")],
  file.path(tab_dir, "cleaned_responses.csv"),
  row.names = FALSE
)

# Export K=6 within-cluster percentage profile table
k6_prof_rows <- list()
for (cl_id in 1:6) {
  sub_df <- df[df$Cluster_K6 == cl_id, ]
  for (q in q_cols) {
    pcts <- round(100 * prop.table(table(factor(sub_df[[q]], levels = c("A","B","C","D","E","F")))), 1)
    k6_prof_rows[[length(k6_prof_rows) + 1]] <- data.frame(
      Cluster = cl_id,
      Archetype = archetype_k6[as.character(cl_id)],
      n = nrow(sub_df),
      Question = q,
      Opt_A = pcts["A"], Opt_B = pcts["B"], Opt_C = pcts["C"],
      Opt_D = pcts["D"], Opt_E = pcts["E"],
      Opt_F = ifelse(q %in% c("Q3", "Q4"), NA, pcts["F"])
    )
  }
}
k6_prof_df <- do.call(rbind, k6_prof_rows)
write.csv(k6_prof_df, file.path(tab_dir, "k6_cluster_profiles.csv"), row.names = FALSE)

# Export External Validation Tables (Q6 and S4 for K=6 and K=5)
q6_val_k6 <- do.call(data.frame, aggregate(
  df$Q6_Num,
  by = list(Cluster = df$Cluster_K6, Archetype = df$Archetype_K6),
  FUN = function(x) c(n = length(x), Mean = round(mean(x), 2), SD = round(sd(x), 2),
                      Median = median(x), IQR = IQR(x))
))
q6_val_k6 <- q6_val_k6[order(q6_val_k6$Cluster), ]
write.csv(q6_val_k6, file.path(tab_dir, "external_validation_q6_k6.csv"), row.names = FALSE)

known_s4 <- df$S4_Clean != "Unspecified"
s4_ct_k6 <- table(Cluster = df$Cluster_K6[known_s4], Year = droplevels(df$S4_Clean[known_s4]))
s4_pct_k6 <- round(100 * prop.table(s4_ct_k6, margin = 1), 1)
write.csv(as.data.frame.matrix(s4_ct_k6), file.path(tab_dir, "external_validation_s4_counts_k6.csv"))
write.csv(as.data.frame.matrix(s4_pct_k6), file.path(tab_dir, "external_validation_s4_pct_k6.csv"))

# ------------------------------------------------------------------------------
# 5. Generate Publication-Quality Figures
# ------------------------------------------------------------------------------

# Figure 1: Marginal Response Distributions across Q1-Q5
save_dual_plot("fig01_marginal_responses", 8.5, 4.8, function() {
  par(mar = c(4.5, 5.5, 3.2, 8.5), xpd = TRUE)
  mat_pct <- matrix(0, nrow = 6, ncol = 5,
                    dimnames = list(c("A", "B", "C", "D", "E", "F"),
                                    c("Q1: AI Disagrees\nwith You",
                                      "Q2: Two AIs\nDisagree",
                                      "Q3: Missing\nPaper (5 opts)",
                                      "Q4: Unclear\nStep (5 opts)",
                                      "Q5: AI Flips\nAnswer")))
  for (j in seq_along(q_cols)) {
    q <- q_cols[j]
    tb <- prop.table(table(df[[q]])) * 100
    mat_pct[names(tb), j] <- as.numeric(tb)
  }
  cols <- c("#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02")
  bp <- barplot(mat_pct, beside = TRUE, col = cols, ylim = c(0, 48),
                ylab = "Percentage of Respondents (%)",
                main = "Marginal Distribution of Student Responses Across Scenarios Q1-Q5 (n = 261)",
                las = 1, cex.names = 0.88, cex.axis = 0.9, cex.main = 1.05, border = "white")
  abline(h = seq(10, 40, by = 10), col = "gray88", lty = 2)
  barplot(mat_pct, beside = TRUE, col = cols, ylim = c(0, 48), add = TRUE,
          axes = FALSE, axisnames = FALSE, border = "white")
  # Add value labels on top of bars > 0
  for (j in 1:5) {
    for (i in 1:6) {
      if (mat_pct[i, j] > 0) {
        text(bp[i, j], mat_pct[i, j] + 1.5, sprintf("%.0f%%", mat_pct[i, j]), cex = 0.65, col = "gray20")
      }
    }
  }
  legend("topright", inset = c(-0.22, 0),
         legend = c("Option A", "Option B", "Option C", "Option D", "Option E", "Option F"),
         fill = cols, border = "white", bty = "n", cex = 0.85, title = "Choice Code")
})

# Figure 2: Pairwise Normalized Hamming Distance Distribution
save_dual_plot("fig02_hamming_distribution", 7.5, 4.5, function() {
  par(mar = c(4.5, 4.8, 3.2, 2.0))
  dist_tab <- table(factor(round(dist_vec, 1), levels = c(0, 0.2, 0.4, 0.6, 0.8, 1.0)))
  dist_pct <- 100 * prop.table(dist_tab)
  bp <- barplot(dist_pct, col = "#386cb0", border = "white", ylim = c(0, 45),
                xlab = "Normalized Hamming / Gower Distance d(X_i, X_j)",
                ylab = "Percentage of Respondent Pairs (%)",
                main = "Distribution of Pairwise Normalized Hamming Distances (33,930 Pairs)",
                las = 1)
  grid(nx = NA, ny = NULL, col = "gray88", lty = 2)
  barplot(dist_pct, col = "#386cb0", border = "white", ylim = c(0, 45), add = TRUE, axes = FALSE)
  text(bp, as.numeric(dist_pct) + 2.2,
       labels = sprintf("%.2f%%\n(%d pairs)", as.numeric(dist_pct), as.integer(dist_tab)),
       cex = 0.78, col = "gray15")
})

# Figure 3: Dendrogram Comparison (Single, Complete, Average Linkage)
save_dual_plot("fig03_dendrograms_comparison", 11.0, 4.2, function() {
  par(mfrow = c(1, 3), mar = c(2.5, 4.0, 3.2, 1.0))
  plot(hc_single, labels = FALSE, hang = -1, col = "#e41a1c",
       main = sprintf("Single Linkage\n(Cophenetic r = %.3f)", coph_single),
       xlab = "", sub = "", ylab = "Normalized Hamming Distance", ylim = c(0, 1.05))
  abline(h = 0.35, lty = 2, col = "gray40")
  
  plot(hc_complete, labels = FALSE, hang = -1, col = "#ff7f00",
       main = sprintf("Complete Linkage\n(Cophenetic r = %.3f)", coph_complete),
       xlab = "", sub = "", ylab = "Normalized Hamming Distance", ylim = c(0, 1.05))
  rect.hclust(hc_complete, k = 6, border = "gray35")
  
  plot(hc_average, labels = FALSE, hang = -1, col = "#1f78b4",
       main = sprintf("Average Linkage / UPGMA\n(Cophenetic r = %.3f)", coph_average),
       xlab = "", sub = "", ylab = "Normalized Hamming Distance", ylim = c(0, 1.05))
  rect.hclust(hc_average, k = 6, border = "#d95f02")
})

# Figure 4: Silhouette Width & Largest Cluster % across K = 2..8
save_dual_plot("fig04_silhouette_comparison", 9.0, 4.3, function() {
  par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3.0, 1.5))
  
  # Left panel: Average Silhouette Width
  sil_s <- eval_df$Avg_Silhouette[eval_df$Method == "Single"]
  sil_c <- eval_df$Avg_Silhouette[eval_df$Method == "Complete"]
  sil_a <- eval_df$Avg_Silhouette[eval_df$Method == "Average"]
  
  plot(k_range, sil_a, type = "b", pch = 19, lwd = 2.2, col = "#1f78b4",
       ylim = c(-0.27, 0.24), xlab = "Number of Clusters (K)",
       ylab = "Average Silhouette Width",
       main = "Average Silhouette Width vs. K", las = 1)
  grid(col = "gray88", lty = 2)
  lines(k_range, sil_c, type = "b", pch = 17, lwd = 2.0, col = "#ff7f00")
  lines(k_range, sil_s, type = "b", pch = 15, lwd = 2.0, col = "#e41a1c")
  abline(h = 0, lty = 3, col = "gray40")
  points(6, sil_a[k_range == 6], cex = 2.0, col = "#1f78b4", lwd = 2)
  legend("bottomleft", legend = c("Average (UPGMA)", "Complete", "Single"),
         col = c("#1f78b4", "#ff7f00", "#e41a1c"), pch = c(19, 17, 15),
         lwd = 2, bty = "n", cex = 0.85)
  
  # Right panel: Largest Cluster Share (%) showing Chaining Effect
  max_s <- eval_df$Max_Cluster_Pct[eval_df$Method == "Single"]
  max_c <- eval_df$Max_Cluster_Pct[eval_df$Method == "Complete"]
  max_a <- eval_df$Max_Cluster_Pct[eval_df$Method == "Average"]
  
  plot(k_range, max_a, type = "b", pch = 19, lwd = 2.2, col = "#1f78b4",
       ylim = c(20, 102), xlab = "Number of Clusters (K)",
       ylab = "Largest Cluster Share (% of n = 261)",
       main = "Chaining Diagnostic: Largest Cluster %", las = 1)
  grid(col = "gray88", lty = 2)
  lines(k_range, max_c, type = "b", pch = 17, lwd = 2.0, col = "#ff7f00")
  lines(k_range, max_s, type = "b", pch = 15, lwd = 2.0, col = "#e41a1c")
  legend("bottomleft", legend = c("Average (UPGMA)", "Complete", "Single"),
         col = c("#1f78b4", "#ff7f00", "#e41a1c"), pch = c(19, 17, 15),
         lwd = 2, bty = "n", cex = 0.85)
})

# Figure 5: Subsampling Stability (ARI across 100x 80% Subsamples) & Tie Sensitivity
save_dual_plot("fig05_stability_ari", 8.5, 4.3, function() {
  par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3.0, 1.5))
  
  # Left panel: Boxplot of 100x 80% Subsampling ARI for Average Linkage (K = 2..6)
  boxplot(sub_ari_store, col = "#a6cee3", border = "#1f78b4",
          ylim = c(0, 1.0), xlab = "Number of Clusters (Average Linkage)",
          ylab = "Adjusted Rand Index (ARI)",
          main = "80% Subsampling Stability (100 Runs)", las = 1)
  grid(nx = NA, ny = NULL, col = "gray88", lty = 2)
  means_sub <- sapply(sub_ari_store, mean)
  points(seq_along(means_sub), means_sub, pch = 18, col = "#e31a1c", cex = 1.4)
  legend("bottomright", legend = c("Median & IQR", "Mean ARI"),
         pch = c(15, 18), col = c("#a6cee3", "#e31a1c"), bty = "n", cex = 0.82)
  
  # Right panel: Row-Order Permutation Mean ARI across methods (K = 2..6)
  ks <- 2:6
  p_a <- stability_df$Perm_ARI_Mean[stability_df$Method == "Average"]
  p_c <- stability_df$Perm_ARI_Mean[stability_df$Method == "Complete"]
  p_s <- stability_df$Perm_ARI_Mean[stability_df$Method == "Single"]
  
  plot(ks, p_a, type = "b", pch = 19, lwd = 2.2, col = "#1f78b4",
       ylim = c(0, 1.05), xlab = "Number of Clusters (K)",
       ylab = "Mean Permutation ARI (100 Shuffles)",
       main = "Tie / Row-Order Sensitivity Check", las = 1, xaxt = "n")
  axis(1, at = ks)
  grid(col = "gray88", lty = 2)
  lines(ks, p_c, type = "b", pch = 17, lwd = 2.0, col = "#ff7f00")
  lines(ks, p_s, type = "b", pch = 15, lwd = 2.0, col = "#e41a1c")
  legend("topright", legend = c("Average", "Complete", "Single"),
         col = c("#1f78b4", "#ff7f00", "#e41a1c"), pch = c(19, 17, 15),
         lwd = 2, bty = "n", cex = 0.82)
})

# Figure 6: Behavioral Cluster Profiles (Heatmap of Modal & Option Percentages for K = 6)
save_dual_plot("fig06_cluster_profiles", 10.5, 5.5, function() {
  par(mfrow = c(2, 3), mar = c(4.0, 4.2, 3.0, 1.2))
  cols <- c("#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02")
  short_titles <- c(
    "C1: Cross-AI & Peer (n=46, 17.6%)",
    "C2: Same-AI Probe (n=49, 18.8%)",
    "C3: Self-Solvers (n=60, 23.0%)",
    "C4: Course Material (n=68, 26.1%)",
    "C5: AI Conformers (n=20, 7.7%)",
    "C6: Skeptic Anchors (n=18, 6.9%)"
  )
  for (cl_id in 1:6) {
    sub_df <- df[df$Cluster_K6 == cl_id, ]
    mat_c <- matrix(0, nrow = 6, ncol = 5,
                    dimnames = list(c("A","B","C","D","E","F"), q_cols))
    for (j in seq_along(q_cols)) {
      tb <- 100 * prop.table(table(factor(sub_df[[q_cols[j]]], levels = c("A","B","C","D","E","F"))))
      mat_c[, j] <- as.numeric(tb)
    }
    barplot(mat_c, beside = TRUE, col = cols, ylim = c(0, 95),
            main = short_titles[cl_id], ylab = "Within-Cluster %",
            las = 1, border = "white", cex.main = 0.95)
    abline(h = c(25, 50, 75), col = "gray88", lty = 2)
    barplot(mat_c, beside = TRUE, col = cols, ylim = c(0, 95),
            add = TRUE, axes = FALSE, axisnames = FALSE, border = "white")
    if (cl_id == 1) {
      legend("topleft", legend = c("A", "B", "C", "D", "E", "F"),
             fill = cols, border = "white", horiz = TRUE, bty = "n", cex = 0.78)
    }
  }
})

# Figure 7: External Validation -- AI Usage (Q6) and Year of Study (S4) across K = 6 Clusters
save_dual_plot("fig07_external_validation", 10.0, 4.5, function() {
  par(mfrow = c(1, 2), mar = c(5.5, 4.5, 3.2, 1.5))
  
  # Left panel: Boxplot + means of Q6 (AI Usage Days) by Cluster
  cl_labels <- c("C1\nCross-AI\n(n=46)", "C2\nSame-AI\n(n=49)",
                 "C3\nSelf-Solve\n(n=60)", "C4\nCourse-Mat\n(n=68)",
                 "C5\nConformer\n(n=20)", "C6\nSkeptic\n(n=18)")
  cl_cols <- c("#e7298a", "#7570b3", "#d95f02", "#1b9e77", "#66a61e", "#e6ab02")
  boxplot(Q6_Num ~ Cluster_K6, data = df, names = cl_labels, col = cl_cols,
          ylab = "AI Usage in Past 7 Days (Q6: 0-7 Days)", xlab = "",
          main = "External Validation 1: AI Usage (Q6)\n(Kruskal-Wallis p = 0.0147, ANOVA p = 0.0130)",
          las = 1, cex.axis = 0.78, cex.main = 0.95, ylim = c(0, 7.5))
  q6_means <- tapply(df$Q6_Num, df$Cluster_K6, mean)
  points(1:6, q6_means, pch = 18, col = "white", cex = 1.6)
  points(1:6, q6_means, pch = 18, col = "black", cex = 1.2)
  
  # Right panel: Stacked bar chart of Year of Study (S4) by Cluster
  par(mar = c(5.5, 4.5, 3.2, 6.8), xpd = TRUE)
  s4_prop <- prop.table(t(s4_ct_k6), margin = 2) * 100
  colnames(s4_prop) <- c("C1", "C2", "C3", "C4", "C5", "C6")
  yr_cols <- c("#c6dbef", "#6baed6", "#2171b5", "#08306b", "#fd8d3c")
  barplot(s4_prop, col = yr_cols, border = "white",
          ylab = "Within-Cluster Percentage (%)",
          xlab = "Cluster (Average Linkage, K = 6)",
          main = "External Validation 2: Year of Study (S4)\n(Chi-square = 76.66, p = 0.0001)",
          las = 1, cex.main = 0.95)
  legend("topright", inset = c(-0.34, 0),
         legend = c("1st year", "2nd year", "3rd year", "4th year", "Grad/Master"),
         fill = yr_cols, border = "white", bty = "n", cex = 0.78, title = "Study Year")
})

cat("\nAll figures and CSV tables successfully generated in:", out_dir, "\n")
