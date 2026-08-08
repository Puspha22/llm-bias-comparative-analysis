library(ggplot2)
library(jsonlite)
library(dplyr)
library(tidyr)

theme_set(theme_minimal(base_family = "serif", base_size = 13) +
          theme(
            plot.title = element_text(hjust = 0.5, face = "bold", size = 15),
            axis.title = element_text(face = "bold", size = 13),
            panel.grid.minor = element_blank(),
            panel.grid.major.x = element_blank(),
            legend.position = "bottom",
            legend.title = element_blank(),
            legend.text = element_text(size = 11)
          ))

legacy   <- fromJSON("reports/feature_metrics/complexity_legacy.json")
expanded <- fromJSON("reports/feature_metrics/complexity_expanded.json")
gemini   <- fromJSON("reports/feature_metrics/complexity_gemini.json")
grok     <- fromJSON("reports/feature_metrics/complexity_grok.json")

df_legacy   <- data.frame(Attributes = legacy,   Model = "Gemini Legacy (Cond. 1)")
df_expanded <- data.frame(Attributes = expanded, Model = "Gemini Expanded (Cond. 2)")
df_gemini   <- data.frame(Attributes = gemini,   Model = "Gemini Unified (Cond. 3)")
df_grok     <- data.frame(Attributes = grok,     Model = "Grok Unified (Cond. 4)")

df <- bind_rows(df_legacy, df_expanded, df_gemini, df_grok)
df$Model <- factor(df$Model, levels = c(
  "Gemini Legacy (Cond. 1)", 
  "Gemini Expanded (Cond. 2)", 
  "Gemini Unified (Cond. 3)", 
  "Grok Unified (Cond. 4)"
))

p <- ggplot(df, aes(x = Attributes, fill = Model)) +
  geom_bar(position = position_dodge(preserve = "single"), alpha = 0.9, width = 0.85, color = "black", size = 0.25) +
  scale_fill_manual(values = c(
    "Gemini Legacy (Cond. 1)"   = "#9ecae1",
    "Gemini Expanded (Cond. 2)" = "#4292c6",
    "Gemini Unified (Cond. 3)"  = "#08519c",
    "Grok Unified (Cond. 4)"    = "#2c3e50"
  )) +
  labs(
    title = "Distribution of Utilized Input Variables Across Controlled Prompt Conditions",
    x = "Number of Input Variables Utilized Per Function", 
    y = "Number of Generated Functions"
  ) +
  scale_x_continuous(breaks = seq(0, 15, 1)) +
  coord_cartesian(xlim = c(-0.5, 12.5))

# Save to reports/figures
dir.create("reports/figures", showWarnings = FALSE, recursive = TRUE)
ggsave("reports/figures/complexity_combined.pdf", plot = p, width = 10, height = 5.2, device = "pdf")
ggsave("reports/figures/complexity_combined.png", plot = p, width = 10, height = 5.2, dpi = 300)

# Save to MDPI Assets
mdpi_dir <- "MDPI___A_Comparative_Analysis_of_Implicit_Bias_and_Logical_Inconsistency_in_General_Purpose_and_Code_Specialized_Large_Language_Models/Assets"
if (dir.exists(mdpi_dir)) {
  ggsave(file.path(mdpi_dir, "complexity_combined.pdf"), plot = p, width = 10, height = 5.2, device = "pdf")
  ggsave(file.path(mdpi_dir, "complexity_combined.png"), plot = p, width = 10, height = 5.2, dpi = 300)
}

cat("Successfully generated publication-ready complexity_combined plots in R!\n")

