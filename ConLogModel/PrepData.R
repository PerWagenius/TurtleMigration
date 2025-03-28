#This code simply reshaped the data from wide to long format in preperation for the model fitting in ConLogModels.R

library(dplyr) # For data manipulation
library(readr) # For reading CSVs
library(stringr) # For string operations
library(tidyverse)

# Step 1: List all CSV files in the directory
setwd("C:/Users/18479/OneDrive/Desktop/Code Turtle Project/FakePathsAdded")
csv_files <- list.files(pattern = "*.csv") # Adjust the path if needed


# Step 2: Function to process each file into long format
process_file <- function(file_name) {
  # Extract turtle ID (first 6 characters of the filename)
  turtle_id <- substr(file_name, 1, 6)
  
  # Read the CSV file
  data <- read_csv(file_name)
  
  # Columns for real paths
  real_path_cols <- c("datetime", "latitude", "longitude", 
                      "bat_realpath", "int_realpath", "inc_realpath")
  
  # Reshape real paths into long format
  real_path <- data %>%
    select(all_of(real_path_cols)) %>%
    mutate(is_realpath = 1,  # Add metadata for real path
           path_id = "realpath",  # Identifier for real path
           turtle_id = turtle_id) %>% # Add turtle ID
    rename(lat = latitude,
         lon = longitude,
         time = datetime,
         bat = bat_realpath,
         int = int_realpath,
         inc = inc_realpath)
  
  # Reshape fake paths into long format
  fake_path <- data %>%
    select(-all_of(real_path_cols)) %>%  # Exclude real path columns
    pivot_longer(
      cols = everything(),
      names_to = c(".value", "fakepath_id"),  # Extract variable names and path ID
      names_pattern = "(.*)_fakepath_(\\d+)"
    ) %>%
    mutate(is_realpath = 0,  # Add metadata for fake paths
           path_id = paste0("fakepath_", fakepath_id),  # Unique path ID
           turtle_id = turtle_id)  # Add turtle ID
  
  # Combine real and fake paths into long format
  long_data <- bind_rows(real_path, fake_path)
  
  return(long_data)
}

# Step 3: Apply the function to all files and combine the results
all_data <- csv_files %>%
  lapply(process_file) %>%  # Process each file
  bind_rows()  # Combine all processed files

# Step 4: Write combined long-format data to a new CSV
write_csv(all_data, "combined_turtle_data_long.csv")
