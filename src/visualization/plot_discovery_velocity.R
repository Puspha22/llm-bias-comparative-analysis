# Discovery Velocity Publication Plotting Script in R (ggplot2)
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

# Scaling factor for dual Y axis
coeff <- max(df$K) / max(df$Velocity)

p <- ggplot(df, aes(x = N)) +
  # Soft pastel area fill under K(N)
  geom_area(aes(y = K), fill = "#EBF4FF", alpha = 0.7) +
  
  # Saturation threshold vertical line at 100k
  geom_vline(xintercept = 100000, linetype = "dashed", color = "#C53030", linewidth = 0.8) +
  
  # Primary Line: Cumulative Failure Modes K(N)
  geom_line(aes(y = K, color = "Cumulative Failures K(N)"), linewidth = 1.3) +
  geom_point(aes(y = K, color = "Cumulative Failures K(N)"), size = 3, shape = 19) +
  
  # Secondary Line: Discovery Velocity dK/dN
  geom_line(aes(y = Velocity * coeff, color = "Discovery Velocity dK/dN"), linewidth = 1.1, linetype = "dotdash") +
  geom_point(aes(y = Velocity * coeff, color = "Discovery Velocity dK/dN"), size = 2.8, shape = 15) +
  
  # Axes scales and formatting
  scale_y_continuous(
    name = "Cumulative Unique Failures Discovered K(N)",
    limits = c(0, 45),
    expand = c(0, 0),
    sec.axis = sec_axis(~./coeff, name = "Discovery Velocity (dK/dN)")
  ) +
  scale_x_continuous(
    name = "Sample Budget (N Iterations)",
    labels = comma,
    breaks = c(0, 25000, 50000, 75000, 100000),
    limits = c(0, 105000),
    expand = c(0, 0)
  ) +
  
  # Color Palette
  scale_color_manual(
    values = c(
      "Cumulative Failures K(N)" = "#1A365D",
      "Discovery Velocity dK/dN" = "#C53030"
    )
  ) +
  
  # Clean Academic Journal Theme
  theme_bw(base_size = 13, base_family = "sans") +
  theme(
    plot.background = element_rect(fill = "#FFFFFF", color = NA),
    panel.background = element_rect(fill = "#FFFFFF", color = NA),
    panel.border = element_rect(color = "#2D3748", fill = NA, linewidth = 0.8),
    panel.grid.major = element_line(color = "#EDF2F7", linewidth = 0.5),
    panel.grid.minor = element_blank(),
    
    plot.title = element_text(face = "bold", size = 15, hjust = 0.5, color = "#1A202C", margin = margin(b = 12)),
    
    axis.title.x = element_text(face = "bold", color = "#2D3748", size = 12, margin = margin(t = 10)),
    axis.title.y.left = element_text(face = "bold", color = "#1A365D", size = 12, margin = margin(r = 10)),
    axis.title.y.right = element_text(face = "bold", color = "#C53030", size = 12, margin = margin(l = 10)),
    
    axis.text.x = element_text(color = "#4A5568", size = 10),
    axis.text.y.left = element_text(color = "#1A365D", size = 10, face = "bold"),
    axis.text.y.right = element_text(color = "#C53030", size = 10, face = "bold"),
    
    legend.position = "top",
    legend.title = element_blank(),
    legend.background = element_rect(fill = "#FFFFFF", color = "#E2E8F0", linewidth = 0.5),
    legend.key = element_rect(fill = "#FFFFFF", color = NA),
    legend.text = element_text(size = 11, face = "bold", color = "#2D3748"),
    legend.margin = margin(t = 4, b = 6, l = 10, r = 10)
  ) +
  labs(
    title = "Monte Carlo Discovery Velocity & Failure Mode Saturation (dK/dN)"
  )

# Save high-res publication PNG
ggsave("reports/figures/discovery_velocity_ggplot2.png", plot = p, width = 9, height = 5.5, dpi = 300, bg = "white")
cat("Saved publication-grade ggplot2 figure to reports/figures/discovery_velocity_ggplot2.png\n")
