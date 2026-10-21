import streamlit as st
import pandas as pd

from predict import predict_match


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Football Match Predictor",
    page_icon="⚽",
    layout="centered"
)


# ============================================================
# LOAD TEAMS
# ============================================================

df = pd.read_csv("data/features.csv")

teams = sorted(
    set(df["home_team"]) |
    set(df["away_team"])
)


# ============================================================
# TITLE
# ============================================================

st.title("⚽ Football Match Predictor")

st.markdown(
    "### Predict the outcome of a football match"
)

st.write(
    "Select two teams and estimate the probability of "
    "a home win, draw or away win using a machine learning model."
)

st.divider()


# ============================================================
# TEAM SELECTION
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("🏠 Home team")

    home_team = st.selectbox(
        "Select the home team",
        teams,
        key="home"
    )


with col2:

    st.subheader("✈️ Away team")

    away_team = st.selectbox(
        "Select the away team",
        teams,
        key="away"
    )


st.write("")


# ============================================================
# PREDICT BUTTON
# ============================================================

predict_button = st.button(
    "⚽ Predict match",
    use_container_width=True
)


if predict_button:

    if home_team == away_team:

        st.warning(
            "Please select two different teams."
        )

    else:

        result = predict_match(
            home_team,
            away_team
        )


        if result is None:

            st.error(
                "One or both teams were not found in the dataset."
            )

        else:

            st.divider()

            # ------------------------------------------------
            # MAIN PREDICTION
            # ------------------------------------------------

            prediction = result["prediction"]

            if prediction == "HOME_TEAM":

                prediction_text = (
                    f"🏠 {home_team} is the most likely winner"
                )

            elif prediction == "AWAY_TEAM":

                prediction_text = (
                    f"✈️ {away_team} is the most likely winner"
                )

            else:

                prediction_text = (
                    "🤝 A draw is the most likely outcome"
                )


            st.success(
                prediction_text
            )


            # ------------------------------------------------
            # PROBABILITIES
            # ------------------------------------------------

            st.subheader("Match probabilities")


            home_probability = (
                result["home_probability"]
            )

            draw_probability = (
                result["draw_probability"]
            )

            away_probability = (
                result["away_probability"]
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "🏠 Home win",
                    f"{home_probability:.1%}"
                )


            with col2:

                st.metric(
                    "🤝 Draw",
                    f"{draw_probability:.1%}"
                )


            with col3:

                st.metric(
                    "✈️ Away win",
                    f"{away_probability:.1%}"
                )


            # ------------------------------------------------
            # PROBABILITY BARS
            # ------------------------------------------------

            st.write("")


            st.write(
                f"🏠 **{home_team}**"
            )

            st.progress(
                home_probability
            )


            st.write(
                f"🤝 **Draw**"
            )

            st.progress(
                draw_probability
            )


            st.write(
                f"✈️ **{away_team}**"
            )

            st.progress(
                away_probability
            )


# ============================================================
# ABOUT THE MODEL
# ============================================================

st.divider()

with st.expander("ℹ️ About the model"):

    st.write(
        "The model is trained using historical football "
        "matches from five European leagues."
    )

    st.write(
        "It uses team performance features such as points "
        "per game, recent form, attacking and defensive "
        "performance, rest days and Elo rating."
    )

    st.write(
        "The final model is a Logistic Regression classifier "
        "evaluated using a chronological train/validation/test split."
    )

    st.caption(
        "The predictions are experimental and should not be "
        "interpreted as betting advice."
    )