# power_analysis.R — Pre-experiment power analysis for Lion's Feed A/B test
#
# Computes minimum detectable effect size for the planned sample size
# and generates a power curve visualization.

library(pwr)

# ---- Parameters ----
n_per_group <- 30       # Target: 30 users per group
alpha       <- 0.05     # Significance level
power_target <- 0.80    # Desired power

# ---- User-level power analysis (two-proportion z-test) ----
cat("=== User-Level Power Analysis ===\n")
cat(sprintf("n per group: %d\n", n_per_group))
cat(sprintf("Alpha: %.2f (two-sided)\n", alpha))
cat(sprintf("Target power: %.0f%%\n\n", power_target * 100))

# What effect size can we detect?
result <- pwr.2p.test(
  n = n_per_group,
  sig.level = alpha,
  power = power_target,
  alternative = "two.sided"
)
cat(sprintf("Minimum detectable effect size (Cohen's h): %.3f\n", result$h))

# Convert to concrete CTR difference example
# If baseline CTR ~ 40%, what difference can we detect?
p_baseline <- 0.40
h_detectable <- result$h
# Cohen's h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))
# Solve for p2 given p1 and h
p_treatment <- sin(asin(sqrt(p_baseline)) + h_detectable / 2)^2
cat(sprintf(
  "Example: If baseline CTR = %.0f%%, detectable treatment CTR ~ %.0f%% (diff = %.0f pp)\n\n",
  p_baseline * 100, p_treatment * 100, (p_treatment - p_baseline) * 100
))

# ---- Article-level power (mixed-effects compensates for small n) ----
cat("=== Article-Level Observations ===\n")
n_articles <- 6
n_obs_per_group <- n_per_group * n_articles
cat(sprintf("Each user sees %d articles -> ~%d observations per group\n", n_articles, n_obs_per_group))
cat(sprintf("Total observations: ~%d\n", n_obs_per_group * 2))
cat("Mixed-effects logistic regression with user random intercept\n")
cat("leverages repeated measures for better power than user-level test.\n\n")

# ---- Power curve ----
cat("=== Generating Power Curve ===\n")
n_range <- seq(10, 100, by = 5)
effect_sizes <- c(0.3, 0.4, 0.5, 0.6, 0.8)

pdf("power_curve.pdf", width = 8, height = 5)
par(mar = c(4, 4, 2, 1))

colors <- c("#2c3e50", "#2980b9", "#27ae60", "#f39c12", "#e74c3c")
plot(NULL, xlim = c(10, 100), ylim = c(0, 1),
     xlab = "Sample Size per Group", ylab = "Power",
     main = "Power Curves for Two-Proportion Z-Test (Two-Sided, alpha = 0.05)")
abline(h = 0.80, lty = 2, col = "gray60")
text(12, 0.82, "80% power", col = "gray40", cex = 0.8)
abline(v = 30, lty = 3, col = "gray60")
text(32, 0.05, "n=30", col = "gray40", cex = 0.8)

for (i in seq_along(effect_sizes)) {
  powers <- sapply(n_range, function(n) {
    pwr.2p.test(h = effect_sizes[i], n = n, sig.level = alpha,
                alternative = "two.sided")$power
  })
  lines(n_range, powers, col = colors[i], lwd = 2)
}

legend("bottomright",
       legend = paste("h =", effect_sizes),
       col = colors, lwd = 2, cex = 0.8,
       title = "Effect Size (Cohen's h)")

dev.off()
cat("Saved: power_curve.pdf\n")
