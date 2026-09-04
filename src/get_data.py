import requests
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix


API_KEY = "57c131ee53d94bc2bc59dfcd4cd9d788"

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
        "matchday": "matchday",
        "competition": "competition",
        "homeTeam.name": "home_team",
        "awayTeam.name": "away_team",
        "score.winner": "winner",
        "score.fullTime.home": "home_goals",
        "score.fullTime.away": "away_goals"
    }
)

clean_df["date"] = pd.to_datetime(clean_df["date"])

clean_df = clean_df.sort_values("date").reset_index(drop=True)


clean_df["home_points"] = 0
clean_df["away_points"] = 0

clean_df["home_position"] = 0
clean_df["away_position"] = 0

clean_df["home_rest_days"] = 0
clean_df["away_rest_days"] = 0

clean_df["last_h2h"] = 0

clean_df["home_goals_scored"] = 0
clean_df["away_goals_scored"] = 0

clean_df["home_goals_conceded"] = 0
clean_df["away_goals_conceded"] = 0

clean_df["home_form_points"] = 0
clean_df["away_form_points"] = 0

clean_df["home_avg_goals_scored"] = 0.0
clean_df["away_avg_goals_scored"] = 0.0

clean_df["home_avg_goals_conceded"] = 0.0
clean_df["away_avg_goals_conceded"] = 0.0


points = {}
positions = {}
form = {}
last_match = {}
goals = {}
goals_conceded = {}
recent_goals_scored = {}
recent_goals_conceded = {}


for index, match in clean_df.iterrows():

    homeTeam = match["home_team"]
    awayTeam = match["away_team"]
    winner = match["winner"]
    competition = match["competition"]

    home_key = (competition, homeTeam)
    away_key = (competition, awayTeam)


    previous_matches = clean_df.iloc[:index][
        (clean_df.iloc[:index]["competition"] == competition) &
        (
            (
                (clean_df.iloc[:index]["home_team"] == homeTeam) &
                (clean_df.iloc[:index]["away_team"] == awayTeam)
            )
            |
            (
                (clean_df.iloc[:index]["home_team"] == awayTeam) &
                (clean_df.iloc[:index]["away_team"] == homeTeam)
            )
        )
    ]

    
    if home_key not in points:
        points[home_key] = 0

    if away_key not in points:
        points[away_key] = 0


    if home_key not in form:
        form[home_key] = []

    if away_key not in form:
        form[away_key] = []


    if home_key not in last_match:
        last_match[home_key] = None

    if away_key not in last_match:
        last_match[away_key] = None


    if home_key not in goals:
        goals[home_key] = 0

    if away_key not in goals:
        goals[away_key] = 0


    if home_key not in goals_conceded:
        goals_conceded[home_key] = 0

    if away_key not in goals_conceded:
        goals_conceded[away_key] = 0


    if home_key not in recent_goals_scored:
        recent_goals_scored[home_key] = []

    if away_key not in recent_goals_scored:
        recent_goals_scored[away_key] = []

    if home_key not in recent_goals_conceded:
        recent_goals_conceded[home_key] = []

    if away_key not in recent_goals_conceded:
        recent_goals_conceded[away_key] = []



    if last_match[home_key] is None:
        home_rest_days = 0
    else:
        home_rest_days = (
            match["date"] - last_match[home_key]
        ).days


    if last_match[away_key] is None:
        away_rest_days = 0
    else:
        away_rest_days = (
            match["date"] - last_match[away_key]
        ).days


    home_form = form[home_key][-5:]
    away_form = form[away_key][-5:]


    home_form_points = 0
    away_form_points = 0


    for result in home_form:

        if result == "W":
            home_form_points += 3

        elif result == "D":
            home_form_points += 1


    for result in away_form:

        if result == "W":
            away_form_points += 3

        elif result == "D":
            away_form_points += 1


    clean_df.loc[index, "home_points"] = points[home_key]
    clean_df.loc[index, "away_points"] = points[away_key]

    clean_df.loc[index, "home_rest_days"] = home_rest_days
    clean_df.loc[index, "away_rest_days"] = away_rest_days

    clean_df.loc[index, "home_goals_scored"] = goals[home_key]
    clean_df.loc[index, "away_goals_scored"] = goals[away_key]

    clean_df.loc[index, "home_goals_conceded"] = goals_conceded[home_key]
    clean_df.loc[index, "away_goals_conceded"] = goals_conceded[away_key]

    clean_df.loc[index, "home_form_points"] = home_form_points
    clean_df.loc[index, "away_form_points"] = away_form_points


    competition_points = {
        team: pts
        for (comp, team), pts in points.items()
        if comp == competition
    }

    sorted_teams = sorted(
        competition_points.items(),
        key=lambda x: x[1],
        reverse=True
    )


    if match["matchday"] == 1:

        clean_df.loc[index, "home_position"] = 0
        clean_df.loc[index, "away_position"] = 0

    else:

        for position, (team, pts) in enumerate(sorted_teams):

            positions[(competition, team)] = position + 1

        clean_df.loc[index, "home_position"] = positions[home_key]
        clean_df.loc[index, "away_position"] = positions[away_key]


    last_h2h = previous_matches[-1:]

    last_h2h_team = 0


    if len(last_h2h) > 0:

        last_home_team = last_h2h["home_team"].iloc[0]
        last_winner = last_h2h["winner"].iloc[0]


        if last_winner == "HOME_TEAM":

            if last_home_team == homeTeam:
                last_h2h_team = 1
            else:
                last_h2h_team = -1


        elif last_winner == "AWAY_TEAM":

            if last_home_team == homeTeam:
                last_h2h_team = -1
            else:
                last_h2h_team = 1


        elif last_winner == "DRAW":

            last_h2h_team = 0


    clean_df.loc[index, "last_h2h"] = last_h2h_team


    home_recent_scored = recent_goals_scored[home_key][-5:]
    away_recent_scored = recent_goals_scored[away_key][-5:]

    home_recent_conceded = recent_goals_conceded[home_key][-5:]
    away_recent_conceded = recent_goals_conceded[away_key][-5:]


    if len(home_recent_scored) > 0:
        home_avg_goals_scored = sum(home_recent_scored) / len(home_recent_scored)
    else:
        home_avg_goals_scored = 0

    if len(away_recent_scored) > 0:
        away_avg_goals_scored = sum(away_recent_scored) / len(away_recent_scored)
    else:
        away_avg_goals_scored = 0

    if len(home_recent_conceded) > 0:
        home_avg_goals_conceded = sum(home_recent_conceded) / len(home_recent_conceded)
    else:
        home_avg_goals_conceded = 0

    if len(away_recent_conceded) > 0:
        away_avg_goals_conceded = sum(away_recent_conceded) / len(away_recent_conceded)
    else:
        away_avg_goals_conceded = 0


    clean_df.loc[index, "home_avg_goals_scored"] = home_avg_goals_scored
    clean_df.loc[index, "away_avg_goals_scored"] = away_avg_goals_scored
    clean_df.loc[index, "home_avg_goals_conceded"] = home_avg_goals_conceded
    clean_df.loc[index, "away_avg_goals_conceded"] = away_avg_goals_conceded



    if winner == "HOME_TEAM":

        points[home_key] += 3

    elif winner == "AWAY_TEAM":

        points[away_key] += 3

    elif winner == "DRAW":

        points[home_key] += 1
        points[away_key] += 1



    if winner == "HOME_TEAM":

        form[home_key].append("W")
        form[away_key].append("L")

    elif winner == "AWAY_TEAM":

        form[home_key].append("L")
        form[away_key].append("W")

    elif winner == "DRAW":

        form[home_key].append("D")
        form[away_key].append("D")



    last_match[home_key] = match["date"]
    last_match[away_key] = match["date"]


    goals[home_key] += match["home_goals"]
    goals[away_key] += match["away_goals"]


    goals_conceded[home_key] += match["away_goals"]
    goals_conceded[away_key] += match["home_goals"]

    recent_goals_scored[home_key].append(match["home_goals"])
    recent_goals_scored[away_key].append(match["away_goals"])

    recent_goals_conceded[home_key].append(match["away_goals"])
    recent_goals_conceded[away_key].append(match["home_goals"])


competition_codes = {
    "PD": 0,
    "PL": 1,
    "BL1": 2,
    "SA": 3,
    "FL1": 4
}

clean_df["competition_code"] = clean_df["competition"].map(competition_codes)

X = clean_df[
    [
        "home_points",
        "away_points",
        "home_position",
        "away_position",
        "home_rest_days",
        "away_rest_days",
        "last_h2h",
        "home_goals_scored",
        "away_goals_scored",
        "home_goals_conceded",
        "away_goals_conceded",
        "home_form_points",
        "away_form_points",
        "competition_code",
        "home_avg_goals_scored",
        "away_avg_goals_scored",
        "home_avg_goals_conceded",
        "away_avg_goals_conceded"
    ]
]

y = clean_df["winner"]


split = int(len(clean_df) * 0.8)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]



baseline = DummyClassifier(strategy="most_frequent")

baseline.fit(X_train, y_train)

baseline_pred = baseline.predict(X_test)

baseline_accuracy = accuracy_score(y_test, baseline_pred)

print("Baseline accuracy:", baseline_accuracy)



logistic_model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

logistic_model.fit(X_train, y_train)

logistic_pred = logistic_model.predict(X_test)

logistic_accuracy = accuracy_score(y_test, logistic_pred)

print("Logistic Regression accuracy:", logistic_accuracy)

logistic_matrix = confusion_matrix(y_test, logistic_pred)

print("Logistic Regression confusion matrix:")
print(logistic_matrix)

print("Logistic Regression coefficients:")

for feature, coefficient in zip(X.columns, logistic_model.coef_[0]):
    print(feature, coefficient)


random_forest = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

random_forest.fit(X_train, y_train)

rf_pred = random_forest.predict(X_test)

rf_accuracy = accuracy_score(y_test, rf_pred)

print("Random Forest accuracy:", rf_accuracy)



print()
print("========== COMPARACIÓN ==========")
print("Baseline:", baseline_accuracy)
print("Logistic Regression:", logistic_accuracy)
print("Random Forest:", rf_accuracy)
