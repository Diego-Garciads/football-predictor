# ⚽ Football Match Predictor

Machine learning project for predicting football match outcomes using historical data from five major European leagues.

The project collects historical match data, builds pre-match features based only on information available before each match, trains a classification model, and provides an interactive Streamlit application for making predictions.

> This is an educational and experimental project. The predictions should not be interpreted as betting advice.

---

## 📌 Project Overview

The objective of this project is to explore how machine learning can be applied to football match prediction.

The model predicts one of three possible outcomes:

- 🏠 Home win
- 🤝 Draw
- ✈️ Away win

The project was developed as a learning project focused on data collection, feature engineering, machine learning, model evaluation and deployment through a simple web application.

---

## 📊 Dataset

The data is obtained from the [football-data.org](https://www.football-data.org/) API.

The project uses matches from five European leagues:

- Spanish La Liga
- English Premier League
- German Bundesliga
- Italian Serie A
- French Ligue 1

The data includes information such as:

- Match date
- Home team
- Away team
- Match winner
- Home goals
- Away goals
- Matchday
- Competition

---

## ⚙️ Feature Engineering

The model uses information that was available before each match.

The main features are:

- **Points per game difference**
- **Recent form difference**
- **Attacking performance difference**
- **Defensive performance difference**
- **Rest days difference**
- **Elo rating difference**

Historical information is processed chronologically so that future match information is not used when creating features for previous matches.

---

## 🤖 Model

The final model is a **Logistic Regression classifier**.

Before training, numerical features are standardized using `StandardScaler`.

The data is divided chronologically into:

- 64% training
- 16% validation
- 20% testing

A chronological split is used instead of a random split because football prediction is a time-dependent problem.

The model was also compared against a simple majority-class baseline.

---

## 📈 Results

The final model achieved approximately:

**48.4% accuracy on the test set.**

This result should be interpreted carefully.

The model performs substantially better at identifying home wins than draws, while draw prediction remains a major weakness.

The results show that predicting football outcomes is a difficult problem and that relatively simple historical features are not sufficient to produce highly accurate predictions.

The purpose of this project is therefore primarily educational rather than predictive performance.

---

## 🌐 Interactive Application

The project includes a Streamlit web application.

Users can:

1. Select a home team.
2. Select an away team.
3. Generate a prediction.
4. See the estimated probability of each outcome.

The application also includes information about the model and its limitations.

To launch the application:

```bash
streamlit run src/app.py