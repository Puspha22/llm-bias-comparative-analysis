library(ggplot2)
library(jsonlite)
library(dplyr)
library(tidyr)

theme_set(theme_minimal(base_family = "serif", base_size = 14) +
          theme(
            plot.title = element_text(hjust = 0.5, face = "bold"),
            panel.grid.minor = element_blank(),
            legend.position = "bottom",
            legend.title = element_blank(),
            axis.text.x = element_text(angle = 45, hjust = 1)
          ))

legacy <- fromJSON("reports/frequency_legacy.json")
gemini <- fromJSON("reports/frequency_gemini.json")
grok <- fromJSON("reports/frequency_grok.json")

df_legacy <- data.frame(Attribute = names(legacy), Count = as.numeric(legacy), Model = "Legacy Prompts")
df_gemini <- data.frame(Attribute = names(gemini), Count = as.numeric(gemini), Model = "Gemini 2.5 Flash")
df_grok <- data.frame(Attribute = names(grok), Count = as.numeric(grok), Model = "Grok-Code-Fast-1")

df <- bind_rows(df_legacy, df_gemini, df_grok)

# Get the top 15 most frequent attributes overall to avoid overcrowding the x-axis
top_attrs <- df %>%
  group_by(Attribute) %>%
  summarise(TotalCount = sum(Count)) %>%
  arrange(desc(TotalCount)) %>%
  head(12) %>%
  pull(Attribute)

df_filtered <- df %>% filter(Attribute %in% top_attrs)

df_filtered$Model <- factor(df_filtered$Model, levels = c("Legacy Prompts", "Gemini 2.5 Flash", "Grok-Code-Fast-1"))
df_filtered$Attribute <- factor(df_filtered$Attribute, levels = top_attrs)

p <- ggplot(df_filtered, aes(x = Attribute, y = Count, fill = Model)) +
  geom_bar(stat = "identity", position = "dodge", alpha = 0.85, width = 0.8) +
  scale_fill_manual(values = c("Legacy Prompts" = "#34A853", "Gemini 2.5 Flash" = "#4285F4", "Grok-Code-Fast-1" = "#2c3e50")) +
  labs(x = "Input Attribute", y = "Total Occurrences", title = "Top 12 Most Frequently Utilized Attributes Across Models")

dir.create("reports/figures", showWarnings = FALSE, recursive = TRUE)
ggsave("reports/figures/frequency_combined.pdf", plot = p, width = 10, height = 5, device = "pdf")
