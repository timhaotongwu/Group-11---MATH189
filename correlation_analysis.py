from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

scriptDir = Path(__file__).resolve().parent
inputDir = scriptDir
outputDir = scriptDir

countyYearFile = inputDir / "ca_aqi_acs_master_county_year.csv"
countyAvgFile = inputDir / "ca_aqi_acs_master_county_avg.csv"
dataDictFile = inputDir / "ca_aqi_acs_data_dictionary.csv"
missingFile = inputDir / "ca_aqi_acs_missingness_report.csv"

allCorrOut = outputDir / "correlation_results_all.csv"
keyCorrOut = outputDir / "correlation_results_key_pairs.csv"
matrixOut = outputDir / "correlation_matrix_soc_air.csv"
yearlyOut = outputDir / "year_by_year_correlation_summary.csv"
summaryOut = outputDir / "correlation_analysis_summary.md"
heatmapOut = outputDir / "correlation_heatmap_soc_air.png"

socioCols = [
    "median_household_income",
    "mean_household_income",
    "per_capita_income",
    "poverty_rate_all_people",
    "unemployment_rate",
    "pct_high_school_or_higher",
    "pct_bachelors_or_higher",
    "pct_no_health_insurance",
]

airCols = [
    "avg_bad_aqi_day_pct_2020_2024",
    "avg_bad_aqi_days_2020_2024",
    "avg_median_aqi_2020_2024",
    "avg_aqi_90th_percentile_2020_2024",
    "avg_max_aqi_2020_2024",
    "avg_pct_days_pm25_main_pollutant_2020_2024",
    "avg_pct_days_ozone_main_pollutant_2020_2024",
    "avg_pct_days_no2_main_pollutant_2020_2024",
]

yearlyAirMap = {
    "avg_bad_aqi_day_pct_2020_2024": "bad_aqi_day_pct",
    "avg_median_aqi_2020_2024": "median_aqi",
    "avg_aqi_90th_percentile_2020_2024": "aqi_90th_percentile",
    "avg_max_aqi_2020_2024": "max_aqi",
    "avg_pct_days_pm25_main_pollutant_2020_2024": "pct_days_pm25_main_pollutant",
    "avg_pct_days_ozone_main_pollutant_2020_2024": "pct_days_ozone_main_pollutant",
}

prettyNames = {
    "median_household_income": "median household income",
    "mean_household_income": "mean household income",
    "per_capita_income": "per capita income",
    "poverty_rate_all_people": "poverty rate",
    "unemployment_rate": "unemployment rate",
    "pct_high_school_or_higher": "high school or higher",
    "pct_bachelors_or_higher": "bachelor's or higher",
    "pct_no_health_insurance": "no health insurance",
    "avg_bad_aqi_day_pct_2020_2024": "bad AQI day %",
    "avg_bad_aqi_days_2020_2024": "bad AQI days",
    "avg_median_aqi_2020_2024": "median AQI",
    "avg_aqi_90th_percentile_2020_2024": "90th percentile AQI",
    "avg_max_aqi_2020_2024": "max AQI",
    "avg_pct_days_pm25_main_pollutant_2020_2024": "PM2.5 main-pollutant day %",
    "avg_pct_days_ozone_main_pollutant_2020_2024": "ozone main-pollutant day %",
    "avg_pct_days_no2_main_pollutant_2020_2024": "NO2 main-pollutant day %",
}


def checkFiles():
    neededFiles = [countyYearFile, countyAvgFile, dataDictFile, missingFile]
    missingFiles = [path for path in neededFiles if not path.exists()]
    if missingFiles:
        raise FileNotFoundError(f"Missing cleaned files: {missingFiles}")


def getCorr(data, xCol, yCol):
    pairData = data[[xCol, yCol]].dropna()
    n = len(pairData)
    if n < 3:
        return None

    pearsonR, pearsonP = stats.pearsonr(pairData[xCol], pairData[yCol])
    spearmanR, spearmanP = stats.spearmanr(pairData[xCol], pairData[yCol])

    return {
        "socio_variable": xCol,
        "air_variable": yCol,
        "n": n,
        "pearson_r": pearsonR,
        "pearson_p": pearsonP,
        "spearman_r": spearmanR,
        "spearman_p": spearmanP,
    }


def addBenjaminiHochberg(results, pCol, outCol):
    ranked = results[pCol].rank(method="first")
    m = results[pCol].notna().sum()
    results[outCol] = (results[pCol] * m / ranked).clip(upper=1)
    results[outCol] = results[outCol].sort_values(ascending=False).cummin()
    return results


def makeCorrelationTables(countyAvg):
    rows = []
    for socioCol in socioCols:
        for airCol in airCols:
            corrRow = getCorr(countyAvg, socioCol, airCol)
            if corrRow is not None:
                rows.append(corrRow)

    results = pd.DataFrame(rows)
    results["abs_pearson_r"] = results["pearson_r"].abs()
    results["abs_spearman_r"] = results["spearman_r"].abs()
    results = addBenjaminiHochberg(results, "pearson_p", "pearson_fdr_p")
    results = addBenjaminiHochberg(results, "spearman_p", "spearman_fdr_p")
    results = results.sort_values("abs_pearson_r", ascending=False)

    keyPairs = results[
        results["air_variable"].isin(
            [
                "avg_bad_aqi_day_pct_2020_2024",
                "avg_median_aqi_2020_2024",
                "avg_aqi_90th_percentile_2020_2024",
                "avg_pct_days_pm25_main_pollutant_2020_2024",
                "avg_pct_days_ozone_main_pollutant_2020_2024",
            ]
        )
    ].copy()

    matrix = pd.DataFrame(index=socioCols, columns=airCols, dtype=float)
    for socioCol in socioCols:
        for airCol in airCols:
            corrRow = getCorr(countyAvg, socioCol, airCol)
            if corrRow is not None:
                matrix.loc[socioCol, airCol] = corrRow["pearson_r"]

    results.to_csv(allCorrOut, index=False)
    keyPairs.to_csv(keyCorrOut, index=False)
    matrix.to_csv(matrixOut)

    return results, keyPairs, matrix


def makeYearlySummary(countyYear):
    rows = []
    for year, yearData in countyYear.groupby("year"):
        for socioCol in socioCols:
            for avgCol, yearCol in yearlyAirMap.items():
                corrRow = getCorr(yearData, socioCol, yearCol)
                if corrRow is not None:
                    corrRow["year"] = int(year)
                    corrRow["air_variable"] = yearCol
                    rows.append(corrRow)

    yearly = pd.DataFrame(rows)
    yearly = yearly.sort_values(["year", "pearson_p"])
    yearly.to_csv(yearlyOut, index=False)
    return yearly


def saveHeatmap(matrix):
    plotMatrix = matrix.copy()
    plotMatrix.index = [prettyNames.get(col, col) for col in plotMatrix.index]
    plotMatrix.columns = [prettyNames.get(col, col) for col in plotMatrix.columns]

    figHeight = max(5, len(plotMatrix.index) * 0.55)
    figWidth = max(8, len(plotMatrix.columns) * 1.15)
    fig, ax = plt.subplots(figsize=(figWidth, figHeight))
    image = ax.imshow(plotMatrix.values.astype(float), vmin=-1, vmax=1)

    ax.set_xticks(np.arange(len(plotMatrix.columns)))
    ax.set_yticks(np.arange(len(plotMatrix.index)))
    ax.set_xticklabels(plotMatrix.columns, rotation=45, ha="right")
    ax.set_yticklabels(plotMatrix.index)

    for i in range(len(plotMatrix.index)):
        for j in range(len(plotMatrix.columns)):
            value = plotMatrix.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8)

    ax.set_title("Pearson correlations: socioeconomic factors vs air quality")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.04)
    fig.tight_layout()
    fig.savefig(heatmapOut, dpi=300)
    plt.close(fig)


def saveScatter(countyAvg, xCol, yCol, fileName):
    plotData = countyAvg[["county", xCol, yCol]].dropna()
    slope, intercept, rVal, pVal, stdErr = stats.linregress(plotData[xCol], plotData[yCol])

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(plotData[xCol], plotData[yCol])

    xLine = np.linspace(plotData[xCol].min(), plotData[xCol].max(), 100)
    yLine = intercept + slope * xLine
    ax.plot(xLine, yLine)

    ax.set_xlabel(prettyNames.get(xCol, xCol))
    ax.set_ylabel(prettyNames.get(yCol, yCol))
    ax.set_title(f"{prettyNames.get(xCol, xCol)} vs {prettyNames.get(yCol, yCol)}")
    ax.text(
        0.03,
        0.97,
        f"r = {rVal:.2f}\np = {pVal:.4f}",
        transform=ax.transAxes,
        va="top",
    )
    fig.tight_layout()
    fig.savefig(outputDir / fileName, dpi=300)
    plt.close(fig)


def makeSummary(countyAvg, results, keyPairs, yearly):
    topRows = keyPairs.sort_values("pearson_p").head(8)

    lines = [
        "# Correlation Analysis Summary",
        "",
        f"Main dataset: county averages from 2020-2024, n = {len(countyAvg)} counties.",
        "",
        "I used county averages because the ACS income and demographic values repeat across years.",
        "",
        "## Main takeaways",
        "",
        "- Most correlations are weak to moderate, so this shows patterns, not causation.",
        "- Higher income and education usually relate to better AQI outcomes.",
        "- Counties with more uninsured residents tend to have worse AQI outcomes.",
        "- Pollutant variables are main-pollutant day percentages, not actual PM2.5 or ozone concentrations.",
        "",
        "## Strongest project correlations",
        "",
    ]

    for _, row in topRows.iterrows():
        socioName = prettyNames.get(row["socio_variable"], row["socio_variable"])
        airName = prettyNames.get(row["air_variable"], row["air_variable"])
        lines.append(
            f"- {socioName} vs {airName}: Pearson r = "
            f"{row['pearson_r']:.3f}, p = {row['pearson_p']:.4f}."
        )

    lines.extend([
        "",
        "## Report wording",
        "",
        "Overall, the correlations give some support for our project question. "
        "Lower income, lower education, and higher uninsured rates often line up "
        "with worse AQI outcomes, but the relationships are not strong enough to "
        "treat as a final answer by themselves."
    ])

    summaryOut.write_text("\n".join(lines))


def main():
    checkFiles()

    countyYear = pd.read_csv(countyYearFile)
    countyAvg = pd.read_csv(countyAvgFile)
    dataDictionary = pd.read_csv(dataDictFile)
    missingReport = pd.read_csv(missingFile)

    highMissing = missingReport[missingReport["missing_pct"] > 20]
    if len(highMissing) > 0:
        print("Warning: some columns have high missingness:")
        print(highMissing[["column", "missing_pct"]])

    results, keyPairs, matrix = makeCorrelationTables(countyAvg)
    yearly = makeYearlySummary(countyYear)
    saveHeatmap(matrix)

    saveScatter(
        countyAvg,
        "median_household_income",
        "avg_bad_aqi_day_pct_2020_2024",
        "scatter_income_bad_aqi_pct.png",
    )
    saveScatter(
        countyAvg,
        "poverty_rate_all_people",
        "avg_bad_aqi_day_pct_2020_2024",
        "scatter_poverty_bad_aqi_pct.png",
    )
    saveScatter(
        countyAvg,
        "pct_no_health_insurance",
        "avg_bad_aqi_day_pct_2020_2024",
        "scatter_uninsured_bad_aqi_pct.png",
    )

    makeSummary(countyAvg, results, keyPairs, yearly)

    print("saved files:")
    for path in [
        allCorrOut,
        keyCorrOut,
        matrixOut,
        yearlyOut,
        summaryOut,
        heatmapOut,
        outputDir / "scatter_income_bad_aqi_pct.png",
        outputDir / "scatter_poverty_bad_aqi_pct.png",
        outputDir / "scatter_uninsured_bad_aqi_pct.png",
    ]:
        print(f"- {path.name}")

    print()
    print("Strongest project correlations:")
    colsToShow = [
        "socio_variable",
        "air_variable",
        "n",
        "pearson_r",
        "pearson_p",
        "spearman_r",
        "spearman_p",
    ]
    print(keyPairs.sort_values("pearson_p")[colsToShow].head(8).round(4))


if __name__ == "__main__":
    main()
