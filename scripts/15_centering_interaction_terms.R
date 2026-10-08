df <- read.csv("reconstructed_raw_data_50.csv")
df$ALV_c <- scale(df$ALV, scale = FALSE)
df$AIA_c <- scale(df$AI_Agency, scale = FALSE)
df$interaction <- df$ALV_c * df$AIA_c
write.csv(df, "script_outputs/centered_data.csv", row.names = FALSE)
cat("Mean-centering and interaction terms computed and saved.\n")
