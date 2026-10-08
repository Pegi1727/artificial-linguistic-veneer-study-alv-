df <- read.csv("reconstructed_raw_data_50.csv")
df$ALV_c <- df$ALV - mean(df$ALV)
df$AIA_c <- df$AI_Agency - mean(df$AI_Agency)
df$Int <- df$ALV_c * df$AIA_c
m3 <- lm(ODP ~ ALV_c + AIA_c + Int, data = df)

b1 <- coef(m3)["ALV_c"]
b3 <- coef(m3)["Int"]
sd_mod <- sd(df$AIA_c)

cat("Simple Slope at -1 SD (Low Agency): ", b1 - b3 * sd_mod, "\n")
cat("Simple Slope at Mean (Mean Agency): ", b1, "\n")
cat("Simple Slope at +1 SD (High Agency):", b1 + b3 * sd_mod, "\n")
