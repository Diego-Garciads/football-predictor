import requests
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler


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

clean_df["home_elo"] = 1500.0
clean_df["away_elo"] = 1500.0
clean_df["elo_difference"] = 0.0

clean_df["home_points_per_game"] = 0.0
clean_df["away_points_per_game"] = 0.0


points = {}
games_played = {}
positions = {}
form = {}
last_match = {}
goals = {}
goals_conceded = {}
home_recent_goals_scored = {}
home_recent_goals_conceded = {}
away_recent_goals_scored = {}
away_recent_goals_conceded = {}
elo = {}


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


    if home_key not in games_played:
        games_played[home_key] = 0

    if away_key not in games_played:
        games_played[away_key] = 0


    if home_key not in elo:
        elo[home_key] = 1500

    if away_key not in elo:
        elo[away_key] = 1500


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


    if home_key not in home_recent_goals_scored:
        home_recent_goals_scored[home_key] = []

    if away_key not in away_recent_goals_scored:
        away_recent_goals_scored[away_key] = []

    if home_key not in home_recent_goals_conceded:
        home_recent_goals_conceded[home_key] = []

    if away_key not in away_recent_goals_conceded:
        away_recent_goals_conceded[away_key] = []



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

    if games_played[home_key] > 0:
        home_points_per_game = points[home_key] / games_played[home_key]
    else:
        home_points_per_game = 0

    if games_played[away_key] > 0:
        away_points_per_game = points[away_key] / games_played[away_key] 
    else:
        away_points_per_game = 0

    clean_df.loc[index, "home_points_per_game"] = home_points_per_game
    clean_df.loc[index, "away_points_per_game"] = away_points_per_game

    clean_df.loc[index, "home_elo"] = elo[home_key]
    clean_df.loc[index, "away_elo"] = elo[away_key]

    clean_df.loc[index, "elo_difference"] = (
        elo[home_key] - elo[away_key]
    )

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


    home_recent_scored = home_recent_goals_scored[home_key][-5:]
    away_recent_scored = away_recent_goals_scored[away_key][-5:]

    home_recent_conceded = home_recent_goals_conceded[home_key][-5:]
    away_recent_conceded = away_recent_goals_conceded[away_key][-5:]

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


    clean_df.loc[index, "points_per_game_difference"] = (
        home_points_per_game -
        away_points_per_game
    )

    clean_df.loc[index, "form_difference"] = (
        home_form_points -
        away_form_points
    )

    clean_df.loc[index, "attack_difference"] = (
        home_avg_goals_scored -
        away_avg_goals_scored
    )

    clean_df.loc[index, "defense_difference"] = (
        away_avg_goals_conceded -
        home_avg_goals_conceded
    )

    clean_df.loc[index, "rest_difference"] = (
        home_rest_days -
        away_rest_days
    )



    if winner == "HOME_TEAM":
        points[home_key] += 3

    elif winner == "AWAY_TEAM":
        points[away_key] += 3

    elif winner == "DRAW":
        points[home_key] += 1
        points[away_key] += 1

    games_played[home_key] += 1
    games_played[away_key] += 1

    if winner == "HOME_TEAM":
        form[home_key].append("W")
        form[away_key].append("L")

    elif winner == "AWAY_TEAM":
        form[home_key].append("L")
        form[away_key].append("W")

    elif winner == "DRAW":
        form[home_key].append("D")
        form[away_key].append("D")


    K = 20

    home_elo = elo[home_key]
    away_elo = elo[away_key]

    expected_home = 1 / (
        1 + 10 ** ((away_elo - home_elo) / 400)
    )

    if winner == "HOME_TEAM":
        actual_home = 1

    elif winner == "DRAW":
        actual_home = 0.5

    else:
        actual_home = 0

    elo[home_key] = home_elo + K * (
     actual_home - expected_home
    )

    elo[away_key] = away_elo + K * (
        (1 - actual_home) - (1 - expected_home)
    )


    last_match[home_key] = match["date"]
    last_match[away_key] = match["date"]


    goals[home_key] += match["home_goals"]
    goals[away_key] += match["away_goals"]


    goals_conceded[home_key] += match["away_goals"]
    goals_conceded[away_key] += match["home_goals"]

    home_recent_goals_scored[home_key].append(match["home_goals"])
    away_recent_goals_scored[away_key].append(match["away_goals"])

    home_recent_goals_conceded[home_key].append(match["away_goals"])
    away_recent_goals_conceded[away_key].append(match["home_goals"])



X = clean_df[
    [
        "points_per_game_difference",
        "form_difference",
        "attack_difference",
        "defense_difference",
        "rest_difference",
        "elo_difference"
    ]
]

y = clean_df["winner"]


train_end = int(len(clean_df) * 0.64)
validation_end = int(len(clean_df) * 0.80)

X_train = X.iloc[:train_end]
X_validation = X.iloc[train_end:validation_end]
X_test = X.iloc[validation_end:]

y_train = y.iloc[:train_end]
y_validation = y.iloc[train_end:validation_end]
y_test = y.iloc[validation_end:]


baseline = DummyClassifier(strategy="most_frequent")

baseline.fit(X_train, y_train)

baseline_pred = baseline.predict(X_test)

baseline_accuracy = accuracy_score(y_test, baseline_pred)
print( "Baseline accuracy:", baseline_accuracy )

logistic_model = LogisticRegression(
    C=1,
    max_iter=3000,
    random_state=42
)

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_validation_scaled = scaler.transform(X_validation)
X_test_scaled = scaler.transform(X_test)

logistic_model.fit(X_train_scaled, y_train)

validation_proba = logistic_model.predict_proba(X_validation_scaled)
test_proba = logistic_model.predict_proba(X_test_scaled)

draw_class = list(logistic_model.classes_).index("DRAW")

print("\nAverage predicted probabilities - Validation:")

for class_name, class_index in zip(
    logistic_model.classes_,
    range(len(logistic_model.classes_))
):
    print(
        class_name,
        validation_proba[:, class_index].mean()
    )


print("\nAverage DRAW probability by real result:")

for result in logistic_model.classes_:
    mask = y_validation == result

    print(
        result,
        validation_proba[mask, draw_class].mean()
        if mask.sum() > 0 else 0
    )


draw_thresholds = [0.25, 0.27, 0.29, 0.31, 0.33]

best_threshold = None
best_validation_accuracy = 0

for threshold in draw_thresholds:

    validation_pred = logistic_model.predict(X_validation_scaled)

    for i in range(len(validation_pred)):

        if validation_proba[i, draw_class] >= threshold:
            validation_pred[i] = "DRAW"

    validation_accuracy = accuracy_score(
        y_validation,
        validation_pred
    )

    print(
        f"Validation - Draw threshold {threshold:.2f}: "
        f"{validation_accuracy:.4f}"
    )

    if validation_accuracy > best_validation_accuracy:
        best_validation_accuracy = validation_accuracy
        best_threshold = threshold

print("Best draw threshold:", best_threshold)
print(
    "Best validation accuracy:",
    best_validation_accuracy
)



test_pred = logistic_model.predict(X_test_scaled)

for i in range(len(test_pred)):

    if test_proba[i, draw_class] >= best_threshold:
        test_pred[i] = "DRAW"

test_accuracy = accuracy_score(
    y_test,
    test_pred
)

print("\nFinal Test Accuracy:", test_accuracy)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, test_pred))

print("\nClassification Report:")
print(classification_report(y_test, test_pred))

