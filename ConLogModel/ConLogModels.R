#This code fits conditional logistic regression models to the turtle data
#and compares the models using BIC. Models can be made using any subset of the environmental variable stored as combined_turtle_data_long.csv
library(dplyr) # For data manipulation
library(readr) # For reading CSVs
library(survival) #For modeling
library(stringr) # For strings
library(tidyverse)

#Read in the data
all_data <- read_csv("FakePathsAdded/combined_turtle_data_long.csv") 
summary(all_data)

# Fit the model
incIntModel <- clogit(is_realpath ~ inc + int + strata(turtle_id), 
                      data = all_data,
                      method = "efron")

batModel <- clogit(is_realpath ~ bat + strata(turtle_id), 
                   data = all_data,
                   method = "efron")

fullModel <- clogit(is_realpath ~ bat + inc + int + strata(turtle_id),
                    data = all_data,
                    method = "efron")
nullModel <- clogit(is_realpath ~ 1 + strata(turtle_id),
                    data = all_data,
                    method = "efron")

summary(batModel)
summary(incIntModel)
summary(fullModel)
summary(nullModel)

# Print BIC values
bic_bathy <- BIC(batModel)
bic_incInt <- BIC(incIntModel)
bic_both <- BIC(fullModel)
bic_null <- BIC(nullModel)
cat("BIC for bathymetry model: ", bic_bathy, "\n")
cat("BIC for int/inc model: ", bic_incInt, "\n")
cat("BIC for both model: ", bic_both, "\n")
cat("BIC for null model: ", bic_null, "\n")