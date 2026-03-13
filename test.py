import requests
import os

token = os.getenv("FOOTBALL_DATA_KEY")

url = "https://api.football-data.org/v4/competitions/PL/matches"
headers = {"X-Auth-Token": token}
params = {"status": "SCHEDULED"}

response = requests.get(url, headers=headers, params=params)
data = response.json()

for match in data["matches"]:
    date = match["utcDate"][:10]
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    print(f"{date}  {home} vs {away}")