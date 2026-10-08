df <- read.csv("reconstructed_raw_data_50.csv")
df$ALV_c <- df$ALV - mean(df$ALV)
df$AIA_c <- df$AI_Agency - mean(df$AI_Agency)
df$Int <- df$ALV_c * df$AIA_c
m <- lm(ODP ~ ALV_c + AIA_c + Int, data = df)
# JN significance cutoff evaluation across moderator range
mod_seq <- seq(min(df$AIA_c), max(df$AIA_c), length.out = 50)
vc <- vcov(m)
slopes <- coef(m)["ALV_c"] + coef(m)["Int"] * mod_seq
se_slopes <- sqrt(vc["ALV_c", "ALV_c"] + (mod_seq^2) * vc["Int", "Int"] + 2 * mod_seq * vc["ALV_c", "Int"])
t_vals <- slopes / se_slopes
cat("JN Analysis completed across moderator range.\n")
