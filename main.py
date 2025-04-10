import streamlit as st
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from luca_model.streamlit_func import compute_team_elo

# Generate player list with Elo ratings
data_ratings = pd.read_csv('PADEL_ELO_RATINGS.csv')
print(list(data_ratings['Name']))
player_names = list(data_ratings['Name'])
players = dict(zip(data_ratings['Name'], data_ratings['Elo Rating']))
print(players)


def calculate_win_probability(team1_avg, team2_avg):
    """Returns the probability of Team 1 winning against Team 2."""
    diff = team1_avg - team2_avg
    prob_team1 = 1 / (1 + 10 ** (-diff / 400))
    return prob_team1, 1 - prob_team1

st.title("🎾 Padel Predictor")
st.sidebar.header("Select Players")

# Team selection
team1 = st.sidebar.multiselect("Team 1", player_names, default=player_names[:2])
team2 = st.sidebar.multiselect("Team 2", player_names, default=player_names[2:4])

if len(team1) == 2 and len(team2) == 2:
    team1_rating = compute_team_elo(players[team1[0]], players[team1[1]], alpha=0.25)
    team2_rating = compute_team_elo(players[team2[0]], players[team2[1]], alpha=0.25)
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
    rating_df = (
        pd.DataFrame(players.items(), columns=["Player", "Rating"])
        .sort_values(by="Rating", ascending=False)
        .reset_index(drop=True)
    )
    rating_df.index += 1

    st.table(rating_df)
    
    # Rating history simulation
    # st.subheader("📊 Rating Progression")
    # for player in players.keys():
    #     plt.figure(figsize=(6, 3))
    #     history = [players[player] + random.randint(-50, 50) for _ in range(10)]
    #     plt.plot(history, label=player, marker='o')
    #     plt.xlabel("Games")
    #     plt.ylabel("Elo Rating")
    #     plt.title(f"Rating Progression - {player}")
    #     plt.legend()
    #     st.pyplot(plt)
else:
    st.error("Select exactly two players for each team!")

from itertools import combinations, permutations
import datetime


import datetime
from itertools import combinations
from collections import defaultdict
import random
import math


# === UI ===
st.title("🎾 Padel Match Optimizer")
available_players = st.multiselect("Available Players", player_names, default=player_names[:6])
game_day = st.date_input("Game Day", value=datetime.date.today())
total_matches_today = st.number_input("🧮 Matches to schedule", min_value=1, max_value=30, value=10, step=1)

# === Генерация всех возможных матчей ===
def generate_all_possible_matches(players_list, rating_dict):
    all_matches = set()
    match_list = []

    for four in combinations(players_list, 4):
        four = list(four)
        for team1 in combinations(four, 2):
            team2 = tuple(p for p in four if p not in team1)
            sorted_teams = tuple(sorted([tuple(sorted(team1)), tuple(sorted(team2))]))
            if sorted_teams in all_matches:
                continue
            all_matches.add(sorted_teams)

            team1, team2 = sorted_teams
            r1 = compute_team_elo(rating_dict[team1[0]], rating_dict[team1[1]])
            r2 = compute_team_elo(rating_dict[team2[0]], rating_dict[team2[1]])
            prob1, prob2 = calculate_win_probability(r1, r2)

            match_list.append({
                'team1': team1,
                'team2': team2,
                'players': set(team1 + team2),
                'prob1': round(prob1 * 100, 2),
                'prob2': round(prob2 * 100, 2),
                'diff': round(abs(prob1 - prob2) * 100, 2)
            })

    return sorted(match_list, key=lambda x: x['diff'])

# === Жадный выбор матчей с минимальным дисбалансом по игрокам ===
def pick_balanced_matches(all_matches, players, total_matches):
    selected_matches = []
    game_count = defaultdict(int)

    for match in all_matches:
        if len(selected_matches) == total_matches:
            break

        if all(game_count[p] <= total_matches * 4 // len(players) for p in match['players']):
            selected_matches.append(match)
            for p in match['players']:
                game_count[p] += 1

    return selected_matches

# === Основной вызов ===
if len(available_players) >= 4:
    all_matches = generate_all_possible_matches(available_players, players)
    best_matches = pick_balanced_matches(all_matches, available_players, total_matches_today)

    if best_matches:
        st.success(f"🎯 Generated {len(best_matches)} optimized matches")

        for i, match in enumerate(best_matches, 1):
            team1 = f"{match['team1'][0]} & {match['team1'][1]}"
            team2 = f"{match['team2'][0]} & {match['team2'][1]}"
            st.markdown(
                f"""
                <div style='background-color: #222; padding: 20px; margin-bottom: 20px; border-radius: 15px; color: white;'>
                    <h4 style='text-align:center;'>Match {i}</h4>
                    <table style='width:100%; text-align: center; font-size: 20px; font-weight: bold;'>
                        <tr style='background-color:#333;'>
                            <td style='padding: 10px; color: #00ff88;'>{team1}</td>
                            <td style='padding: 10px; color: #3399ff;'>{team2}</td>
                        </tr>
                        <tr>
                            <td style='padding: 10px;'>Win %: {match['prob1']}%</td>
                            <td style='padding: 10px;'>Win %: {match['prob2']}%</td>
                        </tr>
                        <tr style='background-color:#444;'>
                            <td colspan='2'>⚖️ Difference: {match['diff']}%</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True
            )

        # Подсчёт игр на игрока
        count_games = defaultdict(int)
        for match in best_matches:
            for p in match['players']:
                count_games[p] += 1

        df_stats = pd.DataFrame([
            {"Player": p, "Games Played": count_games[p]} for p in available_players
        ]).sort_values(by="Games Played", ascending=False)

        st.subheader("📊 Player Game Count")
        st.table(df_stats)

    else:
        st.warning("❌ Could not find a valid match combination.")
else:
    st.info("ℹ️ Please select at least 4 players.")