library(ggplot2)
library(jsonlite)
library(dplyr)
library(tidyr)

theme_set(theme_minimal(base_family = "serif", base_size = 14) +
          theme(
            plot.title = element_text(hjust = 0.5, face = "bold"),
            panel.grid.minor = element_blank(),
            legend.position = "bottom",
            legend.title = element_blank()
          ))

legacy <- fromJSON("reports/complexity_legacy.json")
gemini <- fromJSON("reports/complexity_gemini.json")
grok <- fromJSON("reports/complexity_grok.json")

df_legacy <- data.frame(Attributes = legacy, Model = "Legacy Prompts")
df_gemini <- data.frame(Attributes = gemini, Model = "Gemini 2.5 Flash")
df_grok <- data.frame(Attributes = grok, Model = "Grok-Code-Fast-1")

df <- bind_rows(df_legacy, df_gemini, df_grok)
df$Model <- factor(df$Model, levels = c("Legacy Prompts", "Gemini 2.5 Flash", "Grok-Code-Fast-1"))

p <- ggplot(df, aes(x = Attributes, fill = Model)) +
  geom_bar(position = position_dodge(preserve = "single"), alpha = 0.85, width = 0.8) +
  scale_fill_manual(values = c("Legacy Prompts" = "#34A853", "Gemini 2.5 Flash" = "#4285F4", "Grok-Code-Fast-1" = "#2c3e50")) +
  labs(x = "Number of Input Variables Utilized", y = "Number of Functions") +
  scale_x_continuous(breaks = seq(0, 15, 1)) +
  coord_cartesian(xlim = c(0, 15))

ggsave("siuethesis/Assets/complexity_combined.pdf", plot = p, width = 10, height = 5, device = "pdf")
