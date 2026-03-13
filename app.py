import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import numpy as np

# ─────────────────────────────
# Page config
# ─────────────────────────────
st.set_page_config(
    page_title="PL Predictor",
    page_icon="⚽",
    layout="wide",
)

# ─────────────────────────────
# Custom CSS
# ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');

.stApp { background-color: #0a0e1a; color: #f0f0f0; }
header { visibility: hidden; }

.big-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    letter-spacing: 4px;
    color: #ffffff;
    line-height: 1;
}
.title-accent { color: #00d4aa; }

.stat-card {
    background: #141929;
    border: 1px solid #1e2840;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.stat-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #00d4aa;
    line-height: 1;
}
.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: #6b7a99;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
}

.form-dot-W { display:inline-block; width:18px; height:18px; border-radius:50%; background:#00d4aa; margin:2px; }
.form-dot-D { display:inline-block; width:18px; height:18px; border-radius:50%; background:#f59e0b; margin:2px; }
.form-dot-L { display:inline-block; width:18px; height:18px; border-radius:50%; background:#ef4444; margin:2px; }

div.stButton > button {
    background: linear-gradient(135deg, #00d4aa, #0099ff);
    color: #0a0e1a;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem;
    letter-spacing: 3px;
    border: none;
    border-radius: 8px;
    padding: 14px 40px;
    width: 100%;
    cursor: pointer;
}

.result-win {
    background: linear-gradient(135deg, #00d4aa22, #00d4aa11);
    border: 1px solid #00d4aa;
    border-radius: 12px;
    padding: 28px;
    text-align: center;
}
.result-loss {
    background: linear-gradient(135deg, #ef444422, #ef444411);
    border: 1px solid #ef4444;
    border-radius: 12px;
    padding: 28px;
    text-align: center;
}
.result-text { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; letter-spacing: 3px; }
.confidence-text { font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #6b7a99; margin-top: 8px; }
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 3px;
    color: #6b7a99;
    border-bottom: 1px solid #1e2840;
    padding-bottom: 8px;
    margin-bottom: 16px;
}
.stSelectbox label { color: #6b7a99 !important; font-size: 0.8rem !important; letter-spacing: 1px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────
# Load data + model
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

matches           = load_data()
model, predictors = load_model()
finished          = matches[matches["Status"] == "FT"]


# ─────────────────────────────
# Header
# ─────────────────────────────
st.markdown("""
<div style='padding: 24px 0 32px 0;'>
    <div class='big-title'>PREMIER LEAGUE<br><span class='title-accent'>MATCH PREDICTOR</span></div>
    <div style='font-family:Inter; font-size:0.9rem; color:#6b7a99; margin-top:8px;'>
        Random Forest · 4 seasons · 1520 matches · 66% accuracy
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────
# Top stats
# ─────────────────────────────
total  = len(finished)
home_w = len(finished[finished["Result"] == "H"])
draws  = len(finished[finished["Result"] == "D"])
away_w = len(finished[finished["Result"] == "A"])

c1, c2, c3, c4 = st.columns(4)
for col, num, label in zip(
    [c1, c2, c3, c4],
    [total, f"{home_w/total:.0%}", f"{draws/total:.0%}", "66%"],
    ["Matches Analysed", "Home Win Rate", "Draw Rate", "Model Accuracy"]
):
    with col:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number'>{num}</div>
            <div class='stat-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────
# Main layout
# ─────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown("<div class='section-header'>SELECT FIXTURE</div>", unsafe_allow_html=True)
    home_team = st.selectbox("Home Team", sorted(finished["Home"].unique()))
    away_team = st.selectbox("Away Team", sorted(finished["Away"].unique()))

    # Head to head
    h2h = finished[((finished["Home"] == home_team) & (finished["Away"] == away_team))]
    if not h2h.empty:
        h2h_hw = len(h2h[h2h["Result"] == "H"])
        h2h_d  = len(h2h[h2h["Result"] == "D"])
        h2h_aw = len(h2h[h2h["Result"] == "A"])
        st.markdown(f"""
        <div style='margin-top:20px;'>
        <div class='section-header'>HEAD TO HEAD ({len(h2h)} games)</div>
        <div style='display:flex; gap:12px;'>
            <div class='stat-card' style='flex:1'>
                <div class='stat-number' style='color:#00d4aa'>{h2h_hw}</div>
                <div class='stat-label'>{home_team[:12]}</div>
            </div>
            <div class='stat-card' style='flex:1'>
                <div class='stat-number' style='color:#f59e0b'>{h2h_d}</div>
                <div class='stat-label'>Draws</div>
            </div>
            <div class='stat-card' style='flex:1'>
                <div class='stat-number' style='color:#ef4444'>{h2h_aw}</div>
                <div class='stat-label'>{away_team[:12]}</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("⚡  PREDICT OUTCOME")

with right:
    # Form dots
    st.markdown("<div class='section-header'>RECENT FORM — LAST 5</div>", unsafe_allow_html=True)

    def get_form(team):
        games = finished[(finished["Home"] == team) | (finished["Away"] == team)].sort_values("Date").tail(5)
        results = []
        for _, row in games.iterrows():
            if row["Home"] == team:
                results.append("W" if row["Result"] == "H" else ("D" if row["Result"] == "D" else "L"))
            else:
                results.append("W" if row["Result"] == "A" else ("D" if row["Result"] == "D" else "L"))
        return results

    for team in [home_team, away_team]:
        form = get_form(team)
        dots = "".join([f"<span class='form-dot-{r}'></span>" for r in form])
        st.markdown(f"""
        <div style='margin-bottom:16px;'>
            <div style='font-family:Inter; font-size:0.78rem; color:#6b7a99; margin-bottom:6px; letter-spacing:1px; text-transform:uppercase;'>{team}</div>
            {dots}
        </div>""", unsafe_allow_html=True)

    # Goals bar chart
    st.markdown("<div class='section-header' style='margin-top:16px;'>AVG GOALS SCORED — LAST 5</div>", unsafe_allow_html=True)

    def avg_goals(team):
        g = finished[(finished["Home"] == team) | (finished["Away"] == team)].tail(5)
        return round(np.mean([row["HomeGoals"] if row["Home"] == team else row["AwayGoals"] for _, row in g.iterrows()]), 2)

    h_g, a_g = avg_goals(home_team), avg_goals(away_team)
    fig, ax = plt.subplots(figsize=(5, 1.6))
    fig.patch.set_facecolor("#141929")
    ax.set_facecolor("#141929")
    bars = ax.barh([away_team[:16], home_team[:16]], [a_g, h_g], color=["#ef4444","#00d4aa"], height=0.45)
    for bar, val in zip(bars, [a_g, h_g]):
        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2, f"{val}", va="center", color="#f0f0f0", fontsize=10, fontweight="bold")
    ax.set_xlim(0, max(h_g, a_g)*1.6+0.3)
    ax.tick_params(colors="#6b7a99", labelsize=8)
    ax.spines[:].set_visible(False)
    ax.xaxis.set_visible(False)
    st.pyplot(fig, use_container_width=True)
    plt.close()


# ─────────────────────────────
# Prediction
# ─────────────────────────────
if predict_btn:
    team_cats     = finished["Home"].astype("category").cat.categories
    opponent_cats = finished["Away"].astype("category").cat.categories
    team_code     = list(team_cats).index(home_team)     if home_team in list(team_cats)     else 0
    opponent_code = list(opponent_cats).index(away_team) if away_team in list(opponent_cats) else 0

    matchup = finished[(finished["Home"] == home_team) & (finished["Away"] == away_team)]
    prob_h = matchup["ProbH"].mean() if not matchup.empty else finished["ProbH"].mean()
    prob_d = matchup["ProbD"].mean() if not matchup.empty else finished["ProbD"].mean()
    prob_a = matchup["ProbA"].mean() if not matchup.empty else finished["ProbA"].mean()

    hf = finished[finished["Home"] == home_team].tail(5)
    pts5 = hf["Points"].mean() if not hf.empty else 1.0
    gf5  = hf["GF"].mean()     if not hf.empty else 1.0
    ga5  = hf["GA"].mean()     if not hf.empty else 1.0

    input_data = pd.DataFrame([{
        "Team_Code": team_code, "Opponent_Code": opponent_code,
        "Venue_Code": 0, "Day_Code": 5, "Hour": 15,
        "Points_form5": pts5, "GF_form5": gf5, "GA_form5": ga5,
        "ProbH": prob_h, "ProbD": prob_d, "ProbA": prob_a,
        "WinStreak": 0, "LossStreak": 0, "UnbeatenStreak": 0,
    }])[predictors]

    prediction = model.predict(input_data)[0]
    prob       = model.predict_proba(input_data)[0][1]

    st.markdown("<br>", unsafe_allow_html=True)
    if prediction == 1:
        st.markdown(f"""<div class='result-win'>
            <div class='result-text' style='color:#00d4aa'>🏆 {home_team.upper()} TO WIN</div>
            <div class='confidence-text'>Model confidence: {prob:.0%}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class='result-loss'>
            <div class='result-text' style='color:#ef4444'>❌ {home_team.upper()} NOT FAVOURED</div>
            <div class='confidence-text'>Model confidence: {1-prob:.0%} against</div>
        </div>""", unsafe_allow_html=True)

# Probability cards
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>OUTCOME PROBABILITIES</div>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number' style='color:#00d4aa'>{prob_h:.0%}</div>
            <div class='stat-label'>🏠 {home_team} Win</div>
        </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number' style='color:#f59e0b'>{prob_d:.0%}</div>
            <div class='stat-label'>🤝 Draw</div>
        </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number' style='color:#ef4444'>{prob_a:.0%}</div>
            <div class='stat-label'>✈️ {away_team} Win</div>
        </div>""", unsafe_allow_html=True)
        
        # Reasoning
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>WHY THIS PREDICTION?</div>", unsafe_allow_html=True)

    reasons = []

    # Form comparison
    away_form_df = finished[finished["Away"] == away_team].tail(5)
    away_pts5 = away_form_df["Points"].mean() if not away_form_df.empty else 1.0

    if pts5 > away_pts5:
        reasons.append(f"✅ **{home_team}** are in better recent form ({pts5:.1f} pts/game vs {away_pts5:.1f})")
    elif away_pts5 > pts5:
        reasons.append(f"⚠️ **{away_team}** are in better recent form ({away_pts5:.1f} pts/game vs {pts5:.1f})")
    else:
        reasons.append(f"➖ Both teams in similar form ({pts5:.1f} pts/game)")

    # Bookmaker odds
    if prob_h > prob_a:
        reasons.append(f"✅ Bookmakers favour **{home_team}** to win ({prob_h:.0%} implied probability)")
    elif prob_a > prob_h:
        reasons.append(f"⚠️ Bookmakers favour **{away_team}** to win ({prob_a:.0%} implied probability)")

    # Goals form
    if gf5 > a_g:
        reasons.append(f"✅ **{home_team}** scoring more ({gf5:.1f} goals/game vs {a_g:.1f})")
    elif a_g > gf5:
        reasons.append(f"⚠️ **{away_team}** scoring more ({a_g:.1f} goals/game vs {gf5:.1f})")

    # Head to head
    if not h2h.empty:
        if h2h_hw > h2h_aw:
            reasons.append(f"✅ **{home_team}** lead the head to head ({h2h_hw}W {h2h_d}D {h2h_aw}L)")
        elif h2h_aw > h2h_hw:
            reasons.append(f"⚠️ **{away_team}** lead the head to head ({h2h_aw}W {h2h_d}D {h2h_hw}L)")
        else:
            reasons.append(f"➖ Head to head is evenly matched ({h2h_hw}W {h2h_d}D {h2h_aw}L)")

    # Home advantage
    home_win_rate = len(finished[finished["Result"] == "H"]) / len(finished)
    reasons.append(f"✅ Home advantage — {home_win_rate:.0%} of PL games are won by the home team")

    for r in reasons:
        st.markdown(r)