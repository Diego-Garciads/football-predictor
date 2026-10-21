import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "points_per_game_difference",
    "form_difference",
    "attack_difference",
    "defense_difference",
    "rest_difference",
    "elo_difference"
]


def train_model():

    df = pd.read_csv("data/features.csv")

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)

    n = len(df)

    train_end = int(n * 0.80)

    X_train = df[FEATURES].iloc[:train_end]
    y_train = df["winner"].iloc[:train_end]

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(
        C=1,
        max_iter=3000,
        random_state=42
    )

    model.fit(X_train_scaled, y_train)

    return df, model, scaler


def predict_match(home_team, away_team):

    df, model, scaler = train_model()

    home_matches = df[
        (df["home_team"] == home_team) |
        (df["away_team"] == home_team)
    ]

    away_matches = df[
        (df["home_team"] == away_team) |
        (df["away_team"] == away_team)
    ]

    if home_matches.empty:
        return None

    if away_matches.empty:
        return None

    home_last = home_matches.iloc[-1]
    away_last = away_matches.iloc[-1]

    features = [
        home_last["points_per_game_difference"]
        - away_last["points_per_game_difference"],

        home_last["form_difference"]
        - away_last["form_difference"],

        home_last["attack_difference"]
        - away_last["attack_difference"],

        home_last["defense_difference"]
        - away_last["defense_difference"],

        home_last["rest_difference"]
        - away_last["rest_difference"],

        home_last["elo_difference"]
        - away_last["elo_difference"]
    ]

    X_prediction = pd.DataFrame(
        [features],
        columns=FEATURES
    )

    X_prediction_scaled = scaler.transform(
        X_prediction
    )

    probabilities = model.predict_proba(
        X_prediction_scaled
    )[0]

    classes = model.classes_

    results = dict(
        zip(classes, probabilities)
    )

    prediction = classes[probabilities.argmax()]

    return {
        "prediction": prediction,
        "home_probability": results.get("HOME_TEAM", 0),
        "draw_probability": results.get("DRAW", 0),
        "away_probability": results.get("AWAY_TEAM", 0)
    }
