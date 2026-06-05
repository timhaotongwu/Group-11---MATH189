import pandas as pd

df = pd.read_csv("ca_aqi_acs_master_county_avg.csv")

print(df.shape)
print(df.columns.tolist())
print(df.head())