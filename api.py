import requests
import pandas as pd
import time

# ─────────────────────────────────────────
# 1. ALL DATA (football-data.co.uk)
#    Results + Bet365 odds + upcoming fixtures
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

def get_upcoming():
    import os
    token = os.getenv("FOOTBALL_DATA_KEY")
    
    print("  Fetching upcoming fixtures from football-data.org ...")
    url     = "https://api.football-data.org/v4/competitions/PL/matches"
    headers = {"X-Auth-Token": token}
    params  = {"status": "SCHEDULED"}
    
    response = requests.get(url, headers=headers, params=params)
    data     = response.json()
    
    # Team name cleanup (they use full names like "Arsenal FC")
    name_map = {
        "Arsenal FC":                    "Arsenal",
        "Aston Villa FC":                "Aston Villa",
        "AFC Bournemouth":               "Bournemouth",
        "Brentford FC":                  "Brentford",
        "Brighton & Hove Albion FC":     "Brighton",
        "Burnley FC":                    "Burnley",
        "Chelsea FC":                    "Chelsea",
        "Crystal Palace FC":             "Crystal Palace",
        "Everton FC":                    "Everton",
        "Fulham FC":                     "Fulham",
        "Leeds United FC":               "Leeds United",
        "Liverpool FC":                  "Liverpool",
        "Manchester City FC":            "Manchester City",
        "Manchester United FC":          "Manchester United",
        "Newcastle United FC":           "Newcastle",
        "Nottingham Forest FC":          "Nottingham Forest",
        "Sunderland AFC":                "Sunderland",
        "Tottenham Hotspur FC":          "Tottenham",
        "West Ham United FC":            "West Ham",
        "Wolverhampton Wanderers FC":    "Wolverhampton",
    }
    
    rows = []
    for match in data.get("matches", []):
        home = name_map.get(match["homeTeam"]["name"], match["homeTeam"]["name"])
        away = name_map.get(match["awayTeam"]["name"], match["awayTeam"]["name"])
        rows.append({
            "Date":      match["utcDate"][:10],
            "Home":      home,
            "Away":      away,
            "HomeGoals": None,
            "AwayGoals": None,
            "Result":    None,
            "OddsH":     None,
            "OddsD":     None,
            "OddsA":     None,
            "Season":    "2025/2026",
            "Status":    "NS",
            "Venue":     None,
            "Referee":   None,
        })
    
    if not rows:
        print("  → No upcoming fixtures found")
        return pd.DataFrame()
    
    print(f"  → {len(rows)} upcoming fixtures found")
    return pd.DataFrame(rows)
# ─────────────────────────────────────────
# 3. RUN
# ─────────────────────────────────────────
print("Fetching all historical data from football-data.co.uk ...")
historical = standardise(get_all_seasons())
print(f"  → {len(historical)} finished matches")

print("\nFetching upcoming fixtures from football-data.org ...")
upcoming = standardise(get_upcoming())
print(f"  → {len(upcoming)} upcoming fixtures")

combined = pd.concat([historical, upcoming], ignore_index=True)
combined = combined.drop_duplicates(subset=["Date", "Home", "Away"])
combined = combined.sort_values("Date").reset_index(drop=True)

combined.to_csv("matches_all.csv", index=False)
print(f"\nTotal: {len(combined)} rows saved to matches_all.csv ✅")
print(f"\nFinished: {len(combined[combined['Status']=='FT'])}")
print(f"Upcoming: {len(combined[combined['Status']=='NS'])}")