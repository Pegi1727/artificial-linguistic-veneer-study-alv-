df <- read.csv("reconstructed_raw_data_50.csv")
vars <- c("ALV", "AI_Agency", "ODP")
stats <- data.frame(
  Variable = vars,
  Mean = sapply(df[vars], mean),
  SD = sapply(df[vars], sd),
  Min = sapply(df[vars], min),
  Max = sapply(df[vars], max)
)
print(stats)
write.csv(stats, "script_outputs/descriptive_statistics.csv", row.names = FALSE)
