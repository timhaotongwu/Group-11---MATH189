from pathlib import Path
import re
import numpy as np
import pandas as pd

scriptDir = Path(__file__).resolve().parent
inputDir = scriptDir
outputDir = scriptDir
years = range(2020, 2025)

aqiFiles = [inputDir / f"annual_aqi_by_county_{year}.csv" for year in years]
dp02File = inputDir / "ACSDP5Y2024.DP02-Data.csv"
dp03File = inputDir / "ACSDP5Y2024.DP03-Data.csv"

countyYearOut = outputDir / "ca_aqi_acs_master_county_year.csv"
countyAvgOut = outputDir / "ca_aqi_acs_master_county_avg.csv"
dataDictionaryOut = outputDir / "ca_aqi_acs_data_dictionary.csv"
missingnessOut = outputDir / "ca_aqi_acs_missingness_report.csv"

aqiRename = {
    "State": "state",
    "County": "county",
    "Year": "year",
    "Days with AQI": "days_with_aqi",
    "Good Days": "good_days",
    "Moderate Days": "moderate_days",
    "Unhealthy for Sensitive Groups Days": "usg_days",
    "Unhealthy Days": "unhealthy_days",
    "Very Unhealthy Days": "very_unhealthy_days",
    "Hazardous Days": "hazardous_days",
    "Max AQI": "max_aqi",
    "90th Percentile AQI": "aqi_90th_percentile",
    "Median AQI": "median_aqi",
    "Days CO": "days_co_main_pollutant",
    "Days NO2": "days_no2_main_pollutant",
    "Days Ozone": "days_ozone_main_pollutant",
    "Days PM2.5": "days_pm25_main_pollutant",
    "Days PM10": "days_pm10_main_pollutant",
}

# DP02 has some social/education variables
dp02Cols = {
    "GEO_ID": "geo_id",
    "NAME": "acs_name",
    "DP02_0059E": "population_25_plus",
    "DP02_0067PE": "pct_high_school_or_higher",
    "DP02_0068PE": "pct_bachelors_or_higher",
}

# hte economic variables that matter most for our question
dp03Cols = {
    "GEO_ID": "geo_id",
    "NAME": "acs_name",
    "DP03_0001E": "population_16_plus",
    "DP03_0009PE": "unemployment_rate",
    "DP03_0062E": "median_household_income",
    "DP03_0063E": "mean_household_income",
    "DP03_0088E": "per_capita_income",
    "DP03_0128PE": "poverty_rate_all_people",
    "DP03_0099PE": "pct_no_health_insurance",
}

columnNotes = {
    "geo_id": "Census county ID.",
    "county": "California county name.",
    "state": "State from the EPA AQI file.",
    "year": "AQI year.",
    "days_with_aqi": "Days with AQI observations.",
    "good_days": "Days with Good AQI.",
    "moderate_days": "Days with Moderate AQI.",
    "usg_days": "Days unhealthy for sensitive groups.",
    "unhealthy_days": "Days with Unhealthy AQI.",
    "very_unhealthy_days": "Days with Very Unhealthy AQI.",
    "hazardous_days": "Days with Hazardous AQI.",
    "bad_aqi_days": "Total days with AQI worse than Moderate.",
    "bad_aqi_day_pct": "Percent of AQI days that were USG or worse.",
    "max_aqi": "Highest AQI value in the county-year.",
    "aqi_90th_percentile": "90th percentile AQI.",
    "median_aqi": "Median AQI.",
    "days_co_main_pollutant": "Days where CO drove AQI.",
    "days_no2_main_pollutant": "Days where NO2 drove AQI.",
    "days_ozone_main_pollutant": "Days where ozone drove AQI.",
    "days_pm25_main_pollutant": "Days where PM2.5 drove AQI.",
    "days_pm10_main_pollutant": "Days where PM10 drove AQI.",
    "pct_days_ozone_main_pollutant": "Percent of AQI days driven by ozone.",
    "pct_days_pm25_main_pollutant": "Percent of AQI days driven by PM2.5.",
    "population_25_plus": "ACS population age 25 and older.",
    "pct_high_school_or_higher": "Percent with high school degree or higher.",
    "pct_bachelors_or_higher": "Percent with bachelor's degree or higher.",
    "population_16_plus": "ACS population age 16 and older.",
    "unemployment_rate": "ACS unemployment rate.",
    "median_household_income": "Median household income from ACS DP03.",
    "mean_household_income": "Mean household income from ACS DP03.",
    "per_capita_income": "Per capita income from ACS DP03.",
    "poverty_rate_all_people": "Percent of people below the poverty level.",
    "pct_no_health_insurance": "Percent without health insurance.",
    "income_quartile": "County income quartile.",
    "lower_income_group": "True if county is in the lower half by income.",
}


def cleanCountyName(name):
    if pd.isna(name):
        return np.nan

    cleaned = str(name).strip()
    cleaned = re.sub(r",\s*California$", "", cleaned)
    cleaned = re.sub(r"\s+County$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def makeNumeric(series):
    cleaned = series.astype(str).str.replace(",", "", regex=False)
    cleaned = cleaned.replace({"nan": np.nan, "N": np.nan, "-": np.nan})
    cleaned = cleaned.replace({"(X)": np.nan})
    cleaned = cleaned.str.replace("+", "", regex=False)
    cleaned = cleaned.str.replace("median-", "", regex=False)
    cleaned = cleaned.str.replace("median+", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def loadAqiData():
    frames = []
    missingFiles = [path for path in aqiFiles if not path.exists()]
    if missingFiles:
        raise FileNotFoundError(f"Missing AQI files: {missingFiles}")

    for path in aqiFiles:
        frames.append(pd.read_csv(path))

    aqi = pd.concat(frames, ignore_index=True)
    aqi = aqi.rename(columns=aqiRename)
    aqi = aqi[aqi["state"].eq("California")].copy()
    aqi["county"] = aqi["county"].apply(cleanCountyName)

    numericCols = [col for col in aqi.columns if col not in {"state", "county"}]
    for col in numericCols:
        aqi[col] = makeNumeric(aqi[col])

    aqi["bad_aqi_days"] = (
        aqi["usg_days"]
        + aqi["unhealthy_days"]
        + aqi["very_unhealthy_days"]
        + aqi["hazardous_days"]
    )

    aqi["bad_aqi_day_pct"] = np.where(
        aqi["days_with_aqi"] > 0,
        aqi["bad_aqi_days"] / aqi["days_with_aqi"] * 100,
        np.nan,
    )

    pollutantDayCols = [
        "days_co_main_pollutant",
        "days_no2_main_pollutant",
        "days_ozone_main_pollutant",
        "days_pm25_main_pollutant",
        "days_pm10_main_pollutant",
    ]

    for col in pollutantDayCols:
        pctCol = "pct_" + col
        aqi[pctCol] = np.where(
            aqi["days_with_aqi"] > 0,
            aqi[col] / aqi["days_with_aqi"] * 100,
            np.nan,
        )

    return aqi.sort_values(["county", "year"]).reset_index(drop=True)


def loadAcsTable(path, keepCols):
    if not path.exists():
        raise FileNotFoundError(f"Missing ACS file: {path}")

    acs = pd.read_csv(path, dtype=str)
    acs = acs[acs["GEO_ID"].str.startswith("0500000US06", na=False)].copy()
    acs = acs[list(keepCols)].rename(columns=keepCols)
    acs["county"] = acs["acs_name"].apply(cleanCountyName)

    for col in acs.columns:
        if col not in {"geo_id", "acs_name", "county"}:
            acs[col] = makeNumeric(acs[col])

    return acs


def loadAcsData():
    dp02 = loadAcsTable(dp02File, dp02Cols)
    dp03 = loadAcsTable(dp03File, dp03Cols)

    acs = dp02.merge(
        dp03.drop(columns=["acs_name"]),
        on=["geo_id", "county"],
        how="outer",
        validate="one_to_one",
    )

    acs["income_quartile"] = pd.qcut(
        acs["median_household_income"],
        q=4,
        labels=["Q1 lowest income", "Q2", "Q3", "Q4 highest income"],
    )

    incomeCutoff = acs["median_household_income"].median()
    acs["lower_income_group"] = acs["median_household_income"] <= incomeCutoff

    return acs.sort_values("county").reset_index(drop=True)


def averageByCounty(master):
    aqiCols = [
        "days_with_aqi",
        "good_days",
        "moderate_days",
        "usg_days",
        "unhealthy_days",
        "very_unhealthy_days",
        "hazardous_days",
        "bad_aqi_days",
        "bad_aqi_day_pct",
        "max_aqi",
        "aqi_90th_percentile",
        "median_aqi",
        "days_co_main_pollutant",
        "days_no2_main_pollutant",
        "days_ozone_main_pollutant",
        "days_pm25_main_pollutant",
        "days_pm10_main_pollutant",
        "pct_days_co_main_pollutant",
        "pct_days_no2_main_pollutant",
        "pct_days_ozone_main_pollutant",
        "pct_days_pm25_main_pollutant",
        "pct_days_pm10_main_pollutant",
    ]

    acsCols = [
        "geo_id",
        "acs_name",
        "population_25_plus",
        "pct_high_school_or_higher",
        "pct_bachelors_or_higher",
        "population_16_plus",
        "unemployment_rate",
        "median_household_income",
        "mean_household_income",
        "per_capita_income",
        "poverty_rate_all_people",
        "pct_no_health_insurance",
        "income_quartile",
        "lower_income_group",
    ]

    countyAqi = (
        master.groupby("county", as_index=False)[aqiCols]
        .mean(numeric_only=True)
        .rename(columns={col: f"avg_{col}_2020_2024" for col in aqiCols})
    )

    acsByCounty = master[["county"] + acsCols].drop_duplicates("county")
    return acsByCounty.merge(countyAqi, on="county", how="left")


def saveDataDictionary(columns):
    rows = []
    for col in columns:
        note = columnNotes.get(col, "Kept or created during cleaning.")
        rows.append({"column": col, "description": note})

    pd.DataFrame(rows).to_csv(dataDictionaryOut, index=False)


def saveMissingReport(df):
    report = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": df.isna().sum().values,
            "missing_pct": (df.isna().mean().values * 100).round(2),
        }
    )
    report.to_csv(missingnessOut, index=False)


def buildMaster():
    aqi = loadAqiData()
    acs = loadAcsData()

    masterByYear = aqi.merge(acs, on="county", how="left", validate="many_to_one")
    masterCountyAvg = averageByCounty(masterByYear)

    masterByYear.to_csv(countyYearOut, index=False)
    masterCountyAvg.to_csv(countyAvgOut, index=False)
    saveDataDictionary(masterByYear.columns)
    saveMissingReport(masterByYear)

    matchedCounties = masterByYear.loc[
        masterByYear["geo_id"].notna(), "county"
    ].nunique()
    unmatchedCounties = sorted(
        masterByYear.loc[
            masterByYear["geo_id"].isna(), "county"
        ].dropna().unique()
    )

    print("new files:")
    print(f"- {countyYearOut.name}")
    print(f"- {countyAvgOut.name}")
    print(f"- {dataDictionaryOut.name}")
    print(f"- {missingnessOut.name}")
    print()
    print(f"County-year rows: {len(masterByYear)}")
    print(f"Counties in AQI data: {masterByYear['county'].nunique()}")
    print(f"Counties matched to ACS: {matchedCounties}")
    print(f"Unmatched AQI counties: {unmatchedCounties or 'None'}")

    return masterByYear, masterCountyAvg


if __name__ == "__main__":
    buildMaster()
