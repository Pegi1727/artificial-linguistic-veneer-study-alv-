df <- read.csv("reconstructed_raw_data_50.csv")
m1 <- lm(ODP ~ ALV, data = df)
summary(m1)
