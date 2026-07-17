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
clean_df["home_position"] = 0
clean_df["away_position"] = 0
clean_df["home_form"] = ""
clean_df["away_form"] = ""
clean_df["home_rest_days"] = 0
clean_df["away_rest_days"] = 0
clean_df["last_h2h"] = ""

points = {}
positions = {}
form = {}
last_match = {}

for index, match in clean_df.iterrows():
    homeTeam = match["home_team"]
    awayTeam = match["away_team"]
    winner = match["winner"]
    previous_matches = clean_df.iloc[:index][
    (
        (clean_df.iloc[:index]["home_team"] == homeTeam) &
        (clean_df.iloc[:index]["away_team"] == awayTeam)
    )
    |
    (
        (clean_df.iloc[:index]["home_team"] == awayTeam) &
        (clean_df.iloc[:index]["away_team"] == homeTeam)
    )
]

    if homeTeam not in points:
        points[homeTeam] = 0
    
    if awayTeam not in points:
        points[awayTeam] = 0
    

    if homeTeam not in form:
        form[homeTeam] = []
    
    if awayTeam not in form:
        form[awayTeam] = []
    

    if homeTeam not in last_match:
        last_match[homeTeam] = None
    
    if awayTeam not in last_match:
        last_match[awayTeam] = None
    
    if last_match[homeTeam] is None:
        home_rest_days = 0
    else:
        home_rest_days = (match["date"] - last_match[homeTeam]).days
    
    if last_match[awayTeam] is None:
        away_rest_days = 0
    else:
        away_rest_days = (match["date"] - last_match[awayTeam]).days

    
    home_form = form[homeTeam][-5:]
    away_form = form[awayTeam][-5:]

    clean_df.loc[index, "home_form"] = str(home_form)
    clean_df.loc[index, "away_form"] = str(away_form)

    clean_df.loc[index, "home_points"] = points[homeTeam]
    clean_df.loc[index, "away_points"] = points[awayTeam]

    clean_df.loc[index, "home_rest_days"] = home_rest_days
    clean_df.loc[index, "away_rest_days"] = away_rest_days


    sorted_teams = sorted(points.items(), key=lambda x: x[1], reverse=True)
    
    if match["matchday"] == 1:
        clean_df.loc[index, "home_position"] = 0
        clean_df.loc[index, "away_position"] = 0
    else:
        for position, (team, pts) in enumerate(sorted_teams):
            positions[team] = position + 1
        
        clean_df.loc[index, "home_position"] = positions[homeTeam]
        clean_df.loc[index, "away_position"] = positions[awayTeam]

    last_h2h = previous_matches[-1:]
    last_h2h_team = "NONE"
    if len(last_h2h) > 0:
        last_home_team = last_h2h["home_team"].iloc[0]
        last_winner = last_h2h["winner"].iloc[0]
    
        if last_winner == "HOME_TEAM":
            if last_home_team == homeTeam:
                last_h2h_team = homeTeam
            else:
                last_h2h_team = awayTeam
    
        elif last_winner == "AWAY_TEAM":
            if last_home_team == homeTeam:
                last_h2h_team = awayTeam
            else:
                last_h2h_team = homeTeam
    
        elif last_winner == "DRAW":
            last_h2h_team = "DRAW"
    
    clean_df.loc[index, "last_h2h"] = last_h2h_team


    if winner == "HOME_TEAM":
        points[homeTeam] += 3
    
    elif winner == "AWAY_TEAM":
        points[awayTeam] += 3

    elif winner == "DRAW":
        points[homeTeam] += 1
        points[awayTeam] += 1
    
    if winner == "HOME_TEAM":
        form[homeTeam].append("W")
        form[awayTeam].append("L")
    
    elif winner == "AWAY_TEAM":
        form[homeTeam].append("L")
        form[awayTeam].append("W")
    
    elif winner == "DRAW":
        form[homeTeam].append("D")
        form[awayTeam].append("D")

    last_match[homeTeam] = match["date"]
    last_match[awayTeam] = match["date"]