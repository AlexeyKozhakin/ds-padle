import pandas as pd
import math


def compute_team_elo(player1_elo, player2_elo, alpha=0.25):
    
    """ 
        Compute the team ELO considering unbalanced teams.
        Some experiments with alpha needed.
        
        --- Parameters ---
        player1_elo: int
        player2_elo: int
        alpha: float (default = 0.25)
        
        --- Returns ---
        team_elo: int
    """
    
    stronger = max(player1_elo, player2_elo)
    weaker = min(player1_elo, player2_elo)
    
    #Compute penalty based on skill gap
    penalty = alpha * (stronger - weaker)
    team_elo = (stronger + weaker) / 2 - penalty
    
    return round(team_elo)



def expected_score(team1_elo, team2_elo, target):
    
    """
        Define the expected score based on the teams' ELO.
        Uses the chess formula to compute win probabilities
        and then predicts the expected score.
        
        --- Parameters ---
        team1_elo: int
        team2_elo: int
        target: int (final target score)
        
        --- Returns ---
        team1_score: int
        team2_score: int
    """
    
    #Computing probabilities of winning for each team
    if abs(team1_elo - team2_elo) > 400:
        if team1_elo > team2_elo:
            team2_elo = team1_elo - 400
        else:
            team1_elo = team2_elo - 400
    
    team1_to_win = round(1 / (1 + 10 ** ((team2_elo - team1_elo) / 400)), 2)
    team2_to_win = round(1 - team1_to_win, 2)
    
    #Calculating expected score
    team1_score = math.ceil(target / max(team1_to_win, team2_to_win) * team1_to_win)
    team2_score = math.ceil(target / max(team1_to_win, team2_to_win) * team2_to_win) 
    
    return team1_score, team2_score



def compare_scores(score_team1, score_team2, expected_score):
    
    """
        Calculate the delta from the expected and actual score for team1.
        
        --- Parameters ---
        score_team1: int
        score_team2: int
        expected_score: tuple (expected scores for both teams)
        
        --- Returns ---
        val: int (delta adjustment for ELO update)
    """
    
    actual_score = (score_team1, score_team2)
    delta = tuple(x - y for x, y in zip(expected_score, actual_score)) 
    
    val = - delta[0] + delta[1]
    
    return val


 
def elo_variation(elo_team1, elo_team2, score, target=8, beta=7):
    
    """
        Compute the ELO variation based on expected vs actual score.
        
        --- Parameters ---
        elo_team1: int
        elo_team2: int
        score: tuple (actual scores for both teams)
        target: int (default = 8) 
        beta: int (default = 7, controls the impact of deviation)
        
        --- Returns ---
        team1_var: int (ELO variation for team1)
    """
    
    exp_score = expected_score(elo_team1, elo_team2, target)
    
    variation = compare_scores(score[0], score[1], exp_score)

    team1_var = variation * beta
    
    return int(team1_var)
    


def read_elo_ratings(csv_path):
    
    """
        Read player names from CSV and initialize ELO ratings.
        
        --- Parameters ---
        csv_path: str (path to CSV file)
        
        --- Returns ---
        data: DataFrame (match data)
        ratings: dict (player ELO ratings initialized at 1800)
        games_count: dict (games played per player, initialized at 0)
    """

    data = pd.read_csv(csv_path)  # Read CSV
    ratings = {player: 1800 for player in data["List of players"].dropna()}
    games_count = {player: 0 for player in data["List of players"].dropna()}
    
    columns_to_keep = ["player 1a", "player 1b", "score team a", "score team b", "player 2a", "player 2b"]
    data = data[columns_to_keep].dropna()
 
    return data, ratings, games_count



def update_ratings(data, ratings, games_count):
    
    """
        Update the ELO ratings for each player based on match results.
        
        --- Parameters ---
        data: DataFrame (match results)
        ratings: dict (current ELO ratings)
        games_count: dict (number of games played per player)
        
        --- Returns ---
        ratings: dict (updated ELO ratings)
        games_count: dict (updated game counts)
    """
    
    for _, row in data.iterrows():
        team1 = (row['player 1a'], row['player 1b'])
        team2 = (row['player 2a'], row['player 2b'])
        score_team1 = (row['score team a'])
        score_team2 = (row['score team b'])
        elo_team1 = compute_team_elo(ratings[team1[0]], ratings[team1[1]])
        elo_team2 = compute_team_elo(ratings[team2[0]], ratings[team2[1]])
        team1_var = elo_variation(elo_team1, elo_team2, (score_team1, score_team2), target=8, beta=7)
        team2_var = - team1_var
        for team, team_var in [(team1, team1_var), (team2, team2_var)]:
            for player in team:
                ratings[player] += int(team_var / 7 * 17) if games_count[player] < 10 \
                                   else (int(team_var / 7 * 13) if games_count[player] < 20 else team_var)
                games_count[player] += 1
                
    return ratings, games_count



def create_elo_rating_file(ratings, games_count):
    
    """
        Create and save the ELO ratings file.
        
        --- Parameters ---
        ratings: dict (player ELO ratings)
        games_count: dict (number of games played per player)
        
        --- Returns ---
        elo_data: dataframe (elo ratings data)
    """
    
    elo_data = pd.DataFrame({
        'Name': list(ratings.keys()),
        'Elo Rating': list(ratings.values()),
        'Games': [games_count[name] for name in ratings]
    })
    
    elo_data = elo_data[elo_data['Games'] >= 8] #*****
    elo_data = elo_data.sort_values(by='Elo Rating', ascending=False)
    
    elo_data["Position"] = range(1, len(elo_data) + 1)
    elo_data = elo_data[["Position", "Name", "Elo Rating", "Games"]] #reorder columns
    
    elo_data.to_csv('PADEL_ELO_RATINGS.csv', index=False)
    print('Elo Ratings File Updated!')
    
    return elo_data
    
                
            
    
def main():
    
    """
        Main function to execute the ELO rating update process.
    """
    
    data, ratings, games_count = read_elo_ratings(r'luca_model/Padel_Data.csv')
    ratings, games_count = update_ratings(data, ratings, games_count)
    create_elo_rating_file(ratings, games_count)
    


if __name__ == "__main__":
    main()
