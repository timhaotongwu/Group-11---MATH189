# Cluster Analysis

We applied K-means clustering (K=3) using six variables:

- pct_bachelors_or_higher
- unemployment_rate
- median_household_income
- poverty_rate_all_people
- avg_bad_aqi_day_pct_2020_2024
- avg_median_aqi_2020_2024

The Elbow Method suggested K=3 as an appropriate number of clusters.

## Results

Cluster 0 (26 counties):
- Highest education level
- Highest household income
- Best air quality

Cluster 1 (21 counties):
- Lower income and education
- Moderate air quality

Cluster 2 (6 counties):
- Fresno
- Kern
- Los Angeles
- Riverside
- San Bernardino
- Tulare

This cluster exhibited substantially worse air quality, with an average median AQI of 77.7 compared to approximately 45 for the other clusters.

## Figures

Figure 1: Elbow Plot

Figure 2: PCA Cluster Visualization