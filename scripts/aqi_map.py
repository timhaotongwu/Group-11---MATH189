import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

df = pd.read_csv("/Users/kashikasharma/Downloads/ca_aqi_acs_master_county_avg.csv")

counties = gpd.read_file(
    "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
)

ca = counties[counties["STATE_NAME"] == "California"].copy()

df["county_clean"] = df["county"].str.lower().str.strip()
ca["county_clean"] = ca["NAME"].str.lower().str.strip()

merged = ca.merge(df, on="county_clean", how="left")

fig, ax = plt.subplots(figsize=(10, 12))

merged.plot(
    column="avg_bad_aqi_day_pct_2020_2024",
    cmap="Reds",
    linewidth=0.5,
    edgecolor="black",
    legend=True,
    ax=ax,
    missing_kwds={"color": "lightgrey", "label": "Missing data"}
)

ax.set_title(
    "Average Percentage of Unhealthy AQI Days by California County (2020–2024)",
    fontsize=14
)

ax.axis("off")
plt.tight_layout()

output_path = "/Users/kashikasharma/Downloads/california_bad_aqi_map.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved map to: {output_path}")

top10 = (
    df.sort_values("avg_bad_aqi_day_pct_2020_2024", ascending=False)
    [["county", "avg_bad_aqi_day_pct_2020_2024"]]
    .head(10)
)

print("\nTop 10 Counties by Bad AQI Percentage:")
print(top10.to_string(index=False))