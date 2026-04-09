# analysis.R — Statistical analysis and visualization for Lion's Feed A/B test
#
# Reads clean_data.csv and click_level.csv produced by process_data.py.
# Runs primary and secondary statistical tests, generates ggplot2 visualizations.

library(dplyr)
library(ggplot2)
library(lme4)

theme_lions <- theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", size = 15),
    plot.subtitle = element_text(color = "gray40"),
    panel.grid.minor = element_blank()
  )

COLUMBIA_BLUE <- "#B9D9EB"
GROUP_COLORS <- c("A" = "#2c3e50", "B" = COLUMBIA_BLUE)

# ---- Load Data ----
cat("Loading data...\n")
user_data  <- read.csv("clean_data.csv", stringsAsFactors = FALSE)
click_data <- read.csv("click_level.csv", stringsAsFactors = FALSE)

n_a <- sum(user_data$group == "A")
n_b <- sum(user_data$group == "B")
cat(sprintf("Group A: %d users, Group B: %d users\n\n", n_a, n_b))

# ============================================================
# PRIMARY TEST: Two-proportion z-test for CTR
# ============================================================
cat("=== PRIMARY: Two-Proportion Z-Test (CTR) ===\n")

clicks_a <- sum(user_data$total_clicks[user_data$group == "A"])
clicks_b <- sum(user_data$total_clicks[user_data$group == "B"])
n_articles <- max(click_data %>% distinct(article_id) %>% nrow(), 6)
opportunities_a <- n_a * n_articles
opportunities_b <- n_b * n_articles

prop_test <- prop.test(
  x = c(clicks_a, clicks_b),
  n = c(opportunities_a, opportunities_b),
  alternative = "two.sided",
  correct = TRUE  # Yates' continuity correction for small samples
)

cat(sprintf("CTR_A = %d/%d = %.3f\n", clicks_a, opportunities_a,
            clicks_a / opportunities_a))
cat(sprintf("CTR_B = %d/%d = %.3f\n", clicks_b, opportunities_b,
            clicks_b / opportunities_b))
cat(sprintf("Chi-squared = %.4f, p-value = %.4f\n", prop_test$statistic,
            prop_test$p.value))
cat(sprintf("95%% CI for difference: [%.4f, %.4f]\n\n",
            prop_test$conf.int[1], prop_test$conf.int[2]))

# ============================================================
# SECONDARY TESTS
# ============================================================

# --- Mann-Whitney U for time on page ---
cat("=== SECONDARY: Mann-Whitney U (Article Read Time) ===\n")
time_a <- user_data$avg_article_time[user_data$group == "A"]
time_b <- user_data$avg_article_time[user_data$group == "B"]
time_a <- time_a[!is.na(time_a)]
time_b <- time_b[!is.na(time_b)]

if (length(time_a) > 0 && length(time_b) > 0) {
  wilcox_time <- wilcox.test(time_a, time_b, alternative = "two.sided")
  cat(sprintf("Median article time A: %.1fs, B: %.1fs\n",
              median(time_a), median(time_b)))
  cat(sprintf("W = %.1f, p-value = %.4f\n\n", wilcox_time$statistic,
              wilcox_time$p.value))
} else {
  cat("Insufficient article time data for test.\n\n")
}

# --- Mann-Whitney U for scroll depth ---
cat("=== SECONDARY: Mann-Whitney U (Scroll Depth) ===\n")
scroll_a <- user_data$max_scroll_depth[user_data$group == "A"]
scroll_b <- user_data$max_scroll_depth[user_data$group == "B"]

if (length(scroll_a) > 0 && length(scroll_b) > 0) {
  wilcox_scroll <- wilcox.test(scroll_a, scroll_b, alternative = "two.sided")
  cat(sprintf("Median scroll A: %.0f%%, B: %.0f%%\n",
              median(scroll_a), median(scroll_b)))
  cat(sprintf("W = %.1f, p-value = %.4f\n\n", wilcox_scroll$statistic,
              wilcox_scroll$p.value))
} else {
  cat("Insufficient scroll data for test.\n\n")
}

# --- Mixed-effects logistic regression ---
cat("=== SECONDARY: Mixed-Effects Logistic Regression ===\n")
cat("Model: clicked ~ group + article_position + category + (1|user_id)\n")

click_data$group    <- factor(click_data$group, levels = c("A", "B"))
click_data$category <- factor(click_data$category)
click_data$user_id  <- factor(click_data$user_id)

tryCatch({
  model <- glmer(
    clicked ~ group + article_position + category + (1 | user_id),
    data = click_data,
    family = binomial,
    control = glmerControl(optimizer = "bobyqa")
  )
  cat("\n")
  print(summary(model))

  # Odds ratio for group effect
  coefs <- fixef(model)
  se    <- sqrt(diag(vcov(model)))
  or    <- exp(coefs["groupB"])
  or_ci <- exp(coefs["groupB"] + c(-1.96, 1.96) * se[names(coefs) == "groupB"])
  cat(sprintf(
    "\nGroup B odds ratio: %.3f (95%% CI: %.3f - %.3f)\n\n",
    or, or_ci[1], or_ci[2]
  ))
}, error = function(e) {
  cat(sprintf("Model failed (likely insufficient data): %s\n\n", e$message))
})

# ============================================================
# VISUALIZATIONS
# ============================================================
cat("=== Generating Plots ===\n")
dir.create("plots", showWarnings = FALSE)

# --- 1. CTR bar chart with confidence intervals ---
ctr_summary <- user_data %>%
  group_by(group) %>%
  summarise(
    mean_ctr = mean(ctr, na.rm = TRUE),
    se_ctr = sd(ctr, na.rm = TRUE) / sqrt(n()),
    n = n(),
    .groups = "drop"
  )

p1 <- ggplot(ctr_summary, aes(x = group, y = mean_ctr, fill = group)) +
  geom_col(width = 0.5) +
  geom_errorbar(
    aes(ymin = mean_ctr - 1.96 * se_ctr, ymax = mean_ctr + 1.96 * se_ctr),
    width = 0.15
  ) +
  scale_fill_manual(values = GROUP_COLORS) +
  labs(
    title = "Click-Through Rate by Group",
    subtitle = sprintf("n_A = %d, n_B = %d | p = %.4f", n_a, n_b, prop_test$p.value),
    x = "Experiment Group",
    y = "Mean CTR"
  ) +
  theme_lions +
  theme(legend.position = "none")

ggsave("plots/ctr_by_group.png", p1, width = 6, height = 5, dpi = 150)
cat("  Saved: plots/ctr_by_group.png\n")

# --- 2. Box plot of article read time ---
time_data <- user_data %>% filter(!is.na(avg_article_time))
if (nrow(time_data) > 0) {
  p2 <- ggplot(time_data, aes(x = group, y = avg_article_time, fill = group)) +
    geom_boxplot(width = 0.4, outlier.shape = 21) +
    geom_jitter(width = 0.1, alpha = 0.4, size = 1.5) +
    scale_fill_manual(values = GROUP_COLORS) +
    labs(
      title = "Average Article Read Time by Group",
      x = "Experiment Group",
      y = "Seconds"
    ) +
    theme_lions +
    theme(legend.position = "none")

  ggsave("plots/read_time_by_group.png", p2, width = 6, height = 5, dpi = 150)
  cat("  Saved: plots/read_time_by_group.png\n")
}

# --- 3. Per-article click rates (heatmap) ---
article_clicks <- click_data %>%
  group_by(group, article_id) %>%
  summarise(click_rate = mean(clicked), .groups = "drop")

if (nrow(article_clicks) > 0) {
  p3 <- ggplot(article_clicks, aes(x = group, y = article_id, fill = click_rate)) +
    geom_tile(color = "white", linewidth = 1) +
    scale_fill_gradient(low = "white", high = "#2c3e50",
                        name = "Click Rate", limits = c(0, 1)) +
    labs(
      title = "Click Rate by Article and Group",
      x = "Group",
      y = "Article ID"
    ) +
    theme_lions

  ggsave("plots/click_heatmap.png", p3, width = 7, height = 5, dpi = 150)
  cat("  Saved: plots/click_heatmap.png\n")
}

# --- 4. Total clicks distribution ---
p4 <- ggplot(user_data, aes(x = total_clicks, fill = group)) +
  geom_histogram(binwidth = 1, position = "dodge", color = "white") +
  scale_fill_manual(values = GROUP_COLORS) +
  labs(
    title = "Distribution of Total Clicks per User",
    x = "Number of Articles Clicked",
    y = "Count"
  ) +
  theme_lions

ggsave("plots/clicks_distribution.png", p4, width = 7, height = 5, dpi = 150)
cat("  Saved: plots/clicks_distribution.png\n")

# --- 5. Scroll depth comparison ---
p5 <- ggplot(user_data, aes(x = group, y = max_scroll_depth, fill = group)) +
  geom_boxplot(width = 0.4) +
  geom_jitter(width = 0.1, alpha = 0.4, size = 1.5) +
  scale_fill_manual(values = GROUP_COLORS) +
  labs(
    title = "Maximum Scroll Depth by Group",
    x = "Group",
    y = "Scroll Depth (%)"
  ) +
  theme_lions +
  theme(legend.position = "none")

ggsave("plots/scroll_depth.png", p5, width = 6, height = 5, dpi = 150)
cat("  Saved: plots/scroll_depth.png\n")

cat("\n=== Analysis Complete ===\n")
cat("Note on multiple comparisons: Secondary metrics are exploratory.\n")
cat("Apply Bonferroni correction or interpret as hypothesis-generating.\n")
