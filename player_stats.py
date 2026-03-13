import soccerdata as sd
import pandas as pd

# Scrape PL player stats for last 4 seasons
fbref = sd.FBref(leagues="ENG-Premier League", seasons=["2122","2223","2324","2425"])

# Get player stats per match
stats = fbref.read_player_match_stats(stat_type="summary")
stats.to_csv("player_stats.csv")
print(f"Saved {len(stats)} player stat rows")
print(stats.head())