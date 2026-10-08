df <- read.csv("reconstructed_raw_data_50.csv")
df$ALV_c <- df$ALV - mean(df$ALV)
df$AIA_c <- df$AI_Agency - mean(df$AI_Agency)
df$Int <- df$ALV_c * df$AIA_c

m1 <- lm(ODP ~ ALV_c, data = df)
m2 <- lm(ODP ~ ALV_c + AIA_c, data = df)
m3 <- lm(ODP ~ ALV_c + AIA_c + Int, data = df)

anova(m1, m2, m3)
