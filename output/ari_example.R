A <- c(1, 1, 1, 2, 2, 2)
B <- c(1, 1, 2, 2, 2, 2)
students <- paste0("S", 1:6)

tab <- table(A, B)
nij <- sum(choose(tab, 2))
ai <- sum(choose(rowSums(tab), 2))
bj <- sum(choose(colSums(tab), 2))
N <- choose(6, 2)
expected <- (ai * bj) / N
max_idx <- 0.5 * (ai + bj)
ari <- (nij - expected) / (max_idx - expected)
ri <- (nij + (N - ai - bj + nij)) / N

png("output/figures/diag06_ari_example.png", width = 1800, height = 700, res = 180)
par(mfrow = c(1, 3), mar = c(2.5, 2.0, 3.5, 1.5), oma = c(0, 0, 2, 0))

# --- Panel 1: Two Groupings ---
plot(0, 0, type = "n", xlim = c(0, 10), ylim = c(0, 7), axes = FALSE, xlab = "", ylab = "",
     main = "1. Two Groupings of 6 Students")
# Boxes for Grouping A
rect(0.1, 3.7, 4.2, 6.5, col = "#deebf7", border = "#08519c", lwd = 2)
text(2.15, 6.15, "Grouping A: G1", cex = 0.85, font = 2, col = "#08519c")
rect(0.1, 0.4, 4.2, 3.2, col = "#fee6ce", border = "#d94801", lwd = 2)
text(2.15, 2.85, "Grouping A: G2", cex = 0.85, font = 2, col = "#d94801")

# Boxes for Grouping B
rect(5.8, 4.4, 9.9, 6.5, col = "#deebf7", border = "#08519c", lwd = 2)
text(7.85, 6.15, "Grouping B: G1", cex = 0.85, font = 2, col = "#08519c")
rect(5.8, 0.4, 9.9, 3.9, col = "#fee6ce", border = "#d94801", lwd = 2)
text(7.85, 3.55, "Grouping B: G2", cex = 0.85, font = 2, col = "#d94801")

yA <- c(5.5, 4.8, 4.1, 2.2, 1.5, 0.8)
yB <- c(5.5, 4.8, 2.9, 2.2, 1.5, 0.8)
for (i in 1:6) {
  col_pt <- if (i == 3) "#e31a1c" else "#252525"
  points(1.7, yA[i], pch = 19, cex = 1.3, col = col_pt)
  text(1.85, yA[i], students[i], pos = 4, cex = 0.9, font = if (i == 3) 2 else 1, col = col_pt)
  points(7.4, yB[i], pch = 19, cex = 1.3, col = col_pt)
  text(7.55, yB[i], students[i], pos = 4, cex = 0.9, font = if (i == 3) 2 else 1, col = col_pt)
}
arrows(3.2, yA[3], 6.8, yB[3], col = "#e31a1c", lwd = 2.2, length = 0.1)
text(5.0, 3.85, "S3 moves", col = "#e31a1c", cex = 0.85, font = 2)

# --- Panel 2: Pairwise Agreement (15 pairs) ---
plot(0, 0, type = "n", xlim = c(0.5, 6.5), ylim = c(0.5, 6.8), axes = FALSE, xlab = "", ylab = "",
     main = "2. Check All 15 Pairs")
axis(1, 1:6, students, tick = FALSE, line = -0.8, cex.axis = 0.9)
axis(2, 1:6, rev(students), tick = FALSE, las = 1, line = -0.8, cex.axis = 0.9)

for (i in 1:5) {
  for (j in (i + 1):6) {
    sameA <- A[i] == A[j]
    sameB <- B[i] == B[j]
    if (sameA && sameB) {
      fill <- "#a1d99b"; lbl <- "a"
    } else if (!sameA && !sameB) {
      fill <- "#9ecae1"; lbl <- "b"
    } else {
      fill <- "#fcae91"; lbl <- "X"
    }
    rect(j - 0.45, (7 - i) - 0.45, j + 0.45, (7 - i) + 0.45, col = fill, border = "white", lwd = 1.5)
    text(j, 7 - i, lbl, cex = 0.95, font = 2)
  }
}
legend("bottomleft",
       legend = c("a = Both together (4)", "b = Both apart (6)", "X = Disagree (5)"),
       fill = c("#a1d99b", "#9ecae1", "#fcae91"), bty = "n", cex = 0.85)

# --- Panel 3: RI vs ARI ---
plot(0, 0, type = "n", xlim = c(0, 10), ylim = c(0, 7), axes = FALSE, xlab = "", ylab = "",
     main = "3. Rand Index vs. Adjusted RI")
rect(0.3, 4.0, 9.7, 6.4, col = "#f7f7f7", border = "#969696", lwd = 1.5)
text(5.0, 5.9, "Raw Rand Index (RI)", font = 2, cex = 1.0)
text(5.0, 5.1, "Agreeing pairs / Total = (4 + 6) / 15 = 0.67", cex = 0.88, col = "#08519c")
text(5.0, 4.4, "(Looks high, but ignores random chance!)", cex = 0.78, col = "#636363")

rect(0.3, 0.7, 9.7, 3.4, col = "#edf8e9", border = "#238b45", lwd = 2)
text(5.0, 2.9, "Adjusted Rand Index (ARI)", font = 2, cex = 1.0, col = "#238b45")
text(5.0, 2.1, sprintf("ARI = (4 - %.2f) / (%.2f - %.2f) = %.2f", expected, max_idx, expected, ari),
     cex = 0.9, font = 2, col = "#238b45")
text(5.0, 1.3, "Subtracts chance agreement -> true similarity", cex = 0.8, col = "#252525")

mtext("Worked Example: Measuring Cluster Stability with Rand Index & ARI", outer = TRUE, cex = 1.25, font = 2)
dev.off()
