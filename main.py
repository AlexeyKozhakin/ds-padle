import streamlit as st
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt

# Generate player list with Elo ratings
player_names = ["Harald", "Alexey", "Matthew", "Luca", "Slava", "Miruna", "Angela", "Hikmet", "Ekaterina"]
players = {name: random.randint(1200, 1800) for name in player_names}

def calculate_win_probability(team1_avg, team2_avg):
    """Returns the probability of Team 1 winning against Team 2."""
    diff = team1_avg - team2_avg
    prob_team1 = 1 / (1 + 10 ** (-diff / 400))
    return prob_team1, 1 - prob_team1

st.title("🎾 Padel Predictor")
st.sidebar.header("Select Players")

# Team selection
team1 = st.sidebar.multiselect("Team 1", list(players.keys()), default=list(players.keys())[:2])
team2 = st.sidebar.multiselect("Team 2", list(players.keys()), default=list(players.keys())[2:4])

if len(team1) == 2 and len(team2) == 2:
    team1_rating = round(np.mean([players[p] for p in team1]))
    team2_rating = round(np.mean([players[p] for p in team2]))
    prob_team1, prob_team2 = calculate_win_probability(team1_rating, team2_rating)
    odds_team1 = round(1 / prob_team1, 2)
    odds_team2 = round(1 / prob_team2, 2)
    
    st.subheader("📊 Selected Teams")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='text-align: center; color: green;'>Team 1</h3>", unsafe_allow_html=True)
        for p in team1:
            st.write(f"<b>{p}</b>: {players[p]}", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>Team Rating: {team1_rating}</h4>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3 style='text-align: center; color: blue;'>Team 2</h3>", unsafe_allow_html=True)
        for p in team2:
            st.write(f"<b>{p}</b>: {players[p]}", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>Team Rating: {team2_rating}</h4>", unsafe_allow_html=True)
    
    st.subheader("🔥 Betting Odds & Win Probability 🔥")
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #1e1e1e; padding: 20px; border-radius: 10px; color: white;'>
            <h2 style='color: #ffcc00;'>Match Betting Odds</h2>
            <table style='width:100%; text-align: center; font-size: 22px; font-weight: bold;'>
                <tr>
                    <td style='padding: 15px; color: green;'>Team 1</td>
                    <td style='padding: 15px; color: blue;'>Team 2</td>
                </tr>
                <tr>
                    <td style='padding: 15px; background-color: #333; border-radius: 5px;'>{odds_team1}</td>
                    <td style='padding: 15px; background-color: #333; border-radius: 5px;'>{odds_team2}</td>
                </tr>
                <tr>
                    <td style='padding: 15px;'>Win Probability: {round(prob_team1 * 100)}%</td>
                    <td style='padding: 15px;'>Win Probability: {round(prob_team2 * 100)}%</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("📌 Current Player Ratings")
    rating_df = pd.DataFrame(players.items(), columns=["Player", "Rating"]).sort_values(by="Rating", ascending=False)
    st.table(rating_df)
    
    # Rating history simulation
    st.subheader("📊 Rating Progression")
    for player in players.keys():
        plt.figure(figsize=(6, 3))
        history = [players[player] + random.randint(-50, 50) for _ in range(10)]
        plt.plot(history, label=player, marker='o')
        plt.xlabel("Games")
        plt.ylabel("Elo Rating")
        plt.title(f"Rating Progression - {player}")
        plt.legend()
        st.pyplot(plt)
else:
    st.error("Select exactly two players for each team!")
