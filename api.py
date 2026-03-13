import pandas as pd
import time

# ─────────────────────────────────────────
# 1. ALL DATA (football-data.co.uk)
#    Results + Bet365 odds + upcoming fixtures
#    No API key needed!
# ─────────────────────────────────────────

def get_all_seasons():
    base_url = "https://www.football-data.co.uk/mmz4281"
    seasons = {
        "2122": "2021/2022",
        "2223": "2022/2023",
        "2324": "2023/2024",
        "2425": "2024/2025",
        "2526": "2025/2026",   # includes upcoming fixtures
    }

    all_data = []
    for code, label in seasons.items():
        url = f"{base_url}/{code}/E0.csv"
        print(f"  Downloading {url} ...")
        try:
            df = pd.read_csv(url)
            df = df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
                     "B365H", "B365D", "B365A"]].copy()
            df.columns = ["Date", "Home", "Away", "HomeGoals", "AwayGoals", "Result",
                          "OddsH", "OddsD", "OddsA"]
            df["Season"] = label
            df["Venue"]   = None
            df["Referee"] = None

            # Mark finished vs upcoming based on whether score exists
            df["Status"] = df["HomeGoals"].apply(lambda x: "FT" if pd.notna(x) else "NS")

            all_data.append(df)
            print(f"    → {len(df[df['Status']=='FT'])} finished, {len(df[df['Status']=='NS'])} upcoming")
        except Exception as e:
            print(f"    → Failed to download: {e}")
        time.sleep(0.5)

    return pd.concat(all_data, ignore_index=True)


# ─────────────────────────────────────────
# 2. STANDARDISE
# ─────────────────────────────────────────

def standardise(df):
    if df is None or df.empty:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed").dt.strftime("%Y-%m-%d")

    name_map = {
        "Man United":    "Manchester United",
        "Man City":      "Manchester City",
        "Nott'm Forest": "Nottingham Forest",
        "Spurs":         "Tottenham",
        "Leeds":         "Leeds United",
        "Leicester":     "Leicester City",
        "Wolves":        "Wolverhampton",
        "Sunderland":    "Sunderland",
    }
    df["Home"] = df["Home"].replace(name_map)
    df["Away"] = df["Away"].replace(name_map)

    for col in ["HomeGoals", "AwayGoals", "Venue", "Referee", "Season",
                "Status", "OddsH", "OddsD", "OddsA"]:
        if col not in df.columns:
            df[col] = None

    # Result only for finished matches
    if "Result" not in df.columns:
        df["Result"] = None
    df.loc[df["Status"] == "NS", "Result"] = None

    return df[["Date", "Season", "Home", "Away", "HomeGoals", "AwayGoals",
               "Result", "OddsH", "OddsD", "OddsA", "Venue", "Referee", "Status"]]


# ─────────────────────────────────────────
# 3. RUN
# ─────────────────────────────────────────

print("Fetching all data from football-data.co.uk ...")
combined = standardise(get_all_seasons())
combined = combined.drop_duplicates(subset=["Date", "Home", "Away"])
combined = combined.sort_values("Date").reset_index(drop=True)

combined.to_csv("matches_all.csv", index=False)
print(f"\nTotal: {len(combined)} rows saved to matches_all.csv ✅")
print("\nSeasons:", combined["Season"].value_counts())
print(f"\nFinished matches: {len(combined[combined['Status']=='FT'])}")
print(f"Upcoming fixtures: {len(combined[combined['Status']=='NS'])}")
print("\nUpcoming fixtures:")
print(combined[combined["Status"] == "NS"][["Date", "Home", "Away", "OddsH", "OddsD", "OddsA"]].to_string(index=False))