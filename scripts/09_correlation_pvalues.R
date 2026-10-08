df <- read.csv("reconstructed_raw_data_50.csv")
pairs <- list(c("ALV", "ODP"), c("AI_Agency", "ODP"), c("ALV", "AI_Agency"))
res <- do.call(rbind, lapply(pairs, function(p) {
  ct <- cor.test(df[[p[1]]], df[[p[2]]])
  data.frame(Pair = paste(p[1], "-", p[2]), r = ct$estimate, p_val = ct$p.value, ci_low = ct$conf.int[1], ci_high = ct$conf.int[2])
}))
print(res)
write.csv(res, "script_outputs/correlation_significance.csv", row.names = FALSE)
