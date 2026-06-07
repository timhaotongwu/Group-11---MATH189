import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("/Users/kashikasharma/Downloads/ca_aqi_acs_master_county_avg.csv")

metric = "avg_bad_aqi_day_pct_2020_2024"

top10 = (
    df.sort_values(metric, ascending=False)
    [["county", metric]]
    .head(10)
    .sort_values(metric, ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(top10["county"], top10[metric])

ax.set_title("Top 10 California Counties by Bad AQI Day Percentage (2020–2024)")
ax.set_xlabel("Average bad AQI days (%)")
ax.set_ylabel("County")

plt.tight_layout()

output_path = "figures/top10_bad_aqi_counties.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved bar chart to: {output_path}")
print("\nTop 10 counties:")
print(top10.sort_values(metric, ascending=False).to_string(index=False))