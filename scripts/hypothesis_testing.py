import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

os.makedirs("figures", exist_ok=True)

df = pd.read_csv("ca_aqi_acs_master_county_avg.csv")

low  = df[df["lower_income_group"] == True]
high = df[df["lower_income_group"] == False]

outcomes = {
    "avg_median_aqi_2020_2024":                   "Median AQI",
    "avg_bad_aqi_day_pct_2020_2024":              "% Bad AQI Days",
    "avg_pct_days_pm25_main_pollutant_2020_2024": "% Days PM2.5 Main",
    "avg_pct_days_ozone_main_pollutant_2020_2024":"% Days Ozone Main",
}

print(f"Lower-income counties : {len(low)}")
print(f"Higher-income counties: {len(high)}\n")

rows = []
for col, label in outcomes.items():
    x_low  = low[col].dropna()
    x_high = high[col].dropna()

    t_stat, t_p_two = stats.ttest_ind(x_low, x_high, equal_var=False)
    t_p_one = t_p_two / 2 if t_stat > 0 else 1 - t_p_two / 2

    _, mwu_p = stats.mannwhitneyu(x_low, x_high, alternative="greater")

    pooled_std = np.sqrt((x_low.std(ddof=1)**2 + x_high.std(ddof=1)**2) / 2)
    d = (x_low.mean() - x_high.mean()) / pooled_std if pooled_std > 0 else np.nan

    rows.append({
        "Outcome":          label,
        "Mean (Low)":       round(x_low.mean(), 3),
        "Mean (High)":      round(x_high.mean(), 3),
        "Welch t":          round(t_stat, 4),
        "p (1-tail)":       round(t_p_one, 4),
        "MWU p (1-tail)":   round(mwu_p, 4),
        "Cohen's d":        round(d, 3),
        "Sig (a=0.05)":     "Yes" if t_p_one < 0.05 else "No",
    })

results = pd.DataFrame(rows)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
print("Two-sample test results (lower-income vs higher-income):")
print(results.to_string(index=False))

# Figure 1: Boxplots
fig, axes = plt.subplots(1, len(outcomes), figsize=(14, 5))

for ax, (col, label) in zip(axes, outcomes.items()):
    data = [low[col].dropna().values, high[col].dropna().values]
    ax.boxplot(data, tick_labels=["Lower-\nIncome", "Higher-\nIncome"], widths=0.5)
    ax.set_title(label, fontsize=10)

plt.suptitle("Air Quality Outcomes: Lower- vs Higher-Income Counties", fontsize=12)
plt.tight_layout()
plt.savefig("figures/hypothesis_boxplots.png")
plt.show()

# Figure 2: Cohen's d
fig, ax = plt.subplots(figsize=(8, 4))
labels   = [r["Outcome"] for r in rows]
d_values = [r["Cohen's d"] for r in rows]
colors   = ["steelblue" if d > 0 else "salmon" for d in d_values]
ax.barh(labels, d_values, color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.axvline(0.2, color="gray", linestyle="--", linewidth=0.7)
ax.axvline(0.5, color="gray", linestyle="-.", linewidth=0.7)
ax.axvline(0.8, color="gray", linestyle=":",  linewidth=0.7)
ax.set_xlabel("Cohen's d  (positive = lower-income worse)")
ax.set_title("Effect Sizes: Lower-Income vs Higher-Income Counties")
plt.tight_layout()
plt.savefig("figures/hypothesis_effect_sizes.png")
plt.show()
