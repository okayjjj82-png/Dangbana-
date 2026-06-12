import streamlit as st
import requests

# =========================
# API KEY (PUT YOUR REAL KEY HERE)
# =========================
API_KEY = "ZPVhPipznhgiFNsTVXSDuV9sdTw48PtIdRoEhb71qPGUe2g2NOEDLwjwOUAD"

HEADERS = {
    "x-apisports-key": API_KEY
}

# =========================
# GET FIXTURES
# =========================
def get_fixtures(date):
    url = f"https://v3.football.api-sports.io/fixtures?date={date}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return []

    return r.json().get("response", [])

# =========================
# TEAM PERFORMANCE PROFILE
# =========================
def get_team_data(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=8"
    r = requests.get(url, headers=HEADERS)

    games = r.json().get("response", [])

    wins = 0
    goals_for = 0
    goals_against = 0
    matches = len(games)

    if matches == 0:
        return {"wins": 0, "avg_for": 1, "avg_against": 1}

    for g in games:
        is_home = g["teams"]["home"]["id"] == team_id

        gf = g["goals"]["home"] if is_home else g["goals"]["away"]
        ga = g["goals"]["away"] if is_home else g["goals"]["home"]

        goals_for += gf
        goals_against += ga

        if gf > ga:
            wins += 1

    return {
        "wins": wins,
        "avg_for": goals_for / matches,
        "avg_against": goals_against / matches
    }

# =========================
# MATCH ANALYSIS ENGINE
# =========================
def analyze_match(home_id, away_id):
    home = get_team_data(home_id)
    away = get_team_data(away_id)

    home_power = (home["avg_for"] - away["avg_against"]) + (home["wins"] * 0.6)
    away_power = (away["avg_for"] - home["avg_against"]) + (away["wins"] * 0.6)

    home_score = 50 + home_power * 10
    away_score = 50 + away_power * 10

    total = home_score + away_score

    home_prob = (home_score / total) * 100
    away_prob = (away_score / total) * 100

    return home_prob, away_prob

# =========================
# STREAMLIT UI
# =========================
st.title("Football Match Intelligence System")

date = st.date_input("Select Date")

if st.button("Run Analysis"):
    fixtures = get_fixtures(date)

    if not fixtures:
        st.warning("No matches found or API error.")
        st.stop()

    for f in fixtures:
        home_name = f["teams"]["home"]["name"]
        away_name = f["teams"]["away"]["name"]

        home_id = f["teams"]["home"]["id"]
        away_id = f["teams"]["away"]["id"]

        home_prob, away_prob = analyze_match(home_id, away_id)

        st.subheader(f"{home_name} vs {away_name}")

        st.write(f"Home Win Probability: {home_prob:.1f}%")
        st.write(f"Away Win Probability: {away_prob:.1f}%")

        confidence = max(home_prob, away_prob)

        if confidence >= 70:
            st.success("VERY HIGH CONFIDENCE MATCH")
        elif confidence >= 60:
            st.info("MEDIUM CONFIDENCE MATCH")
        else:
            st.warning("LOW CONFIDENCE - SKIP RECOMMENDED")
