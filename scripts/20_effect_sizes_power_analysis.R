# Post-hoc effect size (Cohen's f2) calculation
# Model 3 R2 = 0.5487, Delta R2 = 0.089
r2 <- 0.5487
f2 <- r2 / (1 - r2)
cat("Model 3 Cohen's f^2 effect size: ", round(f2, 4), "\n")
cat("Effect size is large (f^2 > 0.35)\n")
