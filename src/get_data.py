import requests 
import pandas as pd

API_KEY = "68c5618eae8249d7b235a8697253b1d1"

url = "https://api.football-data.org/v4/competitions/PD/matches"

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
        "score.fullTime.home": "home_goals",
        "score.fullTime.away": "away_goals"
    }
)

clean_df["date"] = pd.to_datetime(clean_df["date"])
print(clean_df.head)