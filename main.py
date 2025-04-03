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
    team1_avg = np.mean([players[p] for p in team1])
    team2_avg = np.mean([players[p] for p in team2])
    prob_team1, prob_team2 = calculate_win_probability(team1_avg, team2_avg)
    
    st.subheader("📊 Selected Teams")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Team 1**")
        for p in team1:
            st.write(f"{p}: {players[p]}")
        st.write(f"Average rating: {team1_avg:.1f}")
    
    with col2:
        st.write("**Team 2**")
        for p in team2:
            st.write(f"{p}: {players[p]}")
        st.write(f"Average rating: {team2_avg:.1f}")
    
    odds_team1 = 1 / prob_team1
    odds_team2 = 1 / prob_team2
    
    st.subheader("📈 Match Prediction")
    st.write(f"**Team 1 Win Probability:** {prob_team1 * 100:.2f}% (Odds {odds_team1:.2f})")
    st.write(f"**Team 2 Win Probability:** {prob_team2 * 100:.2f}% (Odds {odds_team2:.2f})")
    
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