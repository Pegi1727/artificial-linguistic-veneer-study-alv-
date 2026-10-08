df <- read.csv("reconstructed_raw_data_50.csv")
df$ALV_c <- scale(df$ALV, scale = FALSE)
df$AIA_c <- scale(df$AI_Agency, scale = FALSE)
df$Int <- df$ALV_c * df$AIA_c
m <- lm(ODP ~ ALV_c + AIA_c + Int, data = df)

# Manual VIF calculation
r2_alv <- summary(lm(ALV_c ~ AIA_c + Int, data = df))$r.squared
r2_aia <- summary(lm(AIA_c ~ ALV_c + Int, data = df))$r.squared
r2_int <- summary(lm(Int ~ ALV_c + AIA_c, data = df))$r.squared

vifs <- c(ALV = 1 / (1 - r2_alv), AIA = 1 / (1 - r2_aia), Int = 1 / (1 - r2_int))
cat("VIF Values (Centered):\n")
print(vifs)
