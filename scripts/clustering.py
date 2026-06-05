import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

os.makedirs("figures", exist_ok=True)

df = pd.read_csv("ca_aqi_acs_master_county_avg.csv")

features = [
    "pct_bachelors_or_higher",
    "unemployment_rate",
    "median_household_income",
    "poverty_rate_all_people",
    "avg_bad_aqi_day_pct_2020_2024",
    "avg_median_aqi_2020_2024"
]

X = df[features]
X_scaled = StandardScaler().fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

print("\nCluster counts:")
print(df["cluster"].value_counts())

print("\nCluster means:")
print(df.groupby("cluster")[features].mean().round(2))

print("\nCounties in Cluster 2:")
print(df[df["cluster"] == 2][["county"]])

# Figure 1: Elbow plot
k_values = range(1, 11)
inertia = []

for k in k_values:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertia.append(km.inertia_)

plt.figure(1, figsize=(6, 4))
plt.plot(k_values, inertia, marker="o")
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Within-Cluster Sum of Squares")
plt.title("Elbow Method for K-Means Clustering")
plt.grid(True)
plt.tight_layout()
plt.savefig("figures/elbow_plot.png")
plt.show()

# Figure 2: PCA plot
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(2, figsize=(8, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df["cluster"])
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("K-Means Clustering of California Counties")
plt.tight_layout()
plt.savefig("figures/pca_clusters.png")
plt.show()