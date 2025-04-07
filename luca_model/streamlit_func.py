"""Defining 3 functions:
    1. Params: Elo of the players
       Output: Elo of the team
       
    2. Params: Elo of the teams
       Output: Probabilities of winning
       
    3. Params: Probabilities of winning
       Output: Odds
"""

def compute_team_elo(player1_elo, player2_elo, alpha=0.25):
    
    stronger = max(player1_elo, player2_elo)
    weaker = min(player1_elo, player2_elo)
    
    #Compute penalty based on skill gap
    penalty = alpha * (stronger - weaker)
    team_elo = (stronger + weaker) / 2 - penalty
    
    return round(team_elo)

def percentage_of_winning(team1_elo, team2_elo, target):
    
    #Computing probabilities of winning for each team
    if abs(team1_elo - team2_elo) > 400:
        if team1_elo > team2_elo:
            team2_elo = team1_elo - 400
        else:
            team1_elo = team2_elo - 400
    
    team1_to_win = round(1 / (1 + 10 ** ((team2_elo - team1_elo) / 400)), 2)
    team2_to_win = 1 - team1_to_win
    
    team1_to_win = int(team1_to_win*100)
    team2_to_win = int(team2_to_win*100)
    
    return team1_to_win, team2_to_win


def odds(perc_team1, perc_team2):
    
    odds_team1 = round(1 / (perc_team1 / 100), 2)
    odds_team2 = round(1 / (perc_team2 / 100), 2)
    
    return odds_team1, odds_team2