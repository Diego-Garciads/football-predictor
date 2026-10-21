import pandas as pd


FEATURES = [
    "points_per_game_difference",
    "form_difference",
    "attack_difference",
    "defense_difference",
    "rest_difference",
    "elo_difference"
]


def calculate_features(df):
    df = df.copy()

    # Dictionaries to store the information accumulated
    # before each match.
    points = {}
    games_played = {}
    form = {}
    last_match = {}
    elo = {}

    home_recent_goals_scored = {}
    away_recent_goals_scored = {}
    home_recent_goals_conceded = {}
    away_recent_goals_conceded = {}

    feature_rows = []

    for index, match in df.iterrows():

        home_team = match["home_team"]
        away_team = match["away_team"]
        competition = match["competition"]
        winner = match["winner"]

        home_key = (competition, home_team)
        away_key = (competition, away_team)

        # Initialize teams if they have not appeared before.
        for team_key in [home_key, away_key]:

            if team_key not in points:
                points[team_key] = 0

            if team_key not in games_played:
                games_played[team_key] = 0

            if team_key not in form:
                form[team_key] = []

            if team_key not in last_match:
                last_match[team_key] = None

            if team_key not in elo:
                elo[team_key] = 1500

            if team_key not in home_recent_goals_scored:
                home_recent_goals_scored[team_key] = []

            if team_key not in away_recent_goals_scored:
                away_recent_goals_scored[team_key] = []

            if team_key not in home_recent_goals_conceded:
                home_recent_goals_conceded[team_key] = []

            if team_key not in away_recent_goals_conceded:
                away_recent_goals_conceded[team_key] = []

        # --------------------------------------------------
        # REST DAYS
        # --------------------------------------------------

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

        # --------------------------------------------------
        # FORM
        # --------------------------------------------------

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

        # --------------------------------------------------
        # POINTS PER GAME
        # --------------------------------------------------

        if games_played[home_key] > 0:
            home_points_per_game = (
                points[home_key] / games_played[home_key]
            )
        else:
            home_points_per_game = 0

        if games_played[away_key] > 0:
            away_points_per_game = (
                points[away_key] / games_played[away_key]
            )
        else:
            away_points_per_game = 0

        # --------------------------------------------------
        # ELO
        # --------------------------------------------------

        home_elo = elo[home_key]
        away_elo = elo[away_key]

        elo_difference = home_elo - away_elo

        # --------------------------------------------------
        # RECENT GOALS
        # --------------------------------------------------

        home_scored = home_recent_goals_scored[home_key][-5:]
        away_scored = away_recent_goals_scored[away_key][-5:]

        home_conceded = home_recent_goals_conceded[home_key][-5:]
        away_conceded = away_recent_goals_conceded[away_key][-5:]

        if len(home_scored) > 0:
            home_avg_goals_scored = (
                sum(home_scored) / len(home_scored)
            )
        else:
            home_avg_goals_scored = 0

        if len(away_scored) > 0:
            away_avg_goals_scored = (
                sum(away_scored) / len(away_scored)
            )
        else:
            away_avg_goals_scored = 0

        if len(home_conceded) > 0:
            home_avg_goals_conceded = (
                sum(home_conceded) / len(home_conceded)
            )
        else:
            home_avg_goals_conceded = 0

        if len(away_conceded) > 0:
            away_avg_goals_conceded = (
                sum(away_conceded) / len(away_conceded)
            )
        else:
            away_avg_goals_conceded = 0

        # --------------------------------------------------
        # FINAL FEATURES
        # --------------------------------------------------

        points_per_game_difference = (
            home_points_per_game -
            away_points_per_game
        )

        form_difference = (
            home_form_points -
            away_form_points
        )

        attack_difference = (
            home_avg_goals_scored -
            away_avg_goals_scored
        )

        defense_difference = (
            away_avg_goals_conceded -
            home_avg_goals_conceded
        )

        rest_difference = (
            home_rest_days -
            away_rest_days
        )

        feature_rows.append({
            "date": match["date"],
            "competition": competition,
            "home_team": home_team,
            "away_team": away_team,
            "home_goals": match["home_goals"],
            "away_goals": match["away_goals"],
            "winner": winner,

            "points_per_game_difference":
                points_per_game_difference,

            "form_difference":
                form_difference,

            "attack_difference":
                attack_difference,

            "defense_difference":
                defense_difference,

            "rest_difference":
                rest_difference,

            "elo_difference":
                elo_difference
        })

        # --------------------------------------------------
        # UPDATE INFORMATION AFTER THE MATCH
        # --------------------------------------------------

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

        # Update Elo.
        K = 20

        expected_home = 1 / (
            1 + 10 ** (
                (away_elo - home_elo) / 400
            )
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
            (1 - actual_home) -
            (1 - expected_home)
        )

        # Update last match dates.
        last_match[home_key] = match["date"]
        last_match[away_key] = match["date"]

        # Update recent home/away goals.
        home_recent_goals_scored[home_key].append(
            match["home_goals"]
        )

        away_recent_goals_scored[away_key].append(
            match["away_goals"]
        )

        home_recent_goals_conceded[home_key].append(
            match["away_goals"]
        )

        away_recent_goals_conceded[away_key].append(
            match["home_goals"]
        )

    features_df = pd.DataFrame(feature_rows)

    return features_df


# Load matches downloaded by get_data.py.
matches = pd.read_csv("data/matches.csv")

matches["date"] = pd.to_datetime(matches["date"])

matches = matches.sort_values("date").reset_index(drop=True)


# Create the final feature dataset.
features_df = calculate_features(matches)


# Save it for the modelling stage.
features_df.to_csv(
    "data/features.csv",
    index=False
)


print(
    f"Created feature dataset with "
    f"{len(features_df)} matches."
)

print("\nFeatures used by the model:")