import pandas as pd

url = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"
df = pd.read_csv(url)
print(f"Total rows: {len(df)}")
print(f"FTHG null count: {df['FTHG'].isna().sum()}")
print(f"FTHG unique values (last 10): {df['FTHG'].tail(20).tolist()}")
print(df[['Date','HomeTeam','AwayTeam','FTHG','FTAG']].tail(10))