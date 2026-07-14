import requests 
import pandas as pd

API_KEY = "68c5618eae8249d7b235a8697253b1d1"

url = "https://api.football-data.org/v4/competitions/PD/matches?season=2025"

headers = {
    "X-Auth-Token": API_KEY
}

response = requests.get(url, headers=headers)
data = response.json()

matches = data["matches"]

df = pd.json_normalize(matches)

clean_df = df[
    [
        "utcDate",
        "matchday",
        "homeTeam.name",
        "awayTeam.name",
        "score.winner",
        "score.fullTime.home",
        "score.fullTime.away"
    ]
]

clean_df = clean_df.rename(columns= 
    {
        "utcDate": "date",
        "matchday": "matchday",
        "homeTeam.name": "home_team",
        "awayTeam.name": "away_team",
        "score.winner": "winner",
        "score.fullTime.home": "home_goals",
        "score.fullTime.away": "away_goals"
    }
)

clean_df["date"] = pd.to_datetime(clean_df["date"])
clean_df["home_points"] = 0
clean_df["away_points"] = 0

points = {}
for index, match in clean_df.iterrows():
    homeTeam = match["home_team"]
    awayTeam = match["away_team"]
    winner = match["winner"]

    if homeTeam not in points:
        points[homeTeam] = 0
    
    if awayTeam not in points:
        points[awayTeam] = 0
    
    clean_df.loc[index, "home_points"] = points[homeTeam]
    clean_df.loc[index, "away_points"] = points[awayTeam]

    if winner == "HOME_TEAM":
        points[homeTeam] += 3
    
    elif winner == "AWAY_TEAM":
        points[awayTeam] += 3

    elif winner == "DRAW":
        points[homeTeam] += 1
        points[awayTeam] += 1
    



