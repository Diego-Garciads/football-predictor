import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")


headers = {
    "X-Auth-Token": API_KEY
}


def get_matches(competition):
    url = (
        f"https://api.football-data.org/v4/competitions/"
        f"{competition}/matches?season=2025"
    )

    response = requests.get(url, headers=headers)
    data = response.json()

    df = pd.json_normalize(data["matches"])
    df["competition"] = competition

    return df


competitions = ["PD", "PL", "BL1", "SA", "FL1"]

dfs = []

for competition in competitions:
    dfs.append(get_matches(competition))

df = pd.concat(dfs, ignore_index=True)


clean_df = df[
    [
        "utcDate",
        "matchday",
        "competition",
        "homeTeam.name",
        "awayTeam.name",
        "score.winner",
        "score.fullTime.home",
        "score.fullTime.away"
    ]
]


clean_df = clean_df.rename(
    columns={
        "utcDate": "date",
        "homeTeam.name": "home_team",
        "awayTeam.name": "away_team",
        "score.winner": "winner",
        "score.fullTime.home": "home_goals",
        "score.fullTime.away": "away_goals"
    }
)


clean_df["date"] = pd.to_datetime(clean_df["date"])

clean_df = clean_df.sort_values("date").reset_index(drop=True)


clean_df.to_csv("data/matches.csv", index=False)

print(f"Downloaded {len(clean_df)} matches.")







