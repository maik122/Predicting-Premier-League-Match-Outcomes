import streamlit as st
import pandas as pd
import joblib

# ─────────────────────────────
# 1. Load data + model
# ─────────────────────────────
@st.cache_data
def load_data():
    matches = pd.read_csv("matches_all.csv")
    matches["Date"] = pd.to_datetime(matches["Date"])
    matches["Team_Code"]     = matches["Home"].astype("category").cat.codes
    matches["Opponent_Code"] = matches["Away"].astype("category").cat.codes
    matches["Venue_Code"]    = matches["Venue"].fillna("Unknown").astype("category").cat.codes
    matches["Day_Code"]      = matches["Date"].dt.dayofweek
    matches["Hour"]          = 15
    matches["Points"]        = matches["Result"].map({"H": 3, "D": 1, "A": 0})
    matches["GF"]            = matches["HomeGoals"]
    matches["GA"]            = matches["AwayGoals"]
    matches["OddsH"]         = matches["OddsH"].fillna(matches["OddsH"].mean())
    matches["OddsD"]         = matches["OddsD"].fillna(matches["OddsD"].mean())
    matches["OddsA"]         = matches["OddsA"].fillna(matches["OddsA"].mean())
    raw_sum = 1/matches["OddsH"] + 1/matches["OddsD"] + 1/matches["OddsA"]
    matches["ProbH"] = (1/matches["OddsH"]) / raw_sum
    matches["ProbD"] = (1/matches["OddsD"]) / raw_sum
    matches["ProbA"] = (1/matches["OddsA"]) / raw_sum
    return matches

@st.cache_resource
def load_model():
    model      = joblib.load("models/premier_league_model.pkl")
    predictors = joblib.load("models/predictors.pkl")
    return model, predictors

matches         = load_data()
model, predictors = load_model()

# ─────────────────────────────
# 2. UI
# ─────────────────────────────
st.title("Premier League Match Predictor ⚽")

home_team = st.selectbox("Home Team", sorted(matches["Home"].unique()))
away_team = st.selectbox("Away Team", sorted(matches["Away"].unique()))

# Get codes
team_cats     = matches["Home"].astype("category").cat.categories
opponent_cats = matches["Away"].astype("category").cat.categories
team_code     = list(team_cats).index(home_team)     if home_team in list(team_cats)     else 0
opponent_code = list(opponent_cats).index(away_team) if away_team in list(opponent_cats) else 0

# Average odds for this matchup
matchup = matches[(matches["Home"] == home_team) & (matches["Away"] == away_team)]
prob_h = matchup["ProbH"].mean() if not matchup.empty else matches["ProbH"].mean()
prob_d = matchup["ProbD"].mean() if not matchup.empty else matches["ProbD"].mean()
prob_a = matchup["ProbA"].mean() if not matchup.empty else matches["ProbA"].mean()

# Rolling form
home_form = matches[matches["Home"] == home_team].tail(5)
pts5 = home_form["Points"].mean() if not home_form.empty else 1.0
gf5  = home_form["GF"].mean()     if not home_form.empty else 1.0
ga5  = home_form["GA"].mean()     if not home_form.empty else 1.0

if st.button("Predict Outcome"):
    input_dict = {
        "Team_Code":      team_code,
        "Opponent_Code":  opponent_code,
        "Venue_Code":     0,
        "Day_Code":       5,
        "Hour":           15,
        "Points_form5":   pts5,
        "GF_form5":       gf5,
        "GA_form5":       ga5,
        "ProbH":          prob_h,
        "ProbD":          prob_d,
        "ProbA":          prob_a,
        "WinStreak":      0,
        "LossStreak":     0,
        "UnbeatenStreak": 0,
    }
    input_data = pd.DataFrame([input_dict])[predictors]  # correct column order

    prediction = model.predict(input_data)[0]
    prob       = model.predict_proba(input_data)[0][1]

    if prediction == 1:
        st.success(f"{home_team} predicted to **WIN** 🏆 (Confidence: {prob:.0%})")
    else:
        st.error(f"{home_team} predicted to **NOT WIN** ❌ (Confidence: {1-prob:.0%})")