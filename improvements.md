# Premier League Predictor — Project Roadmap
### MoSCoW Prioritisation

**Priority Key:**  
🔴 Must Have | 🟠 Should Have | 🟡 Could Have | ⚪ Won't Have (now)

---

## Data & Features

| Priority | Task | Status |
|----------|------|--------|
| 🔴 Must | Pull historical match data (football-data.co.uk) | ✅ Done |
| 🔴 Must | Add Bet365 odds as model features | ✅ Done |
| 🔴 Must | Encode implied probabilities from odds | ✅ Done |
| 🔴 Must | Rolling averages — 5-game window (pts, GF, GA) | ✅ Done |
| 🔴 Must | Win/loss/unbeaten streak features | ✅ Done |
| 🔴 Must | Upcoming fixtures (football-data.org free API) | ✅ Done |
| 🟠 Should | SQLite database instead of CSV | ⏳ Todo |
| 🟠 Should | Auto-refresh data via cron job | ⏳ Todo |
| 🟠 Should | Rolling averages — 10-game window | 🚫 Skipped (adds noise) |
| 🟡 Could | Player-level stats (goals, assists, xG) | 🚫 Skipped (no free source) |
| 🟡 Could | Referee / weather / stadium factors | ⏳ Later |

---

## Modelling & Evaluation

| Priority | Task | Status |
|----------|------|--------|
| 🔴 Must | XGBoost model (replace/benchmark Random Forest) | ⏳ Next |
| 🔴 Must | SHAP feature importance in app | ⏳ Next |
| 🟠 Should | LightGBM / CatBoost models | ⏳ Todo |
| 🟠 Should | Probability calibration (Platt scaling) | ⏳ Todo |
| 🟠 Should | Brier score + log loss evaluation | ⏳ Todo |
| 🟠 Should | Ensemble predictions (weighted combo) | ⏳ Todo |
| 🟡 Could | Betting ROI simulation on historical odds | ⏳ Later |
| 🟡 Could | Poisson distribution for score prediction | ⏳ Later |

---

## API & Deployment

| Priority | Task | Status |
|----------|------|--------|
| 🟠 Should | FastAPI backend (/predict-match endpoint) | ⏳ Todo |
| 🟠 Should | Daily script to auto-update predictions | ⏳ Todo |
| 🟡 Could | Docker containerisation | ⏳ Later |
| 🟡 Could | Cloud deployment (AWS / GCP / Heroku) | ⏳ Later |
| ⚪ Won't | Live in-play match predictions | ⏳ Later |

---

## Dashboard & UX

| Priority | Task | Status |
|----------|------|--------|
| 🔴 Must | Streamlit app — team selector + predictions | ✅ Done |
| 🔴 Must | Tabs (Predict / Fixtures / Stats) | ✅ Done |
| 🔴 Must | Prediction reasoning / explainability | ✅ Done |
| 🔴 Must | Head-to-head + form dots + goals chart | ✅ Done |
| 🟠 Should | SHAP visualisation in app | ⏳ Next |
| 🟠 Should | Toggle between models (RF vs XGBoost) | ⏳ Todo |
| 🟠 Should | Historical accuracy chart | ⏳ Todo |
| 🟡 Could | xG trend charts per team | ⏳ Later |
| 🟡 Could | User login for custom predictions | ⏳ Later |

---

## Automation & Monitoring

| Priority | Task | Status |
|----------|------|--------|
| 🟠 Should | Cron job for weekly data + model refresh | ⏳ Todo |
| 🟡 Could | MLflow / DVC model versioning | ⏳ Later |
| 🟡 Could | Model drift monitoring + alerts | ⏳ Later |
| 🟡 Could | Airflow ETL pipeline | ⏳ Later |
| ⚪ Won't | Player-level predictive modelling | ⏳ Later |
| ⚪ Won't | Multi-season trend analysis | ⏳ Later |

---

## Next Steps (Priority Order)

1. **XGBoost model** — highest accuracy gain, low effort  
2. **SHAP feature importance in app** — makes predictions explainable  
3. **SQLite database + cron auto-update** — makes it production-ready  
4. **Probability calibration** — improves trust in predictions  
5. **Toggle between models in app** — UX enhancement  
6. **FastAPI backend** — needed for scaling beyond Streamlit