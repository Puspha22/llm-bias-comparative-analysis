# Discovery Velocity Plotting Script in R (ggplot2)
library(jsonlite)
library(ggplot2)
library(scales)

# Read report
report_path <- "reports/summary/sensitivity_analysis_report.json"
data <- fromJSON(report_path)

dv_summary <- data$discovery_velocity_summary
budgets <- as.numeric(names(dv_summary))

df <- data.frame(
  N = budgets,
  K = sapply(dv_summary, function(x) x$cumulative_failure_modes_K),
  Velocity = sapply(dv_summary, function(x) x$discovery_velocity_dK_dN)
)

# Scaling factor for dual Y axis in ggplot2
coeff <- max(df$K) / max(df$Velocity)

p <- ggplot(df, aes(x = N)) +
  geom_area(aes(y = K), fill = "#EBF8FF", alpha = 0.6) +
  geom_line(aes(y = K, color = "Cumulative Failures K(N)"), size = 1.2) +
  geom_point(aes(y = K, color = "Cumulative Failures K(N)"), size = 3) +
  geom_line(aes(y = Velocity * coeff, color = "Discovery Velocity dK/dN"), size = 1.1, linetype = "dashed") +
  geom_point(aes(y = Velocity * coeff, color = "Discovery Velocity dK/dN"), size = 2.5, shape = 15) +
  geom_vline(xintercept = 100000, linetype = "dotted", color = "#E53E3E", size = 1) +
  scale_y_continuous(
    name = "Cumulative Unique Failures Discovered K(N)",
    sec.axis = sec_axis(~./coeff, name = "Discovery Velocity (dK/dN)")
  ) +
  scale_x_continuous(labels = comma, breaks = c(0, 25000, 50000, 75000, 100000)) +
  scale_color_manual(values = c("Cumulative Failures K(N)" = "#2B6CB0", "Discovery Velocity dK/dN" = "#DD6B20")) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 16, hjust = 0.5),
    legend.position = "top",
    legend.title = element_blank(),
    axis.title.y.left = element_text(color = "#2B6CB0", face = "bold"),
    axis.title.y.right = element_text(color = "#DD6B20", face = "bold"),
    panel.grid.minor = element_blank()
  ) +
  labs(
    title = "Monte Carlo Discovery Velocity & Failure Mode Saturation",
    x = "Sample Budget (N Iterations)"
  )

ggsave("reports/figures/discovery_velocity_ggplot2.png", plot = p, width = 9, height = 5.5, dpi = 300)
cat("Saved ggplot2 figure to reports/figures/discovery_velocity_ggplot2.png\n")
