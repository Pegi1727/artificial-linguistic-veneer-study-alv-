df <- read.csv("reconstructed_raw_data_50.csv")
m2 <- lm(ODP ~ ALV + AI_Agency, data = df)
summary(m2)
