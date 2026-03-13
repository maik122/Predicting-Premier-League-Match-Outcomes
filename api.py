import requests
import pandas as pd
import time
import os

API_KEY = os.getenv("FOOTBALL_API_KEY")
if not API_KEY:
    raise ValueError("No API key found! Set FOOTBALL_API_KEY in your terminal.")


# ─────────────────────────────────────────
# 1. HISTORICAL DATA (football-data.co.uk)
#    Results + Bet365 odds, all 4 seasons
# ─────────────────────────────────────────

def get_historical():
    base_url = "https://www.football-data.co.uk/mmz4281"
    seasons = {
        "2122": "2021/2022",
        "2223": "2022/2023",
        "2324": "2023/2024",
        "2425": "2024/2025",
    }

    all_data = []
    for code, label in seasons.items():
        url = f"{base_url}/{code}/E0.csv"
        print(f"  Downloading {url} ...")
        df = pd.read_csv(url)
        df = df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
                 "B365H", "B365D", "B365A"]].copy()
        df.columns = ["Date", "Home", "Away", "HomeGoals", "AwayGoals", "Result",
                      "OddsH", "OddsD", "OddsA"]
        df["Season"] = label
        df["Status"] = "FT"
        df["Venue"]   = None
        df["Referee"] = None
        all_data.append(df)
        time.sleep(0.5)

    return pd.concat(all_data, ignore_index=True)


# ─────────────────────────────────────────
# 2. UPCOMING FIXTURES (API-Football)
#    Next 14 days, not yet played
# ─────────────────────────────────────────

def get_upcoming(days_ahead=14):
    from datetime import date, timedelta
    today = date.today()
    end   = today + timedelta(days=days_ahead)

    print(f"  Fetching upcoming fixtures {today} → {end} ...")
    url     = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params  = {"league": 39, "from": today.isoformat(), "to": end.isoformat()}
    response = requests.get(url, headers=headers, params=params)
    data     = response.json()

    rows = []
    for match in data.get("response", []):
        rows.append({
            "Date":      match["fixture"]["date"][:10],
            "Home":      match["teams"]["home"]["name"],
            "Away":      match["teams"]["away"]["name"],
            "HomeGoals": None,
            "AwayGoals": None,
            "Result":    None,
            "OddsH":     None,
            "OddsD":     None,
            "OddsA":     None,
            "Season":    "2025/2026",
            "Status":    "NS",
            "Venue":     match["fixture"]["venue"]["name"],
            "Referee":   match["fixture"]["referee"],
        })

    if not rows:
        print("  → No upcoming fixtures found (2025/26 not on free plan)")
        return pd.DataFrame()

    return pd.DataFrame(rows)

# ─────────────────────────────────────────
# 3. STANDARDISE
# ─────────────────────────────────────────

def standardise(df):
    if df.empty:
        return df
    
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed").dt.strftime("%Y-%m-%d")

    name_map = {
        "Man United":    "Manchester United",
        "Man City":      "Manchester City",
        "Nott'm Forest": "Nottingham Forest",
        "Spurs":         "Tottenham",
        "Leeds":         "Leeds United",
        "Leicester":     "Leicester City",
        "Wolves":        "Wolverhampton",
    }
    df["Home"] = df["Home"].replace(name_map)
    df["Away"] = df["Away"].replace(name_map)

    for col in ["HomeGoals", "AwayGoals", "Venue", "Referee", "Season",
                "Status", "OddsH", "OddsD", "OddsA"]:
        if col not in df.columns:
            df[col] = None

    if "Result" not in df.columns:
        df["Result"] = df.apply(
            lambda r: "H" if r["HomeGoals"] > r["AwayGoals"]
                      else ("A" if r["HomeGoals"] < r["AwayGoals"] else "D"), axis=1
        )

    return df[["Date", "Season", "Home", "Away", "HomeGoals", "AwayGoals",
               "Result", "OddsH", "OddsD", "OddsA", "Venue", "Referee", "Status"]]


# ─────────────────────────────────────────
# 4. RUN
# ─────────────────────────────────────────

print("Fetching historical data from football-data.co.uk ...")
historical = standardise(get_historical())
print(f"  → {len(historical)} finished matches")

print("\nFetching upcoming fixtures from API ...")
upcoming = standardise(get_upcoming(days_ahead=14))
print(f"  → {len(upcoming)} upcoming matches")

# Combine and save
combined = pd.concat([historical, upcoming], ignore_index=True)
combined = combined.drop_duplicates(subset=["Date", "Home", "Away"])
combined = combined.sort_values("Date").reset_index(drop=True)

combined.to_csv("matches_all.csv", index=False)
print(f"\nTotal: {len(combined)} rows saved to matches_all.csv ✅")
print("\nSeasons:", combined["Season"].value_counts())
print("\nUpcoming fixtures:")
print(combined[combined["Status"] == "NS"][["Date", "Home", "Away"]].to_string(index=False))