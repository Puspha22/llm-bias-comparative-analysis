library(ggplot2)
library(jsonlite)
library(dplyr)
library(tidyr)

# Set base theme for publication ready aesthetic
theme_set(theme_minimal(base_family = "serif", base_size = 14) +
          theme(
            plot.title = element_text(hjust = 0.5, face = "bold"),
            axis.text.x = element_text(angle = 45, hjust = 1),
            panel.grid.minor = element_blank()
          ))

# Function to generate Protected Bias charts
generate_protected_bias <- function(json_path, output_path, model_name, fill_color) {
  cat(paste("Generating Protected Bias for", model_name, "\n"))
  data <- fromJSON(json_path)
  
  # data is a list of lists or objects
  # Wait, let's check the structure. If it's key-value counts:
  df <- data.frame(Attribute = names(data), Count = as.numeric(data))
  
  # Sort descending and take top N
  df <- df[order(-df$Count), ]
  df$Attribute <- factor(df$Attribute, levels = df$Attribute)
  
  p <- ggplot(df, aes(x = Attribute, y = Count)) +
    geom_bar(stat = "identity", fill = fill_color, alpha = 0.8) +
    labs(title = model_name, x = "Protected Attribute", y = "Frequency of Bias")
    
  ggsave(output_path, plot = p, width = 6, height = 5, device = "pdf")
}

# Function to generate Magic Numbers charts
generate_magic_numbers <- function(json_path, output_path, model_name, fill_color) {
  cat(paste("Generating Magic Numbers for", model_name, "\n"))
  data <- fromJSON(json_path)
  
  # data might be list of lists: {attribute, operator, threshold}
  df <- data
  
  counts <- df %>%
    group_by(attribute) %>%
    summarise(Count = n()) %>%
    arrange(desc(Count)) %>%
    head(10)
    
  counts$attribute <- as.character(counts$attribute)
  counts$attribute <- factor(counts$attribute, levels = counts$attribute)
  
  p <- ggplot(counts, aes(x = attribute, y = Count)) +
    geom_bar(stat = "identity", fill = fill_color, alpha = 0.8) +
    labs(title = model_name, x = "Hallucinated Attribute", y = "Frequency")
    
  ggsave(output_path, plot = p, width = 6, height = 5, device = "pdf")
}

# Function to generate Inconsistency charts
generate_inconsistency <- function(json_path, output_path, model_name, fill_color) {
  cat(paste("Generating Inconsistency for", model_name, "\n"))
  data <- fromJSON(json_path)
  
  df <- data.frame(Variance = names(data), Count = as.numeric(data))
  df$Variance <- factor(df$Variance, levels = c("1", "2", "3", "4", "5"))
  
  p <- ggplot(df, aes(x = Variance, y = Count)) +
    geom_bar(stat = "identity", fill = fill_color, alpha = 0.8) +
    labs(title = model_name, x = "Unique Logical Variations", y = "Number of Tasks") +
    theme(axis.text.x = element_text(angle = 0, hjust = 0.5))
    
  ggsave(output_path, plot = p, width = 6, height = 5, device = "pdf")
}

# Generate charts
generate_protected_bias("reports/exp_protected_bias_results_new.json", "siuethesis/Assets/protected_bias_chart_gemini.pdf", "Gemini 2.5 Flash", "#4285F4")
generate_protected_bias("reports/exp_protected_bias_results_grok.json", "siuethesis/Assets/protected_bias_chart_grok.pdf", "Grok-Code-Fast-1", "#000000")

generate_magic_numbers("reports/exp_magic_numbers_results_new.json", "siuethesis/Assets/magic_numbers_chart_gemini.pdf", "Gemini 2.5 Flash", "#4285F4")
generate_magic_numbers("reports/exp_magic_numbers_results_grok.json", "siuethesis/Assets/magic_numbers_chart_grok.pdf", "Grok-Code-Fast-1", "#000000")

generate_inconsistency("reports/consistency_gemini.json", "siuethesis/Assets/inconsistency_chart_gemini.pdf", "Gemini 2.5 Flash", "#4285F4")
generate_inconsistency("reports/consistency_grok.json", "siuethesis/Assets/inconsistency_chart_grok.pdf", "Grok-Code-Fast-1", "#000000")

# Function to generate Complexity Histogram
generate_complexity <- function(json_path, output_path, model_name, fill_color) {
  cat(paste("Generating Complexity for", model_name, "\n"))
  data <- fromJSON(json_path)
  df <- data.frame(Attributes = data)
  
  p <- ggplot(df, aes(x = Attributes)) +
    geom_histogram(binwidth = 1, fill = fill_color, alpha = 0.8, color = "white") +
    labs(title = model_name, x = "Number of Attributes Used", y = "Frequency") +
    scale_x_continuous(breaks = seq(0, 15, 2))
    
  ggsave(output_path, plot = p, width = 6, height = 5, device = "pdf")
}

# Function to generate Attribute Frequency
generate_frequency <- function(json_path, output_path, model_name, fill_color) {
  cat(paste("Generating Frequency for", model_name, "\n"))
  data <- fromJSON(json_path)
  df <- data.frame(Attribute = names(data), Count = as.numeric(data))
  
  df <- df[order(-df$Count), ]
  df$Attribute <- factor(df$Attribute, levels = df$Attribute)
  
  p <- ggplot(df, aes(x = Attribute, y = Count)) +
    geom_bar(stat = "identity", fill = fill_color, alpha = 0.8) +
    labs(title = model_name, x = "Attribute", y = "Total Occurrences") +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
    
  ggsave(output_path, plot = p, width = 6, height = 5, device = "pdf")
}

generate_complexity("reports/complexity_legacy.json", "siuethesis/Assets/complexity_legacy.pdf", "Legacy Prompts", "#34A853")
generate_complexity("reports/complexity_gemini.json", "siuethesis/Assets/complexity_gemini.pdf", "Gemini 2.5 Flash", "#4285F4")
generate_complexity("reports/complexity_grok.json", "siuethesis/Assets/complexity_grok.pdf", "Grok-Code-Fast-1", "#000000")

generate_frequency("reports/frequency_legacy.json", "siuethesis/Assets/frequency_legacy.pdf", "Legacy Prompts", "#34A853")
generate_frequency("reports/frequency_gemini.json", "siuethesis/Assets/frequency_gemini.pdf", "Gemini 2.5 Flash", "#4285F4")
generate_frequency("reports/frequency_grok.json", "siuethesis/Assets/frequency_grok.pdf", "Grok-Code-Fast-1", "#000000")

cat("Done!\n")
