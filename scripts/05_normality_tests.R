df <- read.csv("reconstructed_raw_data_50.csv")
vars <- c("ALV", "AI_Agency", "ODP")
norm_tests <- do.call(rbind, lapply(vars, function(v) {
  st <- shapiro.test(df[[v]])
  data.frame(Variable = v, W = st$statistic, p_value = st$p.value)
}))
print(norm_tests)
write.csv(norm_tests, "script_outputs/normality_tests.csv", row.names = FALSE)
