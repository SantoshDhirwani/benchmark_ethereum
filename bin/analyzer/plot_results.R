#install.packages("ggplot2", dependencies=TRUE, repos = "http://cran.us.r-project.org")
library(ggplot2)

data <- read.csv("analyzer/aggregated-results/data_transfer.csv", header=TRUE, sep=",")

ggplot(data, aes(x=gasLimit, y=blockInterval, size = throughput)) +
    geom_point(alpha=0.7)
ggsave(path = "analyzer/aggregated-results", filename = "plot_results.png")