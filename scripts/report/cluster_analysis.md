## Clustering Analysis

To explore whether California counties could be grouped according to similar socioeconomic and environmental characteristics, we applied K-means clustering. Unlike regression methods that focus on predicting a response variable, clustering is an unsupervised learning technique that identifies natural groupings within the data. This approach allows us to examine whether counties experiencing similar levels of income, education, poverty, employment, and air quality tend to form distinct categories.

For the clustering analysis, six variables were selected:

* Percentage of adults with a bachelor's degree or higher
* Unemployment rate
* Median household income
* Poverty rate
* Percentage of bad AQI days
* Median AQI

These variables were chosen because they represent both socioeconomic conditions and environmental quality. Educational attainment, household income, unemployment, and poverty are commonly used indicators of socioeconomic status, while the AQI variables capture both the frequency and severity of air pollution exposure. Together, these measures provide a comprehensive view of the characteristics that may differentiate California counties.

Before applying K-means, all variables were standardized using z-score normalization. Standardization was necessary because the variables were measured on different scales. For example, median household income is measured in dollars, while unemployment rate and poverty rate are percentages. Without standardization, variables with larger numerical scales would dominate the clustering process and potentially distort the results.

### Determining the Number of Clusters

One challenge in K-means clustering is selecting an appropriate number of clusters (K). To address this issue, we used the Elbow Method. The within-cluster sum of squares (WCSS) was calculated for values of K ranging from 1 to 10.

**Figure 1** shows the resulting elbow plot.

The WCSS decreases dramatically as K increases from 1 to 3, indicating that additional clusters significantly improve the fit of the model. After K = 3, however, the curve begins to flatten, meaning that adding more clusters provides only marginal improvements. This pattern suggests that the majority of meaningful variation in the data is already captured with three clusters.

For this reason, K = 3 was selected as the optimal number of clusters for the final analysis. Choosing a larger value of K would increase model complexity while providing relatively little additional explanatory benefit.

### Clustering Results

Using K = 3, the algorithm partitioned the 53 California counties into three distinct groups:

* Cluster 0: 26 counties
* Cluster 1: 21 counties
* Cluster 2: 6 counties

The average characteristics of each cluster reveal clear socioeconomic and environmental differences.

#### Cluster 0: Higher Socioeconomic Status and Better Air Quality

Cluster 0 contains counties with the highest levels of educational attainment and household income. On average, counties in this group have:

* 40.23% of adults holding a bachelor's degree or higher
* Median household income of approximately $110,606
* Poverty rate of 10.07%
* Unemployment rate of 5.38%
* Average bad AQI day percentage of 3.23%
* Average median AQI of 44.83

These counties generally represent more affluent communities with stronger educational outcomes and relatively favorable air quality conditions.

#### Cluster 1: Lower Socioeconomic Status and Moderate Air Quality

Cluster 1 contains counties with lower income and education levels and higher rates of poverty and unemployment. On average, counties in this cluster have:

* 21.65% bachelor's degree attainment
* Median household income of approximately $69,152
* Poverty rate of 15.51%
* Unemployment rate of 8.55%
* Average bad AQI day percentage of 5.02%
* Average median AQI of 47.10

Although these counties experience somewhat worse socioeconomic conditions than Cluster 0, their air quality indicators remain relatively moderate.

#### Cluster 2: Highest Air Pollution Burden

Cluster 2 is the most distinct group identified by the clustering algorithm. This cluster contains six counties:

* Fresno
* Kern
* Los Angeles
* Riverside
* San Bernardino
* Tulare

Compared to the other two clusters, these counties experience substantially worse air quality outcomes.

On average, counties in Cluster 2 have:

* 24.10% bachelor's degree attainment
* Median household income of approximately $80,729
* Poverty rate of 15.48%
* Unemployment rate of 7.92%
* Average bad AQI day percentage of 31.26%
* Average median AQI of 77.70

The most striking result is the percentage of bad AQI days. Counties in Cluster 2 experience approximately six to ten times more unhealthy air quality days than counties in Clusters 0 and 1. These counties are concentrated in regions known for air quality challenges, including the Los Angeles Basin and the San Joaquin Valley.

This finding suggests that environmental burdens are not distributed evenly across California. Instead, a relatively small subset of counties experiences substantially higher levels of pollution exposure.

### PCA Visualization

To visualize the clustering results, Principal Component Analysis (PCA) was used to reduce the six-dimensional feature space to two principal components.

**Figure 2** presents the PCA visualization.

Each point represents a California county, while colors indicate cluster membership assigned by the K-means algorithm. The PCA projection reveals that the three clusters occupy different regions of the feature space and are reasonably well separated from one another.

In particular, the six counties belonging to Cluster 2 form a distinct group that is separated from many of the counties in Clusters 0 and 1. This separation provides additional evidence that the selected variables successfully capture meaningful differences among California counties.

Overall, the clustering results demonstrate that California counties can be grouped into distinct socioeconomic and environmental profiles. The identification of a small cluster characterized by substantially worse air quality outcomes supports the project's broader goal of examining how environmental exposure varies across communities and whether these differences are associated with underlying socioeconomic characteristics.
