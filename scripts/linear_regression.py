import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

os.makedirs("figures", exist_ok=True)

df = pd.read_csv("ca_aqi_acs_master_county_avg.csv")

predictors = [
    "median_household_income",
    "poverty_rate_all_people",
    "unemployment_rate",
    "pct_bachelors_or_higher",
    "pct_no_health_insurance",
]

outcomes = {
    "avg_median_aqi_2020_2024":                   "Median AQI",
    "avg_bad_aqi_day_pct_2020_2024":              "% Bad AQI Days",
    "avg_pct_days_pm25_main_pollutant_2020_2024": "% Days PM2.5 Main",
}

reg_df = df[predictors + list(outcomes.keys())].dropna().copy()

scaler   = StandardScaler()
X_scaled = scaler.fit_transform(reg_df[predictors])
X_df     = pd.DataFrame(X_scaled, columns=predictors, index=reg_df.index)
X        = sm.add_constant(X_df)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

models = {}
for col, label in outcomes.items():
    y     = reg_df[col]
    model = sm.OLS(y, X).fit()
    models[col] = model
    print(f"\n{'='*60}")
    print(f"Outcome: {label}")
    print(f"  R²      = {model.rsquared:.4f}")
    print(f"  Adj. R² = {model.rsquared_adj:.4f}")
    print(f"  F-stat  = {model.fvalue:.4f}  (p = {model.f_pvalue:.4f})")
    print(model.summary())

pred_labels = {
    "median_household_income": "Median HH Income",
    "poverty_rate_all_people": "Poverty Rate",
    "unemployment_rate":       "Unemployment Rate",
    "pct_bachelors_or_higher": "% Bachelor's+",
    "pct_no_health_insurance": "% No Health Insurance",
}

# Figure 1: Coefficient plot
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for ax, (col, label) in zip(axes, outcomes.items()):
    model = models[col]
    coef  = model.params.drop("const")
    conf  = model.conf_int().drop("const")
    pvals = model.pvalues.drop("const")

    y_pos  = np.arange(len(coef))
    colors = ["steelblue" if p < 0.05 else "lightgray" for p in pvals]

    ax.barh(y_pos, coef.values, color=colors,
            xerr=[coef.values - conf[0].values, conf[1].values - coef.values],
            capsize=4, error_kw={"linewidth": 1})
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([pred_labels[v] for v in predictors], fontsize=9)
    ax.set_title(f"{label}\nAdj. R²={model.rsquared_adj:.3f}", fontsize=10)
    ax.set_xlabel("Standardized Coefficient", fontsize=9)

    for i, (c, p) in enumerate(zip(coef.values, pvals)):
        star = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
        if star:
            ax.text(c + (0.02 if c >= 0 else -0.02), i, star,
                    va="center", ha="left" if c >= 0 else "right", fontsize=9)

plt.suptitle("Regression Coefficients: Socioeconomic Predictors of Air Quality", fontsize=12)
plt.tight_layout()
plt.savefig("figures/regression_coefficients.png")
plt.show()

# Figure 2: Observed vs Predicted (primary model)
primary_col   = "avg_median_aqi_2020_2024"
primary_model = models[primary_col]
fitted        = primary_model.fittedvalues
y_true        = reg_df[primary_col]

fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(y_true, fitted, alpha=0.75, edgecolors="k", linewidths=0.4)
lim = [min(y_true.min(), fitted.min()) - 1, max(y_true.max(), fitted.max()) + 1]
ax.plot(lim, lim, "r--", linewidth=1)
ax.set_xlabel("Observed Median AQI")
ax.set_ylabel("Predicted Median AQI")
ax.set_title(f"Observed vs Predicted — Median AQI\n(R² = {primary_model.rsquared:.3f})")
plt.tight_layout()
plt.savefig("figures/regression_observed_vs_predicted.png")
plt.show()
