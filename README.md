This project contains two main models for running analyses of turtle migration paths, primarily based on Leclerc et al. (2021) and Gill & Taylor (2024) respectively. 

# Condition Logistic Regression Model Comparison

This code processes geospatial turtle paths to analyze environmental and magnetic properties along specified tracks. The code implements a Conditional Logistic Regression Model between real and simulated "fake" turtle paths to identify environmental variables correlated with real turtle migration paths. This approach is inspired by the methodology described in Leclerc et al. (2021). This code uses a Python translation of https://github.com/qbeslab/MagneticModelApp/ for reading magnetic field data, creating plots, and implementing a magnetic field-based migration model described by Gill & Taylor (2024).


# Gill Model Implementation

This code translates code from https://github.com/qbeslab/MagneticModelApp/ into Python for reading magnetic field data, creating plots, and implementing a magnetic field-based migration model described by Gill & Taylor (2024). It applies these files to analyse turtle migrations in the East Indian Ocean. It runs stability analyses on the parameters described by the A-matrix in Gill & Taylor (2024) on our turtles end goal in Oman. It also finds the best parameters for the A-matrix to match the experimental data using a simulating annealing algorithm.


## Features
- Interpolates bathymetry data using the GEBCO dataset.
- Adds magnetic intensity and inclination using a pre-trained magnetic model.
- Generates scrambled paths for analysis.

## Setup
1. Install dependencies:
   ```bash
   pip install xarray pandas numpy
   ```
2. Set environment variables:
   - `GEBCO_PATH`: Path to the GEBCO dataset file.
   - `TRACK_FILE`: Path to the track CSV file.

## Usage
Run the scripts in the project directory to process data and generate outputs.

## References
Leclerc, Martin, Mathieu Leblond, Maël Le Corre, Christian Dussault, and Steeve D. Côté. “Determinants of Migration Trajectory and Movement Rate in a Longdistance Terrestrial Mammal.” *Journal of Mammalogy* 102, no. 5 (2021): 1342–52. https://www.jstor.org/stable/27302202.


Gill, J. P., & Taylor, B. K. (2024). Navigation by magnetic signatures in a realistic model of Earth's magnetic field. *Bioinspiration & Biomimetics*, 19(3), 036006. https://doi.org/10.1088/1748-3190/ad3120

## License
MIT License
