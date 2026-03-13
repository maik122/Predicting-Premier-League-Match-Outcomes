# Case Study: Predicting Premier League Match Outcomes

## 1. Why This Project?
Football is unpredictable — but can data tell us when a team is likely to win?

This project explores whether **machine learning can predict Premier League match results** using **match data from 2021 to the present**, including upcoming fixtures.

The aim is to demonstrate a **full ML workflow**:
- Collect messy, real-world football data
- Clean and engineer meaningful features
- Train and evaluate machine learning models
- Communicate results clearly through visuals and an interactive app

---

## 2. Data Collection

- **Historical results & odds:** football-data.co.uk (2021–present)  
- **Upcoming fixtures:** football-data.co.uk
- Combined dataset includes **finished matches and scheduled fixtures**, cleaned and standardized  
- Team names harmonized (e.g., "Man United" → "Manchester United")  
- Features include: team, opponent, venue, rolling averages, streaks, kickoff time, Bet365 odds, and season

Example snippet to combine and save data:
combined = pd.concat([historical, upcoming], ignore_index=True)
combined = combined.drop_duplicates(subset=["Date", "Home", "Away"])
combined.to_csv("matches_all.csv", index=False)

---

## 3. Feature Engineering

- **Team_Code** – numeric team identifier  
- **Opponent_Code** – proxy for team strength  
- **Venue_Code** – home/away  
- **Day_Code / Hour** – kickoff day and time  
- **Rolling averages** – points, goals for/against (5-game window)  
- **Streaks** – win, loss, unbeaten  
- **Betting probabilities** – implied from odds (ProbH, ProbD, ProbA)  
- Missing scores marked as **upcoming** for scheduled matches

---

## 4. Modelling

**Current baseline:**  
- **Random Forest Classifier** trained on engineered features  
- Evaluated with **accuracy**, **confusion matrix**, and **classification metrics**

**Future roadmap (MoSCoW prioritised):**  
- Upgrade to **XGBoost, LightGBM, CatBoost**  
- Ensemble predictions  
- Probability calibration (Platt scaling / isotonic regression)  
- SHAP feature importance for interpretability

---

## 5. Results

**Random Forest Classifier**  
- **Accuracy:** 0.6619  
- **Key predictors:**  
```
["Team_Code", "Opponent_Code", "Venue_Code", "Hour", "Day_Code",
"Points_form5", "GF_form5", "GA_form5",
"ProbH", "ProbD", "ProbA",
"WinStreak", "LossStreak", "UnbeatenStreak"]
```

**Insight:** Machine learning captures some predictive signal, but football remains highly unpredictable.

---

## 6. Interactive Demo

A **Streamlit app** allows exploring predictions interactively:
- Select two Premier League teams  
- Choose venue and kickoff time  
- View predicted probabilities for Win / Draw / Loss  

Run locally:
```
pip install -r requirements.txt
streamlit run app.py
```
---

## 7. Roadmap & Next Steps (MoSCoW Prioritisation)

### Must-Have
- Upgrade to **XGBoost model**  
- Add **SHAP feature importance** in app  
- SQLite database + automated cron updates  
- Streamlit enhancements (tabs, prediction reasoning, charts)  

### Should-Have
- LightGBM / CatBoost models  
- Probability calibration  
- Ensemble predictions  
- FastAPI backend for scalable predictions  

### Could-Have
- Player-level stats (goals, assists, xG)  
- Referee / weather / stadium factors  
- xG trend charts per team  
- Cloud deployment (AWS/GCP/Heroku)  
- User login for personalised predictions  

### Won’t-Have (for now)
- Live in-play predictions  
- Multi-season long-term trend analysis  
- Player-level predictive modelling