import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


FEATURES = [
    "points_per_game_difference",
    "form_difference",
    "attack_difference",
    "defense_difference",
    "rest_difference",
    "elo_difference"
]


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("data/features.csv")

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)


# --------------------------------------------------
# FEATURES AND TARGET
# --------------------------------------------------

X = df[FEATURES]

y = df["winner"]


# --------------------------------------------------
# TEMPORAL SPLIT
# --------------------------------------------------

n = len(df)

train_end = int(n * 0.64)
validation_end = int(n * 0.80)

X_train = X.iloc[:train_end]
X_validation = X.iloc[train_end:validation_end]
X_test = X.iloc[validation_end:]

y_train = y.iloc[:train_end]
y_validation = y.iloc[train_end:validation_end]
y_test = y.iloc[validation_end:]


print("Training matches:", len(X_train))
print("Validation matches:", len(X_validation))
print("Test matches:", len(X_test))


# --------------------------------------------------
# STANDARDIZATION
# --------------------------------------------------

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_validation_scaled = scaler.transform(X_validation)

X_test_scaled = scaler.transform(X_test)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = LogisticRegression(
    C=1,
    max_iter=3000,
    random_state=42
)

model.fit(X_train_scaled, y_train)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

validation_probabilities = model.predict_proba(
    X_validation_scaled
)

classes = model.classes_

home_index = list(classes).index("HOME_TEAM")
draw_index = list(classes).index("DRAW")
away_index = list(classes).index("AWAY_TEAM")


print("\nValidation results:")

best_threshold = 0
best_accuracy = 0

for threshold in [0.25, 0.27, 0.29, 0.31, 0.33]:

    predictions = []

    for probabilities in validation_probabilities:

        home_probability = probabilities[home_index]
        draw_probability = probabilities[draw_index]
        away_probability = probabilities[away_index]

        if draw_probability >= threshold:
            prediction = "DRAW"

        elif home_probability >= away_probability:
            prediction = "HOME_TEAM"

        else:
            prediction = "AWAY_TEAM"

        predictions.append(prediction)

    accuracy = accuracy_score(
        y_validation,
        predictions
    )

    print(
        f"Threshold {threshold}: "
        f"{accuracy:.4f}"
    )

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_threshold = threshold


print(
    f"\nBest validation threshold: "
    f"{best_threshold}"
)

print(
    f"Best validation accuracy: "
    f"{best_accuracy:.4f}"
)


# --------------------------------------------------
# FINAL TEST
# --------------------------------------------------

test_probabilities = model.predict_proba(
    X_test_scaled
)

test_predictions = []

for probabilities in test_probabilities:

    home_probability = probabilities[home_index]
    draw_probability = probabilities[draw_index]
    away_probability = probabilities[away_index]

    if draw_probability >= best_threshold:
        prediction = "DRAW"

    elif home_probability >= away_probability:
        prediction = "HOME_TEAM"

    else:
        prediction = "AWAY_TEAM"

    test_predictions.append(prediction)


test_accuracy = accuracy_score(
    y_test,
    test_predictions
)


print("\nFinal test accuracy:")
print(f"{test_accuracy:.4f}")


print("\nConfusion matrix:")
print(
    confusion_matrix(
        y_test,
        test_predictions
    )
)
