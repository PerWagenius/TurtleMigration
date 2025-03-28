This project contains two main models for running analyses of turtle migration paths, primarily based on Leclerc et al. (2021) and Gill & Taylor (2024) respectively. 

# Condition Logistic Regression Model Comparison

This code processes geospatial turtle paths to analyze environmental and magnetic properties along specified tracks. The code implements a Conditional Logistic Regression Model between real and simulated "fake" turtle paths to identify environmental variables correlated with real turtle migration paths. This approach is inspired by the methodology described in Leclerc et al. (2021). This code uses a Python translation of https://github.com/qbeslab/MagneticModelApp/ for reading magnetic field data, creating plots, and implementing a magnetic field-based migration model described by Gill & Taylor (2024).


# Gill Model Implementation

This code translates code from https://github.com/qbeslab/MagneticModelApp/ into Python for reading magnetic field data, creating plots, and implementing a magnetic field-based migration model described by Gill & Taylor (2024). It applies these files to analyse turtle migrations in the East Indian Ocean. It runs stability analyses on the parameters described by the A-matrix in Gill & Taylor (2024) on our turtles end goal in Oman. It also finds the best parameters for the A-matrix to match the experimental data using a simulating annealing algorithm.


## Features
# Gill Model:
- Get magnetic field information at any location (choose your own magnetic field dataset or use GeoMag from pygeomag)
- Generate a simulated path using only magnetic field information based on Gill & Taylor paper
- Use simulated annealing to tune parameters to a given real turtle path
- Plots of paths with colored regions corresponding to stability analysis
# Conditional Logistic Model Comparison:
- Example code for adding environmental condition data to a geospacial path
- Generating random shuffling of a path as in Leclerc et al.
- Determine which set of environmental conditions can best predict a turtle's migration path

## References
Leclerc, Martin, Mathieu Leblond, Maël Le Corre, Christian Dussault, and Steeve D. Côté. “Determinants of Migration Trajectory and Movement Rate in a Longdistance Terrestrial Mammal.” *Journal of Mammalogy* 102, no. 5 (2021): 1342–52. https://www.jstor.org/stable/27302202.


Gill, J. P., & Taylor, B. K. (2024). Navigation by magnetic signatures in a realistic model of Earth's magnetic field. *Bioinspiration & Biomimetics*, 19(3), 036006. https://doi.org/10.1088/1748-3190/ad3120

## License
MIT License
